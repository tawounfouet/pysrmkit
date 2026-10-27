"""SupplierQualification Domain ↔ SQLAlchemy mapper tests."""

from datetime import UTC, datetime

from pysrmkit.adapters.sqlalchemy.mappers.qualification import (
    new_qualification_record,
    qualification_from_record,
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

REQUESTED_AT = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
DECIDED_AT = datetime(2026, 10, 27, 13, 0, tzinfo=UTC)


def test_qualification_mapper_preserves_scope_status_and_explainable_decision() -> None:
    decision = QualificationDecision(
        approved=False,
        resulting_status=QualificationStatus.NOT_QUALIFIED,
        reasons=(
            "Assessment score below policy threshold",
            "Required evidence is incomplete",
        ),
        failed_requirements=(
            "ASSESSMENT_MINIMUM_SCORE",
            "REQUIRED_ANSWERS_COMPLETE",
        ),
        decided_at=DECIDED_AT,
    )
    qualification = SupplierQualification.reconstitute(
        qualification_id=QualificationId.new(),
        relationship_id=SupplierRelationshipId.new(),
        scope=QualificationScope(
            organization_id=InternalOrganizationId("ORG-PARIS"),
            category_code=CategoryCode("IT_SERVICES"),
            country_code=CountryCode("FR"),
        ),
        requested_at=REQUESTED_AT,
        status=QualificationStatus.NOT_QUALIFIED,
        decision=decision,
    )

    record = new_qualification_record(qualification)
    restored = qualification_from_record(record)

    assert restored == qualification
    assert restored.relationship_id == qualification.relationship_id
    assert restored.scope == qualification.scope
    assert restored.status is QualificationStatus.NOT_QUALIFIED
    assert restored.decision == decision
    assert restored.pull_events() == ()


def test_qualification_mapper_preserves_absent_optional_scope_dimensions() -> None:
    qualification = SupplierQualification.reconstitute(
        qualification_id=QualificationId.new(),
        relationship_id=SupplierRelationshipId.new(),
        scope=QualificationScope(category_code=CategoryCode("FACILITIES")),
        requested_at=REQUESTED_AT,
        status=QualificationStatus.PENDING,
    )

    restored = qualification_from_record(new_qualification_record(qualification))

    assert restored.scope.organization_id is None
    assert restored.scope.category_code == CategoryCode("FACILITIES")
    assert restored.scope.country_code is None
    assert restored.decision is None
