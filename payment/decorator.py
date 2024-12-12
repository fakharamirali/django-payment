from payment.payment_backends import BaseBackend
from payment.registry import registry


def register(backend_class):
    if not issubclass(backend_class, BaseBackend):
        # Create a subclass of backend_class that inherits from BasePayPortalBackend
        merged_class = type(backend_class.__name__, (BaseBackend, backend_class), {})
        merged_class.__module__ = backend_class.__module__
        backend_class = merged_class

    # Register the backend_class with the registry
    registry.register(backend_class)

    return backend_class
