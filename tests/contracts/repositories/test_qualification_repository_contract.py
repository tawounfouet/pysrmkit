"""Shared behavioral contract for SupplierQualificationRepository implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta

from pysrmkit.domain.qualification.entities import SupplierQualification
from pysrmkit.domain.qualification.value_objects import (
    QualificationDecision,
    QualificationId,
    QualificationScope,
    QualificationStatus,
)
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import CategoryCode
from pysrmkit.ports.repositories.qualification import SupplierQualificationRepository

REQUESTED_AT = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
DECIDED_AT = REQUESTED_AT + timedelta(hours=1)


def make_qualification(
    *,
    relationship_id: SupplierRelationshipId | None = None,
    scope: QualificationScope | None = None,
) -> SupplierQualification:
    return SupplierQualification.request(
        qualification_id=QualificationId.new(),
        relationship_id=relationship_id or SupplierRelationshipId.new(),
        scope=scope or QualificationScope(organization_id=InternalOrganizationId("ORG-A")),
        occurred_at=REQUESTED_AT,
    )


def approved_decision() -> QualificationDecision:
    return QualificationDecision(
        approved=True,
        resulting_status=QualificationStatus.QUALIFIED,
        reasons=("All qualification requirements are satisfied",),
        failed_requirements=(),
        decided_at=DECIDED_AT,
    )


class SupplierQualificationRepositoryContract(ABC):
    """Behavior every SupplierQualificationRepository adapter must preserve."""

    @abstractmethod
    def make_repository(self) -> SupplierQualificationRepository:
        raise NotImplementedError

    def prepare_qualification(self, qualification: SupplierQualification) -> None:
        """Prepare external Aggregate preconditions required by an adapter."""

    def test_save_then_get_returns_same_logical_qualification(self) -> None:
        repository = self.make_repository()
        qualification = make_qualification()
        qualification.pull_events()

        self.prepare_qualification(qualification)
        repository.save(qualification)
        loaded = repository.get(qualification.id)

        assert loaded is not None
        assert loaded == qualification
        assert loaded.relationship_id == qualification.relationship_id
        assert loaded.scope == qualification.scope
        assert loaded.status is QualificationStatus.PENDING
        assert loaded.pull_events() == ()

    def test_unknown_id_returns_none(self) -> None:
        repository = self.make_repository()

        assert repository.get(QualificationId.new()) is None

    def test_find_current_for_scope_returns_matching_qualification(self) -> None:
        repository = self.make_repository()
        relationship_id = SupplierRelationshipId.new()
        scope = QualificationScope(category_code=CategoryCode("IT_SERVICES"))
        qualification = make_qualification(relationship_id=relationship_id, scope=scope)
        qualification.pull_events()
        self.prepare_qualification(qualification)
        repository.save(qualification)

        loaded = repository.find_current_for_scope(relationship_id, scope)

        assert loaded is not None
        assert loaded.id == qualification.id

    def test_different_scopes_do_not_collide(self) -> None:
        repository = self.make_repository()
        relationship_id = SupplierRelationshipId.new()
        first_scope = QualificationScope(category_code=CategoryCode("IT_SERVICES"))
        second_scope = QualificationScope(category_code=CategoryCode("FACILITIES"))
        first = make_qualification(relationship_id=relationship_id, scope=first_scope)
        second = make_qualification(relationship_id=relationship_id, scope=second_scope)
        first.pull_events()
        second.pull_events()
        self.prepare_qualification(first)
        repository.save(first)
        self.prepare_qualification(second)
        repository.save(second)

        loaded_first = repository.find_current_for_scope(relationship_id, first_scope)
        loaded_second = repository.find_current_for_scope(relationship_id, second_scope)

        assert loaded_first is not None
        assert loaded_second is not None
        assert loaded_first.id == first.id
        assert loaded_second.id == second.id

    def test_different_relationships_do_not_collide_for_same_scope(self) -> None:
        repository = self.make_repository()
        scope = QualificationScope(category_code=CategoryCode("IT_SERVICES"))
        first_relationship = SupplierRelationshipId.new()
        second_relationship = SupplierRelationshipId.new()
        first = make_qualification(relationship_id=first_relationship, scope=scope)
        second = make_qualification(relationship_id=second_relationship, scope=scope)
        first.pull_events()
        second.pull_events()
        self.prepare_qualification(first)
        repository.save(first)
        self.prepare_qualification(second)
        repository.save(second)

        loaded_first = repository.find_current_for_scope(first_relationship, scope)
        loaded_second = repository.find_current_for_scope(second_relationship, scope)

        assert loaded_first is not None
        assert loaded_second is not None
        assert loaded_first.id == first.id
        assert loaded_second.id == second.id

    def test_updated_qualification_status_and_decision_survive_save_reload(self) -> None:
        repository = self.make_repository()
        qualification = make_qualification()
        qualification.pull_events()
        self.prepare_qualification(qualification)
        repository.save(qualification)

        loaded = repository.get(qualification.id)
        assert loaded is not None
        loaded.apply_decision(approved_decision())
        loaded.pull_events()
        repository.save(loaded)

        reloaded = repository.get(qualification.id)
        assert reloaded is not None
        assert reloaded.status is QualificationStatus.QUALIFIED
        assert reloaded.decision == approved_decision()
        assert reloaded.pull_events() == ()

    def test_unsaved_decision_does_not_leak_into_repository_state(self) -> None:
        repository = self.make_repository()
        qualification = make_qualification()
        qualification.pull_events()
        self.prepare_qualification(qualification)
        repository.save(qualification)

        loaded = repository.get(qualification.id)
        assert loaded is not None
        loaded.apply_decision(approved_decision())

        unchanged = repository.get(qualification.id)
        assert unchanged is not None
        assert unchanged.status is QualificationStatus.PENDING
        assert unchanged.decision is None

    def test_non_current_historical_qualification_is_not_returned_as_current(self) -> None:
        repository = self.make_repository()
        relationship_id = SupplierRelationshipId.new()
        scope = QualificationScope(category_code=CategoryCode("IT_SERVICES"))
        qualification = SupplierQualification.reconstitute(
            qualification_id=QualificationId.new(),
            relationship_id=relationship_id,
            scope=scope,
            requested_at=REQUESTED_AT,
            status=QualificationStatus.EXPIRED,
        )
        self.prepare_qualification(qualification)
        repository.save(qualification)

        assert repository.find_current_for_scope(relationship_id, scope) is None
