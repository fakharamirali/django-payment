from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.module_loading import autodiscover_modules
from django.utils.translation import gettext_lazy as _

from payment.registry import registry


class PaymentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "payment"
    verbose_name = _('Payment')

    def ready(self):
        from .models import Transaction
        from .signals import update_last_transaction_id

        autodiscover()
        post_save.connect(update_last_transaction_id, sender=Transaction)


def autodiscover():
    autodiscover_modules('payment_backends', register_to=registry)
