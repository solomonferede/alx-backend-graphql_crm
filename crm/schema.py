# crm/schema.py
import re
import graphene
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


# =====================
# GraphQL Types
# =====================

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (relay.Node,)
        fields = "__all__"


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (relay.Node,)
        fields = "__all__"


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (relay.Node,)
        fields = "__all__"


# =====================
# Queries (Relay + Filters)
# =====================

class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(
        CustomerType,
        filterset_class=CustomerFilter
    )

    all_products = DjangoFilterConnectionField(
        ProductType,
        filterset_class=ProductFilter
    )

    all_orders = DjangoFilterConnectionField(
        OrderType,
        filterset_class=OrderFilter
    )


# =====================
# Mutations
# =====================

class CreateCustomer(graphene.Mutation):
    customer = graphene.Field(CustomerType)
    message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")

        if phone:
            phone_regex = r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$"
            if not re.match(phone_regex, phone):
                raise ValidationError("Invalid phone format")

        customer = Customer.objects.create(
            name=name,
            email=email,
            phone=phone
        )

        return CreateCustomer(
            customer=customer,
            message="Customer created successfully"
        )


# ---------- Bulk Create Customers ----------

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class BulkCreateCustomers(graphene.Mutation):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    def mutate(self, info, input):
        created = []
        errors = []

        for idx, data in enumerate(input):
            try:
                with transaction.atomic():
                    if Customer.objects.filter(email=data.email).exists():
                        raise ValidationError("Email already exists")

                    if data.phone:
                        phone_regex = r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$"
                        if not re.match(phone_regex, data.phone):
                            raise ValidationError("Invalid phone format")

                    customer = Customer.objects.create(
                        name=data.name,
                        email=data.email,
                        phone=data.phone
                    )
                    created.append(customer)

            except Exception as e:
                errors.append(f"Record {idx + 1}: {e}")

        return BulkCreateCustomers(customers=created, errors=errors)


# ---------- Create Product ----------

class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int()

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise ValidationError("Price must be positive")

        if stock < 0:
            raise ValidationError("Stock cannot be negative")

        product = Product.objects.create(
            name=name,
            price=price,
            stock=stock
        )

        return CreateProduct(product=product)


# ---------- Create Order ----------

class CreateOrder(graphene.Mutation):
    order = graphene.Field(OrderType)

    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)

    def mutate(self, info, customer_id, product_ids):
        if not product_ids:
            raise ValidationError("At least one product must be selected")

        try:
            customer = relay.Node.get_node_from_global_id(
                info, customer_id, only_type=CustomerType
            )
        except Exception:
            customer = None

        if not customer:
            raise ValidationError("Invalid customer ID")

        products = []
        for pid in product_ids:
            product = relay.Node.get_node_from_global_id(
                info, pid, only_type=ProductType
            )
            if not product:
                raise ValidationError("Invalid product ID")
            products.append(product)

        total = sum((p.price for p in products), Decimal("0.00"))

        with transaction.atomic():
            order = Order.objects.create(
                customer=customer,
                total_amount=total
            )
            order.products.set(products)

        return CreateOrder(order=order)


# =====================
# Root Mutation
# =====================

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
