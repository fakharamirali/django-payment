from payment import globals


def update_last_transaction_id(sender, instance, created, **kwargs):
    if created:
        globals.max_used_id_transaction = max(globals.max_used_id_transaction,
                                              instance.id) if globals.max_used_id_transaction else instance.id
