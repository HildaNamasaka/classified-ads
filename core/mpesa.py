import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
from django.core.exceptions import ImproperlyConfigured

def get_mpesa_token():
    consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', None)
    consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', None)

    if not consumer_key or not consumer_secret:
        raise ImproperlyConfigured('M-pesa credentials not defined in settings.py')

    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    try:
        response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret), timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('access_token')
    
    except requests.exceptions.RequestException as e:
        print('mpesa token failed to generate', {e})
        return None