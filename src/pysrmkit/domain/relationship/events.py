"""Domain Events emitted by the SupplierRelationship Aggregate."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId


@dataclass(frozen=True, slots=True)
class SupplierRelationshipCreated:
    """Fact emitted after a Supplier relationship is created successfully."""

    event_id: UUID
    relationship_id: SupplierRelationshipId
    supplier_id: SupplierId
    organization_id: InternalOrganizationId
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class SupplierInvited:
    """Fact emitted after a SupplierRelationship is invited successfully."""

    event_id: UUID
    relationship_id: SupplierRelationshipId
    supplier_id: SupplierId
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class SupplierOnboardingStarted:
    """Fact emitted after onboarding starts for a SupplierRelationship."""

    event_id: UUID
    relationship_id: SupplierRelationshipId
    occurred_at: datetime
