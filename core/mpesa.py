import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
from django.core.exceptions import ImproperlyConfigured
from datetime import datetime
import base64

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from.models import Transaction
from rest_framework.permissions import AllowAny
from django.db import transaction as db_transaction

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

def stk_push(access_token, amount, phone_number):
    access_token = get_mpesa_token()
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
    url= "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    try:
        response = requests.get(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f'stk push failed', {e})
        return('error', str(e))

class MpesaCallback(APIView):
    permission_classes= [AllowAny]

    def post(self, request):
        callback_data = request.data.get('Body', {}).get('stkCallback', {})

        checkout_request_id = callback_data.get("CheckoutRequestID")
        result_code = callback_data.get('ResultCode')
        result_desc = callback_data.get('ResultDesc')

        with db_transaction.atomic():
            transaction_obj = Transaction.objects.select_for_update().filter(checkout_request_id=checkout_request_id)

            if transaction_obj is None:
                return Response({'ResultCode' : 0, 'ResultDesc':'Accepted'}, status=status.HTTP_200_OK)

            if result_code == 0:
                metadata = callback_data.get('CallbackMetadata', {}).get('Item')
                values = {item['name'] : item.get('value') for item in metadata}

                if transaction_obj.status in ['success', 'failed']:
                    return Response({'ResultCode' : 0, 'ResultDesc' : 'Already processed'}, status=status.HTTP_200_OK)

                transaction_obj.status = 'success'
                transaction_obj.mpesa_receipt_number = values.get('MpesaReceiptNumber')
                transaction_obj.save()
            else:
                transaction_obj.status = 'failed'
                transaction_obj.result_desc = result_desc
                transaction_obj.save()
        return Response({'ResultCode' : 0, 'ResultDesc':'Accepted'}, status=status.HTTP_200_OK)