"""SupplierQualification Aggregate Root."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import uuid4

from pysrmkit.domain.common.events import DomainEvent
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
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


def _domain_event_list() -> list[DomainEvent]:
    return []


@dataclass(slots=True, eq=False)
class SupplierQualification:
    """Qualification of one SupplierRelationship within an explicit business scope."""

    qualification_id: QualificationId
    relationship_id: SupplierRelationshipId
    scope: QualificationScope
    requested_at: datetime
    _status: QualificationStatus = field(repr=False)
    _decision: QualificationDecision | None = field(default=None, repr=False)
    _events: list[DomainEvent] = field(default_factory=_domain_event_list, repr=False)

    @classmethod
    def request(
        cls,
        *,
        qualification_id: QualificationId,
        relationship_id: SupplierRelationshipId,
        scope: QualificationScope,
        occurred_at: datetime,
    ) -> Self:
        qualification = cls(
            qualification_id=qualification_id,
            relationship_id=relationship_id,
            scope=scope,
            requested_at=occurred_at,
            _status=QualificationStatus.PENDING,
        )
        qualification._record(
            SupplierQualificationRequested(
                event_id=uuid4(),
                qualification_id=qualification_id,
                relationship_id=relationship_id,
                scope=scope,
                occurred_at=occurred_at,
            )
        )
        return qualification

    @classmethod
    def reconstitute(
        cls,
        *,
        qualification_id: QualificationId,
        relationship_id: SupplierRelationshipId,
        scope: QualificationScope,
        requested_at: datetime,
        status: QualificationStatus,
        decision: QualificationDecision | None = None,
    ) -> Self:
        return cls(
            qualification_id=qualification_id,
            relationship_id=relationship_id,
            scope=scope,
            requested_at=requested_at,
            _status=status,
            _decision=decision,
        )

    @property
    def id(self) -> QualificationId:
        return self.qualification_id

    @property
    def status(self) -> QualificationStatus:
        return self._status

    @property
    def decision(self) -> QualificationDecision | None:
        return self._decision

    @property
    def is_current(self) -> bool:
        return self._status not in {QualificationStatus.REVOKED, QualificationStatus.EXPIRED}

    def apply_decision(self, decision: QualificationDecision) -> None:
        if self._status is not QualificationStatus.PENDING:
            raise InvalidQualificationState(
                f"Qualification decision requires PENDING status, got {self._status}"
            )

        self._status = decision.resulting_status
        self._decision = decision

        if decision.approved:
            self._record(
                SupplierQualified(
                    event_id=uuid4(),
                    qualification_id=self.id,
                    relationship_id=self.relationship_id,
                    scope=self.scope,
                    occurred_at=decision.decided_at,
                )
            )
        else:
            self._record(
                SupplierQualificationRejected(
                    event_id=uuid4(),
                    qualification_id=self.id,
                    relationship_id=self.relationship_id,
                    scope=self.scope,
                    decision_reasons=decision.reasons,
                    occurred_at=decision.decided_at,
                )
            )

    def pull_events(self) -> tuple[DomainEvent, ...]:
        events = tuple(self._events)
        self._events.clear()
        return events

    def _record(self, event: DomainEvent) -> None:
        self._events.append(event)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, SupplierQualification)
            and self.qualification_id == other.qualification_id
        )
