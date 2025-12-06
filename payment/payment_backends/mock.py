import uuid
from collections import defaultdict
from functools import cached_property
from typing import Any

from django.core.cache import caches

from payment import signals
from payment.decorator import register
from payment.exceptions import FailedPaymentError
from payment.models import PayPortal
from payment.payment_backends.base import BaseBackend
from payment.status import StatusChoices
from payment.utils import KeyPrefix


@register
class MockPaymentBackend(BaseBackend):
    _storage: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    auto_pay: bool = False
    name = "Mock payment backend"

    @classmethod
    def get_storage_from_portal(cls, portal: PayPortal):
        portal_id = portal.api_key
        prefix = portal.order_id_prefix or f"{cls.__module__}.{cls.__qualname__}"
        if portal_id in caches:
            store = caches[portal_id]
        else:
            store = cls._storage[portal_id]
        return KeyPrefix(store, prefix)

    @cached_property
    def storage(self):
        return self.get_storage_from_portal(self.portal)

    def _check_transaction_exists(self, raise_exception=False):
        if self.transaction_id not in self.storage:
            self.transaction.status = StatusChoices.TRANSITION_ID_INVALID
            if raise_exception:
                raise FailedPaymentError(status=StatusChoices.TRANSITION_ID_INVALID,
                                         code=StatusChoices.TRANSITION_ID_INVALID)
            return False
        return True

    def create(self, callback_url, **kwargs) -> bool:
        signals.pre_create_transaction.send(self.__class__, transaction=self.transaction, callback_url=callback_url)
        self.transaction_id = str(uuid.uuid4())
        self.storage[self.transaction_id] = {
            "callback_url": callback_url,
            'kwargs': kwargs,
            'status': StatusChoices.WAIT_FOR_PAY
        }
        self.transaction.status = StatusChoices.WAIT_FOR_PAY
        self.transaction.save()

        signals.post_create_transaction.send(self.__class__, transaction=self.transaction)
        return True

    def verify(self):
        self._check_transaction_exists(raise_exception=True)
        signals.pre_verify_transaction.send(self.__class__, transaction=self.transaction)
        if self.auto_pay:
            self.storage[self.transaction_id]['status'] = StatusChoices.SUCCESSFUL
        self.transaction.status = self.storage[self.transaction_id]['status']
        signals.post_verify_transaction.send(self.__class__, transaction=self.transaction)
        return self.transaction

    def refund(self):
        self._check_transaction_exists(raise_exception=True)
        signals.pre_refund_transaction.send(self.__class__, transaction=self.transaction)
        if self.storage[self.api_key][self.transaction_id]['status'] == StatusChoices.SUCCESSFUL:
            self.storage[self.api_key][self.transaction_id]['status'] = StatusChoices.REFUNDED
        signals.post_refund_transaction.send(self.__class__, transaction=self.transaction)
        return self.transaction

    def get_redirect_url(self) -> str:
        return self.storage[self.transaction_id]['callback_url']

    @classmethod
    def support_refund(cls) -> bool:
        return True

    def mark_as(self, status: StatusChoices):
        self.storage[self.transaction_id]['status'] = status

    def mark_as_paid(self):
        self.mark_as(StatusChoices.SUCCESSFUL)


@register
class AutoPayMockBackend(MockPaymentBackend):
    name = 'Auto payment mock backend'
    auto_pay = True
