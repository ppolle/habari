from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habari.settings')

app = Celery('habari')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

app.conf.beat_schedule = {
    'crawl-dn-articles': {  #name of the scheduler
        'task': 'dn_crawler',  # task name which we have created in tasks.py
        'schedule': 300.0,   # set the period of running
    }
}