from logging.config import dictConfig
import os

from celery import Celery
from celery.schedules import crontab
from celery.signals import setup_logging
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

@setup_logging.connect
def config_loggers(*args, **kwargs):
    dictConfig(settings.LOGGING)

app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Daily
    'flush_expired_tokens_daily': {
        'task': 'tokens.tasks.flush_expired_tokens',
        'schedule': crontab(minute=0, hour=0),  # Runs daily at midnight
    },

    # Weekly
    "update_restaurants_weekly": {
        "task": "restaurants.tasks.update_restaurants_task",
        "schedule": crontab(minute=0, hour=3, day_of_week=0),  # Runs every Sunday at 3 AM
    },
    "update_menu_items_weekly": {
        "task": "menu_items.tasks.update_menu_items_task",
        "schedule": crontab(minute=0, hour=3, day_of_week=1),  # Runs every Monday at 3 AM
    },

    # Biweekly
    "prune_restaurants_biweekly": {
        "task": "restaurants.tasks.prune_restaurants_task",
        "schedule": crontab(minute=0, hour=4, day_of_week="*/14"),  # Runs every two weeks on Sunday at 4 AM
    },
}
