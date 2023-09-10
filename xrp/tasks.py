import requests
import logging
import json
from celery import shared_task
from .models import Deposits, Address
from decimal import Decimal

logger = logging.getLogger(__name__)

@shared_task
def fetch_xrp_deposits():
    ledger = 81699197
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
                        exchange_rate = Decimal("0.50")
                        usd_amount = xrp_amount_decimal * exchange_rate
                        fiat = round(usd_amount, 2)
                        form_fiat = '{:.2f}'.format(fiat / Decimal('1000000'))
                        logger.warning(xrp_amount_decimal )
                        logger.warning(form_fiat)
                        
                        Deposits.objects.create(
                            address=transaction["Destination"],
                            sender_address=transaction["Account"],
                            amount=xrp_amount_decimal / Decimal('1000000'),  
                            amount_fiat=form_fiat,
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

