from django.utils.module_loading import autodiscover_modules

from .registry import pay_portal_backend_registry


def autodiscover():
    autodiscover_modules('payment_backends', register_to=pay_portal_backend_registry)
