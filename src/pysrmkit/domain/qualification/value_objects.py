"""Value Objects and domain results for Supplier Qualification."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Self
from uuid import UUID, uuid4

from pysrmkit.domain.qualification.errors import (
    InvalidQualificationDecision,
    InvalidQualificationScope,
)
from pysrmkit.domain.relationship.value_objects import InternalOrganizationId
from pysrmkit.domain.supplier.value_objects import CategoryCode, CountryCode


def _normalized_text_tuple(values: tuple[str, ...]) -> tuple[str, ...]:
    normalized = tuple(value.strip() for value in values if value.strip())
    return normalized


@dataclass(frozen=True, slots=True)
class QualificationId:
    """Stable internal identity of a SupplierQualification Aggregate."""

    value: UUID

    @classmethod
    def new(cls) -> Self:
        return cls(uuid4())

    def __str__(self) -> str:
        return str(self.value)


class QualificationStatus(StrEnum):
    """Lifecycle state of a SupplierQualification."""

    PENDING = "PENDING"
    QUALIFIED = "QUALIFIED"
    NOT_QUALIFIED = "NOT_QUALIFIED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


@dataclass(frozen=True, slots=True)
class QualificationScope:
    """Business perimeter in which a Supplier qualification applies."""

    organization_id: InternalOrganizationId | None = None
    category_code: CategoryCode | None = None
    country_code: CountryCode | None = None

    def __post_init__(self) -> None:
        if (
            self.organization_id is None
            and self.category_code is None
            and self.country_code is None
        ):
            raise InvalidQualificationScope(
                "QualificationScope requires at least one meaningful business dimension"
            )


@dataclass(frozen=True, slots=True)
class QualificationDecision:
    """Explainable result produced by a QualificationPolicy."""

    approved: bool
    resulting_status: QualificationStatus
    reasons: tuple[str, ...]
    failed_requirements: tuple[str, ...]
    decided_at: datetime

    def __post_init__(self) -> None:
        reasons = _normalized_text_tuple(self.reasons)
        failed_requirements = _normalized_text_tuple(self.failed_requirements)
        if not reasons:
            raise InvalidQualificationDecision("QualificationDecision requires at least one reason")

        if self.approved:
            if self.resulting_status is not QualificationStatus.QUALIFIED:
                raise InvalidQualificationDecision(
                    "Approved decision must result in QUALIFIED status"
                )
            if failed_requirements:
                raise InvalidQualificationDecision(
                    "Approved decision cannot contain failed requirements"
                )
        elif self.resulting_status is not QualificationStatus.NOT_QUALIFIED:
            raise InvalidQualificationDecision(
                "Rejected decision must result in NOT_QUALIFIED status"
            )

        object.__setattr__(self, "reasons", reasons)
        object.__setattr__(self, "failed_requirements", failed_requirements)
