import requests
import logging
import json
from celery import shared_task
from .models import Deposits, Address
from decimal import Decimal

logger = logging.getLogger(__name__)

@shared_task
def fetch_xrp_deposits():
    ledger = 82398497
    try:
        addresses = Address.objects.all()
        for address in addresses:
            xrp_address = address.address
            xrpscan_api_url = f"https://api.xrpscan.com/api/v1/ledger/{ledger}/transactions"
            response = requests.get(xrpscan_api_url)
            if response.status_code == 200:
                data = response.json()
                for transaction in data:
                    if transaction.get("TransactionType") == "Payment" and transaction.get("Destination") == xrp_address:
                        xrp_amount_str = transaction["Amount"]["value"]
                        xrp_amount_decimal = Decimal(xrp_amount_str)
                        fiat = xrp_amount_decimal * Decimal("0.50")
                        
                        # Convert XRP amount to the desired format (2.410000)
                        formatted_amount = '{:.6f}'.format(xrp_amount_decimal / Decimal('1000000'))
                        
                        Deposits.objects.create(
                            address=transaction["Destination"],
                            sender_address=transaction["Account"],
                            amount=xrp_amount_decimal / Decimal('1000000'),  # Store the original amount for precise calculations if needed
                            amount_fiat=0.0,  # Set this to the appropriate fiat value if available.
                            coin=transaction["Amount"]["currency"],
                            confirmed=True,
                            txid=transaction["hash"],
                            ack=False,
                        )
                        logger.info(f"New deposit created for address {xrp_address}")

            else:
                logger.error(f"Failed to fetch data for address {xrp_address}. Status code: {response.status_code}")

    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")

