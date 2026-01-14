import graphene
from graphene_django import DjangoObjectType
from crm.models import Product


# --------------------------------------------------
# Product Type
# --------------------------------------------------
class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "stock")


# --------------------------------------------------
# Mutation: UpdateLowStockProducts
# --------------------------------------------------
class UpdateLowStockProducts(graphene.Mutation):
    success = graphene.String()
    products = graphene.List(ProductType)

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []

        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated_products.append(product)

        return UpdateLowStockProducts(
            success="Low stock products updated successfully",
            products=updated_products,
        )


# --------------------------------------------------
# Root Query (can be empty if already defined elsewhere)
# --------------------------------------------------
class Query(graphene.ObjectType):
    pass


# --------------------------------------------------
# Root Mutation
# --------------------------------------------------
class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
