from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NextpayApisConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nextpay.nextpay_apis"
    verbose_name = _("Nextpay APIs")
