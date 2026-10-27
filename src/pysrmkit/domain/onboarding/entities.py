"""SupplierOnboarding Aggregate Root."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import uuid4

from pysrmkit.domain.common.events import DomainEvent
from pysrmkit.domain.onboarding.errors import (
    DuplicateOnboardingRequirement,
    MandatoryOnboardingRequirementsNotSatisfied,
    OnboardingAlreadyCompleted,
    UnknownOnboardingRequirement,
)
from pysrmkit.domain.onboarding.events import SupplierOnboardingCompleted
from pysrmkit.domain.onboarding.value_objects import (
    OnboardingId,
    OnboardingProgress,
    OnboardingRequirement,
    OnboardingRequirementCode,
)
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


def _requirement_map() -> dict[OnboardingRequirementCode, OnboardingRequirement]:
    return {}


def _domain_event_list() -> list[DomainEvent]:
    return []


@dataclass(slots=True, eq=False)
class SupplierOnboarding:
    """Relationship-scoped onboarding readiness Aggregate."""

    onboarding_id: OnboardingId
    relationship_id: SupplierRelationshipId
    started_at: datetime
    _requirements: dict[OnboardingRequirementCode, OnboardingRequirement] = field(
        default_factory=_requirement_map,
        repr=False,
    )
    _completed_at: datetime | None = field(default=None, repr=False)
    _events: list[DomainEvent] = field(default_factory=_domain_event_list, repr=False)

    @classmethod
    def create(
        cls,
        *,
        onboarding_id: OnboardingId,
        relationship_id: SupplierRelationshipId,
        started_at: datetime,
        requirements: Iterable[OnboardingRequirement] = (),
    ) -> Self:
        onboarding = cls(
            onboarding_id=onboarding_id,
            relationship_id=relationship_id,
            started_at=started_at,
        )
        for requirement in requirements:
            onboarding._add_requirement(requirement)
        return onboarding

    @classmethod
    def reconstitute(
        cls,
        *,
        onboarding_id: OnboardingId,
        relationship_id: SupplierRelationshipId,
        started_at: datetime,
        requirements: Iterable[OnboardingRequirement] = (),
        completed_at: datetime | None = None,
    ) -> Self:
        onboarding = cls(
            onboarding_id=onboarding_id,
            relationship_id=relationship_id,
            started_at=started_at,
            _completed_at=completed_at,
        )
        for requirement in requirements:
            onboarding._add_requirement(requirement)
        return onboarding

    @property
    def id(self) -> OnboardingId:
        return self.onboarding_id

    @property
    def requirements(self) -> tuple[OnboardingRequirement, ...]:
        return tuple(self._requirements.values())

    @property
    def completed_at(self) -> datetime | None:
        return self._completed_at

    @property
    def is_complete(self) -> bool:
        return self._completed_at is not None

    @property
    def progress(self) -> OnboardingProgress:
        requirements = self.requirements
        mandatory = tuple(item for item in requirements if item.mandatory)
        satisfied = tuple(item for item in requirements if item.satisfied)
        satisfied_mandatory = tuple(item for item in mandatory if item.satisfied)
        missing = tuple(item.code for item in mandatory if not item.satisfied)
        return OnboardingProgress(
            total_requirements=len(requirements),
            satisfied_requirements=len(satisfied),
            mandatory_requirements=len(mandatory),
            satisfied_mandatory_requirements=len(satisfied_mandatory),
            missing_mandatory_requirements=missing,
            completed=self.is_complete,
        )

    def satisfy_requirement(self, code: OnboardingRequirementCode) -> None:
        self._require_open()
        requirement = self._requirements.get(code)
        if requirement is None:
            raise UnknownOnboardingRequirement(f"Unknown onboarding requirement {code}")
        self._requirements[code] = requirement.satisfy()

    def complete(self, *, occurred_at: datetime) -> None:
        self._require_open()
        missing = self.progress.missing_mandatory_requirements
        if missing:
            raise MandatoryOnboardingRequirementsNotSatisfied(missing)
        self._completed_at = occurred_at
        self._record(
            SupplierOnboardingCompleted(
                event_id=uuid4(),
                onboarding_id=self.id,
                relationship_id=self.relationship_id,
                occurred_at=occurred_at,
            )
        )

    def pull_events(self) -> tuple[DomainEvent, ...]:
        events = tuple(self._events)
        self._events.clear()
        return events

    def _add_requirement(self, requirement: OnboardingRequirement) -> None:
        if requirement.code in self._requirements:
            raise DuplicateOnboardingRequirement(
                f"Onboarding requirement {requirement.code} is duplicated"
            )
        self._requirements[requirement.code] = requirement

    def _require_open(self) -> None:
        if self.is_complete:
            raise OnboardingAlreadyCompleted(f"SupplierOnboarding {self.id} is already complete")

    def _record(self, event: DomainEvent) -> None:
        self._events.append(event)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SupplierOnboarding) and self.onboarding_id == other.onboarding_id
