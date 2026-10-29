# PySRMKit - Supplier Search Query Plans and Index Decision

**Document:** `25_PYSRMKIT_SUPPLIER_QUERY_PLAN_AND_INDEX_QUALIFICATION.md`  
**Cycle:** 4 - `0.4.0a3` Query Adapter Qualification  
**Work package:** A3-07 - Query Performance & Index Qualification  
**Date:** 2026-10-29  
**Status:** Observed on SQLite and PostgreSQL 18 CI; final PR qualification pending

## 1. Objective and scope

Establish an evidence trail for the **existing** SQLAlchemy Supplier search:
`lower(legal_name)`, `lower(trading_name)`, filters on country/type,
`COUNT(*)` before pagination, stable ordering on lower-case legal name
and ascending supplier UUID, and the two query executions per search.

This is **query plan characterization, not a production-scale latency SLA**.
Do not infer production performance from a single shared GitHub runner or
compare SQLite and PostgreSQL milliseconds as a fair benchmark.

## 2. Method

The test infrastructure in `tests/performance/` generates **1,200**
synthetic Supplier rows with stable UUIDs, names, trading names, types and
country codes. These are loaded into an isolated database schema.

Instead of writing a separate approximation of the WHERE/ORDER BY clauses,
the test runs the **real `SqlAlchemySupplierRepository.search_suppliers()`**,
records the two SQL SELECT statements referring to the `suppliers` table
through SQLAlchemy's `before_cursor_execute` event, then explains them
with their original bound DBAPI parameters.

- **SQLite:** `EXPLAIN QUERY PLAN`.
- **PostgreSQL 18 CI:** `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)`.
- Each case captures the actual `COUNT` and page `SELECT` separately.
- Relationship select-in loads are not confused with the base Supplier
  count/page SQL.
- `ANALYZE suppliers` refreshes planner statistics before the observations.
- The query result is checked for correct pagination bounds and total.
- A legacy `list_suppliers()` check ensures UUID ordering is unchanged.
- Exactly **one** measured invocation per scenario is logged to identify
  gross anomalies, *not* to create a statistically significant latency estimate.

The same three cases execute in both database engines:

| Scenario | Text search | Country | Type | Offset / limit |
| --- | --- | --- | --- | --- |
| `unfiltered` | none | none | none | 20 / 25 |
| `substring` | `atlas` | none | none | 20 / 25 |
| `combined-filters` | `atlas` | FR | MANUFACTURER | 20 / 25 |

All cases use `sort_by=legal_name, sort_order=asc`.

## 3. Evidence collection

The existing CI `quality` job runs the SQLite test; the `postgresql`
job runs against an actual PostgreSQL 18 service. Each also has an explicit
`pytest -q -s` diagnostic step so the actual plans are visible in logs.

Search for:

```text
QUERY_PLAN backend=sqlite scenario=substring rows=1200 ...
QUERY_PLAN backend=postgresql scenario=combined-filters rows=1200 ...
QUERY_PLAN_DETAIL ...
```

Raw plan output and single-run execution times should be consulted in the
exact GitHub Actions run. CI output is the evidence, not hard-coded values
in this document.

### Observations from CI (2026-10-29)

| Scenario | Matches / page | SQLite count | SQLite page | PostgreSQL count | PostgreSQL page |
| --- | --- | --- | --- | --- | --- |
| `unfiltered` | 1,200 / 25 | Covering PK index scan | Table scan + temporary B-tree ORDER BY | Sequential scan + aggregate | Sequential scan + sort |
| `substring` | 382 / 25 | Table scan | Table scan + temporary B-tree ORDER BY | Sequential scan + aggregate | Sequential scan + sort |
| `combined-filters` | 26 / 6 | Table scan | Table scan + temporary B-tree ORDER BY | Sequential scan + aggregate | Sequential scan + sort |

**Actual evidence:**
- [PR #37 CI #246](https://github.com/tawounfouet/pysrmkit/actions/runs/40911709365) PostgreSQL `postgresql` job: real `EXPLAIN (ANALYZE, BUFFERS)` details.
  This first CI had a failed **format check** in `quality`, which was corrected in `ea12f24`; the PostgreSQL plan job nevertheless succeeded.
- [PR #37 CI #247](https://github.com/tawounfouet/pysrmkit/actions/runs/40911818953) `quality` job: SQLite `EXPLAIN QUERY PLAN` and the 389 non-PostgreSQL tests passed.

PostgreSQL 18 reports approximately **0.14/0.94 ms** for the unfiltered
count/page, **0.43/0.82 ms** for substring count/page, and **0.14/0.19 ms**
for combined-filter count/page in the **individual EXPLAIN ANALYZE runs**
on 1,200 rows. These numbers are isolated server-side observations,
not total API latency or an SLA. The query outputs also include a
distinct ORM call time and related-object loading.

In the substring scenario, PostgreSQL's optimizer estimated **4** rows
but observed **382**. For combined filters it estimated **1** and
observed **26**. This is a query-selectivity estimation issue worth
testing under more representative workloads; it does **not** itself
prove that any proposed index would improve latency.

**Interpretation:** The observed access patterns are consistent with
function-wrapped name columns and `%atlas%` substring predicates on a
small synthetic corpus. The SQLite primary-key covering scan for the
unfiltered count is an expected special case. Both engines perform
explicit name sorting for the requested page. No evidence yet justifies
an unconditional cross-backend migration or a new runtime dependency.

**Qualification outstanding:** Confirm all jobs of the exact latest
PR head and run a separate post-merge CI before closing A3-07.

## 4. Index hypotheses - no change without evidence

Current `SupplierRecord` defines `supplier_id` as the primary key and
defines **no explicit index on the legal/trading names, supplier_type, or
country_code**.

| Candidate | Potential benefit | Limitation / verification |
| --- | --- | --- |
| Expression index on `lower(legal_name)` | May support name-based ORDER BY | Need to inspect actual plan and selectivity; index maintenance cost |
| B-tree on `(country_code, supplier_type)` | May help selective filters | May not help when filters are absent, low-selectivity or combined with substring |
| PostgreSQL trigram indexes for normalized names | May accelerate substring lookup | Requires optional `pg_trgm`, migration, size and realistic workload qualification |
| SQLite FTS / specialized search index | Could accelerate text search | Separate feature, tokenization semantics may not match literal substring |
| No new index | Minimal write overhead and portable schema | Could become expensive at scale; require measurements at realistic row counts |

For the current `lower(column).contains(...)` query, arbitrary substring
search has a leading wildcard in SQL. A conventional B-tree on the
unmodified column is not automatically an effective substring index.
The `OR` across legal and trading names further affects plan selection.

**Decision:** No new index, extension or migration in A3-07. Record the
observed access paths first and open a separate, evidence-backed design
change if representative workloads show an actual bottleneck.

## 5. Limits and next steps

- The synthetic 1,200-row fixture is intentionally modest; plan choices can
  differ dramatically for 100,000+ suppliers and with skewed distributions.
- GitHub Actions CPU, disk and cache variability make single-call latency
  observations unsuitable for SLA or regression threshold enforcement.
- SQL query plans are sensitive to engine version, statistics, collation,
  available indexes and runtime configuration.
- This work does not change the Unicode/Collation Policy ADR. ASCII search
  remains the normative portable comparison contract.
- The optional SQLAlchemy adapter, Domain, Ports, public `SuppliersAPI` and
  original `list()` API remain unchanged.

For a future production-oriented index decision, obtain realistic row
counts/distributions, record P50/P95 query latency under controlled repeated
runs, compare read and write costs with/without candidate indexes, validate
plans on the supported databases and add an Alembic migration only when
the benefit is demonstrated.

## 6. Software design learning

- **Evidence-Based Design:** observed plans precede tuning.
- **Separation of Concerns:** diagnostic probes live in tests, not Domain
  logic or the public API.
- **KISS / YAGNI:** avoid indexes and extensions before a real workload
  requires them.
- **Ports and Adapters:** the same Supplier query port is evaluated through
  specific persistence adapters without changing consumers.
- **Test Determinism:** fixed dataset and scenarios, but no flaky
  latency assertion against shared CI infrastructure.
