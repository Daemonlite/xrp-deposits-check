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