"""Application errors raised by Supplier Relationship use cases."""


class SupplierNotFound(LookupError):
    """Raised when a Supplier required by a relationship use case does not exist."""


class SupplierRelationshipNotFound(LookupError):
    """Raised when a SupplierRelationship required by a use case does not exist."""


class RelationshipAlreadyExists(ValueError):
    """Raised when the Supplier/organization relationship already exists."""
