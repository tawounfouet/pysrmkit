"""Compatibility tests for the 0.3.0a5 public Domain Event surface."""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from pysrmkit import (
    PySRMKit,
    SupplierCreated,
    SupplierInvited,
    SupplierRelationshipCreated,
)
from pysrmkit.adapters.sqlalchemy.schema import load_persistence_metadata
from pysrmkit.public import PersistenceError


def test_in_memory_runtime_exposes_typed_public_subscription_in_order() -> None:
    srm = PySRMKit.in_memory()
    observed: list[str] = []

    srm.events.subscribe(SupplierCreated, lambda event: observed.append(type(event).__name__))
    srm.events.subscribe(
        SupplierRelationshipCreated,
        lambda event: observed.append(type(event).__name__),
    )
    srm.events.subscribe(SupplierInvited, lambda event: observed.append(type(event).__name__))

    supplier = srm.suppliers.register(legal_name="Event Supplier")
    relationship = srm.relationships.create(
        supplier_id=supplier.supplier_id,
        organization_id="HQ",
    )
    srm.relationships.invite(relationship_id=relationship.relationship_id)

    assert observed == [
        "SupplierCreated",
        "SupplierRelationshipCreated",
        "SupplierInvited",
    ]


def test_sql_public_event_is_delivered_after_commit() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    load_persistence_metadata().create_all(engine)
    srm = PySRMKit.sql(engine)
    committed_supplier_ids = []

    def observe(event: SupplierCreated) -> None:
        view = srm.suppliers.get(supplier_id=event.supplier_id)
        committed_supplier_ids.append(view.supplier_id)

    srm.events.subscribe(SupplierCreated, observe)
    result = srm.suppliers.register(legal_name="Committed Event Supplier")

    assert committed_supplier_ids == [result.supplier_id]


def test_public_event_contract_exposes_stable_identity_and_timestamp() -> None:
    srm = PySRMKit.in_memory()
    observed: list[SupplierCreated] = []
    srm.events.subscribe(SupplierCreated, observed.append)

    result = srm.suppliers.register(legal_name="Contract Supplier")

    assert len(observed) == 1
    event = observed[0]
    assert event.supplier_id == result.supplier_id
    assert event.event_id is not None
    assert event.occurred_at.tzinfo is not None


def test_failed_sql_commit_publishes_no_public_event() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    load_persistence_metadata().create_all(engine)
    srm = PySRMKit.sql(engine)
    observed: list[SupplierCreated] = []
    srm.events.subscribe(SupplierCreated, observed.append)

    def fail_commit(session: Session) -> None:
        del session
        raise SQLAlchemyError("forced commit failure")

    event.listen(Session, "before_commit", fail_commit)
    try:
        with pytest.raises(PersistenceError):
            srm.suppliers.register(legal_name="Must Roll Back")
    finally:
        event.remove(Session, "before_commit", fail_commit)

    assert observed == []
