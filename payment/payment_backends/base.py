from typing import Literal

import requests
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import URLValidator
from django.db.models import Model
from django.db.models.base import ModelBase
from django.utils.timezone import now
from requests import Response
from rest_framework.generics import get_object_or_404

from payment import signals
from payment.exceptions import FailedPaymentError
from payment.models import PayPortal, Transaction
from payment.status import StatusChoices, HARD_FAILED_STATUSES, FAIL_MESSAGES

__all__ = ['CURRENCY_TYPE', 'BasePayPortalBackend']

CURRENCY_TYPE = Literal['IRR', "IRT", None]
User = get_user_model()


class BasePayPortalBackend:
    @classmethod
    def support_refund(cls):
        return cls.URLs.get('REFUND') is not None
    
    name = None
    URLs = {}
    ERROR_MAPPING = {}
    
    # API Key in pay portal send to pay portal by this key name
    # Must override if pay portal use other key name
    API_KEY_NAME = "api_key"
    
    # Transaction ID send to pay portal by this key name
    # Must override
    TRANSACTION_ID_KEY_NAME = 'trans_id'
    
    def __init__(self, transaction: Transaction):
        self.transaction = transaction
    
    # ------------------------------------- CREATE ------------------------------------------------
    
    @classmethod
    def create(cls, portal: "PayPortal", amount: int, callback_uri: str, user: "User|None" = None,
               linked_model: "ContentType|ModelBase|None" = None, description: str = None,
               linked_object=None, currency: CURRENCY_TYPE = None, other: dict = None,
               **kwargs) -> "Transaction | None":
        if isinstance(linked_model, ModelBase):
            linked_model = ContentType.objects.get_for_model(linked_model)
        if linked_object is not None:
            if not isinstance(linked_object, Model):
                if linked_model is not None:
                    try:
                        linked_model.get_object_for_this_type(pk=linked_object)
                    except ObjectDoesNotExist:
                        pass
                
                if not isinstance(linked_object, Model):
                    raise TypeError(
                        "You must set linked_object a model instance ot define linked_model and set linked_object "
                        "valid pk")
            else:
                if linked_model is not None:
                    if not isinstance(linked_object, linked_model.model_class()):
                        raise TypeError(
                            "If you set linked_model and linked_object together! if you set both, the type of object "
                            "must be linked_model")
        if currency is None:
            if portal.default_currency is None:
                raise TypeError("You must set a currency if you don't have default currency")
            currency = portal.default_currency
        transaction = Transaction(portal=portal, amount=amount, user=user, other=other, currency=currency,
                                  description=description)
        if linked_object is not None:
            transaction.linked_content_object = linked_object
        else:
            if linked_model is not None:
                transaction.linked_contenttype = linked_model
        signals.pre_create_transaction.send(cls, transaction=transaction, callback_uri=callback_uri)
        response = cls.send_create_request(transaction, callback_uri, **kwargs)
        if not response.ok:
            signals.create_transaction_failed.send(cls, request=response, transaction=transaction)
            return
        cls.handle_create(transaction, response)
        signals.post_create_transaction.send(cls, transaction=transaction)
        return transaction
    
    @classmethod
    def handle_create(cls, transaction: Transaction, response: Response):
        """
        This method for handle response status of create request
        Must override in children or define error mapping
        This method receive response and return status
        Also you can do some process in function body
        :param: obj: Transaction
        :param: response: Response
        :return: StatusChoices
        """
        if not cls.ERROR_MAPPING:
            if transaction.pk:
                transaction.delete()
            raise NotImplementedError

        res_data = response.json()
        transaction.status = cls.ERROR_MAPPING.get(res_data['code'], StatusChoices.FAILED)

        if transaction.status is None or transaction.status in HARD_FAILED_STATUSES:
            if transaction.pk:
                transaction.delete()
            if transaction is None:
                raise ValueError("Uncaught code")
            raise FailedPaymentError(FAIL_MESSAGES[transaction.status])
        transaction.transaction_id = res_data[cls.TRANSACTION_ID_KEY_NAME]
        transaction.save()

    @classmethod
    def send_create_request(cls, transaction: Transaction, callback_uri, **kwargs) -> Response:
        if not cls.URLs.get("CREATE"):
            raise NotImplementedError("Define URLs['CREATE'] or override .send_create_request()")

        try:
            URLValidator()(callback_uri)
        except ValidationError:
            raise ValueError("Callback URL is incorrect")
        transaction.locate_id()
        order_suffix = transaction.portal.order_id_prefix or transaction.portal.code_name
        data = {
            cls.API_KEY_NAME: str(transaction.portal.api_key),
            'order_id': f"{order_suffix}_{transaction.id}",
            'amount': transaction.amount,
            'callback_uri': callback_uri,
            'currency': transaction.currency,
            **cls.get_create_context(transaction, **kwargs)
        }
        response = requests.post(cls.URLs["CREATE"], data=data, headers=cls.get_headers(portal=transaction.portal))
        return response

    @classmethod
    def get_create_context(cls, transaction: Transaction, **kwargs):
        """
        This function get transaction and return data that will send additional to default data
        :param transaction: Transaction
        :return: A dict include additional data to send to pay portal
        """
        raise NotImplementedError
    
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
        self.transaction.status = self.ERROR_MAPPING[response.json()['code']]
        self.transaction.last_verify = now()
        self.transaction.save()
    
    def send_verify_request(self) -> Response:
        if not self.URLs.get('VERIFY'):
            raise NotImplementedError("Define URLs['VERIFY'] or override .send_verify_request()")
        data = self.get_verify_context()
        return requests.post(self.URLs['VERIFY'], data=data, headers=self.get_headers(self.transaction.portal))
    
    def get_verify_context(self):
        return {
            self.API_KEY_NAME: self.transaction.portal.api_key,
            self.TRANSACTION_ID_KEY_NAME: self.transaction.transaction_id,
            'amount': self.transaction.amount,
            'currency': self.transaction.currency,
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
        self.transaction.status = self.ERROR_MAPPING.get(response.json()['code'], StatusChoices.REFUND_FAILED)
        self.transaction.last_verify = now()
        self.transaction.save()
    
    def send_refund_request(self) -> Response:
        if not self.URLs.get('REFUND'):
            raise NotImplementedError("Define URLs['REFUND'] or override .send_refund_request()")
        data = self.get_refund_context()
        return requests.post(self.URLs['REFUND'], data=data, headers=self.get_headers(self.transaction.portal))
    
    def get_refund_context(self):
        raise NotImplementedError
    
    # ----------------------------------- END REFUND ------------------------------------------------
    
    # ------------------------------------- OTHER ---------------------------------------------------

    def get_redirect_url(self):
        if not self.URLs.get('REDIRECT'):
            raise NotImplementedError("Define URLs['REDIRECT'] or override .send_redirect_request()")
        return self.URLs['REDIRECT'].format(transaction=self.transaction)

    @classmethod
    def get_transaction_from_query_params(cls, query_params: dict):
        return get_object_or_404(Transaction, transaction_id=query_params[cls.TRANSACTION_ID_KEY_NAME])

    @classmethod
    def get_headers(cls, portal):
        ...
