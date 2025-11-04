#!/bin/bash
#
# This script cleans inactive customers

command="
from crm.models import Customer
from datetime import datetime, timedelta

cutoff = datetime.now().date() - timedelta(days=365)
qs = Customer.objects.exclude(orders__order_date__gte=cutoff)
delete_count, _ = qs.delete()
print(delete_count)
"

# Execute delete query and store number of deleted customers
count=$(/home/scott/alx/alx_pdbe/graphql/bin/python3 manage.py shell -c "$command")

# Log number of customers deleted with timestamp
echo \"$(date +"%Y%m%d_%H%M%S"): $count Customers Deleted\" >>  /tmp/customer_cleanup_log.txt

