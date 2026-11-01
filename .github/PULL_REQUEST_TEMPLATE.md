## Purpose and change scope

- Problem / linked issue or audit:
- Paths changed:
- Current behavior vs proposed behavior:
- Out of scope:

## Design and compatibility review

- [ ] No Supplier Domain or public API contract change, OR an explicit owner decision is linked
- [ ] No durable event semantics or persistence migration change, OR an explicit owner decision is linked
- [ ] No licensing decision is introduced without owner approval
- [ ] Alternatives, tradeoffs and rollback described where relevant
- [ ] Learning notes / architecture principles recorded when a new pattern is involved

## Evidence and gates

- [ ] Exact PR head SHA recorded
- [ ] `quality` completed successfully
- [ ] `postgresql` completed successfully
- [ ] `integration` completed successfully
- [ ] Relevant local checks or CI limitations documented
- [ ] Review comments resolved and human approval recorded
- [ ] Owner-approved merge required; PR CI success alone is not a release authorization

## Operational boundaries

- Does this require branch protection changes, secrets, publication, or production deployment?
- What could fail and how will this be detected?
- Was the documentation reconciled with the implemented state?

**Note:** This template is guidance. Actual branch protection and review enforcement are administered separately (see `docs/governance/BRANCH_PROTECTION_AND_REVIEW_POLICY.md`).
