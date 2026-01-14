from datetime import datetime
from celery import shared_task
from gql import gql, Client
import requests
from gql.transport.requests import RequestsHTTPTransport

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/crm_report_log.txt"


@shared_task
def generate_crm_report():
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
      customers {
        id
      }
      orders {
        id
        totalAmount
      }
    }
    """)

    result = client.execute(query)

    customers_count = len(result.get("customers", []))
    orders = result.get("orders", [])
    orders_count = len(orders)
    total_revenue = sum(order.get("totalAmount", 0) for order in orders)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a") as log:
        log.write(
            f"{timestamp} - Report: {customers_count} customers, "
            f"{orders_count} orders, {total_revenue} revenue\n"
        )
