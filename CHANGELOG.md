# Changelog

All notable changes to PySRMKit will be documented in this file.

## Unreleased

## 0.2.0a3 - 2026-10-27

### Added

- SQLAlchemy persistence records for SupplierOnboarding and owned requirements.
- SQLAlchemy persistence records for SupplierAssessment, question snapshots, and answers.
- Explicit Onboarding and Assessment Domain ↔ persistence mappers.
- SqlAlchemySupplierOnboardingRepository and SqlAlchemySupplierAssessmentRepository.
- Portable UTCDateTime SQLAlchemy type preserving timezone-aware UTC semantics across SQLite and PostgreSQL.
- SQLite and PostgreSQL execution of existing Onboarding and Assessment Repository Contracts.
- Explicit persistence ordering for owned requirements, questions, and answers.
- SQLite relational constraint tests for Relationship FKs, one Onboarding per Relationship, and Answer → Question integrity.

### Qualified

- Existing Domain and Repository Port APIs remain unchanged.
- Onboarding requirement satisfaction and completion state survive SQL round trips.
- Assessment questions, answers, score, decision, and completion state survive SQL round trips.
- Reconstitution creates no historical Domain Events.
- SQLite restores business timestamps as timezone-aware UTC datetimes.
- PostgreSQL 18 executes the same Onboarding and Assessment repository contracts.
- Quality CI: 213 passed, 29 PostgreSQL-marked tests skipped, 98.49% coverage.
- PostgreSQL CI: 29 selected tests passed against PostgreSQL 18.6.

### Refined

- Onboarding and Assessment shared contracts gained no-op preparation hooks so relational adapters can prepare required Relationship parents without teaching child repositories to create parent Aggregates.
- PostgreSQL exposed that a composite Answer → Question FK alone did not give SQLAlchemy enough object-level ordering information. The persistence model now uses a technical question_id FK and explicit ORM relationship while the Domain remains question-code based.
- SQLite UTC persistence required an explicit UTCDateTime adapter type because SQLite does not preserve timezone information natively.

### Deferred

- Qualification SQL persistence remains in 0.2.0a4.
- UnitOfWork and post-commit event dispatch remain in 0.2.0a5.
- Alembic migration history remains deferred.
- Async persistence remains deferred.


## 0.2.0a2 - 2026-10-27

### Added

- SQLAlchemy `SupplierRecord` persistence model.
- Owned `supplier_external_identifiers` persistence table.
- SQLAlchemy `SupplierRelationshipRecord` persistence model.
- Explicit Supplier Domain ↔ persistence mappers.
- Explicit SupplierRelationship Domain ↔ persistence mappers.
- `SqlAlchemySupplierRepository`.
- `SqlAlchemySupplierRelationshipRepository`.
- SQLite execution of the existing Supplier Repository Contract.
- SQLite execution of the existing SupplierRelationship Repository Contract.
- Real PostgreSQL execution of the same Repository Contracts.
- Optional `postgresql` extra using Psycopg 3.
- Dedicated PostgreSQL 18 GitHub Actions service/job.
- Supplier → Relationship foreign-key constraint.
- Supplier + organization relationship uniqueness constraint.
- External identifier identity uniqueness constraint.
- Repository test proving `save()` does not commit the Session.

### Qualified

- Domain and Application layers remain unchanged and SQLAlchemy-free.
- Existing Repository Ports remain unchanged.
- Supplier identity, optional identity fields, country, external identifiers, source system, and jurisdiction round-trip through explicit mappers.
- SupplierRelationship identity, organization context, Supplier reference, and lifecycle stage round-trip through explicit mappers.
- The same SQLAlchemy repository classes pass shared contracts on SQLite and PostgreSQL.
- SQLite enforces Supplier FK, relationship uniqueness, and external-identifier uniqueness.
- Relationship Repository contract keeps FK setup outside repository behavior through a test-harness preparation hook.
- Repositories stage SQLAlchemy state but never commit.
- Persistence metadata contains exactly the implemented Supplier/Relationship tables.
- Ruff, Ruff format, Pyright strict, architecture tests, and Pytest are green.
- Quality CI #79: 191 passed, 15 PostgreSQL-marked tests skipped, 99.19% coverage.
- PostgreSQL CI #79: 15 PostgreSQL Repository Contract tests passed against PostgreSQL 18.

### Refined

- The `0.2.0a1` metadata test evolved from 'metadata must be empty' to 'metadata must contain exactly implemented tables'.
- The shared Relationship Repository Contract gained a no-op preparation hook so SQL adapters can satisfy an external Supplier FK without teaching the repository to create Suppliers implicitly.
- The original SQLite-only intermediate qualification was extended before merge to honor the persistence architecture requirement for first PostgreSQL contracts in `0.2.0a2`.

### Deferred

- Onboarding and Assessment SQL persistence remain in `0.2.0a3`.
- Qualification SQL persistence remains in `0.2.0a4`.
- UnitOfWork remains deferred until the first SQL-backed multi-repository atomic use case.
- Alembic migration history remains deferred.
- Async persistence remains deferred.


## 0.2.0a1 - 2026-10-27

### Added

- Optional `persistence` extra targeting SQLAlchemy `2.1.x`.
- `pysrmkit.adapters.sqlalchemy` persistence adapter package.
- `PersistenceBase` SQLAlchemy declarative metadata boundary.
- `create_persistence_engine(...)` Engine factory owned by infrastructure.
- Explicit SQLite `PRAGMA foreign_keys = ON` configuration on every SQLAlchemy connection.
- `create_session_factory(...)` with externally owned Engine.
- Architecture tests preventing SQLAlchemy, Alembic, and Psycopg imports in Domain, Application, and Ports.
- SQLite relational smoke tests for connectivity, Session binding, and foreign-key enforcement.
- Package version `0.2.0a1`.

### Qualified

- Importing the package still creates no Engine or database connection.
- SQLAlchemy exists only below the Adapter boundary.
- Domain remains persistence-ignorant.
- Application remains persistence-ignorant.
- Repository Ports remain persistence-framework agnostic.
- SQLite foreign keys are enabled explicitly and proven by a failing invalid insert.
- Session creation is explicit and uses an externally created Engine.
- Persistence metadata begins with no speculative business tables.
- Existing first-Core behavior remains unchanged.
- Ruff, Ruff format, Pyright strict, architecture tests, and Pytest are green.
- 170 tests pass with 99.12% total coverage on PR validation CI #72.

### Deferred

- No Supplier or SupplierRelationship SQLAlchemy persistence model yet.
- No SQL-backed Repository implementation yet.
- No UnitOfWork yet.
- No Alembic migration files yet.
- No PostgreSQL runtime/driver dependency yet.
- No AsyncSession or async persistence model.
- No DI container.

### Implementation feedback

- The first CI run exposed only an unused local variable in the SQLite foreign-key test; no persistence-design correction was required.


## 0.1.0a8 - 2026-10-27

### Added

- Executable `examples/local_qualification.py` local composition root.
- Manual assembly of Supplier, Relationship, Onboarding, Assessment, and Qualification InMemory repositories.
- Manual assembly of `FixedClock`, `InProcessDomainEventDispatcher`, `QualificationPolicy`, and Application Handlers.
- End-to-end success scenario producing `QUALIFIED`.
- End-to-end rejection scenario producing `NOT_QUALIFIED` and `SupplierQualificationRejected`.
- Exact Domain Event trace assertions across the whole first business journey.
- Entry-point test proving the example's pedagogical console trace and final result output.

### Qualified

- Supplier registration works inside the complete vertical slice.
- Relationship creation, invitation, and onboarding start remain relationship-scoped.
- Mandatory onboarding readiness is satisfied and onboarding completion is explicit.
- Assessment answers are recorded and Assessment completion provides qualification facts.
- Qualification request preserves explicit Relationship + Scope semantics.
- Qualification evaluation delegates to `QualificationPolicy` and persists the explainable Decision.
- Success produces `SupplierQualified`; insufficient evidence produces `SupplierQualificationRejected`.
- Relationship lifecycle remains independently `ONBOARDING` after Qualification evaluation.
- No network, database, framework runtime, broker, or external service is required.
- Package import remains side-effect free.
- All unit, application, contract, architecture, and scenario tests are green.
- Ruff, formatting, Pyright strict, and Pytest are green.
- 165 tests pass with 99.17% total coverage on PR validation CI #62.

### Refined

- The `0.1.0a8` roadmap sequence now explicitly includes `SatisfyOnboardingRequirement`, `CompleteSupplierOnboarding`, and `RecordAssessmentAnswer` because implementation made those prerequisites real.
- The reference event trace now includes `SupplierOnboardingCompleted`.
- `0.1.0a7` final `main` qualification evidence is recorded from CI #56.

### Deferred / Post-Core

- No next capability is preselected after the first local Core cycle.
- A common Aggregate event-recording abstraction is now a legitimate refactoring candidate because event recording is repeated across multiple Aggregates, but it is not introduced inside the final qualification milestone.
- UnitOfWork remains deferred until a persistence adapter can provide a real transaction boundary.
- Relationship lifecycle advancement after a Qualification decision remains a separate future use case.
- PostgreSQL, ORM, HTTP API, external connectors, broker, workflow engine, and deployment concerns remain outside the first Core.


## 0.1.0a7 - 2026-10-27

### Added

- Minimal relationship-scoped `SupplierAssessment` Aggregate Root.
- `AssessmentId`, `AssessmentType`, `AssessmentQuestion`, `AssessmentAnswer`, `AssessmentScore`, and `AssessmentDecision` domain types.
- Mandatory-answer completion guards and assessment immutability after completion.
- Deterministic percentage scoring for the first local qualification scenario.
- `SupplierAssessmentCompleted` Domain Event.
- `SupplierAssessmentRepository` and `InMemorySupplierAssessmentRepository`.
- `CreateSupplierAssessment`, `RecordAssessmentAnswer`, and `CompleteSupplierAssessment` application flows.
- `RequestSupplierQualification` and `EvaluateSupplierQualification` application flows.
- `RequestSupplierQualificationHandler` cross-instance uniqueness check for Relationship + Scope.
- `EvaluateSupplierQualificationHandler` fact collection from Onboarding + Assessment.
- Explicit delegation from the Evaluate Handler to `QualificationPolicy`.
- `InProcessDomainEventDispatcher` for synchronous local event dispatch.
- Cross-capability boundary tests proving Application-level coordination.

### Qualified

- Assessment questions are immutable snapshots inside one assessment execution.
- Answers must reference known questions and remain inside each question scoring range.
- Mandatory questions must be answered before Assessment completion.
- Completed Assessments are immutable by default.
- Assessment score is persisted and rehydrated without recreating historical events.
- Qualification requests require an existing Relationship.
- Duplicate current Qualification for the same Relationship + Scope is rejected.
- Evaluate Handler explicitly invokes the injected QualificationPolicy.
- Application code does not duplicate the minimum-score rule.
- Policy decisions are applied through `SupplierQualification.apply_decision(...)`.
- Qualified and rejected Domain Events are dispatched through the Application layer.
- Qualification evaluation does not mutate Relationship lifecycle state.
- Completing an Assessment does not directly create or mutate Qualification.
- `FixedClock` controls request, assessment-completion, and qualification-decision timestamps in tests.
- Ruff, formatting, Pyright strict, architecture tests, and Pytest are green.
- 162 tests pass with 99.17% total coverage on PR validation CI #54.

### Deferred

- UnitOfWork remains deferred because each new `a7` command writes one main Aggregate.
- Assessment templates, questionnaire engines, evidence storage, and external providers remain out of scope.
- Automatic event-to-command cascades remain deferred; reactions stay explicit use cases.
- Relationship lifecycle is not automatically advanced by Qualification evaluation.
- The full composition-root scenario remains in `0.1.0a8`.


## 0.1.0a6 - 2026-10-27

### Added

- `QualificationId` and explicit `QualificationScope` Value Objects.
- `QualificationStatus` with the reference statuses `PENDING`, `QUALIFIED`, `NOT_QUALIFIED`, `REVOKED`, and `EXPIRED`.
- Explainable `QualificationDecision` Domain Result.
- `QualificationContext` containing pre-collected onboarding and assessment facts.
- Concrete deterministic `QualificationPolicy` with configurable minimum assessment score.
- `SupplierQualification` Aggregate Root with request and apply-decision behavior.
- `SupplierQualificationRequested`, `SupplierQualified`, and `SupplierQualificationRejected` Domain Events.
- `SupplierQualificationRepository` Protocol and `InMemorySupplierQualificationRepository`.
- Shared qualification repository contract tests.

### Qualified

- Empty Qualification scopes are rejected.
- Organization, category, and country can independently define a meaningful scope.
- Qualifications start in `PENDING`.
- Approved decisions are consistent with `QUALIFIED`.
- Rejected decisions are consistent with `NOT_QUALIFIED` and preserve explanations.
- Policy success and all first-core rejection branches are tested.
- Policy evaluation is deterministic for the same facts and explicit evaluation time.
- Only a current pending Qualification can receive its first decision.
- Qualification success/rejection emits the correct Domain Event.
- Repository lookup isolates Relationship + Scope combinations.
- Updated decision/status survives repository round trip.
- Unsaved Aggregate mutation does not leak into repository state.
- Ruff, formatting, Pyright strict, architecture tests, and Pytest are green.
- 133 tests pass with 99.82% total coverage on PR validation CI #47.

### Deferred

- `RequestSupplierQualification` and `EvaluateSupplierQualification` Application handlers remain in `0.1.0a7`.
- Assessment Aggregate implementation remains in `0.1.0a7`.
- Revocation, expiration, and renewal behaviors are not implemented yet.
- Business-unit, capability, service-type, and financial-limit scope dimensions remain deferred until real use cases require them.
- No database, HTTP API, vendor SDK, or external provider is called from the Policy.


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
