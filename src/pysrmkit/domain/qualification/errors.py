"""Domain errors raised by SupplierQualification rules."""


class InvalidQualificationScope(ValueError):
    """Raised when a QualificationScope has no meaningful business dimension."""


class InvalidQualificationDecision(ValueError):
    """Raised when a QualificationDecision is internally inconsistent."""


class InvalidQualificationState(ValueError):
    """Raised when a qualification lifecycle transition is not allowed."""
