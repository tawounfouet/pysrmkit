# PySRMKit

> Technology-agnostic Python domain framework for Supplier Relationship Management.

PySRMKit is intended to provide a reusable Supplier Domain Engine for Python applications while keeping business rules independent from persistence, APIs, cloud services, workflow engines, and external SRM platforms.

## Status

**Early alpha — repository bootstrap in progress.**

Current milestone:

```text
0.1.0a1 — Repository Bootstrap
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

The repository will progressively establish:

- a `src/` package layout;
- Domain / Application / Ports / Adapters boundaries;
- linting and formatting with Ruff;
- static typing with Pyright;
- tests with Pytest;
- executable architecture checks;
- GitHub Actions CI;
- the pre-implementation specification baseline.

Once `0.1.0a1` is green, generic scaffolding stops and implementation moves to:

```text
0.1.0a2 — Supplier Core
```

## Development

Local setup commands will be finalized during the bootstrap milestone.

## Documentation

The pre-implementation specifications will live under:

```text
docs/specifications/
```
