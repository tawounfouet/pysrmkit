"""Domain Events emitted by SupplierQualification."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pysrmkit.domain.qualification.value_objects import QualificationId, QualificationScope
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


@dataclass(frozen=True, slots=True)
class SupplierQualificationRequested:
    """Fact emitted when a qualification is requested for a scoped relationship."""

    event_id: UUID
    qualification_id: QualificationId
    relationship_id: SupplierRelationshipId
    scope: QualificationScope
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class SupplierQualified:
    """Fact emitted when a pending qualification receives an approved decision."""

    event_id: UUID
    qualification_id: QualificationId
    relationship_id: SupplierRelationshipId
    scope: QualificationScope
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class SupplierQualificationRejected:
    """Fact emitted when a pending qualification receives a rejected decision."""

    event_id: UUID
    qualification_id: QualificationId
    relationship_id: SupplierRelationshipId
    scope: QualificationScope
    decision_reasons: tuple[str, ...]
    occurred_at: datetime
