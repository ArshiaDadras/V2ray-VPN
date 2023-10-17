import json
import uuid
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from .models import Customer, Inbound, Client

plans_prices = {
    '1 Month - 10 GB': 80,
    '3 Month - 30 GB': 190,
    '1 Month - 30 GB': 150,
    '3 Month - 90 GB': 420,
    '1 Month - 50 GB': 225,
    '3 Month - 150 GB': 630,
    '1 Month - 80 GB': 320,
    '3 Month - 240 GB': 900,
    '1 Month - 120 GB': 420,
    '3 Month - 360 GB': 1150,
}

def add_customer(request):
    destination_card = request.POST.get('destination_card')
    payment_code = request.POST.get('payment_code')
    firstname = request.POST.get('firstname')
    lastname = request.POST.get('lastname')
    mobile = request.POST.get('mobile')
    email = request.POST.get('email')
    plan = request.POST.get('plan')

    try:
        Inbound.objects.using('x-ui').get(remark=f'{firstname} - {lastname}')

        if mobile and email:
            return JsonResponse({
                'message': 'customer already exists',
            }, status=409)
        
        mobile = email = 'provided during registration'
    except Exception:
        if not mobile and not email:
            return JsonResponse({
                'message': 'customer not found',
            }, status=404)
        
        if Customer.objects.count() + Inbound.objects.using('x-ui').count() >= 50:
            return JsonResponse({
                'message': 'registration is banned',
            }, status=403)
        
    if destination_card == 'NextPay':
        response = requests.request('POST', 'https://nextpay.org/nx/gateway/token', data={
            'api_key': settings.NEXTPAY_API_KEY,
            'order_id': uuid.uuid4().hex,
            'amount': plans_prices[plan] * 1000,
            'callback_url': f'https://{settings.SERVER_NAME}/api/verify-payment',
            'payer_name': f'{firstname} - {lastname}',
            'payer_desc': f'{settings.SERVER_NAME} - {plan}',
        }).text

        try:
            payment_code = json.loads(response)['trans_id']
        except Exception:
            return JsonResponse({
                'message': 'failed to create payment',
                'amount': plans_prices[plan],
                'response': response,
            }, status=400)

    customer = Customer(name=firstname+' - '+lastname,
                        payment_code=payment_code,
                        destination_card=destination_card,
                        mobile=mobile,
                        email=email,
                        plan=plan)

    try:
        customer.save()
    except Exception as e:
        return JsonResponse({
            'message': str(e),
        }, status=500)

    return JsonResponse({
        'message': 'customer created',
        'payment_code': payment_code,
    })

def customer_data(request):
    firstname = request.POST.get('firstname')
    lastname = request.POST.get('lastname')

    try:
        customer = Customer.objects.get(name=f'{firstname} - {lastname}')
    except Exception:
        customer = None

    try:
        inbound = Inbound.objects.using('x-ui').get(remark=f'{firstname} - {lastname}')
    except Exception:
        inbound = None

    if inbound:
        clients = Client.objects.using('x-ui').filter(inbound_id=inbound.id)

        return JsonResponse({
            'message': 'done!',
            'user_type': 'registered',
            'data': inbound.to_json(),
            'clients': [
                client.to_json() for client in clients
            ],
            'order': customer.to_json() if customer else None,
        })
    
    if customer:
        return JsonResponse({
            'message': 'done!',
            'user_type': 'waitlist',
            'data': customer.to_json(),
        })
    
    return JsonResponse({
        'message': 'customer not found',
    }, status=404)

def verify_payment(request):
    trans_id = request.GET.get('trans_id')
    try:
        customer = Customer.objects.get(payment_code=trans_id)
        if customer.verified:
            return JsonResponse({
                'message': 'already verified',
            }, status=409)
        
        response = requests.request('POST', 'https://nextpay.org/nx/gateway/verify', data={
            'api_key': settings.NEXTPAY_API_KEY,
            'trans_id': trans_id,
            'amount': plans_prices[customer.plan] * 1000,
        }).text

        if json.loads(response)['code'] == 0:
            customer.verified = True
            customer.save()
        else:
            return JsonResponse({
                'message': 'payment failed',
                'response': response,
            }, status=400)
    except Exception:
        pass

    return redirect('main')