import requests
import logging
from celery import shared_task
from .models import Deposits, Address, LastProcessedLedger
from decimal import Decimal
import decimal
from wallets.settings import REDIS
from xrpl.clients import WebsocketClient
from xrpl.models import Subscribe, StreamParameter

logger = logging.getLogger(__name__)

@shared_task
def fetch_xrp_deposits():
    url = "wss://s.altnet.rippletest.net/"
    try:
        req = Subscribe(streams=[StreamParameter.LEDGER])
        with WebsocketClient(url) as client:
            client.send(req)
            for message in client:
                if "ledger_index" in message:
                    ledger = message["ledger_index"]
                    logger.warning(f"Current ledger is {ledger}")
                    break  # Exit the loop after obtaining the ledger value

        if ledger is None:
            logger.warning("No ledger information received. Exiting.")
            return

        addresses = Address.objects.values("address").iterator(chunk_size=100)
        for address in addresses:
            xrp_address = address["address"]  # Extract the address value
            xrpscan_api_url = f"https://api.xrpscan.com/api/v1/ledger/{ledger}/transactions"

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
                        fiat = usd_amount.quantize(Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)
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

            except Exception as e:
                logger.error(f"Request to XRPScan API failed: {str(e)}")

        if not addresses:
            logger.info("No addresses to process.")

    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")
