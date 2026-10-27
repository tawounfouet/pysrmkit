"""Explicit mapping between SupplierAssessment Domain state and persistence records."""

from pysrmkit.adapters.sqlalchemy.models.assessment import (
    AssessmentAnswerRecord,
    AssessmentQuestionRecord,
    SupplierAssessmentRecord,
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


def _question_records(
    assessment: SupplierAssessment,
) -> list[AssessmentQuestionRecord]:
    return [
        AssessmentQuestionRecord(
            position=position,
            code=question.code,
            mandatory=question.mandatory,
            maximum_score=question.maximum_score,
        )
        for position, question in enumerate(assessment.questions)
    ]


def _answer_records(
    assessment: SupplierAssessment,
) -> list[AssessmentAnswerRecord]:
    return [
        AssessmentAnswerRecord(
            position=position,
            question_code=answer.question_code,
            score=answer.score,
        )
        for position, answer in enumerate(assessment.answers)
    ]


def new_assessment_record(assessment: SupplierAssessment) -> SupplierAssessmentRecord:
    """Create a new persistence record from current Assessment state."""

    return SupplierAssessmentRecord(
        assessment_id=assessment.id.value,
        relationship_id=assessment.relationship_id.value,
        assessment_type=assessment.assessment_type.value,
        created_at=assessment.created_at,
        completed_at=assessment.completed_at,
        score=assessment.score.value if assessment.score is not None else None,
        decision=assessment.decision.value if assessment.decision is not None else None,
        questions=_question_records(assessment),
        answers=_answer_records(assessment),
    )


def apply_assessment_state(
    record: SupplierAssessmentRecord,
    assessment: SupplierAssessment,
) -> None:
    """Synchronize an existing persistence record from an Assessment Aggregate."""

    record.relationship_id = assessment.relationship_id.value
    record.assessment_type = assessment.assessment_type.value
    record.created_at = assessment.created_at
    record.completed_at = assessment.completed_at
    record.score = assessment.score.value if assessment.score is not None else None
    record.decision = assessment.decision.value if assessment.decision is not None else None
    record.questions = _question_records(assessment)
    record.answers = _answer_records(assessment)


def assessment_from_record(record: SupplierAssessmentRecord) -> SupplierAssessment:
    """Reconstitute a persistence-ignorant SupplierAssessment Aggregate."""

    return SupplierAssessment.reconstitute(
        assessment_id=AssessmentId(record.assessment_id),
        relationship_id=SupplierRelationshipId(record.relationship_id),
        assessment_type=AssessmentType(record.assessment_type),
        created_at=record.created_at,
        questions=tuple(
            AssessmentQuestion(
                code=item.code,
                mandatory=item.mandatory,
                maximum_score=item.maximum_score,
            )
            for item in record.questions
        ),
        answers=tuple(
            AssessmentAnswer(
                question_code=item.question_code,
                score=item.score,
            )
            for item in record.answers
        ),
        completed_at=record.completed_at,
        score=AssessmentScore(record.score) if record.score is not None else None,
        decision=AssessmentDecision(record.decision) if record.decision is not None else None,
    )
