"""Domain errors raised by SupplierOnboarding rules."""

from __future__ import annotations

from pysrmkit.domain.onboarding.value_objects import OnboardingRequirementCode


class DuplicateOnboardingRequirement(ValueError):
    """Raised when an onboarding contains the same requirement code more than once."""


class UnknownOnboardingRequirement(LookupError):
    """Raised when an onboarding requirement code is not part of the onboarding."""


class MandatoryOnboardingRequirementsNotSatisfied(ValueError):
    """Raised when onboarding completion is attempted with missing mandatory requirements."""

    def __init__(self, missing: tuple[OnboardingRequirementCode, ...]) -> None:
        self.missing = missing
        joined = ", ".join(str(code) for code in missing)
        super().__init__(f"Mandatory onboarding requirements are not satisfied: {joined}")


class OnboardingAlreadyCompleted(ValueError):
    """Raised when a completed onboarding is mutated or completed again."""
