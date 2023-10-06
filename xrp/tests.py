# @shared_task
# def fetch_xrp_deposits(ledger_index):
#     address = REDIS.get("xrp_address_list")
#     addresses = address

#     try:
#         xrpscan_api_url = f"https://api.xrpscan.com/api/v1/ledger/{ledger_index}/transactions"
#         response = requests.get(xrpscan_api_url)
#         response.raise_for_status()  # Raise an exception if the request fails
#         data = response.json()

#         # Create a list of addresses to filter in a single query
#         xrp_addresses = [address["address"] for address in addresses]

#         # Filter transactions in a single query
#         deposits_to_create = Deposits.objects.filter(
#             Q(TransactionType="Payment"),
#             Q(Destination__in=xrp_addresses),
#         ).values()

#         # Create Deposits objects from filtered data
#         deposits_objects = [
#             Deposits(
#                 address=transaction["Destination"],
#                 sender_address=transaction["Account"],
#                 amount=Decimal(transaction["Amount"]["value"]) / Decimal('1000000'),
#                 amount_fiat=Decimal('0.50') * Decimal(transaction["Amount"]["value"]) / Decimal('1000000'),
#                 coin=transaction["Amount"]["currency"],
#                 confirmed=True,
#                 txid=transaction["hash"],
#                 ack=False,
#             )
#             for transaction in deposits_to_create
#         ]

#         # Bulk create the Deposits objects
#         Deposits.objects.bulk_create(deposits_objects)
#         logger.info(f"Created {len(deposits_objects)} new deposits.")

#     except Exception as e:
#         logger.error(f"Request to XRPScan API failed: {str(e)}")

#     if not addresses:
#         logger.info("No addresses to process.")
