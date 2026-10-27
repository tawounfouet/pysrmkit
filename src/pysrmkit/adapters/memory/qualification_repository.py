"""In-memory implementation of SupplierQualificationRepository."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pysrmkit.domain.qualification.entities import SupplierQualification
from pysrmkit.domain.qualification.value_objects import (
    QualificationDecision,
    QualificationId,
    QualificationScope,
    QualificationStatus,
)
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


@dataclass(frozen=True, slots=True)
class _StoredQualification:
    qualification_id: QualificationId
    relationship_id: SupplierRelationshipId
    scope: QualificationScope
    requested_at: datetime
    status: QualificationStatus
    decision: QualificationDecision | None


class InMemorySupplierQualificationRepository:
    """Persistence-like in-memory repository for SupplierQualification Aggregates."""

    def __init__(self) -> None:
        self._qualifications: dict[QualificationId, _StoredQualification] = {}

    def get(self, qualification_id: QualificationId) -> SupplierQualification | None:
        stored = self._qualifications.get(qualification_id)
        if stored is None:
            return None
        return self._restore(stored)

    def save(self, qualification: SupplierQualification) -> None:
        self._qualifications[qualification.id] = _StoredQualification(
            qualification_id=qualification.id,
            relationship_id=qualification.relationship_id,
            scope=qualification.scope,
            requested_at=qualification.requested_at,
            status=qualification.status,
            decision=qualification.decision,
        )

    def find_current_for_scope(
        self,
        relationship_id: SupplierRelationshipId,
        scope: QualificationScope,
    ) -> SupplierQualification | None:
        for stored in self._qualifications.values():
            if stored.relationship_id != relationship_id or stored.scope != scope:
                continue
            qualification = self._restore(stored)
            if qualification.is_current:
                return qualification
        return None

    @staticmethod
    def _restore(stored: _StoredQualification) -> SupplierQualification:
        return SupplierQualification.reconstitute(
            qualification_id=stored.qualification_id,
            relationship_id=stored.relationship_id,
            scope=stored.scope,
            requested_at=stored.requested_at,
            status=stored.status,
            decision=stored.decision,
        )
