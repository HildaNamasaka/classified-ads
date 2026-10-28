from celery import shared_task
from .models import Transaction, TransactionStatus
from .mpesa import stk_query
from datetime import timedelta
from django.utils import timezone
from django.db import transaction as db_transaction
import requests

@shared_task
def reconcile_stale_payments():
    cut_off = timezone.now() - timedelta(minutes=3)
    stale_payments = Transaction.objects.filter(status = TransactionStatus.PENDING, created_at__lt=cut_off)
    for payment in stale_payments:
        check_stk_status.delay(payment.checkout_request_id)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def check_stk_status(self, checkout_request_id):
    if not Transaction.objects.filter(checkout_request_id=checkout_request_id, status=TransactionStatus.PENDING).exists():
        return

    result = stk_query(checkout_request_id)

    if 'error' in result:
        return
    with db_transaction.atomic():
        transaction_obj = Transaction.objects.select_for_update().filter(checkout_request_id=checkout_request_id, status=TransactionStatus.PENDING).first()
        result_code = result.get('ResultCode')
        result_desc = result.get('ResultDesc')
        transaction_obj.apply_result(result_code, result_desc)
    
    
   