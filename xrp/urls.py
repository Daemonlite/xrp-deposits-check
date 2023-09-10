from django.urls import path
from .views import *

urlpatterns = [
  path('wallets_deposits/', get_deposits_by_address),
    
]