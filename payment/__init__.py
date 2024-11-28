from django.utils.module_loading import autodiscover_modules

from .registry import registry

__version__ = '0.0.5b0'
VERSION = (0, 0, 5, 'beta', 0)


def autodiscover():
    autodiscover_modules('payment_backends', register_to=registry)
