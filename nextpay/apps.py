from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NextpayConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nextpay"
    verbose_name = _('Nextpay')
