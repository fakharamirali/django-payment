from django.conf import settings
from django.core import checks


def check_rest_framework_installed(**kwargs):
    errors = []
    if 'rest_framework' not in settings.INSTALLED_APPS:
        errors.append(
            checks.Error("REST Framework is not installed. Add 'rest_framework' to settings.INSTALLED_APPS",
                         id='payment_apis.E001',
                         hint="If you haven't installed 'djangorestframework',"
                              " first install it by pip or other package manager.\n"
                              "> pip install djangorestframework")
        )
    return errors
