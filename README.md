# PySRMKit

> Technology-agnostic Python domain framework for Supplier Relationship Management.

PySRMKit is intended to provide a reusable Supplier Domain Engine for Python applications while keeping business rules independent from persistence, APIs, cloud services, workflow engines, and external SRM platforms.

## Status

**Early alpha — `0.1.0a4` Relationship Lifecycle qualified on `main`.**

Qualified milestones:

```text
0.1.0a1 — Repository Bootstrap
0.1.0a2 — Supplier Core
0.1.0a3 — Supplier Relationships
0.1.0a4 — Relationship Lifecycle
```

Next milestone:

```text
0.1.0a5 — Onboarding Core
```

The bootstrap deliberately creates the development foundation before implementing the business domain.

No Supplier aggregate, business repository, database adapter, API, message broker, or external connector is implemented at this stage.

## Bootstrap principles

```text
minimal
explicit
repeatable
green
```

`0.1.0a4` is green. Supplier relationships now move through explicit guarded lifecycle transitions from discovery to onboarding.

## Architecture

The bootstrap exposes four explicit package boundaries:

- `domain` — business model and business truth;
- `application` — use-case orchestration;
- `ports` — replaceable contracts required by the core;
- `adapters` — implementations of ports when they become necessary.

At `0.1.0a1`, these boundaries exist structurally but contain no speculative business abstractions.

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

The bootstrap target is currently **80% minimum coverage**. The threshold is expected to rise as real domain behavior appears.

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
