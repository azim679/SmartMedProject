import os
from celery import Celery

# Set default settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartMed.settings')

app = Celery('SmartMed')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in installed Django apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
