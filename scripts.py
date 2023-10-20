import os
import django
from wallets.settings import REDIS

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wallets.settings")
django.setup()

from xrp.models import Deposits
from xrp.utils import Cache

# Create an instance of the Cache class
cache_instance = Cache(
    Deposits, "deposits"
)  # Replace "your_template_name" with the actual template name

# Call the save_values method on the cache instance
cache_instance.save_values()

# Optionally, you can fetch the values and print them
cached_values = cache_instance.fetch_values()
print(cached_values)


cache = Cache(cls=Deposits, template="deposits")
print(cache.fetch_values())
print()
