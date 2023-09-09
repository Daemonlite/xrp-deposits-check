import requests
import logging
import json
from celery import shared_task
from .models import Deposits, Address

logger = logging.getLogger(__name__)

@shared_task
def fetch_xrp_deposits():
    try:
        addresses = Address.objects.all()

        for address in addresses:
            xrp_address = address.address
            xrpscan_api_url = "https://api.xrpscan.com/api/v1/ledger/82398497/transactions"

            response = requests.get(xrpscan_api_url)

            if response.status_code == 200:
                data = response.json()

                for transaction in data:
                    if (
                        transaction.get("TransactionType") == "Payment" and
                        transaction.get("Destination") == xrp_address
                    ):
                        Deposits.objects.create(
                            address=xrp_address,
                            sender_address=transaction["Account"],
                            amount=transaction["Amount"]["value"],
                            confirmed=True,
                            txid=transaction["hash"],
                        )
                        logger.info(f"New deposit created for address {xrp_address}")

            else:
                logger.error(f"Failed to fetch data for address {xrp_address}. Status code: {response.status_code}")

    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")
