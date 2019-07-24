import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habari.settings')

app = Celery('habari')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()