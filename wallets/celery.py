import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wallets.settings')

app = Celery('wallets')
app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()
app.conf.broker_url = 'redis://localhost:6379/2'
app.conf.result_backend = 'redis://localhost:6379/3'
app.conf.timezone = 'UTC'

app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'
app.conf.beat_schedule = {
    'Run every 20 seconds': {
        'task': 'xrp.tasks.fetch_xrp_deposits',
        'schedule': 20,   
    },
}