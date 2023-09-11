from .models import Address, Deposits,LastProcessedLedger
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_GET


@require_GET
@csrf_exempt
def get_deposits_by_address(request):
    data = json.loads(request.body)
    address = data["address"]
    deposits = Deposits.objects.filter(address=address).values()
    return JsonResponse(list(deposits), safe=False)

@require_GET    
@csrf_exempt
def get_last_processed_ledger(request):
    last_processed_ledger = LastProcessedLedger.objects.get().ledger
    return JsonResponse({"last_processed_ledger": last_processed_ledger})


@require_GET
@csrf_exempt
def get_all_addresses(request):
    addresses = Address.objects.values() 
    return JsonResponse(list(addresses), safe=False)