"""Supplier Core domain errors."""


class InvalidSupplierIdentity(ValueError):
    """Raised when a SupplierIdentity cannot represent a valid supplier identity."""


class InvalidExternalIdentifier(ValueError):
    """Raised when an ExternalIdentifier is structurally invalid."""


class DuplicateExternalIdentifier(ValueError):
    """Raised when the same ExternalIdentifier is added more than once."""
