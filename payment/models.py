from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import StepValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from payment.status import StatusChoices


class DefaultCurrencyChoices(models.TextChoices):
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
    code_name = models.CharField(_("Code Name"), help_text=_("This name use to access from code and don't show user"),
                                 max_length=128, primary_key=True)
    api_key = models.UUIDField(_("API Key"))
    
    order_id_prefix = models.CharField(_("Order Prefix"), max_length=128)
    default_currency = models.CharField(_("Default Currency"), choices=DefaultCurrencyChoices.choices, null=True,
                                        blank=True)
    # TODO :Add Backend


class Transaction(models.Model):
    portal = models.ForeignKey('PayPortal', models.RESTRICT, verbose_name=_("Pay Portal"))
    user = models.ForeignKey(get_user_model(), None, related_name='transactions', related_query_name='transactions',
                             verbose_name=_("User"), null=True, blank=True)  # FIXME: ON DELETE
    linked_contenttype = models.ForeignKey("contenttypes.ContentType", models.SET_NULL, verbose_name=_("Linked Model"),
                                           null=True, blank=True)
    linked_content_id = models.PositiveBigIntegerField(_("Linked Object Id"), null=True, blank=True)
    linked_content_object = GenericForeignKey('linked_contenttype', 'linked_content_id')
    order_id = models.PositiveBigIntegerField(_("Order ID"), auto_created=True)
    amount = models.PositiveBigIntegerField(_("Amount"), validators=(StepValueValidator(1000),))
    status = models.PositiveSmallIntegerField(_("Status"), choices=StatusChoices.choices)
    other = models.JSONField(_("Other Information"), null=True, blank=True)
