"""SQLAlchemy persistence metadata foundation tests."""

from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.models import (
    AssessmentAnswerRecord,
    AssessmentQuestionRecord,
    OnboardingRequirementRecord,
    QualificationDecisionReasonRecord,
    QualificationFailedRequirementRecord,
    SupplierAssessmentRecord,
    SupplierExternalIdentifierRecord,
    SupplierOnboardingRecord,
    SupplierQualificationRecord,
    SupplierRecord,
    SupplierRelationshipRecord,
)


def test_persistence_metadata_contains_only_implemented_tables() -> None:
    assert set(PersistenceBase.metadata.tables) == {
        "suppliers",
        "supplier_external_identifiers",
        "supplier_relationships",
        "supplier_onboardings",
        "supplier_onboarding_requirements",
        "supplier_assessments",
        "supplier_assessment_questions",
        "supplier_assessment_answers",
        "supplier_qualifications",
        "supplier_qualification_decision_reasons",
        "supplier_qualification_failed_requirements",
    }

    assert SupplierRecord.__table__ is PersistenceBase.metadata.tables["suppliers"]
    assert (
        SupplierExternalIdentifierRecord.__table__
        is PersistenceBase.metadata.tables["supplier_external_identifiers"]
    )
    assert (
        SupplierRelationshipRecord.__table__
        is PersistenceBase.metadata.tables["supplier_relationships"]
    )

    assert (
        SupplierOnboardingRecord.__table__
        is PersistenceBase.metadata.tables["supplier_onboardings"]
    )
    assert (
        OnboardingRequirementRecord.__table__
        is PersistenceBase.metadata.tables["supplier_onboarding_requirements"]
    )
    assert (
        SupplierAssessmentRecord.__table__
        is PersistenceBase.metadata.tables["supplier_assessments"]
    )
    assert (
        AssessmentQuestionRecord.__table__
        is PersistenceBase.metadata.tables["supplier_assessment_questions"]
    )
    assert (
        AssessmentAnswerRecord.__table__
        is PersistenceBase.metadata.tables["supplier_assessment_answers"]
    )

    assert (
        SupplierQualificationRecord.__table__
        is PersistenceBase.metadata.tables["supplier_qualifications"]
    )
    assert (
        QualificationDecisionReasonRecord.__table__
        is PersistenceBase.metadata.tables["supplier_qualification_decision_reasons"]
    )
    assert (
        QualificationFailedRequirementRecord.__table__
        is PersistenceBase.metadata.tables["supplier_qualification_failed_requirements"]
    )
