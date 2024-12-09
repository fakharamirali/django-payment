from django.utils.translation import gettext_lazy as _

from payment import status
from payment.decorator import register
from payment.payment_backends import BaseBackend


@register
class ZibalBackend(BaseBackend):
    name = _('Zibal')
    API_KEY_NAME = 'merchant'
    TRANSACTION_ID_KEY_NAME = "trackId"

    def get_status(self, data: dict):
        return data.get('status') or data.get('result')

    URLS = {
        "CREATE": "https://gateway.zibal.ir/request/lazy",
        "AUTO_VERIFY_CREATE": "https://gateway.zibal.ir/v1/request",
        "VERIFY": "https://gateway.zibal.ir/v1/verify",
        "REDIRECT": "https://gateway.zibal.ir/start/{transaction.transaction_id}"
    }

    ERROR_MAPPING = {
        -1: status.StatusChoices.WAIT_FOR_PAY,
        1: status.StatusChoices.SUCCESSFUL,
        2: status.StatusChoices.WAIT_FOR_BANK,
        3: status.StatusChoices.CANCELED_BY_USER,
        4: status.StatusChoices.CARD_INVALID,
        5: status.StatusChoices.BALANCE_IS_NOT_ENOUGH_LIMIT,
        15: status.StatusChoices.REFUNDED,
        100: status.StatusChoices.WAIT_FOR_PAY,
        102: status.StatusChoices.API_KEY_INVALID,
        103: status.StatusChoices.API_KEY_INVALID,
        104: status.StatusChoices.API_KEY_INVALID,
        201: status.StatusChoices.SUCCESSFUL,
        202: status.StatusChoices.FAILED,
        203: status.StatusChoices.TRANSITION_ID_INVALID,
        114: status.StatusChoices.CANCELED
    }

    TRANSLATE_DICTIONARY = BaseBackend.TRANSLATE_DICTIONARY | {
        'phone': 'mobile',
        'allowed_card': 'allowedCards',
        'national_code': 'nationalCode',
        'check_mobile_number': 'checkMobileWithCard',
        'order_id': 'orderId',
        'shaparak_tracking_code': 'refNumber',
        'callback_uri': 'callbackUrl',
        'card_holder': 'cardNumber'
    }
