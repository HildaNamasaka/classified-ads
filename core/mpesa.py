import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
from django.core.exceptions import ImproperlyConfigured
from datetime import datetime
import base64
from decouple import config


def get_mpesa_token():
    consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', None)
    consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', None)

    if not consumer_key or not consumer_secret:
        raise ImproperlyConfigured('M-pesa credentials not defined in settings.py')

    token_url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    try:
        response = requests.get(token_url, auth=HTTPBasicAuth(consumer_key, consumer_secret), timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('access_token')
    
    except requests.exceptions.RequestException as e:
        print('mpesa token failed to generate', {e})
        return None
    
def normalize_phone_number(phone_number):
    if phone_number.startswith('0'):
        return '254' + phone_number[1:0]
    return phone_number

def stk_push(amount, phone_number):
    access_token = get_mpesa_token()
    phone_number = normalize_phone_number

    if access_token is None:
        return {'error' : 'Access token cannot be found'}    

    shortcode = getattr(settings, 'MPESA_SHORTCODE', None)
    passkey = getattr(settings, 'MPESA_PASSKEY', None)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    raw_password = f'{shortcode}{passkey}{timestamp}'
    password = base64.b64encode(raw_password.encode()).decode()

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": getattr(settings, 'MPESA_CALLBACK_URL', None),
        "AccountReference": "Order001",
        "TransactionDesc": "Payment for ad"
    }

    headers = {'Authorization' : f'Bearer {access_token}'}
    stk_url = f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
    try:
        response = requests.post(stk_url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f'stk push failed', {e})
        return('error', str(e))

