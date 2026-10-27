"""End-to-end qualification of the 0.3.0a2 in-memory public runtime."""

from pysrmkit import PySRMKit
from pysrmkit.application.assessment.commands import AssessmentQuestionInput
from pysrmkit.application.onboarding.commands import OnboardingRequirementInput
from pysrmkit.domain.qualification.value_objects import (
    CountryCode,
    QualificationScope,
    QualificationStatus,
)


def test_in_memory_runtime_executes_supplier_lifecycle() -> None:
    srm = PySRMKit.in_memory()

    supplier = srm.suppliers.register(
        legal_name="ACME SAS",
        trading_name="ACME",
        country_code="FR",
    )
    relationship = srm.relationships.create(
        supplier_id=supplier.supplier_id,
        organization_id="FR-BU",
    )
    srm.relationships.invite(relationship_id=relationship.relationship_id)
    srm.relationships.start_onboarding(
        relationship_id=relationship.relationship_id,
        requirements=(OnboardingRequirementInput(code="KYC"),),
    )

    # The onboarding identifier is intentionally not guessed by the public layer.
    # Qualification of onboarding-id discovery belongs to the later public views/query surface.


def test_in_memory_runtime_shares_state_across_capability_handlers() -> None:
    srm = PySRMKit.in_memory()
    supplier = srm.suppliers.register(legal_name="Shared State Supplier")
    relationship = srm.relationships.create(
        supplier_id=supplier.supplier_id,
        organization_id="HQ",
    )

    assessment = srm.assessments.create(
        relationship_id=relationship.relationship_id,
        assessment_type="ESG",
        questions=(AssessmentQuestionInput(code="Q1"),),
    )
    srm.assessments.record_answer(
        assessment_id=assessment.assessment_id,
        question_code="Q1",
        score=100,
    )
    completed = srm.assessments.complete(assessment_id=assessment.assessment_id)

    assert completed.score.value == 100


def test_in_memory_runtime_evaluates_qualification_with_shared_repositories() -> None:
    srm = PySRMKit.in_memory()
    supplier = srm.suppliers.register(legal_name="Qualification Supplier")
    relationship = srm.relationships.create(
        supplier_id=supplier.supplier_id,
        organization_id="HQ",
    )
    assessment = srm.assessments.create(
        relationship_id=relationship.relationship_id,
        assessment_type="RISK",
        questions=(AssessmentQuestionInput(code="R1"),),
    )
    srm.assessments.record_answer(
        assessment_id=assessment.assessment_id,
        question_code="R1",
        score=100,
    )
    srm.assessments.complete(assessment_id=assessment.assessment_id)

    requested = srm.qualifications.request(
        relationship_id=relationship.relationship_id,
        scope=QualificationScope(country=CountryCode("FR")),
    )
    evaluated = srm.qualifications.evaluate(qualification_id=requested.qualification_id)

    # No onboarding was completed, proving evaluation sees the same assessment
    # repository while the domain policy still enforces the missing prerequisite.
    assert evaluated.status is QualificationStatus.NOT_QUALIFIED
    assert "ONBOARDING_COMPLETE" in evaluated.decision.failed_requirements
