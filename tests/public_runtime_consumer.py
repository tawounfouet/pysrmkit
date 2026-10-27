"""Consumer-style qualification helpers using only PySRMKit public business imports."""

from dataclasses import dataclass

from pysrmkit.public import (
    AssessmentQuestionInput,
    InternalOrganizationId,
    OnboardingRequirementInput,
    PySRMKit,
    QualificationId,
    QualificationScope,
    QualificationStatus,
    SupplierId,
    SupplierLifecycleStage,
    SupplierQualificationRejected,
    SupplierQualified,
    SupplierRelationshipId,
)


@dataclass(frozen=True, slots=True)
class PublicJourneyOutcome:
    supplier_id: SupplierId
    relationship_id: SupplierRelationshipId
    qualification_id: QualificationId
    relationship_stage: SupplierLifecycleStage
    onboarding_complete: bool
    assessment_complete: bool
    assessment_score: int
    qualification_status: QualificationStatus
    approved: bool
    failed_requirements: tuple[str, ...]
    observed_events: tuple[str, ...]


def run_public_qualification(
    srm: PySRMKit,
    *,
    assessment_score: int,
) -> PublicJourneyOutcome:
    """Execute the complete Supplier qualification journey through the public facade."""
    observed: list[str] = []
    srm.events.subscribe(SupplierQualified, lambda event: observed.append(type(event).__name__))
    srm.events.subscribe(
        SupplierQualificationRejected,
        lambda event: observed.append(type(event).__name__),
    )

    supplier = srm.suppliers.register(
        legal_name=f"Public Supplier {assessment_score}",
        country_code="FR",
    )
    relationship = srm.relationships.create(
        supplier_id=supplier.supplier_id,
        organization_id=f"ORG-{assessment_score}",
    )
    srm.relationships.invite(relationship_id=relationship.relationship_id)
    srm.relationships.start_onboarding(
        relationship_id=relationship.relationship_id,
        requirements=(OnboardingRequirementInput(code="KYC"),),
    )
    onboarding = srm.onboardings.get_for_relationship(relationship_id=relationship.relationship_id)
    srm.onboardings.satisfy_requirement(
        onboarding_id=onboarding.onboarding_id,
        requirement_code="KYC",
    )
    srm.onboardings.complete(onboarding_id=onboarding.onboarding_id)

    assessment = srm.assessments.create(
        relationship_id=relationship.relationship_id,
        assessment_type="RISK",
        questions=(AssessmentQuestionInput(code="RISK_SCORE"),),
    )
    srm.assessments.record_answer(
        assessment_id=assessment.assessment_id,
        question_code="RISK_SCORE",
        score=assessment_score,
    )
    srm.assessments.complete(assessment_id=assessment.assessment_id)

    scope = QualificationScope(organization_id=InternalOrganizationId(f"ORG-{assessment_score}"))
    requested = srm.qualifications.request(
        relationship_id=relationship.relationship_id,
        scope=scope,
    )
    srm.qualifications.evaluate(qualification_id=requested.qualification_id)

    relationship_view = srm.relationships.get(relationship_id=relationship.relationship_id)
    onboarding_view = srm.onboardings.get_for_relationship(
        relationship_id=relationship.relationship_id
    )
    assessment_view = srm.assessments.get(assessment_id=assessment.assessment_id)
    qualification_view = srm.qualifications.get(qualification_id=requested.qualification_id)

    assert assessment_view.score is not None
    assert qualification_view.approved is not None

    return PublicJourneyOutcome(
        supplier_id=supplier.supplier_id,
        relationship_id=relationship.relationship_id,
        qualification_id=requested.qualification_id,
        relationship_stage=relationship_view.stage,
        onboarding_complete=onboarding_view.completed,
        assessment_complete=assessment_view.completed,
        assessment_score=assessment_view.score.value,
        qualification_status=qualification_view.status,
        approved=qualification_view.approved,
        failed_requirements=qualification_view.failed_requirements,
        observed_events=tuple(observed),
    )
