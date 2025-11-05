from celery import shared_task
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
import requests


GRAPHQL_URL = "http://localhost:8000/graphql"


@shared_task()
def generate_crm_report():
    """
    This function generates a crm report from a graphql
    endpint and logs it.
    """
    # Establish connection to graphql endpoint
    transport = RequestsHTTPTransport(url=GRAPHQL_URL)
    client = Client(transport=transport)

    path_to_log_file = "/tmp/crm_report_log.txt"

    # Define and execute query
    query = gql(
        """
        query {
          stats {
            totalCustomers
            totalOrders
            totalRevenue
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
            curr_time = datetime.now().strftime("%d/%m/%y-%H:%M:%S")
            err_msg = f"{curr_time} - Report stats query failed: {e}"
            f.write(err_msg)
            print(err_msg)
        return

    # extract stats from response
    stats = response.get('stats')
    tc = stats.get("totalCustomers")
    to = stats.get("totalOrders")
    tr = stats.get("totalRevenue")

    with open(path_to_log_file, "a", encoding="utf-8") as f:
        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_msg = f"{curr_time} - Report {tc} customers, {to} orders, {tr} revenue."
        f.write(report_msg)

    print('Report generated successfully')

if __name__ == "__main__":
    generate_crm_report()