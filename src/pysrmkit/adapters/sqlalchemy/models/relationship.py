"""SQLAlchemy persistence record for SupplierRelationship."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase

if TYPE_CHECKING:
    from pysrmkit.adapters.sqlalchemy.models.supplier import SupplierRecord


class SupplierRelationshipRecord(PersistenceBase):
    """Persistence representation of the SupplierRelationship Aggregate Root."""

    __tablename__ = "supplier_relationships"
    __table_args__ = (
        UniqueConstraint(
            "supplier_id",
            "organization_id",
            name="uq_supplier_relationship_supplier_organization",
        ),
    )

    relationship_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    supplier_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("suppliers.supplier_id"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[str] = mapped_column(String(255), nullable=False)
    stage: Mapped[str] = mapped_column(String(50), nullable=False)

    supplier: Mapped[SupplierRecord] = relationship(back_populates="relationships")
