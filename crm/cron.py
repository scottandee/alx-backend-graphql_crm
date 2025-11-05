from datetime import datetime
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from cron_jobs.send_order_reminders import get_formatted_current_datetime


GRAPHQL_URL = "http://localhost:8000/graphql"


def log_crm_heartbeat():
    """
    This function defines a cron for the django-crontab
    It monitors the crm app and logs its status
    """
    # Establish connection to graphql endpoint
    transport = RequestsHTTPTransport(url=GRAPHQL_URL)
    client = Client(transport=transport)

    path_to_log_file = "/tmp/crm_heartbeat_log.txt"

    # Define and execute query
    query = gql(
        """
        {
            hello
        }
        """
    )

    try:
        result = client.execute(query)
    except Exception as e:
        with open(path_to_log_file, "a", encoding="utf-8") as f:
            current_time = get_formatted_current_datetime()
            f.write(f"{current_time} - hello query failed: {e}")
        return

    with open(path_to_log_file, "a", encoding="utf-8") as f:
        date = datetime.now().strftime("%d/%m/%y-%H:%M:%S")

        # Log status to tmp file
        f.write(f"{date} CRM is alive\n")
        f.write(f"{result}\n")


def update_low_stock():
    """
    This function executes an `UpdateLowStockProducts`
    mutation and logs the new stock levels with a timestanp.
    """
    # Establish connection to graphql endpoint
    transport = RequestsHTTPTransport(url=GRAPHQL_URL)
    client = Client(transport=transport)

    path_to_log_file = "/tmp/low_stock_updates_log.txt"

    # Define and execute query
    query = gql(
        """
        mutation {
          updateLowStockProducts {
            products {
              name
              stock
            }
          }
        }
        """
    )

    try:
        # Execute query
        response = client.execute(query)
    except Exception as e:
        # Log errors and terminate function
        with open(path_to_log_file, "a", encoding="utf-8") as f:
            current_time = get_formatted_current_datetime()
            message = f"{current_time} - UpdateLowStock query failed: {e}"
            f.write(message)
            print(message)
        return

    # extract products from response
    products = response.get('updateLowStockProducts').get('products')

    with open(path_to_log_file, "a", encoding="utf-8") as f:
        for p in products:
            current_time = get_formatted_current_datetime()
            p_name = p.get("name")
            p_stock = p.get("stock")

            # Log products and stock
            f.write(
                f"{current_time} - product_name={p_name} product_stock={p_stock}\n")

    print('Low product stock updated!')

