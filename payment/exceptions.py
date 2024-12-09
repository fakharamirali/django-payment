from django.utils.translation import gettext_lazy as _


class FailedPaymentError(Exception):
    status_code = 500
    default_detail = _("An error occurred while processing your transaction (%s, %s)")

    def __init__(self, code, status, detail=None):
        self.code = code
        self.status = status

        self.detail = detail or self.default_detail % (code, status)

    def __str__(self):
        return str(self.detail)

    def get_codes(self):
        return self.code

    def get_full_detail(self):
        return self.detail


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass
