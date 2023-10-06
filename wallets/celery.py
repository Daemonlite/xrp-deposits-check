import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wallets.settings')

app = Celery('wallets')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
app.conf.broker_url = 'redis://localhost:6379/6'
app.conf.result_backend = 'redis://localhost:6379/1'
app.conf.timezone = 'UTC'

app.conf.beat_schedule = {
    'run-every-2-seconds': {
        'task': 'xrp.tasks.fetch_xrp_deposits',
        'schedule': 2.0, 
        'options': {
            'expires': 15.0,
        },
    },
    'fetch_stellar_payments': {
        'task': 'xrp.tasks.fetch_stellar_payments',
        'schedule': 5.0,
        'options': {
            'expires': 15.0,
        }
    },
}
app.conf.timezone = 'UTC'