import requests
import logging
from celery import shared_task
from .models import Deposits
from decimal import Decimal, ROUND_HALF_UP
from wallets.settings import REDIS
import json

logger = logging.getLogger(__name__)


@shared_task
def fetch_xrp_deposits():
    try:
        ledge = REDIS.get("xrp_ledger")

        if ledge is not None:
            last_processed_ledger = int(ledge)
        else:
            last_processed_ledger = 82398495

        next_ledger = last_processed_ledger + 1
        logger.warning(f"active xrp ledger is {next_ledger}")

        # Fetch all addresses from the database
        cached_value = REDIS.get("xrp_address_list")
        addresses = json.loads(cached_value)
        logger.warning(addresses)

        xrpscan_api_url = (
            f"https://api.xrpscan.com/api/v1/ledger/{next_ledger}/transactions"
        )

        try:
            response = requests.get(xrpscan_api_url)

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

            last_processed_ledger = next_ledger
            REDIS.set("xrp_ledger", next_ledger)
        except Exception as e:
            logger.error(f"Request to XRPScan API failed: {str(e)}")

        if not addresses:
            logger.info("No addresses to process.")
    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")


@shared_task
def fetch_stellar_payments():
    try:
        last_processed_ledger = REDIS.get("stellar_ledger") or 48392304
        next_ledger = int(last_processed_ledger) + 1

        logger.warning(f"Active stellar ledger is {next_ledger}")

        cached_value = REDIS.get("xlm_address_list")
        addresses = json.loads(cached_value)
        logger.warning(addresses)

        stellar_api_url = "https://horizon.stellar.org/ledgers"

        ledgers_to_fetch = range(next_ledger, next_ledger + 5)
        ledger_data = []
        logger.warning(ledgers_to_fetch)

        for ledger in ledgers_to_fetch:
            ledger_url = f"{stellar_api_url}/{ledger}/payments"
            try:
                response = requests.get(ledger_url)
                data = response.json()
                ledger_data.append(data)
            except Exception as e:
                logger.error(
                    f"Request to Stellar Horizon API for ledger {ledger} failed: {str(e)}"
                )

        deposits_to_create = []

        for data in ledger_data:
            payments = data.get("_embedded", {}).get("records", [])

            for payment in payments:
                if payment["type"] == "payment" and payment["to"] in addresses:
                    txid = payment["transaction_hash"]

                    if Deposits.objects.filter(txid=txid).exists():
                        # A Deposits object with the same txid already exists, skip creating a new one
                        continue

                    sender = payment["from"]
                    destination = payment["to"]
                    xlm_amount_str = payment["amount"]
                    xlm_amount_decimal = Decimal(xlm_amount_str)
                    exchange_rate = Decimal("0.11")
                    usd_amount = xlm_amount_decimal * exchange_rate
                    fiat = usd_amount.quantize(Decimal("0.00"), ROUND_HALF_UP)
                    form_fiat = "{:.2f}".format(fiat)
                    logger.warning(xlm_amount_decimal)
                    logger.warning(form_fiat)

                    deposit = Deposits(
                        sender_address=sender,
                        address=destination,
                        amount=xlm_amount_decimal,
                        amount_fiat=form_fiat,
                        txid=txid,
                        confirmed=True,
                        coin="xlm",
                    )

                    deposits_to_create.append(deposit)

        # Bulk create deposits in the database
        if deposits_to_create:
            Deposits.objects.bulk_create(deposits_to_create)

        REDIS.set("stellar_ledger", next_ledger + 4)

    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")
