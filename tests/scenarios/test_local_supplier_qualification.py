"""End-to-end local Core Supplier qualification scenarios."""

import pytest

from examples.local_qualification import main, run_local_qualification

from pysrmkit.domain.qualification.value_objects import QualificationStatus
from pysrmkit.domain.relationship.value_objects import SupplierLifecycleStage


def test_local_supplier_qualification_success() -> None:
    outcome = run_local_qualification(assessment_score=90)

    assert outcome.supplier_exists is True
    assert outcome.relationship_exists is True
    assert outcome.relationship_stage is SupplierLifecycleStage.ONBOARDING
    assert outcome.onboarding_complete is True
    assert outcome.assessment_complete is True
    assert outcome.assessment_score == 90
    assert outcome.qualification_scope.organization_id is not None
    assert outcome.qualification_scope.organization_id.value == "ORG-PARIS"
    assert outcome.qualification_status is QualificationStatus.QUALIFIED
    assert outcome.qualification_decision.approved is True
    assert outcome.qualification_decision.failed_requirements == ()
    assert outcome.observed_events == (
        "SupplierCreated",
        "SupplierRelationshipCreated",
        "SupplierInvited",
        "SupplierOnboardingStarted",
        "SupplierOnboardingCompleted",
        "SupplierAssessmentCompleted",
        "SupplierQualificationRequested",
        "SupplierQualified",
    )


def test_local_supplier_qualification_rejection() -> None:
    outcome = run_local_qualification(assessment_score=60)

    assert outcome.supplier_exists is True
    assert outcome.relationship_exists is True
    assert outcome.relationship_stage is SupplierLifecycleStage.ONBOARDING
    assert outcome.onboarding_complete is True
    assert outcome.assessment_complete is True
    assert outcome.assessment_score == 60
    assert outcome.qualification_status is QualificationStatus.NOT_QUALIFIED
    assert outcome.qualification_decision.approved is False
    assert outcome.qualification_decision.failed_requirements == ("ASSESSMENT_MINIMUM_SCORE",)
    assert outcome.observed_events[-1] == "SupplierQualificationRejected"
    assert "SupplierQualified" not in outcome.observed_events

def test_local_example_entrypoint_prints_success_trace(
    capsys: pytest.CaptureFixture[str],
) -> None:
    main()

    output = capsys.readouterr().out
    assert "[EVENT] SupplierCreated" in output
    assert "[EVENT] SupplierQualified" in output
    assert "[RESULT] Qualification status: QUALIFIED" in output
