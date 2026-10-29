"""A3-07 isolated query plan characterization for the real Supplier search path.

Plans are produced from *captured statements executed by the repository*,
not from a parallel hand-written approximation of its WHERE/ORDER BY logic.
The small deterministic dataset is a diagnostic fixture, not a benchmark.
"""

from __future__ import annotations

from time import perf_counter
from typing import Any
from uuid import UUID

from sqlalchemy import event, text
from sqlalchemy.engine import Connection, Engine, ExecutionContext
from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.models.supplier import SupplierRecord
from pysrmkit.adapters.sqlalchemy.repositories.supplier import SqlAlchemySupplierRepository
from pysrmkit.domain.supplier.value_objects import CountryCode

ROW_COUNT = 1200


def _seed(session: Session) -> None:
    """Use deterministic synthetic data, independent of external identifiers."""
    session.add_all(
        [
            SupplierRecord(
                supplier_id=UUID(int=index + 100),
                legal_name=(
                    f"Atlas Components {index:05d}"
                    if index % 4 == 0
                    else f"Vendor {index:05d}"
                ),
                trading_name="Central Atlas" if index % 11 == 0 else None,
                supplier_type="MANUFACTURER" if index % 3 == 0 else "SERVICE",
                country_code="FR" if index % 5 == 0 else "DE",
            )
            for index in range(ROW_COUNT)
        ]
    )
    session.flush()
    session.execute(text("ANALYZE suppliers"))


def _explain(
    session: Session,
    *,
    dialect: str,
    sql: str,
    parameters: Any,
) -> tuple[str, ...]:
    prefix = (
        "EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) "
        if dialect == "postgresql"
        else "EXPLAIN QUERY PLAN "
    )
    rows = session.connection().exec_driver_sql(prefix + sql, parameters).all()
    return tuple(str(row[-1] if dialect == "sqlite" else row[0]) for row in rows)


def characterize_supplier_search(engine: Engine) -> None:
    """Log actual count/page plans, with safety checks but no timing threshold."""
    dialect = engine.dialect.name
    assert dialect in ("sqlite", "postgresql")

    with Session(engine) as session:
        _seed(session)
        repository = SqlAlchemySupplierRepository(session)
        scenarios: tuple[tuple[str, str | None, CountryCode | None, str | None], ...] = (
            ("unfiltered", None, None, None),
            ("substring", "atlas", None, None),
            ("combined-filters", "atlas", CountryCode("FR"), "MANUFACTURER"),
        )
        for label, query, country, supplier_type in scenarios:
            captured: list[tuple[str, Any]] = []

            def record_supplier_sql(
                _connection: Connection,
                _cursor: Any,
                statement: str,
                parameters: Any,
                _context: ExecutionContext,
                _executemany: bool,
            ) -> None:
                if statement.lstrip().upper().startswith("SELECT") and "FROM suppliers" in statement:
                    captured.append((statement, parameters))

            event.listen(engine, "before_cursor_execute", record_supplier_sql)
            try:
                started = perf_counter()
                result = repository.search_suppliers(
                    query=query,
                    country_code=country,
                    supplier_type=supplier_type,
                    sort_by="legal_name",
                    sort_order="asc",
                    offset=20,
                    limit=25,
                )
                duration_ms = (perf_counter() - started) * 1000
            finally:
                event.remove(engine, "before_cursor_execute", record_supplier_sql)

            # SELECT COUNT(*) and SELECT page; selectin related-record loads are
            # excluded by their different table name. Never explain a fabricated query.
            assert len(captured) == 2, f"{dialect}/{label}: {len(captured)} supplier statements"
            assert 0 <= len(result.suppliers) <= 25
            assert result.total >= len(result.suppliers)
            assert result.total <= ROW_COUNT

            print(
                f"QUERY_PLAN backend={dialect} scenario={label} rows={ROW_COUNT} "
                f"matches={result.total} page_size={len(result.suppliers)} "
                f"single_call_ms={duration_ms:.3f}"
            )
            for kind, (statement, parameters) in zip(("count", "page"), captured, strict=True):
                plan = _explain(session, dialect=dialect, sql=statement, parameters=parameters)
                assert plan, f"Empty {dialect} plan for {label}/{kind}"
                print(f"QUERY_PLAN backend={dialect} scenario={label} query={kind}")
                for line in plan:
                    print(f"QUERY_PLAN_DETAIL {line}")

        # Existing listing semantics are independent from search/plan inspection.
        legacy = repository.list_suppliers(offset=0, limit=25)
        assert legacy.total == ROW_COUNT
        assert tuple(item.id.value for item in legacy.suppliers) == tuple(
            UUID(int=index + 100) for index in range(25)
        )
        session.rollback()
