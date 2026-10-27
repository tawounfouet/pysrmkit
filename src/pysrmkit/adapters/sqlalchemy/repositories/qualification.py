"""SQLAlchemy implementation of SupplierQualificationRepository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.mappers.qualification import (
    apply_qualification_state,
    new_qualification_record,
    qualification_from_record,
)
from pysrmkit.adapters.sqlalchemy.models.qualification import SupplierQualificationRecord
from pysrmkit.domain.qualification.entities import SupplierQualification
from pysrmkit.domain.qualification.value_objects import (
    QualificationId,
    QualificationScope,
    QualificationStatus,
)
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


def _scope_values(scope: QualificationScope) -> tuple[str, str, str]:
    return (
        scope.organization_id.value if scope.organization_id is not None else "",
        scope.category_code.value if scope.category_code is not None else "",
        scope.country_code.value if scope.country_code is not None else "",
    )


class SqlAlchemySupplierQualificationRepository:
    """Session-scoped SQLAlchemy SupplierQualification repository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, qualification_id: QualificationId) -> SupplierQualification | None:
        record = self._session.get(SupplierQualificationRecord, qualification_id.value)
        if record is None:
            return None
        return qualification_from_record(record)

    def save(self, qualification: SupplierQualification) -> None:
        record = self._session.get(SupplierQualificationRecord, qualification.id.value)
        if record is None:
            self._session.add(new_qualification_record(qualification))
            return
        apply_qualification_state(record, qualification)

    def find_current_for_scope(
        self,
        relationship_id: SupplierRelationshipId,
        scope: QualificationScope,
    ) -> SupplierQualification | None:
        organization_id, category_code, country_code = _scope_values(scope)
        statement = select(SupplierQualificationRecord).where(
            SupplierQualificationRecord.relationship_id == relationship_id.value,
            SupplierQualificationRecord.scope_organization_id == organization_id,
            SupplierQualificationRecord.scope_category_code == category_code,
            SupplierQualificationRecord.scope_country_code == country_code,
            SupplierQualificationRecord.status.not_in(
                (
                    QualificationStatus.REVOKED.value,
                    QualificationStatus.EXPIRED.value,
                )
            ),
        )
        record = self._session.scalar(statement)
        if record is None:
            return None
        return qualification_from_record(record)
