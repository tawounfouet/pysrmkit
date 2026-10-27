"""Application errors raised by Supplier Assessment use cases."""


class SupplierAssessmentNotFound(LookupError):
    """Raised when a SupplierAssessment required by a use case does not exist."""
