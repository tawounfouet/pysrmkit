"""SupplierAssessment Aggregate tests."""

from datetime import UTC, datetime, timedelta

import pytest

from pysrmkit.domain.assessment.entities import SupplierAssessment
from pysrmkit.domain.assessment.errors import (
    AssessmentAlreadyCompleted,
    DuplicateAssessmentQuestion,
    InvalidAssessmentAnswer,
    MandatoryAssessmentAnswersMissing,
    UnknownAssessmentQuestion,
)
from pysrmkit.domain.assessment.events import SupplierAssessmentCompleted
from pysrmkit.domain.assessment.value_objects import (
    AssessmentAnswer,
    AssessmentDecision,
    AssessmentId,
    AssessmentQuestion,
    AssessmentScore,
    AssessmentType,
)
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId

CREATED_AT = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
COMPLETED_AT = CREATED_AT + timedelta(hours=1)


def make_assessment() -> SupplierAssessment:
    return SupplierAssessment.create(
        assessment_id=AssessmentId.new(),
        relationship_id=SupplierRelationshipId.new(),
        assessment_type=AssessmentType("QUESTIONNAIRE"),
        created_at=CREATED_AT,
        questions=(
            AssessmentQuestion(code="LEGAL", maximum_score=50),
            AssessmentQuestion(code="QUALITY", maximum_score=50),
        ),
    )


def test_assessment_requires_at_least_one_question() -> None:
    with pytest.raises(ValueError):
        SupplierAssessment.create(
            assessment_id=AssessmentId.new(),
            relationship_id=SupplierRelationshipId.new(),
            assessment_type=AssessmentType("QUESTIONNAIRE"),
            created_at=CREATED_AT,
            questions=(),
        )


def test_duplicate_question_codes_are_rejected() -> None:
    with pytest.raises(DuplicateAssessmentQuestion):
        SupplierAssessment.create(
            assessment_id=AssessmentId.new(),
            relationship_id=SupplierRelationshipId.new(),
            assessment_type=AssessmentType("QUESTIONNAIRE"),
            created_at=CREATED_AT,
            questions=(
                AssessmentQuestion(code="LEGAL"),
                AssessmentQuestion(code="legal"),
            ),
        )


def test_answer_must_reference_known_question_and_respect_question_maximum() -> None:
    assessment = make_assessment()

    with pytest.raises(UnknownAssessmentQuestion):
        assessment.record_answer(AssessmentAnswer(question_code="UNKNOWN", score=10))

    with pytest.raises(InvalidAssessmentAnswer):
        assessment.record_answer(AssessmentAnswer(question_code="LEGAL", score=51))

    assert assessment.answers == ()


def test_completion_requires_all_mandatory_answers() -> None:
    assessment = make_assessment()
    assessment.record_answer(AssessmentAnswer(question_code="LEGAL", score=45))

    with pytest.raises(MandatoryAssessmentAnswersMissing) as captured:
        assessment.complete(occurred_at=COMPLETED_AT)

    assert captured.value.missing_question_codes == ("QUALITY",)
    assert assessment.is_complete is False
    assert assessment.score is None
    assert assessment.pull_events() == ()


def test_completion_calculates_percentage_and_records_event() -> None:
    assessment = make_assessment()
    assessment.record_answer(AssessmentAnswer(question_code="LEGAL", score=45))
    assessment.record_answer(AssessmentAnswer(question_code="QUALITY", score=45))

    assessment.complete(
        occurred_at=COMPLETED_AT,
        decision=AssessmentDecision.APPROVED,
    )

    assert assessment.is_complete is True
    assert assessment.completed_at == COMPLETED_AT
    assert assessment.score == AssessmentScore(90)
    assert assessment.decision is AssessmentDecision.APPROVED
    assert assessment.required_answers_complete is True

    events = assessment.pull_events()
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, SupplierAssessmentCompleted)
    assert event.assessment_id == assessment.id
    assert event.relationship_id == assessment.relationship_id
    assert event.score == AssessmentScore(90)
    assert event.decision is AssessmentDecision.APPROVED
    assert event.occurred_at == COMPLETED_AT


def test_completed_assessment_is_immutable_by_default() -> None:
    assessment = make_assessment()
    assessment.record_answer(AssessmentAnswer(question_code="LEGAL", score=45))
    assessment.record_answer(AssessmentAnswer(question_code="QUALITY", score=45))
    assessment.complete(occurred_at=COMPLETED_AT)
    assessment.pull_events()

    with pytest.raises(AssessmentAlreadyCompleted):
        assessment.record_answer(AssessmentAnswer(question_code="LEGAL", score=50))

    with pytest.raises(AssessmentAlreadyCompleted):
        assessment.complete(occurred_at=COMPLETED_AT)

    assert assessment.score == AssessmentScore(90)
    assert assessment.pull_events() == ()


def test_reconstitution_preserves_state_without_recreating_events() -> None:
    assessment = SupplierAssessment.reconstitute(
        assessment_id=AssessmentId.new(),
        relationship_id=SupplierRelationshipId.new(),
        assessment_type=AssessmentType("QUESTIONNAIRE"),
        created_at=CREATED_AT,
        questions=(AssessmentQuestion(code="LEGAL", maximum_score=100),),
        answers=(AssessmentAnswer(question_code="LEGAL", score=88),),
        completed_at=COMPLETED_AT,
        score=AssessmentScore(88),
    )

    assert assessment.is_complete is True
    assert assessment.score == AssessmentScore(88)
    assert assessment.pull_events() == ()
