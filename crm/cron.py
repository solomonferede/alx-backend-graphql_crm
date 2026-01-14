from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/low_stock_updates_log.txt"


def update_low_stock():
    transport = RequestsHTTPTransport(
        url=GRAPHQL_ENDPOINT,
        verify=True,
        retries=3,
    )

    client = Client(
        transport=transport,
        fetch_schema_from_transport=True,
    )

    mutation = gql("""
    mutation {
      updateLowStockProducts {
        success
        products {
          name
          stock
        }
      }
    }
    """)

    result = client.execute(mutation)

    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    products = result.get("updateLowStockProducts", {}).get("products", [])

    with open(LOG_FILE, "a") as log:
        for product in products:
            log.write(
                f"[{timestamp}] Product: {product['name']}, New Stock: {product['stock']}\n"
            )
