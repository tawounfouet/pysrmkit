"""Value Objects owned by the Supplier Relationship capability."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Self
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class SupplierRelationshipId:
    """Stable internal identity of a SupplierRelationship Entity."""

    value: UUID

    @classmethod
    def new(cls) -> Self:
        return cls(uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class InternalOrganizationId:
    """Reference to an organization owned outside PySRMKit."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("InternalOrganizationId value is required")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


class SupplierLifecycleStage(StrEnum):
    """Relationship-scoped lifecycle state."""

    DISCOVERED = "DISCOVERED"
    PROSPECTIVE = "PROSPECTIVE"
    INVITED = "INVITED"
    ONBOARDING = "ONBOARDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    QUALIFIED = "QUALIFIED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    BLOCKED = "BLOCKED"
    INACTIVE = "INACTIVE"
    OFFBOARDED = "OFFBOARDED"


@dataclass(frozen=True, slots=True)
class LifecycleTransitionReason:
    """Explicit business reason available for lifecycle transitions that need one."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("LifecycleTransitionReason value is required")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
