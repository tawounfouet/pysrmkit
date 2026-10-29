"""SQLAlchemy implementation of SupplierRepository."""

from typing import Literal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

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
from pysrmkit.domain.supplier.value_objects import CountryCode, ExternalIdentifier, SupplierId
from pysrmkit.ports.queries.supplier import SupplierPage


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

    def list_suppliers(self, *, offset: int, limit: int) -> SupplierPage:
        total = self._session.scalar(select(func.count()).select_from(SupplierRecord)) or 0
        records = self._session.scalars(
            select(SupplierRecord).order_by(SupplierRecord.supplier_id).offset(offset).limit(limit)
        ).all()
        return SupplierPage(
            suppliers=tuple(supplier_from_record(record) for record in records),
            total=total,
        )

    def search_suppliers(
        self,
        *,
        query: str | None,
        country_code: CountryCode | None,
        supplier_type: str | None,
        sort_by: Literal["legal_name"],
        sort_order: Literal["asc", "desc"],
        offset: int,
        limit: int,
    ) -> SupplierPage:
        """Execute search, count, stable ordering and pagination in the database.

        Filters use bound SQLAlchemy expressions, including escaped literal
        substring matching (%, _ and / are not wildcard query instructions).
        Cross-backend Unicode case folding remains an A3 qualification topic.
        """
        if sort_by != "legal_name":
            raise ValueError("sort_by must be 'legal_name'")
        if sort_order not in ("asc", "desc"):
            raise ValueError("sort_order must be 'asc' or 'desc'")

        predicates: list[ColumnElement[bool]] = []
        if query is not None:
            needle = query.lower()
            predicates.append(
                or_(
                    func.lower(SupplierRecord.legal_name).contains(needle, autoescape=True),
                    func.lower(SupplierRecord.trading_name).contains(needle, autoescape=True),
                )
            )
        if country_code is not None:
            predicates.append(SupplierRecord.country_code == country_code.value)
        if supplier_type is not None:
            predicates.append(SupplierRecord.supplier_type == supplier_type)

        count_stmt = select(func.count()).select_from(SupplierRecord).where(*predicates)
        total = self._session.scalar(count_stmt) or 0
        name_order = func.lower(SupplierRecord.legal_name)
        name_ordering = name_order.asc() if sort_order == "asc" else name_order.desc()
        records = self._session.scalars(
            select(SupplierRecord)
            .where(*predicates)
            .order_by(name_ordering, SupplierRecord.supplier_id.asc())
            .offset(offset)
            .limit(limit)
        ).all()
        return SupplierPage(
            suppliers=tuple(supplier_from_record(record) for record in records),
            total=total,
        )
