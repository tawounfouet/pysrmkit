"""Commands for Supplier Qualification application use cases."""

from dataclasses import dataclass

from pysrmkit.domain.qualification.value_objects import (
    QualificationId,
    QualificationScope,
)
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


@dataclass(frozen=True, slots=True)
class RequestSupplierQualification:
    """Intent to request qualification for one Relationship + Scope."""

    relationship_id: SupplierRelationshipId
    scope: QualificationScope


@dataclass(frozen=True, slots=True)
class EvaluateSupplierQualification:
    """Intent to evaluate one pending qualification from collected domain facts."""

    qualification_id: QualificationId
