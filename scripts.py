import os
import django
from wallets.settings import REDIS

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wallets.settings")
django.setup()

from xrp.models import Address

import requests








# if cached_value:
#     xrp_addresses = cached_value.decode('utf-8')  
#     print(xrp_addresses)
# else:
#     print("XRP addresses not found in the cache.")


import json

addresses = Address.fetch_addresses("xlm")
for address in addresses:
    print(address)



