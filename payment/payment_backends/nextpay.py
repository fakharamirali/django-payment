from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from requests import Response
from rest_framework.exceptions import ValidationError

from .base import BasePayPortalBackend
from ..decorator import register
from ..models import Transaction
from ..status import StatusChoices
from ..validators import complete_card_number_regex


@register
class NextpayBackend(BasePayPortalBackend):
    name = _("Nextpay")
    
    URLs = {
        'CREATE': "https://nextpay.org/nx/gateway/token",
        "VERIFY": "https://nextpay.org/nx/gateway/verify",
        "REFUND": "https://nextpay.org/nx/gateway/verify",
        "REDIRECT": "https://nextpay.org/nx/gateway/payment/{transaction.transaction_id}",
    }
    
    ERROR_MAPPING = {
        0: StatusChoices.SUCCESSFUL,
        -1: StatusChoices.WAIT_FOR_PAY,
        -2: StatusChoices.CANCELED_BY_USER,
        -3: StatusChoices.WAIT_FOR_BANK,
        -4: StatusChoices.CANCELED_BY_USER,
        -90: StatusChoices.REFUNDED,
        -91: StatusChoices.REFUND_FAILED,
        -92: StatusChoices.REFUND_FAILED,
        -93: StatusChoices.REFUND_FAILED_BY_LACK_OF_FUNDS,
    }
    
    @classmethod
    def get_create_context(cls, transaction: Transaction, **kwargs):
        context = {}
        if transaction.user:
            # Get phone Number
            if hasattr(transaction.user, "phone"):
                
                context['customer_phone'] = transaction.user.phone
            elif hasattr(transaction.user, 'get_phone'):
                phone = transaction.user.get_phone() if callable(
                    transaction.user.get_phone) else transaction.user.get_phone
                context['customer_phone'] = phone
            # Get Name
            context['payer_name'] = transaction.user.get_full_name()
        if kwargs.get('auto_verify'):
            context['auto_verify'] = kwargs['auto_verify']
        if kwargs.get("allowed_card"):
            if not complete_card_number_regex.match(kwargs['allowed_card']):
                raise ValidationError(_("Enter Valid card number"))
        return context
    
    def handle_verify(self, response: Response):
        data = response.json()
        status = self.ERROR_MAPPING.get(data["code"])
        if status is not None:
            self.transaction.status = status
        if status == StatusChoices.SUCCESSFUL:
            self.transaction.card_holder = data['card_holder']
            self.transaction.shaparak_tracking_code = data['Shaparak_Ref_Id']
        self.transaction.last_verify = now()
        self.transaction.save()
    
    def get_refund_context(self):
        context = self.get_verify_context()
        context['refund_request'] = 'yes_money_back'
        return context
    
    @classmethod
    def get_headers(cls, portal):
        return {
            'User-Agent': 'PostmanRuntime/7.26.8',
        }
