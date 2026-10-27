"""Handlers orchestrating Supplier Relationship application use cases."""

from __future__ import annotations

from pysrmkit.application.onboarding.errors import SupplierOnboardingAlreadyExists
from pysrmkit.application.relationship.commands import (
    CreateSupplierRelationship,
    InviteSupplierRelationship,
    StartSupplierOnboarding,
)
from pysrmkit.application.relationship.errors import (
    RelationshipAlreadyExists,
    SupplierNotFound,
    SupplierRelationshipNotFound,
)
from pysrmkit.application.relationship.results import CreateSupplierRelationshipResult
from pysrmkit.domain.onboarding.entities import SupplierOnboarding
from pysrmkit.domain.onboarding.value_objects import (
    OnboardingId,
    OnboardingRequirement,
    OnboardingRequirementCode,
)
from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId
from pysrmkit.ports.clock import Clock
from pysrmkit.ports.events import DomainEventDispatcher
from pysrmkit.ports.repositories.relationship import SupplierRelationshipRepository
from pysrmkit.ports.repositories.supplier import SupplierRepository
from pysrmkit.ports.unit_of_work import SupplierOnboardingUnitOfWork


class CreateSupplierRelationshipHandler:
    """Application orchestration for Supplier/organization relationship creation."""

    def __init__(
        self,
        *,
        supplier_repository: SupplierRepository,
        relationship_repository: SupplierRelationshipRepository,
        clock: Clock,
        event_dispatcher: DomainEventDispatcher,
    ) -> None:
        self._supplier_repository = supplier_repository
        self._relationship_repository = relationship_repository
        self._clock = clock
        self._event_dispatcher = event_dispatcher

    def handle(
        self,
        command: CreateSupplierRelationship,
    ) -> CreateSupplierRelationshipResult:
        supplier = self._supplier_repository.get(command.supplier_id)
        if supplier is None:
            raise SupplierNotFound(f"Supplier {command.supplier_id} does not exist")

        existing = self._relationship_repository.find_for_supplier_and_organization(
            command.supplier_id,
            command.organization_id,
        )
        if existing is not None:
            raise RelationshipAlreadyExists(
                "Relationship already exists for this Supplier and internal organization"
            )

        relationship = SupplierRelationship.create(
            relationship_id=SupplierRelationshipId.new(),
            supplier_id=command.supplier_id,
            organization_id=command.organization_id,
            occurred_at=self._clock.now(),
        )
        self._relationship_repository.save(relationship)
        self._event_dispatcher.dispatch(relationship.pull_events())

        return CreateSupplierRelationshipResult(relationship_id=relationship.id)


class InviteSupplierRelationshipHandler:
    """Application orchestration for inviting a SupplierRelationship."""

    def __init__(
        self,
        *,
        relationship_repository: SupplierRelationshipRepository,
        clock: Clock,
        event_dispatcher: DomainEventDispatcher,
    ) -> None:
        self._relationship_repository = relationship_repository
        self._clock = clock
        self._event_dispatcher = event_dispatcher

    def handle(self, command: InviteSupplierRelationship) -> None:
        relationship = self._load(command.relationship_id)
        relationship.invite(occurred_at=self._clock.now())
        self._relationship_repository.save(relationship)
        self._event_dispatcher.dispatch(relationship.pull_events())

    def _load(self, relationship_id: SupplierRelationshipId) -> SupplierRelationship:
        relationship = self._relationship_repository.get(relationship_id)
        if relationship is None:
            raise SupplierRelationshipNotFound(
                f"SupplierRelationship {relationship_id} does not exist"
            )
        return relationship


class StartSupplierOnboardingHandler:
    """Application orchestration for starting SupplierRelationship onboarding."""

    def __init__(
        self,
        *,
        unit_of_work: SupplierOnboardingUnitOfWork,
        clock: Clock,
        event_dispatcher: DomainEventDispatcher,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._clock = clock
        self._event_dispatcher = event_dispatcher

    def handle(self, command: StartSupplierOnboarding) -> None:
        with self._unit_of_work as unit_of_work:
            relationship = self._load(
                unit_of_work.relationship_repository,
                command.relationship_id,
            )
            existing = unit_of_work.onboarding_repository.find_for_relationship(relationship.id)
            if existing is not None:
                raise SupplierOnboardingAlreadyExists(
                    f"SupplierRelationship {relationship.id} already has onboarding"
                )

            occurred_at = self._clock.now()
            requirements = tuple(
                OnboardingRequirement(
                    code=OnboardingRequirementCode(item.code),
                    mandatory=item.mandatory,
                )
                for item in command.requirements
            )
            relationship.start_onboarding(occurred_at=occurred_at)
            onboarding = SupplierOnboarding.create(
                onboarding_id=OnboardingId.new(),
                relationship_id=relationship.id,
                started_at=occurred_at,
                requirements=requirements,
            )

            unit_of_work.relationship_repository.save(relationship)
            unit_of_work.onboarding_repository.save(onboarding)
            events = relationship.pull_events()
            unit_of_work.commit()

        self._event_dispatcher.dispatch(events)

    @staticmethod
    def _load(
        repository: SupplierRelationshipRepository,
        relationship_id: SupplierRelationshipId,
    ) -> SupplierRelationship:
        relationship = repository.get(relationship_id)
        if relationship is None:
            raise SupplierRelationshipNotFound(
                f"SupplierRelationship {relationship_id} does not exist"
            )
        return relationship
