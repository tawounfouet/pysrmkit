"""SQLAlchemy implementation of SupplierRelationshipRepository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.mappers.relationship import (
    apply_relationship_state,
    new_relationship_record,
    relationship_from_record,
)
from pysrmkit.adapters.sqlalchemy.models.relationship import SupplierRelationshipRecord
from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId


class SqlAlchemySupplierRelationshipRepository:
    """Session-scoped SQLAlchemy SupplierRelationship repository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(
        self,
        relationship_id: SupplierRelationshipId,
    ) -> SupplierRelationship | None:
        record = self._session.get(SupplierRelationshipRecord, relationship_id.value)
        if record is None:
            return None
        return relationship_from_record(record)

    def save(self, relationship: SupplierRelationship) -> None:
        record = self._session.get(SupplierRelationshipRecord, relationship.id.value)
        if record is None:
            self._session.add(new_relationship_record(relationship))
            return
        apply_relationship_state(record, relationship)

    def find_for_supplier_and_organization(
        self,
        supplier_id: SupplierId,
        organization_id: InternalOrganizationId,
    ) -> SupplierRelationship | None:
        statement = select(SupplierRelationshipRecord).where(
            SupplierRelationshipRecord.supplier_id == supplier_id.value,
            SupplierRelationshipRecord.organization_id == organization_id.value,
        )
        record = self._session.scalar(statement)
        if record is None:
            return None
        return relationship_from_record(record)
