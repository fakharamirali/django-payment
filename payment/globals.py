from django.db.models import Max
from django.utils.functional import SimpleLazyObject


def max_used_id(cls):
    return cls.objects.aggregate(max_id=Max('id'))['max_id']


def get_transaction_max_id():
    from payment.models import Transaction
    return max_used_id(Transaction)


max_used_id_transaction = SimpleLazyObject(get_transaction_max_id)
