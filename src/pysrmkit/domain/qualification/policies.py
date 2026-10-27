"""Deterministic Domain Policy for Supplier Qualification."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pysrmkit.domain.qualification.value_objects import (
    QualificationDecision,
    QualificationStatus,
)


@dataclass(frozen=True, slots=True)
class QualificationContext:
    """Facts collected before evaluating qualification eligibility."""

    onboarding_complete: bool
    assessment_completed: bool
    assessment_score: int | None
    required_answers_complete: bool

    def __post_init__(self) -> None:
        if self.assessment_score is not None and not 0 <= self.assessment_score <= 100:
            raise ValueError("assessment_score must be between 0 and 100")


@dataclass(frozen=True, slots=True)
class QualificationPolicy:
    """First deterministic qualification policy for the local Core."""

    minimum_assessment_score: int = 80

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_assessment_score <= 100:
            raise ValueError("minimum_assessment_score must be between 0 and 100")

    def evaluate(
        self,
        context: QualificationContext,
        *,
        evaluated_at: datetime,
    ) -> QualificationDecision:
        reasons: list[str] = []
        failed_requirements: list[str] = []

        if not context.onboarding_complete:
            failed_requirements.append("ONBOARDING_COMPLETE")
            reasons.append("Supplier onboarding must be complete")

        if not context.assessment_completed:
            failed_requirements.append("ASSESSMENT_COMPLETE")
            reasons.append("Supplier assessment must be complete")
        elif context.assessment_score is None:
            failed_requirements.append("ASSESSMENT_SCORE_AVAILABLE")
            reasons.append("Completed assessment must provide a score")
        elif context.assessment_score < self.minimum_assessment_score:
            failed_requirements.append("ASSESSMENT_MINIMUM_SCORE")
            reasons.append(f"Assessment score must be at least {self.minimum_assessment_score}")

        if not context.required_answers_complete:
            failed_requirements.append("REQUIRED_ANSWERS_COMPLETE")
            reasons.append("All required assessment answers must be complete")

        if failed_requirements:
            return QualificationDecision(
                approved=False,
                resulting_status=QualificationStatus.NOT_QUALIFIED,
                reasons=tuple(reasons),
                failed_requirements=tuple(failed_requirements),
                decided_at=evaluated_at,
            )

        return QualificationDecision(
            approved=True,
            resulting_status=QualificationStatus.QUALIFIED,
            reasons=("All qualification requirements are satisfied",),
            failed_requirements=(),
            decided_at=evaluated_at,
        )
