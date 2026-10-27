"""SQLAlchemy persistence records for PySRMKit Aggregates."""

from pysrmkit.adapters.sqlalchemy.models.relationship import SupplierRelationshipRecord
from pysrmkit.adapters.sqlalchemy.models.supplier import (
    SupplierExternalIdentifierRecord,
    SupplierRecord,
)

__all__ = [
    "SupplierExternalIdentifierRecord",
    "SupplierRecord",
    "SupplierRelationshipRecord",
]
