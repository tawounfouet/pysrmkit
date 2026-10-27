"""Value Objects and domain results for Supplier Onboarding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class OnboardingId:
    """Stable internal identity of a SupplierOnboarding Aggregate."""

    value: UUID

    @classmethod
    def new(cls) -> Self:
        return cls(uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class OnboardingRequirementCode:
    """Stable business code identifying an onboarding requirement."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().upper()
        if not normalized:
            raise ValueError("OnboardingRequirementCode value is required")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class OnboardingRequirement:
    """Immutable requirement state owned by SupplierOnboarding."""

    code: OnboardingRequirementCode
    mandatory: bool = True
    satisfied: bool = False

    def satisfy(self) -> OnboardingRequirement:
        if self.satisfied:
            return self
        return OnboardingRequirement(
            code=self.code,
            mandatory=self.mandatory,
            satisfied=True,
        )


@dataclass(frozen=True, slots=True)
class OnboardingProgress:
    """Computed onboarding readiness; requirements remain the source of truth."""

    total_requirements: int
    satisfied_requirements: int
    mandatory_requirements: int
    satisfied_mandatory_requirements: int
    missing_mandatory_requirements: tuple[OnboardingRequirementCode, ...]
    completed: bool

    @property
    def ready_for_completion(self) -> bool:
        return not self.missing_mandatory_requirements
