"""SQLAlchemy persistence records for SupplierOnboarding."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.types import UTCDateTime


class SupplierOnboardingRecord(PersistenceBase):
    """Persistence representation of the SupplierOnboarding Aggregate Root."""

    __tablename__ = "supplier_onboardings"
    __table_args__ = (
        UniqueConstraint(
            "relationship_id",
            name="uq_supplier_onboarding_relationship",
        ),
    )

    onboarding_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    relationship_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("supplier_relationships.relationship_id"),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)

    requirements: Mapped[list[OnboardingRequirementRecord]] = relationship(
        back_populates="onboarding",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="OnboardingRequirementRecord.position",
    )


class OnboardingRequirementRecord(PersistenceBase):
    """Owned persistence row for one onboarding requirement."""

    __tablename__ = "supplier_onboarding_requirements"
    __table_args__ = (
        UniqueConstraint(
            "onboarding_id",
            "code",
            name="uq_supplier_onboarding_requirement_code",
        ),
    )

    requirement_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    onboarding_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("supplier_onboardings.onboarding_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False)
    satisfied: Mapped[bool] = mapped_column(Boolean, nullable=False)

    onboarding: Mapped[SupplierOnboardingRecord] = relationship(back_populates="requirements")
