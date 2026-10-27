"""Supplier Qualification Value Object tests."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from pysrmkit.domain.qualification.errors import (
    InvalidQualificationDecision,
    InvalidQualificationScope,
)
from pysrmkit.domain.qualification.value_objects import (
    QualificationDecision,
    QualificationId,
    QualificationScope,
    QualificationStatus,
)
from pysrmkit.domain.relationship.value_objects import InternalOrganizationId
from pysrmkit.domain.supplier.value_objects import CategoryCode, CountryCode

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


def test_qualification_id_has_value_equality_and_stable_string_representation() -> None:
    value = uuid4()

    left = QualificationId(value)
    right = QualificationId(value)

    assert left == right
    assert hash(left) == hash(right)
    assert str(left) == str(value)


def test_qualification_id_new_creates_distinct_identifiers() -> None:
    assert QualificationId.new() != QualificationId.new()


def test_qualification_scope_requires_at_least_one_business_dimension() -> None:
    with pytest.raises(InvalidQualificationScope):
        QualificationScope()


def test_qualification_scope_has_value_equality_across_explicit_dimensions() -> None:
    left = QualificationScope(
        organization_id=InternalOrganizationId("ORG-A"),
        category_code=CategoryCode("IT_SERVICES"),
        country_code=CountryCode("fr"),
    )
    right = QualificationScope(
        organization_id=InternalOrganizationId("ORG-A"),
        category_code=CategoryCode("IT_SERVICES"),
        country_code=CountryCode("FR"),
    )

    assert left == right
    assert hash(left) == hash(right)


def test_each_supported_scope_dimension_is_meaningful_by_itself() -> None:
    assert QualificationScope(organization_id=InternalOrganizationId("ORG-A"))
    assert QualificationScope(category_code=CategoryCode("IT_SERVICES"))
    assert QualificationScope(country_code=CountryCode("FR"))


def test_approved_decision_must_result_in_qualified_without_failures() -> None:
    decision = QualificationDecision(
        approved=True,
        resulting_status=QualificationStatus.QUALIFIED,
        reasons=("  All rules satisfied  ",),
        failed_requirements=(),
        decided_at=NOW,
    )

    assert decision.reasons == ("All rules satisfied",)

    with pytest.raises(InvalidQualificationDecision):
        QualificationDecision(
            approved=True,
            resulting_status=QualificationStatus.NOT_QUALIFIED,
            reasons=("Inconsistent",),
            failed_requirements=(),
            decided_at=NOW,
        )

    with pytest.raises(InvalidQualificationDecision):
        QualificationDecision(
            approved=True,
            resulting_status=QualificationStatus.QUALIFIED,
            reasons=("Inconsistent",),
            failed_requirements=("ASSESSMENT_COMPLETE",),
            decided_at=NOW,
        )


def test_rejected_decision_must_result_in_not_qualified_and_keep_explanation() -> None:
    decision = QualificationDecision(
        approved=False,
        resulting_status=QualificationStatus.NOT_QUALIFIED,
        reasons=("  Assessment score below threshold  ",),
        failed_requirements=("  ASSESSMENT_MINIMUM_SCORE  ",),
        decided_at=NOW,
    )

    assert decision.reasons == ("Assessment score below threshold",)
    assert decision.failed_requirements == ("ASSESSMENT_MINIMUM_SCORE",)

    with pytest.raises(InvalidQualificationDecision):
        QualificationDecision(
            approved=False,
            resulting_status=QualificationStatus.QUALIFIED,
            reasons=("Inconsistent",),
            failed_requirements=("ASSESSMENT_MINIMUM_SCORE",),
            decided_at=NOW,
        )


def test_qualification_decision_requires_a_non_blank_reason() -> None:
    with pytest.raises(InvalidQualificationDecision):
        QualificationDecision(
            approved=False,
            resulting_status=QualificationStatus.NOT_QUALIFIED,
            reasons=("   ",),
            failed_requirements=("ASSESSMENT_COMPLETE",),
            decided_at=NOW,
        )
