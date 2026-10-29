"""Internal query messages used by the public read boundary."""

from dataclasses import dataclass
from typing import Literal

from pysrmkit.domain.assessment.value_objects import AssessmentId
from pysrmkit.domain.qualification.value_objects import QualificationId, QualificationScope
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId
from pysrmkit.domain.supplier.value_objects import CountryCode, SupplierId


@dataclass(frozen=True, slots=True)
class GetSupplier:
    supplier_id: SupplierId


@dataclass(frozen=True, slots=True)
class ListSuppliers:
    offset: int = 0
    limit: int = 100

    def __post_init__(self) -> None:
        if self.offset < 0:
            raise ValueError("offset must be non-negative")
        if self.limit <= 0:
            raise ValueError("limit must be positive")
        if self.limit > 100:
            raise ValueError("limit must not exceed 100")


@dataclass(frozen=True, slots=True)
class SearchSuppliersQuery:
    """Transport-independent, immutable Supplier discovery request.

    Design concepts:
        - Command-Query Separation: reading never mutates Supplier aggregates.
        - DTO: normalized, validated options before delegating to a Query Port.
        - KISS: no HTTP, ORM or backend-specific search objects.
    """

    query: str | None = None
    country_code: str | None = None
    supplier_type: str | None = None
    sort_by: Literal["legal_name"] = "legal_name"
    sort_order: Literal["asc", "desc"] = "asc"
    offset: int = 0
    limit: int = 100

    def __post_init__(self) -> None:
        if self.query is not None:
            if not isinstance(self.query, str):
                raise TypeError("query must be a string or None")
            object.__setattr__(self, "query", self.query.strip() or None)

        if self.country_code is not None:
            if not isinstance(self.country_code, str):
                raise TypeError("country_code must be a string or None")
            object.__setattr__(self, "country_code", CountryCode(self.country_code).value)

        if self.supplier_type is not None:
            if not isinstance(self.supplier_type, str):
                raise TypeError("supplier_type must be a string or None")
            object.__setattr__(self, "supplier_type", self.supplier_type.strip() or None)

        if self.sort_by != "legal_name":
            raise ValueError("sort_by must be 'legal_name'")
        if self.sort_order not in ("asc", "desc"):
            raise ValueError("sort_order must be 'asc' or 'desc'")

        if isinstance(self.offset, bool) or not isinstance(self.offset, int):
            raise TypeError("offset must be an integer")
        if self.offset < 0:
            raise ValueError("offset must be non-negative")
        if isinstance(self.limit, bool) or not isinstance(self.limit, int):
            raise TypeError("limit must be an integer")
        if self.limit <= 0:
            raise ValueError("limit must be positive")
        if self.limit > 100:
            raise ValueError("limit must not exceed 100")


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
