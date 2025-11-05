"""
Send Order Reminders

This script fetches all orders that were
created in the past 7 days and, logs reminders
for each of those orders.
"""
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta
import base64


def decode_relay_id(encoded_id):
    """
    This function decodes a base64 encoded string
    """
    decoded = base64.b64decode(encoded_id).decode("utf-8")
    return decoded.split(":")[1]


def fetch_orders():
    """
    This function fetches orders which were created
    in the past 7 days
    """
    grapql_url = "http://localhost:8000/graphql"
    order_date_range = (
        datetime.now() -
        timedelta(
            days=7)).strftime('%Y-%m-%d')

    # Create connection to url
    transport = RequestsHTTPTransport(url=grapql_url)
    client = Client(transport=transport)

    # Define query and pass order date range as variable
    query = gql(
        """
        query ($date: Date!){
        allOrders(orderDate_Gte: $date) {
        edges {
            node {
            id
            customer {
                email
            }
            }
        }
        }
    }
        """
    )
    variable = {"date": order_date_range}

    try:
        # Execute query
        response = client.execute(query, variable_values=variable)
    except Exception as e:
        print(f"GraphQL query failed: {e}")
        response = {}

    orders = response.get("allOrders", {}).get("edges", [])
    return orders


def get_formatted_current_datetime():
    """
    This function returns a formatted current datetime
    """
    return datetime.now().strftime("%d/%m/%y-%H:%M:%S")


def log_pending_orders(orders):
    """
    This script logs the the email and id of each order
    into the reminders log file
    """
    path_to_log_file = "/tmp/order_reminders_log.txt"

    if not orders:
        with open(path_to_log_file, 'a', encoding="utf-8") as f:
            current_time = get_formatted_current_datetime()
            f.write(f"{current_time}: No pending orders!\n")
    else:
        with open(path_to_log_file, 'a', encoding="utf-8") as f:
            for edge in orders:
                node = edge.get("node")
                order_id = decode_relay_id(node.get("id"))
                email = node.get("customer").get("email")
                if order_id:
                    current_time = get_formatted_current_datetime()
                    f.write(f"{current_time} - id={order_id} email={email}\n")
    print("Order reminders processed!")


if __name__ == "__main__":
    # Fetch orders
    orders = fetch_orders()

    # Log fetched orders
    log_pending_orders(orders=orders)
