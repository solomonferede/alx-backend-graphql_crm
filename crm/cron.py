from datetime import datetime
import requests

LOG_FILE = "/tmp/crm_heartbeat_log.txt"
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    # Optional GraphQL health check
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            json={"query": "{ hello }"},
            timeout=5
        )
        if response.status_code == 200:
            message += " | GraphQL OK"
        else:
            message += " | GraphQL ERROR"
    except Exception:
        message += " | GraphQL UNREACHABLE"

    with open(LOG_FILE, "a") as log:
        log.write(message + "\n")
