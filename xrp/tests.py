from django.test import TestCase
from decimal import Decimal
xrp_amount_str = '2.410000'
xrp_amount_decimal = Decimal(xrp_amount_str)

exchange_rate = Decimal("0.50")

usd_amount = xrp_amount_decimal * exchange_rate

print()