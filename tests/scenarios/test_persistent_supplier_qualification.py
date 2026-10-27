"""Persistent end-to-end Supplier qualification scenarios on SQLite."""

from pathlib import Path

from examples.persistent_qualification import run_persistent_qualification

from pysrmkit.domain.qualification.value_objects import QualificationStatus
from pysrmkit.domain.relationship.value_objects import SupplierLifecycleStage


def test_persistent_sqlite_qualification_survives_fresh_context(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'qualified.db'}"

    outcome = run_persistent_qualification(database_url, assessment_score=90)

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


def test_persistent_sqlite_rejection_survives_fresh_context(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'rejected.db'}"

    outcome = run_persistent_qualification(database_url, assessment_score=60)

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
