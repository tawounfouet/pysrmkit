"""SQLAlchemy persistence records for SupplierQualification."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.types import UTCDateTime


class SupplierQualificationRecord(PersistenceBase):
    """Persistence representation of the SupplierQualification Aggregate Root."""

    __tablename__ = "supplier_qualifications"
    __table_args__ = (
        CheckConstraint(
            "scope_organization_id <> '' "
            "OR scope_category_code <> '' "
            "OR scope_country_code <> ''",
            name="ck_supplier_qualification_non_empty_scope",
        ),
        CheckConstraint(
            "("
            "decision_approved IS NULL "
            "AND decision_resulting_status IS NULL "
            "AND decision_decided_at IS NULL"
            ") OR ("
            "decision_approved IS NOT NULL "
            "AND decision_resulting_status IS NOT NULL "
            "AND decision_decided_at IS NOT NULL"
            ")",
            name="ck_supplier_qualification_decision_completeness",
        ),
        Index(
            "uq_current_supplier_qualification_scope",
            "relationship_id",
            "scope_organization_id",
            "scope_category_code",
            "scope_country_code",
            unique=True,
            sqlite_where=text("status NOT IN ('REVOKED', 'EXPIRED')"),
            postgresql_where=text("status NOT IN ('REVOKED', 'EXPIRED')"),
        ),
    )

    qualification_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    relationship_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("supplier_relationships.relationship_id"),
        nullable=False,
        index=True,
    )
    scope_organization_id: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    scope_category_code: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    scope_country_code: Mapped[str] = mapped_column(String(2), nullable=False, default="")
    requested_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    decision_approved: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    decision_resulting_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    decision_decided_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)

    decision_reasons: Mapped[list[QualificationDecisionReasonRecord]] = relationship(
        back_populates="qualification",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="QualificationDecisionReasonRecord.position",
    )
    failed_requirements: Mapped[list[QualificationFailedRequirementRecord]] = relationship(
        back_populates="qualification",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="QualificationFailedRequirementRecord.position",
    )


class QualificationDecisionReasonRecord(PersistenceBase):
    """Owned persistence row for one QualificationDecision reason."""

    __tablename__ = "supplier_qualification_decision_reasons"

    reason_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    qualification_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("supplier_qualifications.qualification_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)

    qualification: Mapped[SupplierQualificationRecord] = relationship(
        back_populates="decision_reasons"
    )


class QualificationFailedRequirementRecord(PersistenceBase):
    """Owned persistence row for one failed qualification requirement."""

    __tablename__ = "supplier_qualification_failed_requirements"

    failed_requirement_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    qualification_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("supplier_qualifications.qualification_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)

    qualification: Mapped[SupplierQualificationRecord] = relationship(
        back_populates="failed_requirements"
    )
