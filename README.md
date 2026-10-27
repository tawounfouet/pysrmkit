# PySRMKit

> Technology-agnostic Python domain framework for Supplier Relationship Management.

PySRMKit is intended to provide a reusable Supplier Domain Engine for Python applications while keeping business rules independent from persistence, APIs, cloud services, workflow engines, and external SRM platforms.

## Status

**Early alpha — `0.1.0a8` Local Core Qualification qualified on the feature branch.**

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
```

Next decision point:

```text
Post-Core architecture / product review
No next capability is preselected.
```

The first local Core implementation cycle now covers Supplier identity, Relationship context and lifecycle, Onboarding readiness, Assessment, and explainable scoped Qualification using only local InMemory adapters.

Production infrastructure remains intentionally absent: no database, API framework, message broker, cloud service, or external SRM connector is required by the Core.

## Core principles

```text
minimal
explicit
repeatable
green
```

`0.1.0a8` is green. The complete local journey can now produce either `QUALIFIED` or `NOT_QUALIFIED` through Domain and Application layers with an explicit Domain Event trace.

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

The CI threshold remains **80% minimum coverage**. The qualified first local Core currently reaches **99.17%** total coverage; the threshold itself can be revisited during the post-Core review.

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
