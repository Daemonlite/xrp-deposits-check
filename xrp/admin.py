from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Deposits)
class DepositsAdmin(admin.ModelAdmin):
    list_display = ("coin", "confirmed", "amount", "amount_fiat", "txid", "ack")

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("coin", "safoa", "address", "label", "amount_owed", "migrated", "locked")

