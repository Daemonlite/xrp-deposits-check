import requests
import logging
from celery import shared_task
from .models import Deposits, Address, LastProcessedLedger
from decimal import Decimal
import decimal
from wallets.settings import REDIS
from xrpl.clients import JsonRpcClient
from xrpl.models.requests.ledger import Ledger

logger = logging.getLogger(__name__)

@shared_task
def fetch_xrp_deposits():
    # Code for fetching the latest validated ledger index from XRPL node
    xrpl_client = JsonRpcClient("https://s1.ripple.com:51234") 
    latest_ledger_request = Ledger(ledger_index="validated")
    latest_ledger_response = xrpl_client.request(latest_ledger_request)

    if latest_ledger_response.is_successful():
        ledger_index = latest_ledger_response.result["ledger_index"]
        logger.warning(f"Latest Validated Ledger Index: {ledger_index}")
    else:
        logger.error(f"Error: {latest_ledger_response.status_message}")
        return

    addresses = Address.objects.values("address").iterator(chunk_size=100)
    for address in addresses:
        xrp_address = address["address"]  # Extract the address value
        xrpscan_api_url = f"https://api.xrpscan.com/api/v1/ledger/{ledger_index}/transactions"

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
