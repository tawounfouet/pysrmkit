# PySRMKit - Branch Protection and Pull Request Review Policy (PTH-002)

**Status:** Proposed configuration, **not applied** on GitHub.  
**Reviewed against:** `main` at `4b646546958e5476216446d2a2d088d17a7b99bd` (2026-11-01).  
**Scope:** Governance of repository contributions and CI evidence only. No product or licensing decision.

## Current observed baseline

- GitHub's branch response reported `main.protected = false` at the audit baseline.
- The public ruleset listing was empty; the branch-protection details endpoint returned 403 under the available integration.
- PR #50 was merged on 2026-10-30 and had no submitted formal review in its review list.
- PR #50's post-merge main CI run `41005656322` passed `quality`, `postgresql`, and `integration`.
- No `0.4.0a5` GitHub Release or PyPI publication was verified. A historical `v0.4.0a1` Git tag exists.
- No LICENSE file was present in the reviewed repository tree. **The license choice is reserved to the repository owner.**

These observations **do not** constitute a security audit or legal opinion.

## Proposed branch ruleset / protection for `main`

Configure in GitHub repository Settings > Rules > Rulesets (or Branches, where applicable):

1. Require changes through pull requests before they reach `main`. Forbid direct pushes to `main` during ordinary development.
2. Require status checks named **`quality`**, **`postgresql`**, and **`integration`** from the repository's CI workflow. Verify the check names in the GitHub UI before saving rules.
3. Require all review conversations resolved before merge.
4. Enforce non-force-push and non-deletion of `main`; include administrators where supported.
5. Require the head to be up to date before merge when a stable CI result is needed for the exact integration state.
6. Prefer at least one independent approving reviewer once a trusted collaborator is available. **A solo maintainer cannot self-approve** under GitHub's normal approval model; enabling approval enforcement without a reviewer can block all PRs. Until then, use a documented manual owner sign-off outside GitHub approvals, and explicitly record this governance limitation.
7. Grant exemptions only through a documented emergency process with an evidence trail and post-change review.
8. Do not enable auto-merge or releases for agent-authored PRs. Merge and publication remain owner-authorized actions.

**Not executable by PTH-002:** the currently connected GitHub integration cannot read the protected-branch settings endpoint (403), and no permitted write tool is available here to apply an administrative ruleset. Owner action in GitHub Settings is required; this file is only a proposal.

## PR review policy

- Describe business problem, scope, non-goals, changed paths, risk, rollback and test plan.
- Link the exact head SHA and green CI runs; distinguish PR tests from post-merge main checks.
- Changes to Domain contracts, persistent events, security decisions or licensing require a new explicit decision.
- Never claim production qualification because alpha tests or CI are green.
- For security-sensitive changes, require an independent reviewer with relevant competence before shipping.

## Security and reproducibility notes

The PTH-002 CI proposal sets `permissions: contents: read`, pins official GitHub Action revisions to commit SHAs, sets job deadlines and adds dependency consistency and compile checks. This is **workflow hardening**, not vulnerability scanning or a supply-chain attestation. The `ubuntu-latest` runner, `postgres:18` image, Python dependencies and npm resolution are not all immutably pinned. Never infer full hermetic reproducibility.

## Deferred owner decisions

- **License:** choose and approve a license before adding LICENSE or claiming open-source reuse rights.
- **Review policy enforcement:** select actual reviewers/collaborators; assess whether required approvals are operationally feasible.
- **Release:** decide if/when to tag, create a GitHub Release or publish on PyPI.
- **Architecture:** any event durability, Unicode portability or Supplier Domain contract change is explicitly out of PTH-002 scope.

## Audit and verification references

- Source commit: https://github.com/tawounfouet/pysrmkit/commit/4b646546958e5476216446d2a2d088d17a7b99bd
- Final Cycle 4 PR: https://github.com/tawounfouet/pysrmkit/pull/50
- Final Cycle 4 post-merge main CI: https://github.com/tawounfouet/pysrmkit/actions/runs/41005656322
- `docs/qualification/0.4.0a5.md` provides the bounded alpha qualification.
