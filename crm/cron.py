from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"


# --------------------------------------------------
# 1. Heartbeat Logger (EVERY 5 MINUTES)
# --------------------------------------------------
def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    try:
        transport = RequestsHTTPTransport(
            url=GRAPHQL_ENDPOINT,
            verify=True,
            retries=3,
        )

        client = Client(
            transport=transport,
            fetch_schema_from_transport=True,
        )

        query = gql("""
        query {
          hello
        }
        """)

        client.execute(query)
        message += " | GraphQL OK"

    except Exception:
        message += " | GraphQL ERROR"

    with open("/tmp/crm_heartbeat_log.txt", "a") as log:
        log.write(message + "\n")


# --------------------------------------------------
# 2. Low-Stock Product Updater (EVERY 12 HOURS)
# --------------------------------------------------
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

    with open("/tmp/low_stock_updates_log.txt", "a") as log:
        for product in products:
            log.write(
                f"[{timestamp}] Product: {product['name']}, New Stock: {product['stock']}\n"
            )
