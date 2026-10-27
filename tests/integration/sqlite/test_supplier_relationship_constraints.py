"""SQLite integration tests for first SQL-backed Supplier boundaries."""

from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.repositories.relationship import (
    SqlAlchemySupplierRelationshipRepository,
)
from pysrmkit.adapters.sqlalchemy.repositories.supplier import SqlAlchemySupplierRepository
from pysrmkit.adapters.sqlalchemy.session import create_session_factory
from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import (
    ExternalIdentifier,
    SupplierId,
    SupplierIdentity,
)

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


def _session() -> tuple[Session, object]:
    engine = create_persistence_engine("sqlite:///:memory:")
    PersistenceBase.metadata.create_all(engine)
    return create_session_factory(engine)(), engine


def _supplier(
    *,
    supplier_id: SupplierId | None = None,
    identifier: ExternalIdentifier | None = None,
) -> Supplier:
    return Supplier.reconstitute(
        supplier_id=supplier_id or SupplierId.new(),
        identity=SupplierIdentity(legal_name="Constraint Supplier"),
        external_identifiers=() if identifier is None else (identifier,),
    )


def test_relationship_foreign_key_requires_existing_supplier() -> None:
    session, engine = _session()
    repository = SqlAlchemySupplierRelationshipRepository(session)
    relationship = SupplierRelationship.reconstitute(
        relationship_id=SupplierRelationshipId.new(),
        supplier_id=SupplierId.new(),
        organization_id=InternalOrganizationId("ORG-A"),
    )

    try:
        repository.save(relationship)

        with pytest.raises(IntegrityError):
            session.flush()
    finally:
        session.rollback()
        session.close()
        engine.dispose()


def test_relationship_supplier_organization_is_unique() -> None:
    session, engine = _session()
    suppliers = SqlAlchemySupplierRepository(session)
    relationships = SqlAlchemySupplierRelationshipRepository(session)
    supplier = _supplier()
    first = SupplierRelationship.reconstitute(
        relationship_id=SupplierRelationshipId.new(),
        supplier_id=supplier.id,
        organization_id=InternalOrganizationId("ORG-A"),
    )
    second = SupplierRelationship.reconstitute(
        relationship_id=SupplierRelationshipId.new(),
        supplier_id=supplier.id,
        organization_id=InternalOrganizationId("ORG-A"),
    )

    try:
        suppliers.save(supplier)
        relationships.save(first)
        session.flush()
        relationships.save(second)

        with pytest.raises(IntegrityError):
            session.flush()
    finally:
        session.rollback()
        session.close()
        engine.dispose()


def test_external_identifier_identity_is_unique_across_suppliers() -> None:
    session, engine = _session()
    repository = SqlAlchemySupplierRepository(session)
    identifier = ExternalIdentifier(
        kind="SIREN",
        value="123456789",
        source_system="LOCAL",
    )

    try:
        repository.save(_supplier(identifier=identifier))
        session.flush()
        repository.save(_supplier(identifier=identifier))

        with pytest.raises(IntegrityError):
            session.flush()
    finally:
        session.rollback()
        session.close()
        engine.dispose()
