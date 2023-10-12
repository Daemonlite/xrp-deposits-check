# @shared_task
# def fetch_stellar_payments():
#     try:
#         last_processed_ledger_obj, created = StellerLedger.objects.get_or_create()
#         last_processed_ledger = last_processed_ledger_obj.ledger
      
#         next_ledger = last_processed_ledger + 1
#         logger.warning(f"active stellar ledger is {next_ledger}")
        
#         addresses = Address.objects.values_list("address", flat=True)
#         # Define the Stellar Horizon API endpoint
#         stellar_api_url = f"https://horizon.stellar.org/ledgers/{next_ledger}/payments"

#         try:
#             response = requests.get(stellar_api_url)

#             data = response.json()

#             # Filter payments from the response
#             payments = data['_embedded']['records']

#             # Process each payment
#             for payment in payments:
#                 if payment['type'] == 'payment' and payment['to'] in addresses:
#                     sender = payment['from']
#                     destination = payment['to']
#                     xlm_amount_str = payment['amount']
#                     xlm_amount_decimal = Decimal(xlm_amount_str)
#                     exchange_rate = Decimal("0.11")
#                     usd_amount = xlm_amount_decimal * exchange_rate
#                     fiat = usd_amount.quantize(Decimal("0.00"), ROUND_HALF_UP)
#                     form_fiat = "{:.2f}".format(fiat)
#                     logger.warning(xlm_amount_decimal)
#                     logger.warning(form_fiat)

#                     Deposits.objects.create(
#                         sender_address=sender,
#                         address=destination,
#                         amount=xlm_amount_decimal,
#                         amount_fiat=form_fiat,
#                         txid=payment['transaction_hash'],
#                         confirmed=True,
#                         coin='stellar(xlm)',
#                     )

#             # Update the last processed ledger in the database
#             last_processed_ledger_obj.ledger = next_ledger
#             last_processed_ledger_obj.save()

#         except Exception as e:
#             logger.error(f"Request to Stellar Horizon API failed: {str(e)}")

#     except Exception as e:
#         logger.exception(f"An error occurred: {str(e)}")


# import json
# from decimal import Decimal
# import requests
# from concurrent.futures import ThreadPoolExecutor
# from django.db import transaction
# from yourapp.models import Deposits  # Import your Django model

# @shared_task
# def fetch_stellar_payments():
#     try:
#         last_processed_ledger = REDIS.get("stellar_ledger") or 48392304
#         next_ledger = int(last_processed_ledger) + 1

#         cached_value = REDIS.get("xlm_address_list")
#         addresses = json.loads(cached_value)
#         logger.warning(addresses)

#         stellar_api_url = "https://horizon.stellar.org/ledgers"

#         ledgers_to_fetch = range(next_ledger, next_ledger + 5)
#         ledger_data = []
#         logger.warning(ledgers_to_fetch)

#         # Define a function to fetch ledger data
#         def fetch_ledger_data(ledger):
#             ledger_url = f"{stellar_api_url}/{ledger}/payments"
#             try:
#                 response = requests.get(ledger_url)
#                 data = response.json()
#                 return data
#             except Exception as e:
#                 logger.error(f"Request to Stellar Horizon API for ledger {ledger} failed: {str(e)}")
#                 return None

#         # Use a ThreadPoolExecutor to fetch ledger data in parallel
#         with ThreadPoolExecutor(max_workers=5) as executor:
#             ledger_data = list(executor.map(fetch_ledger_data, ledgers_to_fetch))

#         deposits_to_create = []

#         for data in ledger_data:
#             if data is None:
#                 continue  # Skip processing for failed requests

#             payments = data.get("_embedded", {}).get("records", [])

#             for payment in payments:
#                 if payment["type"] == "payment" and payment["to"] in addresses:
#                     txid = payment["transaction_hash"]

#                     if Deposits.objects.filter(txid=txid).exists():
#                         # A Deposits object with the same txid already exists, skip creating a new one
#                         continue

#                     sender = payment["from"]
#                     destination = payment["to"]
#                     xlm_amount_str = payment["amount"]
#                     xlm_amount_decimal = Decimal(xlm_amount_str)
#                     exchange_rate = Decimal("0.11")
#                     usd_amount = xlm_amount_decimal * exchange_rate
#                     fiat = usd_amount.quantize(Decimal("0.00"))
#                     form_fiat = "{:.2f}".format(fiat)
#                     logger.warning(xlm_amount_decimal)
#                     logger.warning(form_fiat)

#                     deposit = Deposits(
#                         sender_address=sender,
#                         address=destination,
#                         amount=xlm_amount_decimal,
#                         amount_fiat=form_fiat,
#                         txid=txid,
#                         confirmed=True,
#                         coin="xlm",
#                     )

#                     deposits_to_create.append(deposit)

#         # Bulk create deposits in the database within a transaction
#         if deposits_to_create:
#             with transaction.atomic():
#                 Deposits.objects.bulk_create(deposits_to_create)

#         REDIS.set("stellar_ledger", next_ledger + 4)

#     except Exception as e:
#         logger.warning(f"An error occurred: {str(e)}")
