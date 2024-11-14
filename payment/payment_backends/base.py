import logging

import requests
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from requests import Response

from payment import signals
from payment.exceptions import FailedPaymentError
from payment.models import Transaction
from payment.status import FAIL_MESSAGES, HARD_FAILED_STATUSES, StatusChoices

__all__ = ['BasePayPortalBackend']

User = get_user_model()
logger = logging.getLogger(__name__)


class BasePayPortalBackend:
    @classmethod
    def support_refund(cls):
        return cls.URLS.get('REFUND') is not None

    name = None
    URLS = {}
    ERROR_MAPPING = {}
    TRANSLATE_DICTIONARY = {
        'card_holder': 'card_holder',
        'allowed_card': 'allowed_card',
        'auto_verify': 'auto_verify',
        'phone': 'phone',
        'shaparak_tracking_code': 'shaparak_tracking_code',
        'national_code': 'national_code',
        'check_mobile_number': 'check_mobile_number',
        'callback_uri': 'callback_uri',
        'amount': 'amount',
        'order_id': 'order_id',
        'description': 'description'
    }
    REQUEST_FLAGS = [
        'allowed_card',
        'auto_verify',
        'phone',
        'national_code',
        'check_mobile_number',
        'description'
    ]
    RECEIVING_FLAGS = [
        'card_holder',
        'shaparak_tracking_code',
    ]

    # API Key in pay portal send to pay portal by this key name
    # Must override if pay portal use other key name
    API_KEY_NAME = "api_key"

    # Transaction ID send to pay portal by this key name
    # Must override
    TRANSACTION_ID_KEY_NAME = 'trans_id'
    STATUS_FIELD = 'code'

    def __init__(self, transaction: Transaction):
        self.transaction = transaction

    # ------------------------------------- CREATE ------------------------------------------------

    def create(self, callback_url, **kwargs) -> None:

        signals.pre_create_transaction.send(self.__class__, transaction=self.transaction, callback_uri=callback_url)
        response = self.send_create_request(callback_url, **kwargs)
        if not response.ok:
            signals.create_transaction_failed.send(self.__class__, request=response, transaction=self.transaction)
            raise FailedPaymentError
        self.handle_create(response)
        signals.post_create_transaction.send(self.__class__, transaction=self.transaction)

    def handle_create(self, response: Response):
        """
        This method for handle response status of create request
        Must override in children or define error mapping
        This method receive response and return status
        Also you can do some process in function body
        :param: obj: Transaction
        :param: response: Response
        :return: StatusChoices
        """
        if not self.ERROR_MAPPING:
            if self.transaction.pk:
                self.transaction.delete()
            raise NotImplementedError

        result = response.json()
        self.transaction.status = self.ERROR_MAPPING.get(self.get_status(result), StatusChoices.FAILED)

        if self.transaction.status is None or self.transaction.status in HARD_FAILED_STATUSES:
            if self.transaction.pk:
                self.transaction.delete()
            if self.transaction is None:
                raise ValueError("Uncaught code")
            raise FailedPaymentError(FAIL_MESSAGES[self.transaction.status])
        self.transaction.transaction_id = result[self.TRANSACTION_ID_KEY_NAME]
        self.transaction.save()

    def send_create_request(self, callback_uri, **kwargs) -> Response:

        if not self.URLS.get("CREATE"):
            raise NotImplementedError("Define URLs['CREATE'] or override .send_create_request()")
        else:
            url = self.URLS["CREATE"]
        if kwargs.get('auto_verify') and 'AUTO_VERIFY_CREATE' in self.URLS:
            url = self.URLS["AUTO_VERIFY_CREATE"]
            kwargs.pop('auto_verify')

        try:
            URLValidator()(callback_uri)
        except ValidationError:
            raise ValueError("Callback URL is incorrect")
        self.transaction.locate_id()
        order_suffix = self.transaction.portal.order_id_prefix or self.transaction.portal.code_name
        data = {
            self.API_KEY_NAME: str(self.transaction.portal.api_key),
            self.translate_flag('order_id'): f"{order_suffix}_{self.transaction.id}",
            self.translate_flag('amount'): self.transaction.amount,
            self.translate_flag('callback_uri'): callback_uri,
            **self.get_create_context(**kwargs)
        }
        params = {
            'url': url,
            'json': data,
        }
        if headers := self.get_headers():
            params['headers'] = headers
        response = requests.post(**params)
        return response

    def get_create_context(self, **kwargs):
        """
        This function get transaction and return data that will send additional to default data
        :return: A dict include additional data to send to pay portal
        """
        context = {}
        for flag in self.REQUEST_FLAGS:
            value = None
            if flag in kwargs:
                value = kwargs[flag]
            elif hasattr(self.transaction, flag):
                value = getattr(self.transaction, flag)
            elif self.transaction.user:
                if hasattr(self.transaction.user, flag):
                    value = getattr(self.transaction.user, flag)
                elif hasattr(self.transaction.user, "get_" + flag) and callable(
                        getattr(self.transaction.user, 'get_' + flag)):
                    value = getattr(self.transaction.user, "get_" + flag)()
            if value is not None:
                translated_flag = self.translate_flag(flag)
                context[translated_flag] = value

        return context

    # ------------------------------------ END CREATE ------------------------------------------

    # -------------------------------------- VERIFY --------------------------------------------

    def verify_transaction(self):
        signals.pre_verify_transaction.send(self.__class__, transaction=self.transaction)
        response = self.send_verify_request()
        self.handle_verify(response)
        signals.post_verify_transaction.send(self.__class__, transaction=self.transaction)
        return self.transaction

    def handle_verify(self, response: Response):
        """
        This method for handle response status of verify request
        Must override in children or define error mapping
        This method receive response and return status
        Also you can do some process in function body
        :param: response: Response
        :return: StatusChoices
        """
        if not self.ERROR_MAPPING:
            raise NotImplementedError
        data: dict = response.json()
        status = self.ERROR_MAPPING.get(self.get_status(data))
        if status is None:
            raise FailedPaymentError(status)
        self.transaction.status = status
        self.apply_to_transaction(data=data)
        self.transaction.last_verify = now()
        self.transaction.save()

    def send_verify_request(self) -> Response:
        if not self.URLS.get('VERIFY'):
            raise NotImplementedError("Define URLs['VERIFY'] or override .send_verify_request()")
        data = self.get_verify_context()
        return requests.post(self.URLS['VERIFY'], json=data, headers=self.get_headers())

    def get_verify_context(self):
        return {
            self.API_KEY_NAME: self.transaction.portal.api_key,
            self.TRANSACTION_ID_KEY_NAME: self.transaction.transaction_id
        }

    # ----------------------------------- END VERIFY -------------------------------------------

    # ------------------------------------ REFUND -----------------------------------------------

    def refund_transaction(self):
        signals.pre_refund_transaction.send(self.__class__, transaction=self.transaction)
        response = self.send_refund_request()
        self.handle_refund(response)
        signals.post_refund_transaction.send(self.__class__, transaction=self.transaction, response=response)
        return self.transaction

    def handle_refund(self, response: Response):
        """
        This method for handle response status of refund request
        Must override in children or define error mapping
        This method receive response and return status
        Also you can do some process in function body
        :param: response: Response
        :return: StatusChoices
        """
        if not self.ERROR_MAPPING:
            raise NotImplementedError
        self.transaction.status = self.ERROR_MAPPING.get(self.get_status(response.json()),
                                                         StatusChoices.REFUND_FAILED)
        self.transaction.last_verify = now()
        self.transaction.save()

    def send_refund_request(self) -> Response:
        if not self.URLS.get('REFUND'):
            raise NotImplementedError("Define URLs['REFUND'] or override .send_refund_request()")
        data = self.get_refund_context()
        return requests.post(self.URLS['REFUND'], json=data, headers=self.get_headers())

    def get_refund_context(self):
        return {}

    # ----------------------------------- END REFUND ------------------------------------------------

    # ------------------------------------- OTHER ---------------------------------------------------

    def get_redirect_url(self):
        if not self.URLS.get('REDIRECT'):
            raise NotImplementedError("Define URLs['REDIRECT'] or override .send_redirect_request()")
        return self.URLS['REDIRECT'].format(transaction=self.transaction)

    @classmethod
    def get_transaction_from_query_params(cls, query_params: dict):
        return get_object_or_404(Transaction, transaction_id=query_params[cls.TRANSACTION_ID_KEY_NAME])

    def get_headers(self):
        pass

    def apply_to_transaction(self, data: dict):
        for flag in self.RECEIVING_FLAGS:
            translated_flag = self.translate_flag(flag)
            if translated_flag in data:
                try:
                    setattr(self.transaction, flag, data.get(translated_flag))
                except AttributeError:
                    pass

    @classmethod
    def translate_flag(cls, flag):
        return cls.TRANSLATE_DICTIONARY.get(flag) or flag

    def get_status(self, data: dict):
        return data.get(self.STATUS_FIELD)
