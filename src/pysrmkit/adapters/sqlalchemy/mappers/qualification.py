"""Explicit mapping between SupplierQualification Domain state and persistence records."""

from pysrmkit.adapters.sqlalchemy.models.qualification import (
    QualificationDecisionReasonRecord,
    QualificationFailedRequirementRecord,
    SupplierQualificationRecord,
)
from pysrmkit.domain.qualification.entities import SupplierQualification
from pysrmkit.domain.qualification.value_objects import (
    QualificationDecision,
    QualificationId,
    QualificationScope,
    QualificationStatus,
)
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import CategoryCode, CountryCode


def _scope_values(scope: QualificationScope) -> tuple[str, str, str]:
    return (
        scope.organization_id.value if scope.organization_id is not None else "",
        scope.category_code.value if scope.category_code is not None else "",
        scope.country_code.value if scope.country_code is not None else "",
    )


def _decision_reason_records(
    decision: QualificationDecision | None,
) -> list[QualificationDecisionReasonRecord]:
    if decision is None:
        return []
    return [
        QualificationDecisionReasonRecord(position=position, value=reason)
        for position, reason in enumerate(decision.reasons)
    ]


def _failed_requirement_records(
    decision: QualificationDecision | None,
) -> list[QualificationFailedRequirementRecord]:
    if decision is None:
        return []
    return [
        QualificationFailedRequirementRecord(position=position, value=requirement)
        for position, requirement in enumerate(decision.failed_requirements)
    ]


def new_qualification_record(
    qualification: SupplierQualification,
) -> SupplierQualificationRecord:
    """Create a new persistence record from current Qualification state."""

    organization_id, category_code, country_code = _scope_values(qualification.scope)
    decision = qualification.decision
    return SupplierQualificationRecord(
        qualification_id=qualification.id.value,
        relationship_id=qualification.relationship_id.value,
        scope_organization_id=organization_id,
        scope_category_code=category_code,
        scope_country_code=country_code,
        requested_at=qualification.requested_at,
        status=qualification.status.value,
        decision_approved=decision.approved if decision is not None else None,
        decision_resulting_status=(
            decision.resulting_status.value if decision is not None else None
        ),
        decision_decided_at=decision.decided_at if decision is not None else None,
        decision_reasons=_decision_reason_records(decision),
        failed_requirements=_failed_requirement_records(decision),
    )


def apply_qualification_state(
    record: SupplierQualificationRecord,
    qualification: SupplierQualification,
) -> None:
    """Synchronize an existing persistence record from a Qualification Aggregate."""

    organization_id, category_code, country_code = _scope_values(qualification.scope)
    decision = qualification.decision
    record.relationship_id = qualification.relationship_id.value
    record.scope_organization_id = organization_id
    record.scope_category_code = category_code
    record.scope_country_code = country_code
    record.requested_at = qualification.requested_at
    record.status = qualification.status.value
    record.decision_approved = decision.approved if decision is not None else None
    record.decision_resulting_status = (
        decision.resulting_status.value if decision is not None else None
    )
    record.decision_decided_at = decision.decided_at if decision is not None else None
    record.decision_reasons = _decision_reason_records(decision)
    record.failed_requirements = _failed_requirement_records(decision)


def _scope_from_record(record: SupplierQualificationRecord) -> QualificationScope:
    return QualificationScope(
        organization_id=(
            InternalOrganizationId(record.scope_organization_id)
            if record.scope_organization_id
            else None
        ),
        category_code=(
            CategoryCode(record.scope_category_code) if record.scope_category_code else None
        ),
        country_code=(
            CountryCode(record.scope_country_code) if record.scope_country_code else None
        ),
    )


def _decision_from_record(
    record: SupplierQualificationRecord,
) -> QualificationDecision | None:
    if record.decision_approved is None:
        return None

    if record.decision_resulting_status is None or record.decision_decided_at is None:
        raise ValueError("Persisted QualificationDecision is incomplete")

    return QualificationDecision(
        approved=record.decision_approved,
        resulting_status=QualificationStatus(record.decision_resulting_status),
        reasons=tuple(item.value for item in record.decision_reasons),
        failed_requirements=tuple(item.value for item in record.failed_requirements),
        decided_at=record.decision_decided_at,
    )


def qualification_from_record(
    record: SupplierQualificationRecord,
) -> SupplierQualification:
    """Reconstitute a persistence-ignorant SupplierQualification Aggregate."""

    return SupplierQualification.reconstitute(
        qualification_id=QualificationId(record.qualification_id),
        relationship_id=SupplierRelationshipId(record.relationship_id),
        scope=_scope_from_record(record),
        requested_at=record.requested_at,
        status=QualificationStatus(record.status),
        decision=_decision_from_record(record),
    )
