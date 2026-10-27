"""Application errors raised by Supplier Qualification use cases."""


class SupplierQualificationNotFound(LookupError):
    """Raised when a SupplierQualification required by a use case does not exist."""


class CurrentQualificationAlreadyExists(ValueError):
    """Raised when a current qualification already exists for Relationship + Scope."""
