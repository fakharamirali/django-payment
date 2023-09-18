from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from . import autodiscover


class PaymentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "payment"
    verbose_name = _('Payment')
    
    def ready(self):
        autodiscover()
