import json
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
        
    if payment_code == '':
        response = json.loads(requests.request('POST', 'https://api.zarinpal.com/pg/v4/payment/request.json', data={
            'amount': plans_prices[plan] * 1000,
            'merchant_id': settings.ZARINPAL_MERCHANT_ID,
            'callback_url': f'https://{settings.SERVER_NAME}/api/verify-payment',
            'description': f'{settings.SERVER_NAME} ({firstname} - {lastname})',
        }).text)

        try:
            payment_code = response['data']['authority']
        except Exception:
            return JsonResponse({
                'message': 'failed to create payment',
                'amount': plans_prices[plan],
                'response': response.text,
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
        'authority': payment_code,
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
    authority = request.GET.get('Authority')
    try:
        customer = Customer.objects.get(payment_code=authority)
        if customer.verified:
            return JsonResponse({
                'message': 'already verified',
            }, status=409)
        
        response = json.loads(requests.request('POST', 'https://api.zarinpal.com/pg/v4/payment/verify.json', data={
            'amount': plans_prices[customer.plan] * 1000,
            'merchant_id': settings.ZARINPAL_MERCHANT_ID,
            'authority': authority,
        }).text)

        if response['data']['code'] == 100:
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