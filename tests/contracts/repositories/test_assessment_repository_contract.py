"""Shared behavioral contract for SupplierAssessmentRepository implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta

from pysrmkit.domain.assessment.entities import SupplierAssessment
from pysrmkit.domain.assessment.value_objects import (
    AssessmentAnswer,
    AssessmentId,
    AssessmentQuestion,
    AssessmentType,
)
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId
from pysrmkit.ports.repositories.assessment import SupplierAssessmentRepository

CREATED_AT = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
LATER = CREATED_AT + timedelta(hours=1)


def make_assessment(
    *,
    relationship_id: SupplierRelationshipId | None = None,
    created_at: datetime = CREATED_AT,
) -> SupplierAssessment:
    return SupplierAssessment.create(
        assessment_id=AssessmentId.new(),
        relationship_id=relationship_id or SupplierRelationshipId.new(),
        assessment_type=AssessmentType("QUESTIONNAIRE"),
        created_at=created_at,
        questions=(AssessmentQuestion(code="LEGAL", maximum_score=100),),
    )


class SupplierAssessmentRepositoryContract(ABC):
    """Behavior every SupplierAssessmentRepository adapter must preserve."""

    @abstractmethod
    def make_repository(self) -> SupplierAssessmentRepository:
        raise NotImplementedError

    def prepare_assessment(self, assessment: SupplierAssessment) -> None:
        """Prepare external Aggregate preconditions required by an adapter."""

    def test_save_then_get_returns_same_logical_assessment(self) -> None:
        repository = self.make_repository()
        assessment = make_assessment()

        self.prepare_assessment(assessment)
        repository.save(assessment)
        loaded = repository.get(assessment.id)

        assert loaded is not None
        assert loaded == assessment
        assert loaded.relationship_id == assessment.relationship_id
        assert loaded.questions == assessment.questions

    def test_unknown_id_returns_none(self) -> None:
        repository = self.make_repository()

        assert repository.get(AssessmentId.new()) is None

    def test_latest_assessment_for_relationship_is_returned(self) -> None:
        repository = self.make_repository()
        relationship_id = SupplierRelationshipId.new()
        first = make_assessment(relationship_id=relationship_id)
        second = make_assessment(relationship_id=relationship_id, created_at=LATER)
        self.prepare_assessment(first)
        repository.save(first)
        self.prepare_assessment(second)
        repository.save(second)

        loaded = repository.find_latest_for_relationship(relationship_id)

        assert loaded is not None
        assert loaded.id == second.id

    def test_answer_and_completion_state_survive_round_trip(self) -> None:
        repository = self.make_repository()
        assessment = make_assessment()
        assessment.record_answer(AssessmentAnswer(question_code="LEGAL", score=90))
        assessment.complete(occurred_at=LATER)
        assessment.pull_events()
        self.prepare_assessment(assessment)
        repository.save(assessment)

        loaded = repository.get(assessment.id)

        assert loaded is not None
        assert loaded.is_complete is True
        assert loaded.score is not None
        assert loaded.score.value == 90
        assert loaded.pull_events() == ()

    def test_unsaved_answer_does_not_leak_into_repository_state(self) -> None:
        repository = self.make_repository()
        assessment = make_assessment()
        self.prepare_assessment(assessment)
        repository.save(assessment)

        loaded = repository.get(assessment.id)
        assert loaded is not None
        loaded.record_answer(AssessmentAnswer(question_code="LEGAL", score=90))

        unchanged = repository.get(assessment.id)
        assert unchanged is not None
        assert unchanged.answers == ()

    def test_different_relationships_remain_isolated(self) -> None:
        repository = self.make_repository()
        first = make_assessment()
        second = make_assessment()
        self.prepare_assessment(first)
        repository.save(first)
        self.prepare_assessment(second)
        repository.save(second)

        loaded_first = repository.find_latest_for_relationship(first.relationship_id)
        loaded_second = repository.find_latest_for_relationship(second.relationship_id)

        assert loaded_first is not None
        assert loaded_second is not None
        assert loaded_first.id == first.id
        assert loaded_second.id == second.id
