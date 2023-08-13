from django.http import JsonResponse
from .models import Customer, Inbound, Client

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