# Changelog

All notable changes to PySRMKit will be documented in this file.

## Unreleased

## 0.1.0a5 - 2026-10-27

### Added

- `SupplierOnboarding` as a relationship-scoped Aggregate Root.
- Strong `OnboardingId` and `OnboardingRequirementCode` Value Objects.
- Immutable `OnboardingRequirement` values with mandatory/optional semantics.
- Computed `OnboardingProgress` Domain Result.
- Mandatory-requirement completion invariant.
- Explicit onboarding Domain Errors for duplicate, unknown, incomplete, and already-completed states.
- `SupplierOnboardingCompleted` Domain Event.
- `SupplierOnboardingRepository` Protocol and `InMemorySupplierOnboardingRepository`.
- `SatisfyOnboardingRequirement`, `CompleteSupplierOnboarding`, and `GetOnboardingProgress` application flows.
- `StartSupplierOnboardingHandler` now creates the relationship-scoped onboarding Aggregate instead of requiring a duplicate create command.
- Shared onboarding repository contract tests.
- Local invite → onboarding → satisfy → complete readiness scenario.

### Qualified

- Onboarding belongs to one `SupplierRelationshipId`.
- Mandatory and optional requirements are represented explicitly.
- Requirement satisfaction is persisted independently.
- Incomplete onboarding cannot be completed while mandatory requirements remain unsatisfied.
- Optional unsatisfied requirements do not block completion.
- Progress is computed from canonical requirement state rather than stored independently.
- Completed onboarding emits `SupplierOnboardingCompleted`.
- Rehydration does not recreate historical events.
- One current onboarding is enforced per Relationship by application orchestration.
- Relationship/onboarding state remains isolated across different Relationships.
- Ruff, formatting, Pyright strict, architecture tests, and Pytest are green.
- 101 tests pass with 99.76% total coverage on PR validation CI #41.

### Deferred

- Task assignment, reminders, timers, reviewer inboxes, escalations, and workflow DSL remain outside PySRMKit Domain.
- No generic workflow engine was introduced.
- No `OnboardingStage` state machine was introduced because requirement readiness is sufficient for the qualification path.
- No UnitOfWork was introduced; a NoOp implementation would not provide real multi-repository atomicity.
- Qualification rules remain in `0.1.0a6`.


## 0.1.0a4 - 2026-10-27

### Added

- `SupplierLifecycleStage` as an explicit relationship-scoped `StrEnum`.
- `LifecycleTransitionReason` Value Object for lifecycle operations that require auditable reasons.
- `InvalidLifecycleTransition` Domain Error carrying source and target stages.
- Explicit `SupplierRelationship.invite(...)` transition.
- Explicit `SupplierRelationship.start_onboarding(...)` transition.
- `SupplierInvited` Domain Event.
- `SupplierOnboardingStarted` Domain Event.
- `InviteSupplierRelationship` and matching Handler.
- `StartSupplierOnboarding` and matching Handler.
- `SupplierRelationshipNotFound` Application Error.
- Lifecycle stage persistence in `InMemorySupplierRelationshipRepository`.
- Transition-matrix, event, handler, repository round-trip, and multi-organization isolation tests.

### Qualified

- New relationships start in `DISCOVERED`.
- The first local path supports `DISCOVERED → INVITED → ONBOARDING`.
- `PROSPECTIVE → INVITED` remains compatible with the reference baseline.
- Forbidden invite/onboarding transitions raise `InvalidLifecycleTransition`.
- Failed transitions leave state unchanged and emit no success event.
- Successful transitions emit the expected Domain Event.
- Lifecycle state survives repository save/reload.
- Unsaved lifecycle changes do not leak into repository state.
- Lifecycle changes remain scoped to the targeted Relationship only.
- Ruff, formatting, Pyright strict, architecture tests, and Pytest are green.
- 73 tests pass with 99.64% total coverage on PR validation CI #34.

### Deferred

- `UNDER_REVIEW` transition remains deferred until onboarding/qualification pressure requires it.
- Qualification, activation, suspension, blocking, reactivation, inactivity, and offboarding behavior remain out of scope.
- No GoF State Pattern is introduced.
- No workflow engine or onboarding infrastructure is introduced.


## 0.1.0a3 - 2026-10-27

### Added

- `SupplierRelationship` Aggregate Root as a distinct association between a canonical Supplier and an internal organization.
- Strong IDs `SupplierRelationshipId` and `InternalOrganizationId`.
- Initial relationship state `DISCOVERED`, without pre-implementing the lifecycle State Machine reserved for `0.1.0a4`.
- `SupplierRelationshipCreated` Domain Event.
- `SupplierRelationshipRepository` Protocol with `get`, `save`, and `find_for_supplier_and_organization`.
- Persistence-like `InMemorySupplierRelationshipRepository`.
- `CreateSupplierRelationship`, `CreateSupplierRelationshipHandler`, and result model.
- Application errors `SupplierNotFound` and `RelationshipAlreadyExists`.
- Shared SupplierRelationship repository contract tests.
- Multi-organization isolation tests.

### Qualified

- Relationship creation requires an existing Supplier.
- A Relationship references exactly one `SupplierId` and one `InternalOrganizationId`.
- Duplicate Supplier/organization relationships are rejected.
- The same Supplier can have independent Relationships with different organizations.
- Relationships belonging to different Suppliers remain isolated.
- `SupplierRelationshipCreated` is recorded and dispatched after successful creation.
- InMemory repository passes the shared contract.
- Ruff, formatting, Pyright strict, architecture tests, and Pytest are green.
- 48 tests pass with 99.57% total coverage on PR validation CI #29.

### Deferred

- Relationship lifecycle transitions remain in `0.1.0a4`.
- Invitation, onboarding transition, qualification, activation, suspension, blocking, and offboarding are not implemented in this milestone.
- Database persistence and query projections remain out of scope.


## 0.1.0a2 - 2026-10-27

### Added

- Supplier Core Aggregate Root with stable `SupplierId`.
- Supplier identity Value Objects: `SupplierIdentity`, `ExternalIdentifier`, `CountryCode`, `Address`, `CategoryCode`, and `CapabilityCode`.
- Supplier identity invariants and duplicate external-identifier protection.
- `SupplierCreated` Domain Event and minimal Aggregate event recording/`pull_events()`.
- `SupplierRepository` Protocol with `get`, `save`, and `find_by_external_identifier`.
- Persistence-like `InMemorySupplierRepository` with explicit save/reload isolation.
- `Clock` and `DomainEventDispatcher` Ports.
- `SystemClock` and `FixedClock` adapters.
- `RegisterSupplier`, `RegisterSupplierHandler`, and `RegisterSupplierResult`.
- Shared repository contract tests executed against the InMemory adapter.

### Qualified

- Supplier can be registered through the Application Handler.
- Supplier has a stable internal identity independent from external identifiers.
- Duplicate identifiers are rejected within one Aggregate.
- Cross-Supplier duplicate identifiers are rejected through repository lookup.
- `SupplierCreated` is recorded and dispatched after successful registration.
- Repository save/get/update/find/isolation behavior passes the shared contract suite.
- Ruff, formatting, Pyright strict, architecture tests, and Pytest are green.
- 31 tests pass with 99.34% total coverage on PR validation CI #24.

### Deferred

- Supplier relationships move to `0.1.0a3`.
- Relationship lifecycle remains `0.1.0a4`.
- Onboarding, qualification, database persistence, and query projections remain out of scope.


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
