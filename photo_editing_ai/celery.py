import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photo_editing_ai.settings')

app = Celery('photo_editing_ai')

# Load Celery configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Specify the task module
app.autodiscover_tasks()
