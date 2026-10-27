"""Queries for Supplier Onboarding readiness."""

from dataclasses import dataclass

from pysrmkit.domain.onboarding.value_objects import OnboardingId


@dataclass(frozen=True, slots=True)
class GetOnboardingProgress:
    """Question asking for the computed readiness of one onboarding."""

    onboarding_id: OnboardingId
