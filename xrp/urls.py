from django.urls import path
from .views import *

urlpatterns = [
  path('wallets_deposits/', get_deposits_by_address),
  path('all_addresses/', get_all_addresses),
    
]