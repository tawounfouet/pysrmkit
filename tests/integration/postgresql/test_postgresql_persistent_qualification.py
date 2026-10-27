"""Persistent end-to-end Supplier qualification scenarios on PostgreSQL."""

import os

import pytest

from examples.persistent_qualification import run_persistent_qualification
from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.schema import load_persistence_metadata
from pysrmkit.domain.qualification.value_objects import QualificationStatus
from pysrmkit.domain.relationship.value_objects import SupplierLifecycleStage

pytestmark = pytest.mark.postgresql
DATABASE_URL = os.environ.get("PYSRMKIT_POSTGRESQL_TEST_URL")


def _database_url() -> str:
    if DATABASE_URL is None:
        pytest.skip("PYSRMKIT_POSTGRESQL_TEST_URL is not configured")
    return DATABASE_URL


def _reset_database(database_url: str) -> None:
    engine = create_persistence_engine(database_url)
    metadata = load_persistence_metadata()
    try:
        metadata.drop_all(engine)
        with engine.begin() as connection:
            connection.exec_driver_sql("DROP TABLE IF EXISTS alembic_version")
    finally:
        engine.dispose()


def test_postgresql_persistent_qualification_survives_fresh_context() -> None:
    database_url = _database_url()
    _reset_database(database_url)
    try:
        outcome = run_persistent_qualification(database_url, assessment_score=90)

        assert outcome.supplier_exists is True
        assert outcome.relationship_exists is True
        assert outcome.relationship_stage is SupplierLifecycleStage.ONBOARDING
        assert outcome.onboarding_complete is True
        assert outcome.assessment_complete is True
        assert outcome.assessment_score == 90
        assert outcome.qualification_status is QualificationStatus.QUALIFIED
        assert outcome.qualification_decision.approved is True
        assert outcome.qualification_decision.failed_requirements == ()
        assert outcome.observed_events[-1] == "SupplierQualified"
    finally:
        _reset_database(database_url)


def test_postgresql_persistent_rejection_survives_fresh_context() -> None:
    database_url = _database_url()
    _reset_database(database_url)
    try:
        outcome = run_persistent_qualification(database_url, assessment_score=60)

        assert outcome.supplier_exists is True
        assert outcome.relationship_exists is True
        assert outcome.relationship_stage is SupplierLifecycleStage.ONBOARDING
        assert outcome.onboarding_complete is True
        assert outcome.assessment_complete is True
        assert outcome.assessment_score == 60
        assert outcome.qualification_status is QualificationStatus.NOT_QUALIFIED
        assert outcome.qualification_decision.approved is False
        assert outcome.qualification_decision.failed_requirements == (
            "ASSESSMENT_MINIMUM_SCORE",
        )
        assert outcome.observed_events[-1] == "SupplierQualificationRejected"
    finally:
        _reset_database(database_url)
