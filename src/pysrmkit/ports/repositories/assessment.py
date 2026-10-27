"""Repository contract for the SupplierAssessment Aggregate Root."""

from __future__ import annotations

from typing import Protocol

from pysrmkit.domain.assessment.entities import SupplierAssessment
from pysrmkit.domain.assessment.value_objects import AssessmentId
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


class SupplierAssessmentRepository(Protocol):
    """Persistence abstraction required by Supplier Assessment use cases."""

    def get(self, assessment_id: AssessmentId) -> SupplierAssessment | None: ...

    def save(self, assessment: SupplierAssessment) -> None: ...

    def find_latest_for_relationship(
        self,
        relationship_id: SupplierRelationshipId,
    ) -> SupplierAssessment | None: ...
