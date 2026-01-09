import graphene

# Step 1: Define Query class
class Query(graphene.ObjectType):
    hello = graphene.String()

    # Step 2: Resolver for hello
    def resolve_hello(root, info):
        return "Hello, GraphQL!"

# Step 3: Create schema
schema = graphene.Schema(query=Query)
