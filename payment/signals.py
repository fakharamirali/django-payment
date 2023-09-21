from django.dispatch import Signal

from payment import globals

pre_create_transaction = Signal()
post_create_transaction = Signal()
create_transaction_failed = Signal()
pre_verify_transaction = Signal()
post_verify_transaction = Signal()
pre_refund_transaction = Signal()
post_refund_transaction = Signal()


def update_last_transaction_id(sender, instance, created, **kwargs):
    if created:
        globals.max_used_id_transaction = max(globals.max_used_id_transaction,
                                              instance.id) if globals.max_used_id_transaction else instance.id
