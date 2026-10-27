"""Repository contract for the SupplierQualification Aggregate Root."""

from __future__ import annotations

from typing import Protocol

from pysrmkit.domain.qualification.entities import SupplierQualification
from pysrmkit.domain.qualification.value_objects import QualificationId, QualificationScope
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


class SupplierQualificationRepository(Protocol):
    """Persistence abstraction required by Supplier Qualification use cases."""

    def get(self, qualification_id: QualificationId) -> SupplierQualification | None: ...

    def save(self, qualification: SupplierQualification) -> None: ...

    def find_current_for_scope(
        self,
        relationship_id: SupplierRelationshipId,
        scope: QualificationScope,
    ) -> SupplierQualification | None: ...
