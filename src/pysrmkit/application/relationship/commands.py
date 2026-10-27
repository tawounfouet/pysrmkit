"""Commands for Supplier Relationship application use cases."""

from dataclasses import dataclass

from pysrmkit.application.onboarding.commands import OnboardingRequirementInput
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId


@dataclass(frozen=True, slots=True)
class CreateSupplierRelationship:
    """Intent to create a relationship between a Supplier and an internal organization."""

    supplier_id: SupplierId
    organization_id: InternalOrganizationId


@dataclass(frozen=True, slots=True)
class InviteSupplierRelationship:
    """Intent to invite an existing SupplierRelationship."""

    relationship_id: SupplierRelationshipId


@dataclass(frozen=True, slots=True)
class StartSupplierOnboarding:
    """Intent to move a Relationship into onboarding and create its onboarding state."""

    relationship_id: SupplierRelationshipId
    requirements: tuple[OnboardingRequirementInput, ...] = ()
