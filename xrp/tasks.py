import requests
import logging
from celery import shared_task
from .models import Deposits, Address, LastProcessedLedger
from decimal import Decimal, ROUND_HALF_UP
from wallets.settings import REDIS
from xrpl.models.requests.ledger import Ledger

logger = logging.getLogger(__name__)


@shared_task
def fetch_xrp_deposits():
    try:
        last_processed_ledger_obj, created = LastProcessedLedger.objects.get_or_create()
        last_processed_ledger = last_processed_ledger_obj.ledger

        next_ledger = last_processed_ledger + 1
        logger.warning(f"active ledger is {next_ledger}")

        # Fetch all addresses from the database
        addresses = Address.objects.values_list("address", flat=True)
        xrpscan_api_url = (
            f"https://api.xrpscan.com/api/v1/ledger/{next_ledger}/transactions"
        )

        try:
            response = requests.get(xrpscan_api_url)
            response.raise_for_status()  # Raise an exception if the request fails

            data = response.json()

            # Filter transactions for the fetched addresses
            filtered_transactions = [
                transaction
                for transaction in data
                if transaction.get("TransactionType") == "Payment"
                and transaction.get("Destination") in addresses
            ]

            # Process each filtered transaction
            for transaction in filtered_transactions:
                xrp_amount_str = transaction["Amount"]["value"]
                xrp_amount_decimal = Decimal(xrp_amount_str)
                exchange_rate = Decimal("0.50")
                usd_amount = xrp_amount_decimal * exchange_rate
                fiat = usd_amount.quantize(Decimal("0.00"), ROUND_HALF_UP)
                form_fiat = "{:.2f}".format(fiat / Decimal("1000000"))
                logger.warning(xrp_amount_decimal)
                logger.warning(form_fiat)

                Deposits.objects.create(
                    address=transaction["Destination"],
                    sender_address=transaction["Account"],
                    amount=xrp_amount_decimal / Decimal("1000000"),
                    amount_fiat=form_fiat,
                    coin=transaction["Amount"]["currency"],
                    confirmed=True,
                    txid=transaction["hash"],
                    ack=False,
                )
                logger.info(
                    f"New deposit created for address {transaction['Destination']}"
                )

            # Update the last processed ledger in the database
            last_processed_ledger_obj.ledger = next_ledger
            last_processed_ledger_obj.save()
        except Exception as e:
            logger.error(f"Request to XRPScan API failed: {str(e)}")

        if not addresses:
            logger.info("No addresses to process.")
    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")
