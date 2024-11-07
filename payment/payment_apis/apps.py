from django.apps import AppConfig
from django.core import checks
from django.utils.translation import gettext_lazy as _

from .checks import check_rest_framework_installed


class PaymentApisConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "payment.payment_apis"
    verbose_name = _("Payment APIs")

    def ready(self):
        checks.register(check_rest_framework_installed)
