"""Application results for Supplier Qualification use cases."""

from dataclasses import dataclass

from pysrmkit.domain.qualification.value_objects import (
    QualificationDecision,
    QualificationId,
    QualificationStatus,
)


@dataclass(frozen=True, slots=True)
class RequestSupplierQualificationResult:
    """Result returned after creating a pending SupplierQualification."""

    qualification_id: QualificationId


@dataclass(frozen=True, slots=True)
class EvaluateSupplierQualificationResult:
    """Result returned after policy evaluation and Aggregate decision application."""

    qualification_id: QualificationId
    status: QualificationStatus
    decision: QualificationDecision
