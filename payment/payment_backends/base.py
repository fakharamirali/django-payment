from abc import ABC, ABCMeta, abstractmethod

from payment.models import PayPortal, Transaction


class BaseBackend(ABC, metaclass=ABCMeta):
    name = None

    def __init__(self, transaction: Transaction):
        self.transaction = transaction

    @abstractmethod
    def create(self, callback_url, **kwargs) -> bool:
        pass

    @abstractmethod
    def verify(self):
        pass

    @abstractmethod
    def refund(self):
        pass

    @abstractmethod
    def get_redirect_url(self) -> str:
        pass

    @property
    def api_key(self) -> str:
        return self.transaction.portal.api_key

    @property
    def portal(self) -> PayPortal:
        return self.transaction.portal

    @portal.setter
    def portal(self, value):
        self.transaction.portal = value

    @classmethod
    def support_refund(cls) -> bool:
        return False

    @property
    def transaction_id(self) -> str:
        return self.transaction.transaction_id

    @transaction_id.setter
    def transaction_id(self, value: str):
        self.transaction.transaction_id = value
