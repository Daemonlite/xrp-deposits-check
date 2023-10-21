from django.db.models.signals import post_migrate
from django.dispatch import receiver

from xrp.utils import Cache
from xrp.models import Deposits


@receiver(post_migrate)
def my_callback(sender, **kwargs):
    cache = Cache(Deposits, "deposits")
    cache.handle_migrations()
    print("handled")
