"""Supplier Domain ↔ SQLAlchemy mapper tests."""

from pysrmkit.adapters.sqlalchemy.mappers.supplier import (
    new_supplier_record,
    supplier_from_record,
)
from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import (
    CountryCode,
    ExternalIdentifier,
    SupplierId,
    SupplierIdentity,
)


def test_supplier_mapper_preserves_full_first_core_identity() -> None:
    supplier = Supplier.reconstitute(
        supplier_id=SupplierId.new(),
        identity=SupplierIdentity(
            legal_name="  ACME France  ",
            trading_name=" ACME ",
            supplier_type=" LEGAL_ENTITY ",
            country=CountryCode("fr"),
        ),
        external_identifiers=(
            ExternalIdentifier(
                kind=" siren ",
                value="123456789",
                source_system=" local ",
                jurisdiction=CountryCode("fr"),
            ),
        ),
    )

    record = new_supplier_record(supplier)
    restored = supplier_from_record(record)

    assert restored == supplier
    assert restored.identity == supplier.identity
    assert restored.external_identifiers == supplier.external_identifiers
    assert restored.pull_events() == ()
