from payment import pay_portal_backend_registry
from payment.payment_backends import BasePayPortalBackend


def register(backend_class):
    if not issubclass(backend_class, BasePayPortalBackend):
        # Create a subclass of backend_class that inherits from BasePayPortalBackend
        merged_class = type(backend_class.__name__, (BasePayPortalBackend, backend_class), {})
        merged_class.__module__ = backend_class.__module__
        backend_class = merged_class
    
    # Register the backend_class with the registry
    pay_portal_backend_registry.register(backend_class)
    
    return backend_class
