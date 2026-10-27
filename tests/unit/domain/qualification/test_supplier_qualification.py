"""SupplierQualification Aggregate tests."""

from datetime import UTC, datetime, timedelta

import pytest

from pysrmkit.domain.qualification.entities import SupplierQualification
from pysrmkit.domain.qualification.errors import InvalidQualificationState
from pysrmkit.domain.qualification.events import (
    SupplierQualificationRejected,
    SupplierQualificationRequested,
    SupplierQualified,
)
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

REQUESTED_AT = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
DECIDED_AT = REQUESTED_AT + timedelta(hours=1)


def make_scope() -> QualificationScope:
    return QualificationScope(organization_id=InternalOrganizationId("ORG-A"))


def approved_decision() -> QualificationDecision:
    return QualificationDecision(
        approved=True,
        resulting_status=QualificationStatus.QUALIFIED,
        reasons=("All qualification requirements are satisfied",),
        failed_requirements=(),
        decided_at=DECIDED_AT,
    )


def rejected_decision() -> QualificationDecision:
    return QualificationDecision(
        approved=False,
        resulting_status=QualificationStatus.NOT_QUALIFIED,
        reasons=("Assessment score must be at least 80",),
        failed_requirements=("ASSESSMENT_MINIMUM_SCORE",),
        decided_at=DECIDED_AT,
    )


def test_request_creates_pending_qualification_and_records_event() -> None:
    qualification_id = QualificationId.new()
    relationship_id = SupplierRelationshipId.new()
    scope = make_scope()

    qualification = SupplierQualification.request(
        qualification_id=qualification_id,
        relationship_id=relationship_id,
        scope=scope,
        occurred_at=REQUESTED_AT,
    )

    assert qualification.id == qualification_id
    assert qualification.relationship_id == relationship_id
    assert qualification.scope == scope
    assert qualification.status is QualificationStatus.PENDING
    assert qualification.decision is None
    assert qualification.is_current is True

    events = qualification.pull_events()
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, SupplierQualificationRequested)
    assert event.qualification_id == qualification_id
    assert event.relationship_id == relationship_id
    assert event.scope == scope
    assert event.occurred_at == REQUESTED_AT
    assert qualification.pull_events() == ()


def test_apply_approved_decision_qualifies_and_records_event() -> None:
    qualification = SupplierQualification.request(
        qualification_id=QualificationId.new(),
        relationship_id=SupplierRelationshipId.new(),
        scope=make_scope(),
        occurred_at=REQUESTED_AT,
    )
    qualification.pull_events()
    decision = approved_decision()

    qualification.apply_decision(decision)

    assert qualification.status is QualificationStatus.QUALIFIED
    assert qualification.decision == decision
    events = qualification.pull_events()
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, SupplierQualified)
    assert event.qualification_id == qualification.id
    assert event.relationship_id == qualification.relationship_id
    assert event.scope == qualification.scope
    assert event.occurred_at == DECIDED_AT


def test_apply_rejected_decision_rejects_and_records_explanation() -> None:
    qualification = SupplierQualification.request(
        qualification_id=QualificationId.new(),
        relationship_id=SupplierRelationshipId.new(),
        scope=make_scope(),
        occurred_at=REQUESTED_AT,
    )
    qualification.pull_events()
    decision = rejected_decision()

    qualification.apply_decision(decision)

    assert qualification.status is QualificationStatus.NOT_QUALIFIED
    assert qualification.decision == decision
    events = qualification.pull_events()
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, SupplierQualificationRejected)
    assert event.decision_reasons == decision.reasons
    assert event.occurred_at == DECIDED_AT


def test_only_pending_qualification_can_receive_first_decision() -> None:
    qualification = SupplierQualification.request(
        qualification_id=QualificationId.new(),
        relationship_id=SupplierRelationshipId.new(),
        scope=make_scope(),
        occurred_at=REQUESTED_AT,
    )
    qualification.pull_events()
    first = approved_decision()
    qualification.apply_decision(first)
    qualification.pull_events()

    with pytest.raises(InvalidQualificationState):
        qualification.apply_decision(rejected_decision())

    assert qualification.status is QualificationStatus.QUALIFIED
    assert qualification.decision == first
    assert qualification.pull_events() == ()


def test_reconstituted_qualification_does_not_recreate_historical_events() -> None:
    decision = approved_decision()
    qualification = SupplierQualification.reconstitute(
        qualification_id=QualificationId.new(),
        relationship_id=SupplierRelationshipId.new(),
        scope=make_scope(),
        requested_at=REQUESTED_AT,
        status=QualificationStatus.QUALIFIED,
        decision=decision,
    )

    assert qualification.status is QualificationStatus.QUALIFIED
    assert qualification.decision == decision
    assert qualification.pull_events() == ()


def test_current_semantics_distinguish_terminal_historical_statuses() -> None:
    for status in (
        QualificationStatus.PENDING,
        QualificationStatus.QUALIFIED,
        QualificationStatus.NOT_QUALIFIED,
    ):
        qualification = SupplierQualification.reconstitute(
            qualification_id=QualificationId.new(),
            relationship_id=SupplierRelationshipId.new(),
            scope=make_scope(),
            requested_at=REQUESTED_AT,
            status=status,
        )
        assert qualification.is_current is True

    for status in (QualificationStatus.REVOKED, QualificationStatus.EXPIRED):
        qualification = SupplierQualification.reconstitute(
            qualification_id=QualificationId.new(),
            relationship_id=SupplierRelationshipId.new(),
            scope=make_scope(),
            requested_at=REQUESTED_AT,
            status=status,
        )
        assert qualification.is_current is False


def test_qualification_entity_equality_uses_qualification_id() -> None:
    qualification_id = QualificationId.new()
    left = SupplierQualification.reconstitute(
        qualification_id=qualification_id,
        relationship_id=SupplierRelationshipId.new(),
        scope=make_scope(),
        requested_at=REQUESTED_AT,
        status=QualificationStatus.PENDING,
    )
    right = SupplierQualification.reconstitute(
        qualification_id=qualification_id,
        relationship_id=SupplierRelationshipId.new(),
        scope=make_scope(),
        requested_at=DECIDED_AT,
        status=QualificationStatus.NOT_QUALIFIED,
    )
    another = SupplierQualification.reconstitute(
        qualification_id=QualificationId.new(),
        relationship_id=left.relationship_id,
        scope=left.scope,
        requested_at=REQUESTED_AT,
        status=QualificationStatus.PENDING,
    )

    assert left == right
    assert left != another
    assert left != object()
