from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

card_holder_validator = RegexValidator(r"^[\d*]{4}(?:-[\d*]{4}){3}$")
number_only_validator = RegexValidator(r"^\d+$", _("This fielf only include number"), "not_number")
