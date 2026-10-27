"""Domain Events emitted by the Supplier Aggregate."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pysrmkit.domain.supplier.value_objects import SupplierId


@dataclass(frozen=True, slots=True)
class SupplierCreated:
    """Fact emitted after a canonical Supplier is created successfully."""

    event_id: UUID
    supplier_id: SupplierId
    occurred_at: datetime
