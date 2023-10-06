import requests
import logging
from celery import shared_task
from .models import Deposits, Address, LastProcessedLedger,StellerLedger
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
        logger.warning(f"active xrp ledger is {next_ledger}")

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


@shared_task
def fetch_stellar_payments():
    try:
        last_processed_ledger_obj, created = StellerLedger.objects.get_or_create()
        last_processed_ledger = last_processed_ledger_obj.ledger
      
        next_ledger = last_processed_ledger + 1
        logger.warning(f"active stellar ledger is {next_ledger}")
        
        addresses = Address.objects.values_list("address", flat=True)
        # Define the Stellar Horizon API endpoint
        stellar_api_url = f"https://horizon.stellar.org/ledgers/{next_ledger}/payments"

        try:
            response = requests.get(stellar_api_url)
            response.raise_for_status()

            data = response.json()

            # Filter payments from the response
            payments = data['_embedded']['records']

            # Process each payment
            for payment in payments:
                if payment['type'] == 'payment' and payment['to'] in addresses:
                    sender = payment['from']
                    destination = payment['to']
                    xlm_amount_str = payment['amount']
                    xlm_amount_decimal = Decimal(xlm_amount_str)
                    exchange_rate = Decimal("9.00")
                    usd_amount = xlm_amount_decimal * exchange_rate
                    fiat = usd_amount.quantize(Decimal("0.00"), ROUND_HALF_UP)
                    form_fiat = "{:.2f}".format(fiat / Decimal("1000000"))

                    Deposits.objects.create(
                        sender=sender,
                        address=destination,
                        amount=xlm_amount_decimal / Decimal("1000000"),
                        amount_fiat=form_fiat,
                        txid=payment['transaction_hash'],
                        confirmed=True,
                        coin='stellar(xlm)',
                    )

            # Update the last processed ledger in the database
            last_processed_ledger_obj.ledger = next_ledger
            last_processed_ledger_obj.save()

        except Exception as e:
            logger.error(f"Request to Stellar Horizon API failed: {str(e)}")

    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")


        