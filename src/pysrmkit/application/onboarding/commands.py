"""Commands and input models for Supplier Onboarding use cases."""

from dataclasses import dataclass

from pysrmkit.domain.onboarding.value_objects import OnboardingId, OnboardingRequirementCode


@dataclass(frozen=True, slots=True)
class OnboardingRequirementInput:
    """Input definition used when a relationship enters onboarding."""

    code: str
    mandatory: bool = True


@dataclass(frozen=True, slots=True)
class SatisfyOnboardingRequirement:
    """Intent to mark one onboarding requirement as satisfied."""

    onboarding_id: OnboardingId
    requirement_code: OnboardingRequirementCode


@dataclass(frozen=True, slots=True)
class CompleteSupplierOnboarding:
    """Intent to complete onboarding once mandatory requirements are satisfied."""

    onboarding_id: OnboardingId
