"""SQLAlchemy implementation of SupplierRepository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.mappers.supplier import (
    apply_supplier_state,
    new_supplier_record,
    supplier_from_record,
)
from pysrmkit.adapters.sqlalchemy.models.supplier import (
    SupplierExternalIdentifierRecord,
    SupplierRecord,
)
from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import ExternalIdentifier, SupplierId


class SqlAlchemySupplierRepository:
    """Session-scoped SQLAlchemy Supplier repository.

    The repository stages persistence state but never commits the Session.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, supplier_id: SupplierId) -> Supplier | None:
        record = self._session.get(SupplierRecord, supplier_id.value)
        if record is None:
            return None
        return supplier_from_record(record)

    def save(self, supplier: Supplier) -> None:
        record = self._session.get(SupplierRecord, supplier.id.value)
        if record is None:
            self._session.add(new_supplier_record(supplier))
            return
        apply_supplier_state(record, supplier)

    def find_by_external_identifier(
        self,
        identifier: ExternalIdentifier,
    ) -> Supplier | None:
        source_system = identifier.source_system or ""
        jurisdiction = identifier.jurisdiction.value if identifier.jurisdiction is not None else ""
        statement = (
            select(SupplierRecord)
            .join(SupplierRecord.external_identifiers)
            .where(
                SupplierExternalIdentifierRecord.kind == identifier.kind,
                SupplierExternalIdentifierRecord.value == identifier.value,
                SupplierExternalIdentifierRecord.source_system == source_system,
                SupplierExternalIdentifierRecord.jurisdiction == jurisdiction,
            )
        )
        record = self._session.scalar(statement)
        if record is None:
            return None
        return supplier_from_record(record)
