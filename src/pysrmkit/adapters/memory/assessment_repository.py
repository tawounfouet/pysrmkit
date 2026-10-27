"""In-memory implementation of SupplierAssessmentRepository."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pysrmkit.domain.assessment.entities import SupplierAssessment
from pysrmkit.domain.assessment.value_objects import (
    AssessmentAnswer,
    AssessmentDecision,
    AssessmentId,
    AssessmentQuestion,
    AssessmentScore,
    AssessmentType,
)
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


@dataclass(frozen=True, slots=True)
class _StoredAssessment:
    assessment_id: AssessmentId
    relationship_id: SupplierRelationshipId
    assessment_type: AssessmentType
    created_at: datetime
    questions: tuple[AssessmentQuestion, ...]
    answers: tuple[AssessmentAnswer, ...]
    completed_at: datetime | None
    score: AssessmentScore | None
    decision: AssessmentDecision | None


class InMemorySupplierAssessmentRepository:
    """Persistence-like in-memory repository for SupplierAssessment Aggregates."""

    def __init__(self) -> None:
        self._assessments: dict[AssessmentId, _StoredAssessment] = {}

    def get(self, assessment_id: AssessmentId) -> SupplierAssessment | None:
        stored = self._assessments.get(assessment_id)
        if stored is None:
            return None
        return self._restore(stored)

    def save(self, assessment: SupplierAssessment) -> None:
        self._assessments[assessment.id] = _StoredAssessment(
            assessment_id=assessment.id,
            relationship_id=assessment.relationship_id,
            assessment_type=assessment.assessment_type,
            created_at=assessment.created_at,
            questions=assessment.questions,
            answers=assessment.answers,
            completed_at=assessment.completed_at,
            score=assessment.score,
            decision=assessment.decision,
        )

    def find_latest_for_relationship(
        self,
        relationship_id: SupplierRelationshipId,
    ) -> SupplierAssessment | None:
        candidates = (
            stored
            for stored in self._assessments.values()
            if stored.relationship_id == relationship_id
        )
        latest = max(candidates, key=lambda item: item.created_at, default=None)
        if latest is None:
            return None
        return self._restore(latest)

    @staticmethod
    def _restore(stored: _StoredAssessment) -> SupplierAssessment:
        return SupplierAssessment.reconstitute(
            assessment_id=stored.assessment_id,
            relationship_id=stored.relationship_id,
            assessment_type=stored.assessment_type,
            created_at=stored.created_at,
            questions=stored.questions,
            answers=stored.answers,
            completed_at=stored.completed_at,
            score=stored.score,
            decision=stored.decision,
        )
