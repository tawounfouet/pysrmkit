"""Domain Events emitted by SupplierAssessment."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pysrmkit.domain.assessment.value_objects import (
    AssessmentDecision,
    AssessmentId,
    AssessmentScore,
    AssessmentType,
)
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


@dataclass(frozen=True, slots=True)
class SupplierAssessmentCompleted:
    """Fact emitted after an assessment is completed successfully."""

    event_id: UUID
    assessment_id: AssessmentId
    relationship_id: SupplierRelationshipId
    assessment_type: AssessmentType
    score: AssessmentScore
    decision: AssessmentDecision | None
    occurred_at: datetime
