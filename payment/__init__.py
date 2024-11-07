from django.utils.module_loading import autodiscover_modules

from .registry import registry

__version__ = '0.0.4a0'
VERSION = (0, 0, 4, 'alpha', 0)


def autodiscover():
    autodiscover_modules('payment_backends', register_to=registry)
