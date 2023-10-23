import os
import django
from wallets.settings import REDIS

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wallets.settings")
django.setup()


print(REDIS.get("deposits"))
