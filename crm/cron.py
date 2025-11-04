from datetime import datetime
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport


def log_crm_heartbeat():
    """
    This function defines a cron for the django-crontab
    It monitors the crm app and logs its status
    """
    # Establish connection to graphql endpoint
    transport = AIOHTTPTransport("http://localhost:8000/graphql")
    client = Client(transport=transport)

    # Define and execute query
    query = gql(
        """
        {
            hello
        }
        """
    )
    result = client.execute(query)

    path_to_file = "/tmp/crm_heartbeat_log.txt"
    with open(path_to_file, "a", encoding="utf-8") as f:
        date = datetime.now().strftime("%d/%m/%y-%H:%M:%S")

        # Log status to tmp file
        f.write(f"{date} CRM is alive\n")
        f.write(f"{result}\n")
