"""Supplier Aggregate tests."""

from datetime import datetime, timezone

import pytest

from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.errors import DuplicateExternalIdentifier
from pysrmkit.domain.supplier.events import SupplierCreated
from pysrmkit.domain.supplier.value_objects import ExternalIdentifier, SupplierId, SupplierIdentity

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)


def test_supplier_create_records_supplier_created_and_preserves_stable_identity() -> None:
    supplier_id = SupplierId.new()
    identifier = ExternalIdentifier(kind="SIREN", value="123456789")

    supplier = Supplier.create(
        supplier_id=supplier_id,
        identity=SupplierIdentity(legal_name="ACME"),
        occurred_at=NOW,
        external_identifiers=(identifier,),
    )

    assert supplier.id == supplier_id
    assert supplier.external_identifiers == (identifier,)

    events = supplier.pull_events()
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, SupplierCreated)
    assert event.supplier_id == supplier_id
    assert event.occurred_at == NOW
    assert supplier.pull_events() == ()


def test_supplier_rejects_duplicate_external_identifier_inside_aggregate() -> None:
    identifier = ExternalIdentifier(kind="SIREN", value="123456789")
    supplier = Supplier.create(
        supplier_id=SupplierId.new(),
        identity=SupplierIdentity(legal_name="ACME"),
        occurred_at=NOW,
        external_identifiers=(identifier,),
    )

    with pytest.raises(DuplicateExternalIdentifier):
        supplier.add_external_identifier(identifier)


def test_supplier_identity_can_be_updated_without_changing_entity_identity() -> None:
    supplier = Supplier.create(
        supplier_id=SupplierId.new(),
        identity=SupplierIdentity(legal_name="Old Name"),
        occurred_at=NOW,
    )
    supplier_id = supplier.id

    supplier.update_identity(SupplierIdentity(legal_name="New Name"))

    assert supplier.id == supplier_id
    assert supplier.identity.legal_name == "New Name"


def test_supplier_entity_equality_uses_supplier_id() -> None:
    supplier_id = SupplierId.new()
    left = Supplier.reconstitute(
        supplier_id=supplier_id,
        identity=SupplierIdentity(legal_name="Old Name"),
    )
    right = Supplier.reconstitute(
        supplier_id=supplier_id,
        identity=SupplierIdentity(legal_name="Different Name"),
    )
    another = Supplier.reconstitute(
        supplier_id=SupplierId.new(),
        identity=SupplierIdentity(legal_name="Old Name"),
    )

    assert left == right
    assert left != another
    assert left != object()


def test_reconstituted_supplier_has_no_pending_domain_events() -> None:
    supplier = Supplier.reconstitute(
        supplier_id=SupplierId.new(),
        identity=SupplierIdentity(legal_name="ACME"),
        external_identifiers=(ExternalIdentifier(kind="SIREN", value="123456789"),),
    )

    assert supplier.pull_events() == ()
