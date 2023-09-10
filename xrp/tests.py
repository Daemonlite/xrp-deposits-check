from django.test import TestCase
from decimal import Decimal

from wallets.settings import REDIS

last_processed_ledger = 81699196

last_processed_ledger = REDIS.set("last_processed_ledger",int(last_processed_ledger))

ledge = REDIS.get("last_processed_ledger")

print(ledge + 1)
