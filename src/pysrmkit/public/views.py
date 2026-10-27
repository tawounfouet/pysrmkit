"""Immutable consumer-facing state views for PySRMKit queries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pysrmkit.domain.assessment.value_objects import (
    AssessmentDecision,
    AssessmentId,
    AssessmentScore,
    AssessmentType,
)
from pysrmkit.domain.onboarding.value_objects import OnboardingId, OnboardingRequirementCode
from pysrmkit.domain.qualification.value_objects import (
    QualificationId,
    QualificationScope,
    QualificationStatus,
)
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierLifecycleStage,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import (
    CountryCode,
    ExternalIdentifier,
    SupplierId,
)


@dataclass(frozen=True, slots=True)
class SupplierView:
    """Immutable snapshot of consumer-relevant Supplier state."""

    supplier_id: SupplierId
    legal_name: str
    trading_name: str | None
    supplier_type: str | None
    country: CountryCode | None
    external_identifiers: tuple[ExternalIdentifier, ...]


@dataclass(frozen=True, slots=True)
class SupplierRelationshipView:
    """Immutable snapshot of one Supplier relationship."""

    relationship_id: SupplierRelationshipId
    supplier_id: SupplierId
    organization_id: InternalOrganizationId
    stage: SupplierLifecycleStage


@dataclass(frozen=True, slots=True)
class OnboardingRequirementView:
    """Immutable public projection of one onboarding requirement."""

    code: OnboardingRequirementCode
    mandatory: bool
    satisfied: bool


@dataclass(frozen=True, slots=True)
class OnboardingView:
    """Immutable snapshot of Supplier onboarding state."""

    onboarding_id: OnboardingId
    relationship_id: SupplierRelationshipId
    started_at: datetime
    requirements: tuple[OnboardingRequirementView, ...]
    completed_at: datetime | None
    completed: bool
    ready_for_completion: bool
    missing_mandatory_requirements: tuple[OnboardingRequirementCode, ...]


@dataclass(frozen=True, slots=True)
class AssessmentQuestionView:
    """Immutable public projection of an assessment question."""

    code: str
    mandatory: bool
    maximum_score: int


@dataclass(frozen=True, slots=True)
class AssessmentAnswerView:
    """Immutable public projection of one scored assessment answer."""

    question_code: str
    score: int


@dataclass(frozen=True, slots=True)
class AssessmentView:
    """Immutable snapshot of Supplier assessment state."""

    assessment_id: AssessmentId
    relationship_id: SupplierRelationshipId
    assessment_type: AssessmentType
    created_at: datetime
    questions: tuple[AssessmentQuestionView, ...]
    answers: tuple[AssessmentAnswerView, ...]
    completed_at: datetime | None
    completed: bool
    score: AssessmentScore | None
    decision: AssessmentDecision | None
    required_answers_complete: bool
    missing_mandatory_question_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class QualificationView:
    """Immutable explainable snapshot of Supplier qualification state."""

    qualification_id: QualificationId
    relationship_id: SupplierRelationshipId
    scope: QualificationScope
    requested_at: datetime
    status: QualificationStatus
    approved: bool | None
    reasons: tuple[str, ...]
    failed_requirements: tuple[str, ...]
    decided_at: datetime | None
