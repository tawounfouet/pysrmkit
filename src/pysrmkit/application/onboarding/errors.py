"""Application errors raised by Supplier Onboarding use cases."""


class SupplierOnboardingNotFound(LookupError):
    """Raised when a SupplierOnboarding required by a use case does not exist."""


class SupplierOnboardingAlreadyExists(ValueError):
    """Raised when the current Relationship already owns an onboarding."""
