from django.db import models
from wallets.settings import REDIS
import json
import logging

logger = logging.getLogger(__name__)
# Create your models here.
class Deposits(models.Model):
	address = models.CharField(max_length=75, blank=True, null=True)
	sender_address = models.CharField(max_length=75, blank=True, null=True)
	amount = models.DecimalField(decimal_places=8, max_digits=16, default=0.0, blank=True)
	amount_fiat = models.DecimalField(decimal_places=2, max_digits=8, default=0.0, blank=True)
	label = models.CharField(max_length=50, blank=True, null=True)
	cli_label = models.CharField(max_length=50, blank=True, null=True)
	category = models.CharField(max_length=50, blank=True, null=True)
	coin = models.CharField(max_length=50, blank=True, null=True)
	token = models.CharField(max_length=50, blank=True, null=True)
	created_at = models.DateTimeField(auto_created=True, auto_now_add=True)
	# transaction = models.ForeignKey("Transaction", on_delete=models.SET_NULL, blank=True, null=True)
	confirmed = models.BooleanField(default=False)
	double_spend = models.BooleanField(default=False)
	txid = models.CharField(max_length=100, blank=True, null=True)
	tx_link = models.CharField(max_length=300, blank=True, null=True)
	confirmations = models.PositiveIntegerField(default=0)
	ack = models.BooleanField(default=False)  # to notify if the webhook recipient has received the request

	def __str__(self):
		return self.coin


class Address(models.Model):
	coin = models.CharField(max_length=15, blank=True, null=True)
	safoa_byte = models.CharField(max_length=800, blank=True, null=True, unique=True)
	safoa = models.CharField(max_length=800, blank=True, null=True, unique=True)
	purpose = models.CharField(max_length=60, blank=True, null=True, unique=True)
	address = models.CharField(max_length=60, blank=True, null=True, unique=True)
	address_type = models.CharField(max_length=20, blank=True, null=True)
	label = models.CharField(max_length=50, blank=True, null=True)
	created_at = models.DateTimeField(auto_created=True, auto_now_add=True)
	locked = models.BooleanField(default=False)
	migrated = models.BooleanField(default=False)
	amount_owed = models.DecimalField(decimal_places=2, max_digits=8, default=0.0, blank=True)
	reason_for_lock = models.TextField(blank=True, null=True)

	def __str__(self):
		return self.address

	def save(self, *args, **kwargs):
		""" saving a cached list of all tron addresses, don't have a better way to do this"""
		if not self.id and self.coin == "trx":
			self.update_addresses(self.address)
		return super().save(*args, **kwargs)

	@staticmethod
	def fetch_tron_addresses():
		try:
			cached_list = REDIS.get("tron_address_list")
			if cached_list:
				cached_list = json.loads(cached_list)
				return cached_list
			else:
				all_tron = Address.objects.values("address").filter(coin="trx").exclude(address=None)
				cached_list = [address["address"] for address in all_tron]
				REDIS.set("tron_address_list", json.dumps(cached_list))
				return cached_list
		except Exception as e:
			logger.warning(str(e))
			return []

	def update_addresses(self, address):
		try:
			cached_list = REDIS.get("tron_address_list")
			if cached_list:
				cached_list = json.loads(cached_list)
			else:
				cached_list = self.fetch_tron_addresses()
			cached_list.append(address)
			REDIS.set("tron_address_list", json.dumps(cached_list))
		except Exception as e:
			logger.warning(str(e))



class LastProcessedLedger(models.Model):
    ledger = models.IntegerField(default=82398496)