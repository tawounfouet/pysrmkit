"""Application results for Supplier use cases."""

from dataclasses import dataclass

from pysrmkit.domain.supplier.value_objects import SupplierId


@dataclass(frozen=True, slots=True)
class RegisterSupplierResult:
    """Result returned after a Supplier has been registered successfully."""

    supplier_id: SupplierId
