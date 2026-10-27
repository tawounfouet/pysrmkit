"""QualificationPolicy tests."""

from datetime import UTC, datetime

import pytest

from pysrmkit.domain.qualification.policies import QualificationContext, QualificationPolicy
from pysrmkit.domain.qualification.value_objects import QualificationStatus

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


def valid_context() -> QualificationContext:
    return QualificationContext(
        onboarding_complete=True,
        assessment_completed=True,
        assessment_score=90,
        required_answers_complete=True,
    )


def test_policy_qualifies_when_all_required_facts_satisfy_policy() -> None:
    decision = QualificationPolicy(minimum_assessment_score=80).evaluate(
        valid_context(),
        evaluated_at=NOW,
    )

    assert decision.approved is True
    assert decision.resulting_status is QualificationStatus.QUALIFIED
    assert decision.failed_requirements == ()
    assert decision.reasons == ("All qualification requirements are satisfied",)
    assert decision.decided_at == NOW


@pytest.mark.parametrize(
    ("context", "expected_requirement"),
    [
        (
            QualificationContext(
                onboarding_complete=False,
                assessment_completed=True,
                assessment_score=90,
                required_answers_complete=True,
            ),
            "ONBOARDING_COMPLETE",
        ),
        (
            QualificationContext(
                onboarding_complete=True,
                assessment_completed=False,
                assessment_score=None,
                required_answers_complete=True,
            ),
            "ASSESSMENT_COMPLETE",
        ),
        (
            QualificationContext(
                onboarding_complete=True,
                assessment_completed=True,
                assessment_score=None,
                required_answers_complete=True,
            ),
            "ASSESSMENT_SCORE_AVAILABLE",
        ),
        (
            QualificationContext(
                onboarding_complete=True,
                assessment_completed=True,
                assessment_score=79,
                required_answers_complete=True,
            ),
            "ASSESSMENT_MINIMUM_SCORE",
        ),
        (
            QualificationContext(
                onboarding_complete=True,
                assessment_completed=True,
                assessment_score=90,
                required_answers_complete=False,
            ),
            "REQUIRED_ANSWERS_COMPLETE",
        ),
    ],
)
def test_policy_rejects_each_required_failure_branch(
    context: QualificationContext,
    expected_requirement: str,
) -> None:
    decision = QualificationPolicy(minimum_assessment_score=80).evaluate(
        context,
        evaluated_at=NOW,
    )

    assert decision.approved is False
    assert decision.resulting_status is QualificationStatus.NOT_QUALIFIED
    assert expected_requirement in decision.failed_requirements
    assert decision.reasons


def test_policy_explains_multiple_failures_in_stable_order() -> None:
    context = QualificationContext(
        onboarding_complete=False,
        assessment_completed=True,
        assessment_score=60,
        required_answers_complete=False,
    )

    decision = QualificationPolicy(minimum_assessment_score=80).evaluate(
        context,
        evaluated_at=NOW,
    )

    assert decision.failed_requirements == (
        "ONBOARDING_COMPLETE",
        "ASSESSMENT_MINIMUM_SCORE",
        "REQUIRED_ANSWERS_COMPLETE",
    )
    assert decision.reasons == (
        "Supplier onboarding must be complete",
        "Assessment score must be at least 80",
        "All required assessment answers must be complete",
    )


def test_policy_is_deterministic_for_same_facts_and_explicit_evaluation_time() -> None:
    policy = QualificationPolicy(minimum_assessment_score=80)
    context = valid_context()

    assert policy.evaluate(context, evaluated_at=NOW) == policy.evaluate(
        context,
        evaluated_at=NOW,
    )


def test_policy_and_context_validate_percentage_ranges() -> None:
    with pytest.raises(ValueError):
        QualificationPolicy(minimum_assessment_score=101)

    with pytest.raises(ValueError):
        QualificationContext(
            onboarding_complete=True,
            assessment_completed=True,
            assessment_score=-1,
            required_answers_complete=True,
        )
