import os

from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dating_site.settings')

app = Celery('dating_site')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'rating_sync': {
        'task': 'matcha.tasks.sync_rating',
        'schedule': crontab(hour='*', minute='*')  # /15
    },
    'reflexive_rating_sync': {
        'task': 'matcha.tasks.sync_relfexive_rating',
        'schedule': crontab(hour='*', minute='*')  # /15
    }
}
