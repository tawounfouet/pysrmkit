"""SQLAlchemy persistence metadata foundation tests."""

from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.models import (
    SupplierExternalIdentifierRecord,
    SupplierRecord,
    SupplierRelationshipRecord,
)


def test_persistence_metadata_contains_only_implemented_tables() -> None:
    assert set(PersistenceBase.metadata.tables) == {
        "suppliers",
        "supplier_external_identifiers",
        "supplier_relationships",
    }

    assert SupplierRecord.__table__ is PersistenceBase.metadata.tables["suppliers"]
    assert (
        SupplierExternalIdentifierRecord.__table__
        is PersistenceBase.metadata.tables["supplier_external_identifiers"]
    )
    assert (
        SupplierRelationshipRecord.__table__
        is PersistenceBase.metadata.tables["supplier_relationships"]
    )
