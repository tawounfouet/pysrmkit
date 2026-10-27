# PySRMKit

> Technology-agnostic Python domain framework for Supplier Relationship Management.

PySRMKit is intended to provide a reusable Supplier Domain Engine for Python applications while keeping business rules independent from persistence, APIs, cloud services, workflow engines, and external SRM platforms.

## Status

**Early alpha — `0.2.0a6` Alembic Migration Baseline qualified on PR #18.**

Qualified milestones:

```text
0.1.0a1 — Repository Bootstrap
0.1.0a2 — Supplier Core
0.1.0a3 — Supplier Relationships
0.1.0a4 — Relationship Lifecycle
0.1.0a5 — Onboarding Core
0.1.0a6 — Qualification Domain
0.1.0a7 — Qualification Application Flow
0.1.0a8 — Local Core Qualification

0.2.0a1 — Persistence Foundation
0.2.0a2 — Supplier + Relationship SQL Persistence
0.2.0a3 — Onboarding + Assessment SQL Persistence
0.2.0a4 — Qualification SQL Persistence
0.2.0a5 — Transaction Boundary / UnitOfWork
0.2.0a6 — Alembic Migration Baseline
```

Next milestone:

```text
0.2.0a7 — Persistent Local Qualification
```

The first local Core implementation cycle covers Supplier identity, Relationship context and lifecycle, Onboarding readiness, Assessment, and explainable scoped Qualification. The second cycle now validates the same architecture against optional relational persistence infrastructure.

SQLAlchemy remains optional: the pure Core still requires no database, API framework, message broker, cloud service, or external SRM connector.

## Core principles

```text
minimal
explicit
repeatable
green
```

`0.2.0a6` is green on PR #18. Empty SQLite and PostgreSQL databases can now be migrated reproducibly to the complete Persistent Core schema through the versioned Alembic baseline, while Domain, Application, and Repository Ports remain persistence-framework agnostic.

## Architecture

The bootstrap exposes four explicit package boundaries:

- `domain` — business model and business truth;
- `application` — use-case orchestration;
- `ports` — replaceable contracts required by the core;
- `adapters` — implementations of ports when they become necessary.

These boundaries were established at `0.1.0a1` and are now exercised by the complete first vertical slice without introducing infrastructure dependencies into the Domain.

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

The CI threshold remains **80% minimum coverage**. The `0.2.0a6` PR qualification reaches **97.74%** total coverage with **235 tests passed** in the quality job, while the PostgreSQL CI job executes **42 selected tests** against PostgreSQL 18.6.

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
```
