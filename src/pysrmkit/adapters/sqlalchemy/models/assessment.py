"""SQLAlchemy persistence records for SupplierAssessment."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.types import UTCDateTime


class SupplierAssessmentRecord(PersistenceBase):
    """Persistence representation of the SupplierAssessment Aggregate Root."""

    __tablename__ = "supplier_assessments"

    assessment_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    relationship_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("supplier_relationships.relationship_id"),
        nullable=False,
        index=True,
    )
    assessment_type: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    decision: Mapped[str | None] = mapped_column(String(50), nullable=True)

    questions: Mapped[list[AssessmentQuestionRecord]] = relationship(
        back_populates="assessment",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="AssessmentQuestionRecord.position",
    )
    answers: Mapped[list[AssessmentAnswerRecord]] = relationship(
        back_populates="assessment",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="AssessmentAnswerRecord.position",
    )


class AssessmentQuestionRecord(PersistenceBase):
    """Owned persistence row for one assessment question snapshot."""

    __tablename__ = "supplier_assessment_questions"
    __table_args__ = (
        UniqueConstraint(
            "assessment_id",
            "code",
            name="uq_supplier_assessment_question_code",
        ),
    )

    question_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("supplier_assessments.assessment_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False)
    maximum_score: Mapped[int] = mapped_column(Integer, nullable=False)

    assessment: Mapped[SupplierAssessmentRecord] = relationship(back_populates="questions")


class AssessmentAnswerRecord(PersistenceBase):
    """Owned persistence row for one assessment answer."""

    __tablename__ = "supplier_assessment_answers"
    __table_args__ = (
        UniqueConstraint(
            "assessment_id",
            "question_id",
            name="uq_supplier_assessment_answer_question",
        ),
    )

    answer_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    assessment_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("supplier_assessments.assessment_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("supplier_assessment_questions.question_id", ondelete="CASCADE"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)

    assessment: Mapped[SupplierAssessmentRecord] = relationship(back_populates="answers")
    question: Mapped[AssessmentQuestionRecord] = relationship(lazy="joined")
