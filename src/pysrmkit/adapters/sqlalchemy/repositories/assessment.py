"""SQLAlchemy implementation of SupplierAssessmentRepository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.mappers.assessment import (
    apply_assessment_state,
    assessment_from_record,
    new_assessment_record,
)
from pysrmkit.adapters.sqlalchemy.models.assessment import SupplierAssessmentRecord
from pysrmkit.domain.assessment.entities import SupplierAssessment
from pysrmkit.domain.assessment.value_objects import AssessmentId
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


class SqlAlchemySupplierAssessmentRepository:
    """Session-scoped SQLAlchemy SupplierAssessment repository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, assessment_id: AssessmentId) -> SupplierAssessment | None:
        record = self._session.get(SupplierAssessmentRecord, assessment_id.value)
        if record is None:
            return None
        return assessment_from_record(record)

    def save(self, assessment: SupplierAssessment) -> None:
        record = self._session.get(SupplierAssessmentRecord, assessment.id.value)
        if record is None:
            self._session.add(new_assessment_record(assessment))
            return
        apply_assessment_state(record, assessment)

    def find_latest_for_relationship(
        self,
        relationship_id: SupplierRelationshipId,
    ) -> SupplierAssessment | None:
        statement = (
            select(SupplierAssessmentRecord)
            .where(SupplierAssessmentRecord.relationship_id == relationship_id.value)
            .order_by(SupplierAssessmentRecord.created_at.desc())
            .limit(1)
        )
        record = self._session.scalar(statement)
        if record is None:
            return None
        return assessment_from_record(record)
