# PySRMKit

> Technology-agnostic Python domain framework for Supplier Relationship Management.

PySRMKit is intended to provide a reusable Supplier Domain Engine for Python applications while keeping business rules independent from persistence, APIs, cloud services, workflow engines, and external SRM platforms.

## Status

**Early alpha - `0.4.0a2` Supplier Query API candidate in PR #32.**

The previous `0.4.0a1` integration reproducibility milestone was qualified on its PR and merged to `main`; final `0.4.0a2` qualification is pending the new CI and merge.

Four implementation cycles:

- **Cycle 1 - `0.1.0a1 → 0.1.0a8`:** Supplier Domain Core, relationships, lifecycle, onboarding, assessment, scoped qualification and InMemory end-to-end journey.
- **Cycle 2 - `0.2.0a1 → 0.2.0a7`:** SQLAlchemy persistence, SQLite/PostgreSQL repository contracts, explicit transactions and UnitOfWork, Alembic migrations and durable restart/reload qualification.
- **Cycle 3 - `0.3.0a1 → 0.3.0a6`:** public facade and capability APIs, InMemory/SQL runtime composition, immutable Views, public error boundary, typed Domain Events and public-only runtime qualification.
- **Cycle 4 - `0.4.0a1 → 0.4.0a5` (In Progress):** Industrialisation & Integration Qualification: reproducible multi-service stack (FastAPI + Next.js + PostgreSQL), E2E browser qualification, query contracts and CI gates.

PySRMKit is a reusable **Supplier Domain Engine**, not a complete SRM application. It remains independent of API frameworks, cloud platforms, message brokers and external SRM products. SQLAlchemy is optional.

## Public Python API

```python
from pysrmkit import PySRMKit, SupplierCreated

srm = PySRMKit.in_memory()
srm.events.subscribe(SupplierCreated, lambda event: print(event.supplier_id))

supplier = srm.suppliers.register(legal_name="Example Supplier", country_code="FR")
relationship = srm.relationships.create(
    supplier_id=supplier.supplier_id,
    organization_id="HQ",
)
srm.relationships.invite(relationship_id=relationship.relationship_id)

supplier_view = srm.suppliers.get(supplier_id=supplier.supplier_id)
supplier_page = srm.suppliers.list(offset=0, limit=25)
search_page = srm.suppliers.search(query="Example", country_code="FR", limit=25)
relationship_view = srm.relationships.get(relationship_id=relationship.relationship_id)
```

Five business capabilities are available under `srm.suppliers`, `srm.relationships`, `srm.onboardings`, `srm.assessments` and `srm.qualifications`. The separate `srm.events` surface supports typed, synchronous, in-process subscriptions.

To use SQL persistence, install the optional `persistence` extra, provision the schema explicitly with Alembic, then construct `PySRMKit.sql(engine)` using an externally managed SQLAlchemy Engine. SQL operations use short-lived transactions; public events are delivered after successful commit. **Event delivery is not durable** and does not provide replay or broker semantics.

Public reads return immutable Views rather than SQLAlchemy records. Domain, Application and Repository Port layers remain persistence-framework agnostic.

## Supplier discovery - `0.4.0a2` candidate

The public `srm.suppliers.search(...)` capability is implemented in both
`PySRMKit.in_memory()` and `PySRMKit.sql(engine)`. The latter requires the
optional SQLAlchemy persistence dependency and a provisioned schema.

```python
from pysrmkit import PySRMKit

srm = PySRMKit.in_memory()
srm.suppliers.register(
    legal_name="Atlas Components",
    trading_name="Atlas",
    supplier_type="MANUFACTURER",
    country_code="FR",
)
page = srm.suppliers.search(
    query="atlas",
    country_code="FR",
    supplier_type="MANUFACTURER",
    sort_by="legal_name",
    sort_order="asc",
    offset=0,
    limit=25,
)
assert page.total == 1
```

- The text query is trimmed and searches partial `legal_name` or
  `trading_name`, case-insensitively for ordinary ASCII text.
- `country_code` is validated as a two-letter country reference;
  `supplier_type` uses exact case-sensitive equality.
- Supported sort is `legal_name` in ascending or descending order.
  Identical names have an ascending Supplier UUID tie-break.
- Pagination uses `offset >= 0` and `1 <= limit <= 100`. The
  `total` count is computed after filtering, before pagination.
- Results are immutable `SupplierPageView` objects with `items`, `total`,
  `offset` and `limit`.
- The legacy `suppliers.list()` retains its signature and UUID-based
  ordering; `search()` has its own semantic ordering.
- No text search over external identifiers or fuzzy matching is promised.
- Unicode/accent/collation equivalence across Python, SQLite and PostgreSQL
  is **not guaranteed** until the `0.4.0a3` adapter qualification.

See [Supplier Query Contract ADR](docs/specifications/22_PYSRMKIT_SUPPLIER_QUERY_CONTRACT_ADR.md).
This is candidate documentation until the release PR and main-branch CI are qualified.

## Core principles

```text
minimal
explicit
repeatable
green
```

`0.3.0a6` qualifies the public Supplier journey on InMemory, SQLite and PostgreSQL, including success/rejection, public Views, Domain Events and SQLite runtime restart/reload. The earlier Persistent Core cycle separately qualifies Alembic bootstrap and durable SQL persistence.

## Architecture

The architecture preserves four Core package boundaries and adds a public consumer-facing facade:

- `domain` — business model and business truth;
- `application` — use-case orchestration;
- `ports` — replaceable contracts required by the core;
- `adapters` — implementations of ports when they become necessary;
- `public` — facade, capability APIs, Views, errors, events and runtime composition.

The Core boundaries were established in Cycle 1, qualified against SQL persistence in Cycle 2, and exposed through a typed public runtime in Cycle 3.

## Requirements

- Python 3.11 or newer
- Git

## Local setup

```bash
git clone https://github.com/tawounfouet/pysrmkit.git
cd pysrmkit

python -m venv .venv
source .venv/bin/activate

python -m pip install -e ".[dev]"
```

For consumers who need the optional relational persistence foundation without the development toolchain:

```bash
python -m pip install -e ".[persistence]"
```

For schema migration tooling:

```bash
python -m pip install -e ".[migrations]"
PYSRMKIT_DATABASE_URL="sqlite:///pysrmkit.db" alembic upgrade head
```

For PostgreSQL support through Psycopg 3:

```bash
python -m pip install -e ".[postgresql,migrations]"
```

For the optional FastAPI host example:

```bash
python -m pip install -e ".[api,migrations]"
createdb -O postgres pysrmkit
PYSRMKIT_DATABASE_URL="postgresql+psycopg://postgres@localhost:5432/pysrmkit" alembic upgrade head
PYSRMKIT_DATABASE_URL="postgresql+psycopg://postgres@localhost:5432/pysrmkit" \
  python -m examples.seed_suppliers
PYSRMKIT_DATABASE_URL="postgresql+psycopg://postgres@localhost:5432/pysrmkit" \
  uvicorn examples.http_api:app --reload --port 8000
```

The interactive OpenAPI documentation is available at `http://localhost:8000/docs`.
This HTTP host is an example consumer of the public facade; FastAPI remains outside the Core.

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Quality gates

Run the same baseline checks used by CI:

```bash
ruff check .
ruff format --check .
pyright
pytest --cov=pysrmkit --cov-report=term-missing
```

The CI threshold remains **80% minimum coverage**. The historical `0.2.0a7` final PR qualification (CI #144) reached **98.11%** coverage with **239 tests passed** in its quality job and **44 PostgreSQL tests**. These are historical Cycle 2 metrics, not the current Cycle 3 totals. Cycle 3's final qualification was validated in CI #188, including the PostgreSQL job.

## Documentation

The frozen pre-implementation baseline is stored under:

```text
docs/specifications/
```

It contains specifications `00 → 14` plus the software-design learning convention and the iterative documentation strategy.

## Roadmap

The first implementation cycle is defined in:

```text
docs/specifications/13_PYSRMKIT_IMPLEMENTATION_ROADMAP.md
```

The operational bootstrap is defined in:

```text
docs/specifications/14_PYSRMKIT_IMPLEMENTATION_BOOTSTRAP_PLAN.md
```

The post-Core review and persistence-cycle architecture are defined in:

```text
docs/specifications/15_PYSRMKIT_POST_CORE_ARCHITECTURE_REVIEW.md
docs/specifications/16_PYSRMKIT_PERSISTENCE_ARCHITECTURE.md
docs/specifications/17_PYSRMKIT_PERSISTENT_CORE_MILESTONE.md
docs/specifications/18_PYSRMKIT_POST_PERSISTENCE_ARCHITECTURE_REVIEW.md
docs/specifications/19_PYSRMKIT_PUBLIC_API_AND_RUNTIME_COMPOSITION_ARCHITECTURE.md
```

## Release history

See [CHANGELOG.md](CHANGELOG.md) for the three completed cycles and detailed alpha milestones.

## Cycle 3 qualification evidence

- [Public Runtime qualification report](docs/cycle-3-public-runtime-qualification.md)
- [Public Domain Event contract](docs/public-events.md)
- [Cycle 3 qualification PR #28](https://github.com/tawounfouet/pysrmkit/pull/28)
- [Cycle 2 historical milestone](docs/specifications/17_PYSRMKIT_PERSISTENT_CORE_MILESTONE.md)
