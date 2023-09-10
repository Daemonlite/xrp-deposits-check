import requests
import logging
from celery import shared_task
from .models import Deposits, Address, LastProcessedLedger
from decimal import Decimal
import time

logger = logging.getLogger(__name__)

@shared_task
def fetch_xrp_deposits():
    try:
        # Get the last processed ledger from the database
        last_processed_ledger_obj, created = LastProcessedLedger.objects.get_or_create()
        last_processed_ledger = last_processed_ledger_obj.ledger

        # Increment the ledger by one for the next fetch
        next_ledger = last_processed_ledger + 1
        logger.warning(f"next ledger is {next_ledger}")
        addresses = Address.objects.all()
        for address in addresses:
            xrp_address = address.address
            xrpscan_api_url = f"https://api.xrpscan.com/api/v1/ledger/{next_ledger}/transactions"
            
            try:
                response = requests.get(xrpscan_api_url)
                response.raise_for_status()  # Raise an exception if the request fails

                data = response.json()
                for transaction in data:
                    if transaction.get("TransactionType") == "Payment" and transaction.get("Destination") == xrp_address:
                        xrp_amount_str = transaction["Amount"]["value"]
                        xrp_amount_decimal = Decimal(xrp_amount_str)
                        exchange_rate = Decimal("0.50")
                        usd_amount = xrp_amount_decimal * exchange_rate
                        fiat = round(usd_amount, 2)
                        form_fiat = '{:.2f}'.format(fiat / Decimal('1000000'))
                        logger.warning(xrp_amount_decimal)
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

                # Update the last processed ledger in the database
                last_processed_ledger_obj.ledger = next_ledger
                last_processed_ledger_obj.save()
            except Exception as e:
                logger.error(f"Request to XRPScan API failed: {str(e)}")
            
            # Implement rate limiting to avoid overwhelming the API
            time.sleep(1)  # Sleep for 1 second before making the next request

        if not addresses:
            logger.info("No addresses to process.")

    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")
