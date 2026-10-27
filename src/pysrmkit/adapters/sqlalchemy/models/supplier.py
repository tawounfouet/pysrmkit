"""SQLAlchemy persistence records for the Supplier Aggregate."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase

if TYPE_CHECKING:
    from pysrmkit.adapters.sqlalchemy.models.relationship import SupplierRelationshipRecord


class SupplierRecord(PersistenceBase):
    """Persistence representation of the Supplier Aggregate Root."""

    __tablename__ = "suppliers"

    supplier_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    trading_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    supplier_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)

    external_identifiers: Mapped[list[SupplierExternalIdentifierRecord]] = relationship(
        back_populates="supplier",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    relationships: Mapped[list[SupplierRelationshipRecord]] = relationship(
        back_populates="supplier",
    )


class SupplierExternalIdentifierRecord(PersistenceBase):
    """Owned persistence row for one Supplier external identifier."""

    __tablename__ = "supplier_external_identifiers"
    __table_args__ = (
        UniqueConstraint(
            "kind",
            "value",
            "source_system",
            "jurisdiction",
            name="uq_supplier_external_identifier_identity",
        ),
    )

    identifier_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    supplier_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("suppliers.supplier_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    source_system: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    jurisdiction: Mapped[str] = mapped_column(String(2), nullable=False, default="")

    supplier: Mapped[SupplierRecord] = relationship(back_populates="external_identifiers")
