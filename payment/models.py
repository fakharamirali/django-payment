from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import StepValueValidator
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from payment import globals, registry
from payment.status import StatusChoices
from payment.validators import card_holder_validator, number_only_validator


class PayPortalManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, code_name):
        self.get(code_name=code_name)


class PayPortal(models.Model):
    class Meta:
        verbose_name = _("Pay Portal")
        verbose_name_plural = _("Pay Portals")

        permissions = [
            ("secret", _("Access secret data of pay portal")),
        ]

    objects = PayPortalManager()

    name = models.CharField(_("Name"), max_length=128)
    code_name = models.SlugField(_("Code Name"), help_text=_("This name use to access from code and don't show user"),
                                 max_length=50, primary_key=True)
    backend = models.CharField(_("Backend"), max_length=512, choices=registry.get_choices)
    api_key = models.CharField(_("API Key"), max_length=255)

    order_id_prefix = models.SlugField(_("Order Prefix"), max_length=128)

    def get_backend(self):
        return import_string(self.backend)


class Transaction(models.Model):
    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        constraints = (
            models.UniqueConstraint(fields=('transaction_id',), condition=Q(transaction_id__isnull=False),
                                    name="transaction_unique"),
        )
        default_permissions = [
            ("create", _("Can Create a new Transaction")),
            ("verify", _("Can verify a transaction with check")),
            ("force_pay", _("Can set it paid without check")),
            ("delete_finished", _("Delete finished transactions")),
            ("delete_force_all", _("Delete transactions"))
        ]

    portal = models.ForeignKey('PayPortal', models.RESTRICT, verbose_name=_("Pay Portal"))  # TODO: SET DEFAULT
    transaction_id = models.CharField(_("Transaction ID"), null=True, max_length=255)
    id = models.BigAutoField(_("Order ID"), primary_key=True)
    user = models.ForeignKey(get_user_model(), models.SET_NULL, related_name='transactions',
                             related_query_name='transactions',
                             verbose_name=_("User"), null=True, blank=True)  # FIXME: ON DELETE
    linked_contenttype = models.ForeignKey("contenttypes.ContentType", models.SET_NULL, verbose_name=_("Linked Model"),
                                           null=True, blank=True)
    linked_content_id = models.PositiveBigIntegerField(_("Linked Object Id"), null=True, blank=True)
    linked_content_object = GenericForeignKey('linked_contenttype', 'linked_content_id')
    amount = models.PositiveBigIntegerField(_("Amount"), validators=(StepValueValidator(1000),))
    card_holder = models.CharField(_("Card Number"), max_length=19,
                                   validators=(card_holder_validator,))
    shaparak_tracking_code = models.CharField(_("Tracking Code"), max_length=12, validators=(number_only_validator,))
    status = models.SmallIntegerField(_("Status"), choices=StatusChoices.choices)
    description = models.TextField(_("Description"), null=True, blank=True)
    other = models.JSONField(_("Other Information"), null=True, blank=True)

    # Important Times
    create_date = models.DateTimeField(_("Create Date"), auto_now_add=True)
    create_transaction_at = models.DateTimeField(_("Create on portal at"), null=True)
    last_verify = models.DateTimeField(_("Last verify"), null=True)
    last_edit = models.DateTimeField(_("Last Edit"), auto_now=True)

    # Functional methods

    @cached_property
    def backend_controller(self):
        return self.portal.get_backend()(self)

    def create(self, callback_uri, **kwargs):
        self.backend_controller.create(callback_uri, **kwargs)

    def verify(self):
        self.backend_controller.verify_transaction()

    def refund(self):
        self.backend_controller.refund_transaction()

    # Other

    @classmethod
    def get_next_available_id(cls):
        max_id = globals.max_used_id_transaction
        return (max_id + 1) if max_id else 1

    def locate_id(self):
        self.id = self.get_next_available_id()

    def get_redirect_url(self):
        return self.backend_controller.get_redirect_url()
