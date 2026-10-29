# PySRMKit - Cycle 4 Final Qualification Plan

**Milestone:** `0.4.0a5` - Cycle 4 Final E2E & CI Qualification  
**Date:** 2026-10-29  
**Status:** Proposed work packages; A5-01 candidate under qualification

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
- [ ] A5-01 PR CI three jobs green with exact SHA logged.
- [ ] A5-01 merge and post-merge main CI green.
- [ ] Remaining A5 lots and final `0.4.0a5` source version qualified.

No Git tag, GitHub Release or PyPI publication is implied.
