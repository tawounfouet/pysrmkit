"""Commands and input models for Supplier Assessment use cases."""

from dataclasses import dataclass

from pysrmkit.domain.assessment.value_objects import AssessmentDecision, AssessmentId
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


@dataclass(frozen=True, slots=True)
class AssessmentQuestionInput:
    """Application-friendly question snapshot used to create an assessment."""

    code: str
    mandatory: bool = True
    maximum_score: int = 100


@dataclass(frozen=True, slots=True)
class CreateSupplierAssessment:
    """Intent to create a relationship-scoped supplier assessment."""

    relationship_id: SupplierRelationshipId
    assessment_type: str
    questions: tuple[AssessmentQuestionInput, ...]


@dataclass(frozen=True, slots=True)
class RecordAssessmentAnswer:
    """Intent to record or replace one assessment answer before completion."""

    assessment_id: AssessmentId
    question_code: str
    score: int


@dataclass(frozen=True, slots=True)
class CompleteSupplierAssessment:
    """Intent to complete an assessment once mandatory answers exist."""

    assessment_id: AssessmentId
    decision: AssessmentDecision | None = None
