"""Final Cycle 3 InMemory public runtime qualification."""

from pysrmkit.public import (
    PySRMKit,
    QualificationStatus,
    SupplierLifecycleStage,
    SupplierQualificationRejected,
    SupplierQualified,
)
from tests.public_runtime_consumer import run_public_qualification


def test_public_in_memory_success_journey() -> None:
    outcome = run_public_qualification(PySRMKit.in_memory(), assessment_score=90)

    assert outcome.relationship_stage is SupplierLifecycleStage.ONBOARDING
    assert outcome.onboarding_complete is True
    assert outcome.assessment_complete is True
    assert outcome.assessment_score == 90
    assert outcome.qualification_status is QualificationStatus.QUALIFIED
    assert outcome.approved is True
    assert outcome.failed_requirements == ()
    assert outcome.observed_events == (SupplierQualified.__name__,)


def test_public_in_memory_rejection_journey() -> None:
    outcome = run_public_qualification(PySRMKit.in_memory(), assessment_score=60)

    assert outcome.relationship_stage is SupplierLifecycleStage.ONBOARDING
    assert outcome.onboarding_complete is True
    assert outcome.assessment_complete is True
    assert outcome.assessment_score == 60
    assert outcome.qualification_status is QualificationStatus.NOT_QUALIFIED
    assert outcome.approved is False
    assert outcome.failed_requirements == ("ASSESSMENT_MINIMUM_SCORE",)
    assert outcome.observed_events == (SupplierQualificationRejected.__name__,)
