# PTH-002 - PySRMKit Remediation and Qualification

**Date:** 2026-11-01  
**Execution authority:** A2 and A3 only (prepare, commit to dedicated branch, open PR).  
**Base SHA:** `4b646546958e5476216446d2a2d088d17a7b99bd`  
**Mission:** Correct PTH-001 evidence drift and strengthen repository CI and review process without changing Supplier Domain behavior.

## Changes proposed

1. Reconcile README and `docs/qualification/0.4.0a5.md` with merged PR #50 and successful post-merge main CI run `41005656322`; distinguish qualified source vs unpublished release.
2. Improve GitHub Actions: `contents: read` token scope, concurrency cancellation, job deadlines, pinned official Node 24-based action revisions, `pip check` and Python source compile check.
3. Add PR template, review policy and specific owner-admin branch-protection checklist.

## Acceptance criteria

- No edits to `src/pysrmkit/`, migrations, API routes, Domain invariants or event durability.
- The existing `quality`, `postgresql` and `integration` jobs must pass on the exact PR head.
- Document the PR URL, exact SHA, outcome and outstanding decisions in the PR conversation / audit report, not by prematurely claiming a successful CI run.
- No merge, tag, GitHub Release, PyPI upload or owner-admin settings change.

## Deferred / explicitly not authorized

- No LICENSE file or selection of legal license.
- No autonomous changes to branch rules or reviewer requirements.
- No improvements that silently change Unicode semantics, SQL schema, event delivery guarantees or any Supplier API contract.
- No claim of security, production or full build reproducibility.

## Design learning

- **Evidence-based engineering:** tie a qualification claim to an immutable commit and its exact successful run.
- **Separation of concerns:** distinguish code quality, repository governance, publication and production operation.
- **Least privilege:** constrain workflow credentials to required read access.
- **Reproducibility:** pin third-party CI actions by immutable commit ID while documenting remaining mutable inputs.
- **Human-in-the-loop:** a PR is a review artifact, not authorization to merge or publish.
