"""SQLite UTC timestamp round-trip tests."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import select

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.models.onboarding import SupplierOnboardingRecord
from pysrmkit.adapters.sqlalchemy.repositories.relationship import (
    SqlAlchemySupplierRelationshipRepository,
)
from pysrmkit.adapters.sqlalchemy.repositories.supplier import SqlAlchemySupplierRepository
from pysrmkit.adapters.sqlalchemy.session import create_session_factory
from pysrmkit.adapters.sqlalchemy.types import UTCDateTime
from pysrmkit.domain.onboarding.value_objects import OnboardingId
from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import SupplierId, SupplierIdentity

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


def test_utc_datetime_rejects_naive_values() -> None:
    value_type = UTCDateTime()

    with pytest.raises(ValueError, match="timezone-aware"):
        value_type.process_bind_param(datetime(2026, 10, 27, 12, 0), None)  # type: ignore[arg-type]


def test_sqlite_round_trip_restores_timezone_aware_utc_datetime() -> None:
    engine = create_persistence_engine("sqlite:///:memory:")
    PersistenceBase.metadata.create_all(engine)
    session = create_session_factory(engine)()

    supplier = Supplier.reconstitute(
        supplier_id=SupplierId.new(),
        identity=SupplierIdentity(legal_name="UTC Supplier"),
    )
    relationship = SupplierRelationship.reconstitute(
        relationship_id=SupplierRelationshipId.new(),
        supplier_id=supplier.id,
        organization_id=InternalOrganizationId("ORG-UTC"),
    )

    try:
        SqlAlchemySupplierRepository(session).save(supplier)
        SqlAlchemySupplierRelationshipRepository(session).save(relationship)
        session.add(
            SupplierOnboardingRecord(
                onboarding_id=OnboardingId.new().value,
                relationship_id=relationship.id.value,
                started_at=NOW,
                completed_at=NOW,
            )
        )
        session.flush()
        session.expire_all()

        stored = session.scalar(select(SupplierOnboardingRecord))
        assert stored is not None
        assert stored.started_at == NOW
        assert stored.started_at.tzinfo is UTC
    finally:
        session.rollback()
        session.close()
        engine.dispose()
