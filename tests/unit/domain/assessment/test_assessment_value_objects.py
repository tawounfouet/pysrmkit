"""Supplier Assessment Value Object tests."""

from uuid import uuid4

import pytest

from pysrmkit.domain.assessment.value_objects import (
    AssessmentAnswer,
    AssessmentId,
    AssessmentQuestion,
    AssessmentScore,
    AssessmentType,
)


def test_assessment_id_has_value_equality_and_stable_string_representation() -> None:
    value = uuid4()

    left = AssessmentId(value)
    right = AssessmentId(value)

    assert left == right
    assert hash(left) == hash(right)
    assert str(left) == str(value)


def test_assessment_type_normalizes_and_rejects_blank_value() -> None:
    assert AssessmentType(" questionnaire ").value == "QUESTIONNAIRE"

    with pytest.raises(ValueError):
        AssessmentType("   ")


def test_assessment_question_validates_code_and_maximum_score() -> None:
    question = AssessmentQuestion(code=" legal ", maximum_score=50)

    assert question.code == "LEGAL"
    assert question.maximum_score == 50

    with pytest.raises(ValueError):
        AssessmentQuestion(code="   ")

    with pytest.raises(ValueError):
        AssessmentQuestion(code="LEGAL", maximum_score=0)


def test_assessment_answer_normalizes_question_code_and_rejects_negative_score() -> None:
    answer = AssessmentAnswer(question_code=" legal ", score=40)

    assert answer.question_code == "LEGAL"
    assert answer.score == 40

    with pytest.raises(ValueError):
        AssessmentAnswer(question_code="LEGAL", score=-1)


def test_assessment_score_is_percentage_value_object() -> None:
    assert AssessmentScore(80).value == 80

    with pytest.raises(ValueError):
        AssessmentScore(101)
