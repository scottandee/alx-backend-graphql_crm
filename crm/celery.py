from __future__ import unicode_literals, absolute_import
import os
from celery import Celery


# Set default django settings module for celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql.settings")

app = Celery('alx_backend_graphql')

app.config_from_object("django.conf:settings", namespace='CELERY')

# Autodiscover tasks in django app
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
