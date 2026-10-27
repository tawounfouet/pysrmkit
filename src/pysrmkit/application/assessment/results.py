"""Application results for Supplier Assessment use cases."""

from dataclasses import dataclass

from pysrmkit.domain.assessment.value_objects import AssessmentId, AssessmentScore


@dataclass(frozen=True, slots=True)
class CreateSupplierAssessmentResult:
    """Result returned after a SupplierAssessment is created."""

    assessment_id: AssessmentId


@dataclass(frozen=True, slots=True)
class CompleteSupplierAssessmentResult:
    """Result returned after SupplierAssessment completion."""

    assessment_id: AssessmentId
    score: AssessmentScore
