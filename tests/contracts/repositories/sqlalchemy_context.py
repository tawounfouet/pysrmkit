"""Shared SQLAlchemy contract setup for Relationship-scoped Aggregates."""

from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.repositories.relationship import (
    SqlAlchemySupplierRelationshipRepository,
)
from pysrmkit.adapters.sqlalchemy.repositories.supplier import SqlAlchemySupplierRepository
from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import SupplierId, SupplierIdentity


def prepare_relationship_context(
    session: Session,
    relationship_id: SupplierRelationshipId,
    *,
    label: str,
) -> None:
    """Create the external Supplier/Relationship precondition if it is absent."""

    relationships = SqlAlchemySupplierRelationshipRepository(session)
    if relationships.get(relationship_id) is not None:
        return

    suppliers = SqlAlchemySupplierRepository(session)
    supplier = Supplier.reconstitute(
        supplier_id=SupplierId.new(),
        identity=SupplierIdentity(legal_name=f"{label} Supplier {relationship_id}"),
    )
    suppliers.save(supplier)
    relationships.save(
        SupplierRelationship.reconstitute(
            relationship_id=relationship_id,
            supplier_id=supplier.id,
            organization_id=InternalOrganizationId(f"{label}-ORG"),
        )
    )
