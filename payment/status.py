from django.db import models
from django.utils.translation import gettext_lazy as _


class StatusChoices(models.IntegerChoices):
    REFUND_FAILED_BY_LACK_OF_FUNDS = -3, _("Refund failed by lake of funds")
    REFUND_FAILED = -2, _("Refund Failed")
    REFUNDED = -1, _("Refunded")
    SUCCESSFUL = 0, _("Successful")
    WAIT_FOR_PAY = 1, _("Wait ...")
    CANCELED = 2, _("Canceled")
    WAIT_FOR_BANK = 3, _("Wait for Bank")
    CANCELED_BY_USER = 4, _("Canceled By User")
    FAILED = 5, _("Failed")
