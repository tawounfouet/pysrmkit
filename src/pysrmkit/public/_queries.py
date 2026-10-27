"""Internal query messages used by the public read boundary."""

from dataclasses import dataclass

from pysrmkit.domain.assessment.value_objects import AssessmentId
from pysrmkit.domain.qualification.value_objects import QualificationId, QualificationScope
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId
from pysrmkit.domain.supplier.value_objects import SupplierId


@dataclass(frozen=True, slots=True)
class GetSupplier:
    supplier_id: SupplierId


@dataclass(frozen=True, slots=True)
class GetSupplierRelationship:
    relationship_id: SupplierRelationshipId


@dataclass(frozen=True, slots=True)
class GetOnboardingForRelationship:
    relationship_id: SupplierRelationshipId


@dataclass(frozen=True, slots=True)
class GetAssessment:
    assessment_id: AssessmentId


@dataclass(frozen=True, slots=True)
class GetQualification:
    qualification_id: QualificationId


@dataclass(frozen=True, slots=True)
class GetCurrentQualificationForScope:
    relationship_id: SupplierRelationshipId
    scope: QualificationScope
