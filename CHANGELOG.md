# Changelog

All notable changes to PySRMKit will be documented in this file.

## Unreleased

## 0.1.0a1 - 2026-10-27

### Added

- Python package bootstrap using a `src/` layout.
- Explicit `domain`, `application`, `ports`, and `adapters` package boundaries.
- Hatchling-based packaging with Python `>=3.11`.
- Zero mandatory third-party runtime dependencies.
- Development toolchain with Pytest, pytest-cov, Ruff, and Pyright.
- Import/version smoke tests.
- Executable architecture dependency tests.
- GitHub Actions quality pipeline.
- Pre-implementation specification baseline `00 → 14`.
- Software-design learning convention and iterative documentation strategy.
- Local development and quality-gate instructions.

### Qualified

- Editable installation succeeds in CI.
- `import pysrmkit` succeeds and reports `0.1.0a1`.
- Ruff lint and formatting checks pass.
- Pyright strict type checking passes.
- Pytest and architecture tests pass.
- Coverage meets the bootstrap threshold of 80%.
- CI is green on `main`.
- Failure drills proved that architecture, lint, and type gates become red when intentionally violated.

### Deferred

- Supplier domain implementation begins in `0.1.0a2 — Supplier Core`.
- Database, API, message broker, external connectors, and business adapters remain out of scope.
- PyPI publication and release-engineering automation remain out of scope.
