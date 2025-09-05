from payment.payment_backends.base import BaseBackend
from payment.registry import registry


def register(backend_class):
    if not issubclass(backend_class, BaseBackend):
        raise TypeError(f"Backend class {backend_class.__name__} is not subclass of BaseBackend")

    # Register the backend_class with the registry
    registry.register(backend_class)

    return backend_class
