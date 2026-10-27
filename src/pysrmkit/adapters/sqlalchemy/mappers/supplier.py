"""Explicit mapping between Supplier Domain state and persistence records."""

from pysrmkit.adapters.sqlalchemy.models.supplier import (
    SupplierExternalIdentifierRecord,
    SupplierRecord,
)
from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import (
    CountryCode,
    ExternalIdentifier,
    SupplierId,
    SupplierIdentity,
)


def _identifier_record(identifier: ExternalIdentifier) -> SupplierExternalIdentifierRecord:
    return SupplierExternalIdentifierRecord(
        kind=identifier.kind,
        value=identifier.value,
        source_system=identifier.source_system or "",
        jurisdiction=identifier.jurisdiction.value if identifier.jurisdiction is not None else "",
    )


def new_supplier_record(supplier: Supplier) -> SupplierRecord:
    """Create a new persistence record from current Supplier state."""

    identity = supplier.identity
    return SupplierRecord(
        supplier_id=supplier.id.value,
        legal_name=identity.legal_name,
        trading_name=identity.trading_name,
        supplier_type=identity.supplier_type,
        country_code=identity.country.value if identity.country is not None else None,
        external_identifiers=[
            _identifier_record(identifier) for identifier in supplier.external_identifiers
        ],
    )


def apply_supplier_state(record: SupplierRecord, supplier: Supplier) -> None:
    """Synchronize an existing persistence record from a Supplier Aggregate."""

    identity = supplier.identity
    record.legal_name = identity.legal_name
    record.trading_name = identity.trading_name
    record.supplier_type = identity.supplier_type
    record.country_code = identity.country.value if identity.country is not None else None
    record.external_identifiers = [
        _identifier_record(identifier) for identifier in supplier.external_identifiers
    ]


def supplier_from_record(record: SupplierRecord) -> Supplier:
    """Reconstitute a persistence-ignorant Supplier Aggregate."""

    return Supplier.reconstitute(
        supplier_id=SupplierId(record.supplier_id),
        identity=SupplierIdentity(
            legal_name=record.legal_name,
            trading_name=record.trading_name,
            supplier_type=record.supplier_type,
            country=CountryCode(record.country_code) if record.country_code is not None else None,
        ),
        external_identifiers=tuple(
            ExternalIdentifier(
                kind=item.kind,
                value=item.value,
                source_system=item.source_system or None,
                jurisdiction=CountryCode(item.jurisdiction) if item.jurisdiction else None,
            )
            for item in record.external_identifiers
        ),
    )
