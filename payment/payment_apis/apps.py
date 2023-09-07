from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PaymentApisConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "payment.payment_apis"
    verbose_name = _("Payment APIs")
