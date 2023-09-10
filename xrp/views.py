from .models import Address, Deposits
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_GET

@csrf_exempt
def get_deposits_by_address(request):
    data = json.loads(request.body)
    if request.method == 'GET':
        address = data['address']
        deposits = Deposits.objects.filter(address=address)
        
        deposits_list = []
        for deposit in deposits:
            deposit_data = {
                "address": deposit.address,
                "sender_address": deposit.sender_address,
                "amount": deposit.amount,
                "coin": deposit.coin,
                "confirmed": deposit.confirmed,
                "txid": deposit.txid
            }
            deposits_list.append(deposit_data)

        return JsonResponse({"deposits": deposits_list})
    else:
        return JsonResponse({"error": "This endpoint only accepts GET requests."})
