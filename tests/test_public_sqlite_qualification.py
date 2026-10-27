"""Final Cycle 3 SQLite public runtime qualification and restart proof."""

from pathlib import Path

from sqlalchemy import create_engine

from pysrmkit.adapters.sqlalchemy.schema import load_persistence_metadata
from pysrmkit.public import (
    PySRMKit,
    QualificationStatus,
    SupplierQualificationRejected,
    SupplierQualified,
)
from tests.public_runtime_consumer import run_public_qualification


def _engine(database_url: str):
    engine = create_engine(database_url)
    load_persistence_metadata().create_all(engine)
    return engine


def test_public_sqlite_success_rejection_and_runtime_restart(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'public-runtime.db'}"
    engine_a = _engine(database_url)
    runtime_a = PySRMKit.sql(engine_a)

    qualified = run_public_qualification(runtime_a, assessment_score=90)
    rejected = run_public_qualification(runtime_a, assessment_score=60)

    assert qualified.qualification_status is QualificationStatus.QUALIFIED
    assert qualified.observed_events == (SupplierQualified.__name__,)
    assert rejected.qualification_status is QualificationStatus.NOT_QUALIFIED
    assert rejected.failed_requirements == ("ASSESSMENT_MINIMUM_SCORE",)
    assert rejected.observed_events == (SupplierQualificationRejected.__name__,)

    engine_a.dispose()

    engine_b = create_engine(database_url)
    runtime_b = PySRMKit.sql(engine_b)
    try:
        qualified_view = runtime_b.qualifications.get(
            qualification_id=qualified.qualification_id
        )
        rejected_view = runtime_b.qualifications.get(
            qualification_id=rejected.qualification_id
        )
        supplier_view = runtime_b.suppliers.get(supplier_id=qualified.supplier_id)

        assert supplier_view.legal_name == "Public Supplier 90"
        assert qualified_view.status is QualificationStatus.QUALIFIED
        assert qualified_view.approved is True
        assert qualified_view.failed_requirements == ()
        assert rejected_view.status is QualificationStatus.NOT_QUALIFIED
        assert rejected_view.approved is False
        assert rejected_view.failed_requirements == ("ASSESSMENT_MINIMUM_SCORE",)
    finally:
        engine_b.dispose()
