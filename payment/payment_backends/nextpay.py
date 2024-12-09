from django.utils.translation import gettext_lazy as _

from .base import BaseBackend
from ..decorator import register
from ..status import StatusChoices


@register
class NextpayBackend(BaseBackend):
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
    TRANSLATE_DICTIONARY = BaseBackend.TRANSLATE_DICTIONARY | {
        'shaparak_tracking_code': 'Shaparak_Ref_Id',
        'phone': 'customer_phone',
        'description': 'payer_desc'
    }
    REQUEST_FLAGS = [
        'allowed_card',
        'auto_verify',
        'phone',
        'description',

    ]

    def get_verify_context(self):
        return super().get_verify_context() | {
            'amount': self.transaction.amount,
            'currency': "IRR"
        }

    def get_refund_context(self):
        return self.get_verify_context() | {'refund_request': 'yes_money_back'}

    def get_headers(self):
        return {
            'User-Agent': 'PostmanRuntime/7.26.8',
        }

    def get_create_context(self, **kwargs):
        return super().get_create_context(**kwargs) | {'currency': 'IRR'}
