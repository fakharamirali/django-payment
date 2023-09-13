from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import StepValueValidator, RegexValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from payment.status import StatusChoices
from payment.validators import card_holder_validator, number_only_validator


class CurrencyChoices(models.TextChoices):
    __empty__ = _("Not set Default")
    IRR = _("Rial")
    IRT = _("Toman")


class PayPortalManager(models.Manager):
    use_in_migrations = True
    
    def get_by_natural_key(self, code_name):
        self.get(code_name=code_name)


class PayPortal(models.Model):
    class Meta:
        verbose_name = _("Pay Portal")
        verbose_name_plural = _("Pay Portals")
    
    objects = PayPortalManager()
    
    name = models.CharField(_("Name"), max_length=128)
    code_name = models.SlugField(_("Code Name"), help_text=_("This name use to access from code and don't show user"),
                                 max_length=50, primary_key=True)
    api_key = models.UUIDField(_("API Key"))
    
    order_id_prefix = models.SlugField(_("Order Prefix"), max_length=128)
    default_currency = models.CharField(_("Default Currency"), choices=CurrencyChoices.choices, null=True,
                                        blank=True, max_length=10, validators=(RegexValidator(r"^\w+$"),))
    # TODO :Add Backend


class Transaction(models.Model):
    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        constraints = (
            models.UniqueConstraint(fields=('transaction_id',), condition=Q(transaction_id__isnull=False),
                                    name="transaction_unique"),
        )
    
    portal = models.ForeignKey('PayPortal', models.RESTRICT, verbose_name=_("Pay Portal"))  # TODO: SET DEFAULT
    transaction_id = models.UUIDField(_("Transaction ID"))
    id = models.BigAutoField(_("Order ID"), primary_key=True)
    user = models.ForeignKey(get_user_model(), models.SET_NULL, related_name='transactions',
                             related_query_name='transactions',
                             verbose_name=_("User"), null=True, blank=True)  # FIXME: ON DELETE
    linked_contenttype = models.ForeignKey("contenttypes.ContentType", models.SET_NULL, verbose_name=_("Linked Model"),
                                           null=True, blank=True)
    linked_content_id = models.PositiveBigIntegerField(_("Linked Object Id"), null=True, blank=True)
    linked_content_object = GenericForeignKey('linked_contenttype', 'linked_content_id')
    amount = models.PositiveBigIntegerField(_("Amount"), validators=(StepValueValidator(1000),))
    currency = models.CharField(_("Currency"), choices=CurrencyChoices.choices, max_length=10,
                                validators=(RegexValidator(r"^\w$"),))
    card_holder = models.CharField(_("Card Number"), max_length=19,
                                   validators=(card_holder_validator,))
    shaparak_tracking_code = models.CharField(_("Tracking Code"), max_length=12, validators=(number_only_validator,))
    status = models.PositiveSmallIntegerField(_("Status"), choices=StatusChoices.choices)
    description = models.TextField(_("Description"), null=True, blank=True)
    other = models.JSONField(_("Other Information"), null=True, blank=True)
    
    # Important Times
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    create_transaction_at = models.DateTimeField(_("Create on portal at"), null=True)
    last_verify = models.DateTimeField(_("Last verify"), null=True)
    last_edit = models.DateTimeField(_("Last Edit"), auto_now=True)
