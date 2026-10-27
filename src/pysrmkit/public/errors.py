"""Stable public errors owned by the PySRMKit boundary."""


class PySRMKitError(Exception):
    """Base class for errors defined specifically by the public/runtime boundary."""


class PersistenceError(PySRMKitError):
    """Stable public representation of an unexpected persistence failure."""


class PersistenceUnavailable(PersistenceError):
    """Raised when the configured persistence backend cannot serve the operation."""


class PersistenceConflict(PersistenceError):
    """Raised when persistence rejects an operation because of a storage constraint."""
