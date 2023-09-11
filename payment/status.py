from django.db import models
from django.utils.translation import gettext_lazy as _


class StatusChoices(models.IntegerChoices):
    refund_failed_by_lack_of_funds = -3, _("Refund failed by lake of funds")
    refund_failed = -2, _("Refund Failed")
    refunded = -1, _("Refunded")
    successful = 0, _("Successful")
    wait_for_pay = 1, _("Wait ...")
    canceled = 2, _("Canceled")
    wait_for_bank = 3, _("Wait for Bank")
    canceled_by_user = 4, _("Canceled By User")
    failed = 5, _("Failed")
