from django.utils.functional import SimpleLazyObject
from django.utils.module_loading import import_string

__all__ = ['PayPortalBackendRegistry', 'pay_portal_backend_registry', 'lazy_choices']


class PayPortalBackendRegistry:
    def __init__(self):
        self._registry = {}
        self._choices = set()
    
    def register(self, backend_class):
        """
        Register a payment backend in the registry by storing class name as key and import path as value
        Update the choices list with the new backend
        """
        backend_name = f"{backend_class.__module__}.{backend_class.__name__}"
        self._registry[backend_class.__name__] = backend_name
        self._choices.add((backend_name, backend_name))
    
    def unregister(self, backend_class):
        """
        Unregister a payment backend from the registry by using the class name as the key
        Remove the backend from the choices list
        """
        backend_name = f"{backend_class.__module__}.{backend_class.__name__}"
        if backend_class.__name__ in self._registry:
            del self._registry[backend_class.__name__]
            self._choices.discard((backend_name, backend_name))
    
    def get_backend(self, backend_name):
        """
        Get the payment backend class by using the backend name as the key from the registry
        Import and return the backend class using import_string
        """
        import_path = self._registry.get(backend_name)
        if import_path:
            return import_string(import_path)
        return None
    
    @property
    def choices(self):
        """
        Get the choices for the CharField dynamically from the registry with import paths as values
        """
        return list(self._choices)


# Create an instance of the registry class
pay_portal_backend_registry = PayPortalBackendRegistry()

# Create a lazy object for choices
lazy_choices = SimpleLazyObject(lambda: pay_portal_backend_registry.choices)
