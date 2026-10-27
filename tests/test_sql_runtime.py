"""End-to-end qualification of the 0.3.0a3 SQL public runtime."""

from sqlalchemy import create_engine

from pysrmkit import PySRMKit
from pysrmkit.adapters.sqlalchemy.schema import load_persistence_metadata
from pysrmkit.application.assessment.commands import AssessmentQuestionInput
from pysrmkit.domain.qualification.value_objects import (
    CountryCode,
    QualificationScope,
    QualificationStatus,
)


def _runtime() -> PySRMKit:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    load_persistence_metadata().create_all(engine)
    return PySRMKit.sql(engine)


def test_sql_runtime_persists_state_across_public_operations() -> None:
    srm = _runtime()

    supplier = srm.suppliers.register(
        legal_name="SQL Supplier",
        country_code="FR",
    )
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
    completed = srm.assessments.complete(assessment_id=assessment.assessment_id)

    assert completed.score.value == 100


def test_sql_runtime_evaluates_using_committed_state_from_prior_operations() -> None:
    srm = _runtime()

    supplier = srm.suppliers.register(legal_name="Qualified SQL Supplier")
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
        scope=QualificationScope(country_code=CountryCode("FR")),
    )
    evaluated = srm.qualifications.evaluate(qualification_id=requested.qualification_id)

    assert evaluated.status is QualificationStatus.NOT_QUALIFIED
    assert "ONBOARDING_COMPLETE" in evaluated.decision.failed_requirements


def test_sql_runtime_rolls_back_failed_public_operation() -> None:
    srm = _runtime()
    supplier = srm.suppliers.register(legal_name="Rollback Supplier")

    relationship = srm.relationships.create(
        supplier_id=supplier.supplier_id,
        organization_id="HQ",
    )

    try:
        srm.relationships.create(
            supplier_id=supplier.supplier_id,
            organization_id="HQ",
        )
    except Exception:
        pass
    else:
        raise AssertionError("duplicate relationship should fail")

    assessment = srm.assessments.create(
        relationship_id=relationship.relationship_id,
        assessment_type="RISK",
        questions=(),
    )
    assert assessment.assessment_id is not None
