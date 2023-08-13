import json
import time
import uuid
import random
import logging
from django.conf import settings
from django.core.mail import send_mail
from .models import Customer, Inbound, Client
from django.core.exceptions import ObjectDoesNotExist
from django_apscheduler.jobstores import register_events
from django_apscheduler.models import DjangoJobExecution
from apscheduler.schedulers import SchedulerAlreadyRunningError
from apscheduler.schedulers.background import BackgroundScheduler


scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)
register_subject='Welcome to GameGuard VPN | Your Account Details Inside!'
with open('UserPanel/templates/registry_email.html', 'r') as f:
    register_html_message = f.read()


def create_account_for_verified_users():
    for customer in Customer.objects.filter(verified=True):
        total = int(customer.plan.split(' ')[3]) * (2 ** 30)
        expiry_time = (int(time.time() / 24 / 60 / 60) + int(customer.plan.split(' ')[0]) * 30) * 24 * 60 * 60 * 1000
        try:
            inbound = Inbound.objects.using('x-ui').get(remark=customer.name)
            inbound.expiry_time = expiry_time
            inbound.total += total
            inbound.enable = True
            inbound.save(using='x-ui')
        except ObjectDoesNotExist:
            port = random.randint(10000, 65535)
            while Inbound.objects.using('x-ui').filter(port=port).exists():
                port = random.randint(10000, 65535)
            email = f"{customer.name.split(' - ')[0]} ({customer.name})"

            inbound = Inbound.objects.using('x-ui').create(
                user_id=1, up=0, down=0, total=total, remark=customer.name, enable=True, expiry_time=expiry_time,
                autoreset=False, ip_alert=False, ip_limit=0, port=port, protocol='vless', settings=json.dumps({
                    'clients': [{
                        'id': str(uuid.uuid4()),
                        'email': email,
                        'flow': '',
                        'fingerprint': 'chrome',
                        'total': 0,
                        'expiryTime': 0
                    }],
                    'decryption': 'none',
                    'fallbacks': []
                }, indent=2), stream_settings=json.dumps({
                    'network': 'ws',
                    'security': 'tls',
                    'tlsSettings': {
                        'serverName': settings.SERVER_NAME,
                        'minVersion': '1.2',
                        'maxVersion': '1.3',
                        'cipherSuites': '',
                        'certificates': [{
                            'ocspStapling': 36000,
                            'certificateFile': '/root/cert.crt',
                            'keyFile': '/root/private.key'
                        }],
                        'alpn': ['h2', 'http/1.1']
                    },
                    'wsSettings': {
                        'path': '/',
                        'headers': {},
                        'acceptProxyProtocol': False
                    }
                }, indent=2), tag=f'inbound-{port}', sniffing=json.dumps({
                    'enabled': True,
                    'destOverride': ['http', 'tls']
                }, indent=2)
            )
            Client.objects.using('x-ui').create(
                inbound_id=inbound.id, enable=True, email=email, up=0, down=0, total=0, expiry_time=0
            )

        if customer.email != 'provided during registration':
            user_data = json.loads(inbound.settings)['clients'][0]
            user_name = user_data['email'].split(' (')[0].replace(' ', '')
            server_name = json.loads(inbound.stream_settings)['tlsSettings']['serverName']
            link = f"vless://{user_data['id']}@{server_name}:{inbound.port}?type=ws&security=tls&path=%2F&sni={server_name}&fp=chrome#{user_name}"

            send_mail(
                subject=register_subject, message=None, from_email=None, recipient_list=[customer.email],
                html_message=register_html_message % (customer.name.replace(' - ', ' '), link)
            )

        customer.delete()

def delete_old_jobs_executions(max_age=3*24*60*60):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

def delete_expired_users(max_age=3*24*60*60):
    for inbound in Inbound.objects.using('x-ui').filter(expiry_time__lt=int((time.time() - max_age) * 1000), expiry_time__gt=0):
        Client.objects.using('x-ui').filter(inbound_id=inbound.id).delete()
        inbound.delete()

def start():
    if settings.DEBUG:
        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    scheduler.add_job(
        create_account_for_verified_users, 'cron', minute='*/15',
        id='create_account_for_verified_users', replace_existing=True, misfire_grace_time=None
    )
    logging.info('Added job : create_account_for_verified_users')
    scheduler.add_job(
        delete_old_jobs_executions, 'cron', hour=0,
        id='delete_old_jobs_executions', replace_existing=True, misfire_grace_time=None
    )
    logging.info('Added job : delete_old_jobs_executions')
    scheduler.add_job(
        delete_expired_users, 'cron', hour=0,
        id='delete_expired_users', replace_existing=True, misfire_grace_time=None
    )
    logging.info('Added job : delete_expired_users')

    register_events(scheduler)
    try:
        logging.info('Scheduler started!')
        scheduler.start()
    except KeyboardInterrupt:
        logging.info('Scheduler stopped manually!')
        scheduler.shutdown()
        logging.info('Scheduler shutdown!')
    except SchedulerAlreadyRunningError:
        logging.info('Scheduler already running!')