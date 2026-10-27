"""SupplierAssessment Aggregate Root."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import uuid4

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
from pysrmkit.domain.common.events import DomainEvent
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


def _question_map() -> dict[str, AssessmentQuestion]:
    return {}


def _answer_map() -> dict[str, AssessmentAnswer]:
    return {}


def _domain_event_list() -> list[DomainEvent]:
    return []


@dataclass(slots=True, eq=False)
class SupplierAssessment:
    """Relationship-scoped assessment execution used as qualification evidence."""

    assessment_id: AssessmentId
    relationship_id: SupplierRelationshipId
    assessment_type: AssessmentType
    created_at: datetime
    _questions: dict[str, AssessmentQuestion] = field(
        default_factory=_question_map,
        repr=False,
    )
    _answers: dict[str, AssessmentAnswer] = field(
        default_factory=_answer_map,
        repr=False,
    )
    _completed_at: datetime | None = field(default=None, repr=False)
    _score: AssessmentScore | None = field(default=None, repr=False)
    _decision: AssessmentDecision | None = field(default=None, repr=False)
    _events: list[DomainEvent] = field(default_factory=_domain_event_list, repr=False)

    @classmethod
    def create(
        cls,
        *,
        assessment_id: AssessmentId,
        relationship_id: SupplierRelationshipId,
        assessment_type: AssessmentType,
        created_at: datetime,
        questions: Iterable[AssessmentQuestion],
    ) -> Self:
        assessment = cls(
            assessment_id=assessment_id,
            relationship_id=relationship_id,
            assessment_type=assessment_type,
            created_at=created_at,
        )
        for question in questions:
            assessment._add_question(question)
        if not assessment._questions:
            raise ValueError("SupplierAssessment requires at least one question")
        return assessment

    @classmethod
    def reconstitute(
        cls,
        *,
        assessment_id: AssessmentId,
        relationship_id: SupplierRelationshipId,
        assessment_type: AssessmentType,
        created_at: datetime,
        questions: Iterable[AssessmentQuestion],
        answers: Iterable[AssessmentAnswer] = (),
        completed_at: datetime | None = None,
        score: AssessmentScore | None = None,
        decision: AssessmentDecision | None = None,
    ) -> Self:
        assessment = cls(
            assessment_id=assessment_id,
            relationship_id=relationship_id,
            assessment_type=assessment_type,
            created_at=created_at,
            _completed_at=completed_at,
            _score=score,
            _decision=decision,
        )
        for question in questions:
            assessment._add_question(question)
        for answer in answers:
            assessment._answers[answer.question_code] = answer
        return assessment

    @property
    def id(self) -> AssessmentId:
        return self.assessment_id

    @property
    def questions(self) -> tuple[AssessmentQuestion, ...]:
        return tuple(self._questions.values())

    @property
    def answers(self) -> tuple[AssessmentAnswer, ...]:
        return tuple(self._answers.values())

    @property
    def completed_at(self) -> datetime | None:
        return self._completed_at

    @property
    def score(self) -> AssessmentScore | None:
        return self._score

    @property
    def decision(self) -> AssessmentDecision | None:
        return self._decision

    @property
    def is_complete(self) -> bool:
        return self._completed_at is not None

    @property
    def required_answers_complete(self) -> bool:
        return not self.missing_mandatory_question_codes

    @property
    def missing_mandatory_question_codes(self) -> tuple[str, ...]:
        return tuple(
            question.code
            for question in self.questions
            if question.mandatory and question.code not in self._answers
        )

    def record_answer(self, answer: AssessmentAnswer) -> None:
        self._require_open()
        question = self._questions.get(answer.question_code)
        if question is None:
            raise UnknownAssessmentQuestion(f"Unknown assessment question {answer.question_code}")
        if answer.score > question.maximum_score:
            raise InvalidAssessmentAnswer(
                f"Answer score for {answer.question_code} exceeds maximum {question.maximum_score}"
            )
        self._answers[answer.question_code] = answer

    def complete(
        self,
        *,
        occurred_at: datetime,
        decision: AssessmentDecision | None = None,
    ) -> None:
        self._require_open()
        missing = self.missing_mandatory_question_codes
        if missing:
            raise MandatoryAssessmentAnswersMissing(missing)

        total_maximum = sum(question.maximum_score for question in self.questions)
        earned = sum(answer.score for answer in self.answers)
        score = AssessmentScore((earned * 100) // total_maximum)

        self._completed_at = occurred_at
        self._score = score
        self._decision = decision
        self._record(
            SupplierAssessmentCompleted(
                event_id=uuid4(),
                assessment_id=self.id,
                relationship_id=self.relationship_id,
                assessment_type=self.assessment_type,
                score=score,
                decision=decision,
                occurred_at=occurred_at,
            )
        )

    def pull_events(self) -> tuple[DomainEvent, ...]:
        events = tuple(self._events)
        self._events.clear()
        return events

    def _add_question(self, question: AssessmentQuestion) -> None:
        if question.code in self._questions:
            raise DuplicateAssessmentQuestion(f"Assessment question {question.code} is duplicated")
        self._questions[question.code] = question

    def _require_open(self) -> None:
        if self.is_complete:
            raise AssessmentAlreadyCompleted(f"SupplierAssessment {self.id} is complete")

    def _record(self, event: DomainEvent) -> None:
        self._events.append(event)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SupplierAssessment) and self.assessment_id == other.assessment_id
