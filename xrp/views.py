from .models import Address, Deposits
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_GET
from wallets.settings import REDIS


@require_GET
@csrf_exempt
def get_deposits_by_address(request):
    data = json.loads(request.body)
    address = data["address"]
    deposits = Deposits.objects.filter(address=address).values()
    return JsonResponse(list(deposits), safe=False)




@require_GET
@csrf_exempt
def get_all_addresses(request):
    addresses = Address.objects.values() 
    return JsonResponse(list(addresses), safe=False)


