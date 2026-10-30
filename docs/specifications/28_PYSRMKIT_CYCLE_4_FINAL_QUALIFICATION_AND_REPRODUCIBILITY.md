# PySRMKit - Cycle 4 Final Qualification Plan

**Milestone:** `0.4.0a5` - Cycle 4 Final E2E & CI Qualification  
**Date:** 2026-10-29  
**Status:** A5-01 and A5-02 qualified on main (CI #279); A5-03 candidate under qualification

## Scope basis

The existing Cycle 4 overview describes reproducible FastAPI, PostgreSQL,
Next.js and browser integration. The previously qualified `0.4.0a4`
source version is backed by PR #45/#46 and main CI #272.

The prior A4-04 and A4-06 reports explicitly identified a remaining
reproducibility gap: the CI checked out the external dashboard's default
branch. Therefore the earlier green result proved only the dashboard
revision available **at that run**, not a stable pinned revision.

The work-package breakdown below is a proposed operational plan, **not**
a claim of an existing frozen `0.4.0a5` specification.

## Proposed work packages

| Lot | Objective | Acceptance |
| --- | --- | --- |
| A5-01 | Pin and verify the exact external Next.js dashboard revision | Dashboard checkout SHA assertion, full CI E2E green |
| A5-02 | Qualify repeatable bootstrap and seed operations in CI | Repeat-run assertions, Alembic state and stable Supplier identity |
| A5-03 | Clarify and exercise failure/cleanup boundaries for the integration stack | Tests for startup failures and process cleanup |
| A5-04 | Produce a traceable Cycle 4 end-to-end CI evidence matrix | Exact pinned SHA, PySRMKit SHA, CI runs and limits |
| A5-05 | Version synchronization and final `0.4.0a5` source qualification | PR/main CI green, final report and no unverified publication claims |

Do not add production-domain behavior, mandatory dependencies, new
persistence indexes, or undocumented changes to the dashboard as part of
a CI qualification cycle.

## A5-01 - External dashboard revision pinning

The integration job previously used:

```yaml
repository: tawounfouet/nextjs-acme-dashboard
path: resources/nextjs-acme-dashboard
```

without a `ref`. That makes a PySRMKit CI rerun sensitive to new
commits in another repository.

The qualified dashboard source is explicitly set to:

```text
Repository: tawounfouet/nextjs-acme-dashboard
Ref:        11ed240f7e25e3de22304a3fa5b1c4a67f787bf2
```

The workflow uses `actions/checkout@v4` with this exact `ref`,
and a separate step asserts `git rev-parse HEAD` equals that SHA.
The log emits `QUALIFIED_DASHBOARD_SHA=...` for traceability.

This fixes **the external source revision**, not every environmental
variable: GitHub-hosted runner images, upstream GitHub Actions tags,
Python/Node package resolution and PostgreSQL image tags can still
change. Future lots can assess those dependencies separately.

### Updating the pin

A future dashboard change must be introduced through an explicit
PySRMKit PR that updates the `ref` and expected SHA together, documents
the source change and runs all three jobs (`quality`, `postgresql`,
`integration`) on the exact head. The existing browser test guards
legacy supplier name, country and vendor-code search semantics.
The new pin is **not** a declaration that dashboard `main` will
remain compatible forever.

## Design concepts

- **Reproducible Builds / Hermeticity (partial):** eliminate one
  uncontrolled external source revision; full hermeticity is not claimed.
- **Consumer-Driven Contract Testing:** test the exact dashboard revision
  that relies on the legacy supplier endpoint.
- **Dependency Pinning:** fix the external source as a deliberate
  versioned input.
- **Separation of Concerns / KISS / YAGNI:** no Supplier Domain or
  API modifications for a CI reproducibility issue.

## Qualification gates

- [x] The previously qualified `0.4.0a4` source release is on main.
- [x] A5-01 PR #47 CI #273 passed all three jobs, with exact SHA logged.
- [x] A5-01 merged as `8ec285b` and post-merge main CI #274 green.
- [x] A5-02 repeated PostgreSQL bootstrap and supplier snapshot PR #48 / main CI #279 green.
- [ ] A5-03 startup failure and process cleanup PR/main CI green.
- [x] A5-04 evidence matrix drafted in `docs/qualification/0.4.0a5.md` (qualification candidate, not final certification).
- [ ] A5-05 exact-head PR CI, merge and post-merge main CI green for `0.4.0a5`.

No Git tag, GitHub Release or PyPI publication is implied.

## A5-02 - Bootstrap and seed repeatability

The pre-existing `test_bootstrap_is_idempotent` only ran one repeat
and checked aggregate counts after the CI bootstrap. A5-02 strengthens
the integration suite with **two further executions** of
`bootstrap(seed_nextjs=False)` against the already bootstrapped real
PostgreSQL database.

The executable evidence in `tests/test_bootstrap_integration.py`
checks after each execution:

- Both PostgreSQL databases remain present (no database creation).
- Supplier seeding creates zero new records and skips exactly eight.
- The eight source-qualified vendor codes remain unique.
- The exact **Supplier UUID, vendor code, and legal name tuples** remain
  stable, not just the supplier count.
- Alembic's `alembic_version` state remains at the exact prior revision.
- The separate Next.js database seed is intentionally excluded with
  `seed_nextjs=False`, because it belongs to the external consumer.

This is a **sequential retry idempotency** test in the controlled CI
stack. It does not prove concurrent bootstraps, automatic recovery
from mid-transaction crashes, or idempotence of the external dashboard
seed. No changes to production bootstrap logic or migrations are needed.

**Design concepts:** Idempotency, State-based Regression Testing,
Reproducible Integration Testing, CQS and Separation of Concerns.

## A5-03 - Startup failure and child cleanup

The integration context manager previously created the FastAPI subprocess
**before** entering its `try/finally` block. If the Next.js spawn
raised (e.g. `npm` not found), FastAPI could outlive the failed
startup. The revised code owns both child launches inside one
`try/finally` boundary, with optional process handles, and always
reaps a force-killed child by calling `wait()` after `kill()`.

The executable regression tests in `tests/test_run_stack_cleanup.py`
exercise failure to spawn the dashboard, FastAPI/Next.js readiness
timeouts, a consumer exception within the context, forced kill after
the graceful termination timeout, and a child already exited.

These tests use isolated process mocks to avoid launching background
servers during the quality job. The existing full Playwright/PostgreSQL
integration remains responsible for the real successful startup path.
Process **descendants** created by npm/Next.js are not individually
tracked by this context manager; this lot does not claim tree-wide
process-group termination, arbitrary-signal resilience or crash
recovery.

**Design concepts:** RAII/context-manager resource ownership,
Exception Safety, Failure-Path Testing, Idempotent Cleanup and SoC.
