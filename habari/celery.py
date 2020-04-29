from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habari.settings')

app = Celery('habari')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

app.conf.beat_schedule = {
    'frequent_crawlers':{
    'task':'frequent_crawlers',
    'schedule':crontab(minute=0,hour='*/4'),
    },
    'non_frequent_crawlers':{
    'task':'non_frequent_crawlers',
    'schedule':crontab(minute=0,hour='*/6')
    },
    'bd_crawler':{
    'task':'bd_crawler',
    'schedule':crontab(minute=0,hour='*/5',day_of_week='1-5')
    },
    'retry_failed_crawls':{
    'task': 'retry_failed_crawls',
    'schedule': crontab(minute='*/30')
    },
    'sanitize_sm_author_field':{
    'task': 'sanitize_sm_author_lists_with_empty_strings',
    'schedule': crontab(minute='*/5')
    }

}