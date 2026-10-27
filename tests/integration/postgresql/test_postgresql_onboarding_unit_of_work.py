"""PostgreSQL integration tests for transactional Supplier onboarding."""

import os
from datetime import UTC, datetime

import pytest
from sqlalchemy.orm import Session, sessionmaker

from pysrmkit.adapters.clock.fixed import FixedClock
from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.repositories.onboarding import (
    SqlAlchemySupplierOnboardingRepository,
)
from pysrmkit.adapters.sqlalchemy.repositories.relationship import (
    SqlAlchemySupplierRelationshipRepository,
)
from pysrmkit.adapters.sqlalchemy.repositories.supplier import SqlAlchemySupplierRepository
from pysrmkit.adapters.sqlalchemy.session import create_session_factory
from pysrmkit.adapters.sqlalchemy.unit_of_work import SqlAlchemySupplierOnboardingUnitOfWork
from pysrmkit.application.relationship.commands import StartSupplierOnboarding
from pysrmkit.application.relationship.handlers import StartSupplierOnboardingHandler
from pysrmkit.domain.common.events import DomainEvent
from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.events import SupplierOnboardingStarted
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierLifecycleStage,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import SupplierId, SupplierIdentity

pytestmark = pytest.mark.postgresql
DATABASE_URL = os.environ.get("PYSRMKIT_POSTGRESQL_TEST_URL")
NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


class RecordingDispatcher:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def dispatch(self, events: tuple[DomainEvent, ...]) -> None:
        self.events.extend(events)


class FailingCommitSession(Session):
    def commit(self) -> None:
        self.flush()
        raise RuntimeError("forced commit failure")


def _engine():
    if DATABASE_URL is None:
        pytest.skip("PYSRMKIT_POSTGRESQL_TEST_URL is not configured")
    engine = create_persistence_engine(DATABASE_URL)
    PersistenceBase.metadata.drop_all(engine)
    PersistenceBase.metadata.create_all(engine)
    return engine


def _seed_invited_relationship(
    session_factory: sessionmaker[Session],
) -> SupplierRelationshipId:
    with session_factory() as session:
        suppliers = SqlAlchemySupplierRepository(session)
        relationships = SqlAlchemySupplierRelationshipRepository(session)
        supplier = Supplier.reconstitute(
            supplier_id=SupplierId.new(),
            identity=SupplierIdentity(legal_name="Transactional PostgreSQL Supplier"),
        )
        relationship = SupplierRelationship.reconstitute(
            relationship_id=SupplierRelationshipId.new(),
            supplier_id=supplier.id,
            organization_id=InternalOrganizationId("ORG-PG"),
            stage=SupplierLifecycleStage.INVITED,
        )
        suppliers.save(supplier)
        relationships.save(relationship)
        session.commit()
        return relationship.id


def test_postgresql_unit_of_work_commits_relationship_and_onboarding_atomically() -> None:
    engine = _engine()
    session_factory = create_session_factory(engine)
    relationship_id = _seed_invited_relationship(session_factory)
    dispatcher = RecordingDispatcher()
    handler = StartSupplierOnboardingHandler(
        unit_of_work=SqlAlchemySupplierOnboardingUnitOfWork(session_factory),
        clock=FixedClock(NOW),
        event_dispatcher=dispatcher,
    )

    try:
        handler.handle(StartSupplierOnboarding(relationship_id=relationship_id))

        with session_factory() as verification:
            relationship = SqlAlchemySupplierRelationshipRepository(verification).get(
                relationship_id
            )
            onboarding = SqlAlchemySupplierOnboardingRepository(
                verification
            ).find_for_relationship(relationship_id)

        assert relationship is not None
        assert relationship.stage is SupplierLifecycleStage.ONBOARDING
        assert onboarding is not None
        assert len(dispatcher.events) == 1
        assert isinstance(dispatcher.events[0], SupplierOnboardingStarted)
    finally:
        engine.dispose()


def test_postgresql_commit_failure_rolls_back_both_aggregates_and_event() -> None:
    engine = _engine()
    normal_factory = create_session_factory(engine)
    relationship_id = _seed_invited_relationship(normal_factory)
    failing_factory = sessionmaker(bind=engine, class_=FailingCommitSession)
    dispatcher = RecordingDispatcher()
    handler = StartSupplierOnboardingHandler(
        unit_of_work=SqlAlchemySupplierOnboardingUnitOfWork(failing_factory),
        clock=FixedClock(NOW),
        event_dispatcher=dispatcher,
    )

    try:
        with pytest.raises(RuntimeError, match="forced commit failure"):
            handler.handle(StartSupplierOnboarding(relationship_id=relationship_id))

        with normal_factory() as verification:
            relationship = SqlAlchemySupplierRelationshipRepository(verification).get(
                relationship_id
            )
            onboarding = SqlAlchemySupplierOnboardingRepository(
                verification
            ).find_for_relationship(relationship_id)

        assert relationship is not None
        assert relationship.stage is SupplierLifecycleStage.INVITED
        assert onboarding is None
        assert dispatcher.events == []
    finally:
        engine.dispose()
