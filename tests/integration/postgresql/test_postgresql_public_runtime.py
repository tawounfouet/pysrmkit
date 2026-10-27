"""Final Cycle 3 PostgreSQL qualification through the public runtime facade."""

import os

import pytest
from sqlalchemy import create_engine

from pysrmkit.adapters.sqlalchemy.schema import load_persistence_metadata
from pysrmkit.public import (
    PySRMKit,
    QualificationStatus,
    SupplierQualificationRejected,
    SupplierQualified,
)
from tests.public_runtime_consumer import run_public_qualification

pytestmark = pytest.mark.postgresql
DATABASE_URL = os.environ.get("PYSRMKIT_POSTGRESQL_TEST_URL")


def _database_url() -> str:
    if DATABASE_URL is None:
        pytest.skip("PYSRMKIT_POSTGRESQL_TEST_URL is not configured")
    return DATABASE_URL


def test_postgresql_public_runtime_success_and_rejection() -> None:
    engine = create_engine(_database_url())
    metadata = load_persistence_metadata()
    metadata.drop_all(engine)
    metadata.create_all(engine)
    runtime = PySRMKit.sql(engine)
    try:
        qualified = run_public_qualification(runtime, assessment_score=90)
        rejected = run_public_qualification(runtime, assessment_score=60)

        assert qualified.qualification_status is QualificationStatus.QUALIFIED
        assert qualified.approved is True
        assert qualified.observed_events == (SupplierQualified.__name__,)

        assert rejected.qualification_status is QualificationStatus.NOT_QUALIFIED
        assert rejected.approved is False
        assert rejected.failed_requirements == ("ASSESSMENT_MINIMUM_SCORE",)
        assert rejected.observed_events == (SupplierQualificationRejected.__name__,)
    finally:
        metadata.drop_all(engine)
        engine.dispose()
