"""Qualification tests for public views and stable error semantics."""

from dataclasses import FrozenInstanceError

import pytest

from pysrmkit import PySRMKit
from pysrmkit.domain.supplier.value_objects import CountryCode
from pysrmkit.public import (
    AssessmentQuestionInput,
    OnboardingRequirementInput,
    QualificationScope,
    SupplierId,
    SupplierNotFound,
)


def test_public_views_expose_complete_qualified_supplier_state() -> None:
    srm = PySRMKit.in_memory()

    supplier_result = srm.suppliers.register(
        legal_name="ACME SAS",
        trading_name="ACME",
        country_code="FR",
    )
    supplier = srm.suppliers.get(supplier_id=supplier_result.supplier_id)
    assert supplier.legal_name == "ACME SAS"
    assert supplier.country == CountryCode("FR")

    relationship_result = srm.relationships.create(
        supplier_id=supplier_result.supplier_id,
        organization_id="HQ",
    )
    srm.relationships.invite(relationship_id=relationship_result.relationship_id)
    srm.relationships.start_onboarding(
        relationship_id=relationship_result.relationship_id,
        requirements=(OnboardingRequirementInput(code="KYC"),),
    )

    relationship = srm.relationships.get(
        relationship_id=relationship_result.relationship_id
    )
    assert relationship.stage.value == "ONBOARDING"

    onboarding = srm.onboardings.get_for_relationship(
        relationship_id=relationship_result.relationship_id
    )
    srm.onboardings.satisfy_requirement(
        onboarding_id=onboarding.onboarding_id,
        requirement_code="KYC",
    )
    srm.onboardings.complete(onboarding_id=onboarding.onboarding_id)
    onboarding = srm.onboardings.get_for_relationship(
        relationship_id=relationship_result.relationship_id
    )
    assert onboarding.completed is True
    assert onboarding.ready_for_completion is True

    assessment_result = srm.assessments.create(
        relationship_id=relationship_result.relationship_id,
        assessment_type="RISK",
        questions=(AssessmentQuestionInput(code="Q1"),),
    )
    srm.assessments.record_answer(
        assessment_id=assessment_result.assessment_id,
        question_code="Q1",
        score=90,
    )
    srm.assessments.complete(assessment_id=assessment_result.assessment_id)
    assessment = srm.assessments.get(assessment_id=assessment_result.assessment_id)
    assert assessment.completed is True
    assert assessment.score is not None
    assert assessment.score.value == 90

    scope = QualificationScope(country_code=CountryCode("FR"))
    qualification_result = srm.qualifications.request(
        relationship_id=relationship_result.relationship_id,
        scope=scope,
    )
    srm.qualifications.evaluate(
        qualification_id=qualification_result.qualification_id
    )
    qualification = srm.qualifications.get(
        qualification_id=qualification_result.qualification_id
    )

    assert qualification.status.value == "QUALIFIED"
    assert qualification.approved is True
    assert qualification.failed_requirements == ()
    assert srm.qualifications.get_current_for_scope(
        relationship_id=relationship_result.relationship_id,
        scope=scope,
    ) == qualification


def test_public_views_are_immutable() -> None:
    srm = PySRMKit.in_memory()
    result = srm.suppliers.register(legal_name="Immutable Supplier")
    view = srm.suppliers.get(supplier_id=result.supplier_id)

    with pytest.raises(FrozenInstanceError):
        view.legal_name = "Changed"  # type: ignore[misc]


def test_public_get_uses_typed_not_found_semantics() -> None:
    srm = PySRMKit.in_memory()

    with pytest.raises(SupplierNotFound):
        srm.suppliers.get(supplier_id=SupplierId.new())
