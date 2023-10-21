import os
import django
from wallets.settings import REDIS

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wallets.settings")
django.setup()

from xrp.models import Deposits
from xrp.utils import Cache

# Create an instance of the Cache class





print(REDIS.get('deposits'))
