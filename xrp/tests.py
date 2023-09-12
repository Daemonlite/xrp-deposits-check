from django.test import TestCase
from decimal import Decimal

from wallets.settings import REDIS


template = {
    "xrp": "xrp_address_list",
    "trx": "tron_address_list",
}

ledge = REDIS.get(template)

print(ledge )
