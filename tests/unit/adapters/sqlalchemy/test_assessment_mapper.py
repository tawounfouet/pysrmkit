"""SupplierAssessment Domain ↔ SQLAlchemy mapper tests."""

from datetime import UTC, datetime

from pysrmkit.adapters.sqlalchemy.mappers.assessment import (
    assessment_from_record,
    new_assessment_record,
)
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

CREATED = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
COMPLETED = datetime(2026, 10, 27, 13, 0, tzinfo=UTC)


def test_assessment_mapper_preserves_snapshot_answers_and_decision() -> None:
    assessment = SupplierAssessment.reconstitute(
        assessment_id=AssessmentId.new(),
        relationship_id=SupplierRelationshipId.new(),
        assessment_type=AssessmentType("QUESTIONNAIRE"),
        created_at=CREATED,
        questions=(
            AssessmentQuestion(code="LEGAL", mandatory=True, maximum_score=60),
            AssessmentQuestion(code="QUALITY", mandatory=False, maximum_score=40),
        ),
        answers=(
            AssessmentAnswer(question_code="LEGAL", score=55),
            AssessmentAnswer(question_code="QUALITY", score=35),
        ),
        completed_at=COMPLETED,
        score=AssessmentScore(90),
        decision=AssessmentDecision.APPROVED,
    )

    record = new_assessment_record(assessment)
    restored = assessment_from_record(record)

    assert restored == assessment
    assert restored.relationship_id == assessment.relationship_id
    assert restored.assessment_type == assessment.assessment_type
    assert restored.created_at == CREATED
    assert restored.completed_at == COMPLETED
    assert restored.questions == assessment.questions
    assert restored.answers == assessment.answers
    assert restored.score == AssessmentScore(90)
    assert restored.decision is AssessmentDecision.APPROVED
    assert restored.pull_events() == ()
