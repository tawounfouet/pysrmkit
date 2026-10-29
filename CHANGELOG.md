# Changelog

All notable changes to PySRMKit are documented here, grouped by implementation cycle and individual alpha milestone. This is an implementation history, not a claim that alpha versions were published to PyPI.

## Cycle overview

| Cycle | Milestones | Focus | Status |
| --- | --- | --- | --- |
| 1 - Local Supplier Core | `0.1.0a1` to `0.1.0a8` | Domain, use cases, InMemory qualification | Completed |
| 2 - Persistent Core | `0.2.0a1` to `0.2.0a7` | SQLAlchemy, transactions, migrations, persistence qualification | Completed |
| 3 - Public API & Runtime Composition | `0.3.0a1` to `0.3.0a6` | Public facade, runtime factories, views, errors, events, consumer qualification | Completed |
| 4 - Industrialisation & Integration Qualification | `0.4.0a1` to `0.4.0a5` | Reproducibility, query contracts, multi-consumer and E2E CI gates | In Progress |

## Cycle 4 - Industrialisation & Integration Qualification

### 0.4.0a2 - Supplier Query API (release candidate - PR #32)

- Added immutable `SearchSuppliersQuery` validation for search text, country, supplier type, sorting and bounded pagination.
- Added a separate optional `SupplierSearchService` read Port, leaving the original listing-only Port unchanged (Interface Segregation).
- Exposed `SuppliersAPI.search()` through the existing facade and `SearchSuppliersHandler`, using immutable `SupplierPageView` projections.
- Implemented filtered Supplier discovery in InMemory and SQLAlchemy (SQLite/PostgreSQL-capable) adapters, counting matches before pagination and sorting by legal name with UUID tie-breaking.
- Wired search handlers into both standard Composition Roots without adding required runtime dependencies.
- Added cross-runtime InMemory/SQLite behavioral and regression tests: partial matching, trading names, literal SQL wildcard characters, country/type filters, total/page semantics, stability, read-only events, and preservation of `list()`.
- Documented public API and limitations in README and ADR. Unicode/accent collation equivalence and the full PostgreSQL search contract suite remain scoped to `0.4.0a3`.
- Qualification status: **pending latest PR CI, merge, and post-merge main verification**. This entry is not proof of publication on PyPI.

### 0.4.0a1 - Integration Reproducibility
- Automated idempotent PostgreSQL database provisioning (`pysrmkit` and `next_dashboard`) via `examples/bootstrap_integration.py`.
- Automated Alembic schema migrations and idempotent seeding of 8 demonstration suppliers into PySRMKit.
- Implemented reproducible Stack Runner (`examples/run_stack.py`) orchestrating FastAPI (port 8000) and Next.js (port 3000) with healthcheck polling and graceful SIGINT cleanup.
- Added automated end-to-end browser qualification test with Playwright (`tests/test_browser_journey.py`) verifying login, 8 suppliers listing, debounced search filtering, and reload.
- Added comprehensive `integration` workflow in `.github/workflows/ci.yml` qualifying PostgreSQL, Next.js build, and E2E browser tests from a clean Ubuntu environment.
- Documented environment variables in `.env.example` across PySRMKit and Next.js Dashboard.

## Cycle 3 - Public API & Runtime Composition (completed 2026-10-27)

### 0.3.0a6 - Public Runtime Qualification
- Added public-only consumer journey exercising Supplier registration, Relationship invitation, Onboarding completion, Assessment completion and scoped Qualification.
- Qualified success (`90 -> QUALIFIED`) and rejection (`60 -> NOT_QUALIFIED`, `ASSESSMENT_MINIMUM_SCORE`) using InMemory, SQLite and PostgreSQL runtimes.
- Verified immutable public Views, typed qualification events, and SQLite durability across Engine/runtime destruction and recreation.
- Strengthened architecture tests to prevent Domain, Application and Ports from importing Public Runtime.
- Recorded Cycle 3 exit evidence in `docs/cycle-3-public-runtime-qualification.md` (PR #28, CI #188).

### 0.3.0a5 - Public Event Surface
- Exposed typed public Domain Event subscriptions via `srm.events`.
- Published selected Supplier, Relationship, Onboarding, Assessment and Qualification events.
- Ensured SQL event delivery occurs only after successful commit; failed transactions discard pending events.
- Kept event delivery synchronous and in-process; no outbox, replay, broker or durable delivery guarantee (PR #27).

### 0.3.0a4 - Public Views & Error Boundary
- Added consumer-facing immutable read Views instead of leaking Domain Aggregates or ORM records.
- Exposed read operations through capability APIs and mapped persistence failures at the public boundary.
- Kept Domain-specific errors explicit and retained Core independence from persistence infrastructure.

### 0.3.0a3 - SQL Runtime Composition
- Added SQL-backed `PySRMKit.sql(engine)` composition using externally owned SQLAlchemy Engine.
- Introduced operation-scoped Sessions and transaction ownership for ordinary commands while retaining the capability-specific onboarding UnitOfWork.
- Preserved Repository Port semantics: repositories stage changes without committing; composition controls commit/rollback.
- Kept SQLAlchemy optional and schema migration/bootstrap explicit.

### 0.3.0a2 - InMemory Runtime Composition
- Added `PySRMKit.in_memory()` Composition Root wiring shared InMemory repositories, handlers, clock, event dispatcher and qualification policy.
- Preserved one shared runtime lifetime across capability APIs and reused the onboarding UnitOfWork.
- Exercised dependency injection without a container or service locator (PR #24).

### 0.3.0a1 - Public API Foundation
- Introduced `PySRMKit` facade, generic Handler Protocol and five typed capability APIs: Suppliers, Relationships, Onboardings, Assessments and Qualifications.
- Established a small Python-first entry point without an HTTP framework or application-layer business rule duplication (PR #23).

## Cycle 2 - Persistent Core (completed 2026-10-27)

The detailed milestone notes below record the SQL persistence evolution, its design decisions, failures and quality evidence. See also `docs/specifications/17_PYSRMKIT_PERSISTENT_CORE_MILESTONE.md`.

## Cycle 1 - Local Supplier Core (completed 2026-10-27)

The detailed `0.1.0a1` to `0.1.0a8` entries below record the Domain, Application, Repository Contracts, InMemory adapters and complete local Supplier qualification journey.

## 0.2.0a7 - 2026-10-27

### Added

- Executable `examples/persistent_qualification.py` SQL-backed composition root.
- `DeferredDomainEventDispatcher` adapter for buffering in-process Domain Events until the surrounding SQL transaction commits.
- SQLite end-to-end success and rejection restart scenarios.
- PostgreSQL 18 end-to-end success and rejection persistence scenarios.
- Fresh Engine, Session, and Repository reconstruction before final business-state assertions.

### Qualified

- The complete Supplier journey executes through existing Application Handlers and SQLAlchemy Repository adapters.
- Empty databases are bootstrapped through the Alembic `head` migration before business execution.
- Supplier, Relationship, Onboarding, Assessment, and Qualification survive durable commits.
- The original Engine, Session, and repository instances are discarded before verification.
- A fresh persistence context reloads the final `QUALIFIED` state with the same Relationship lifecycle, scope, score, decision, and failed-requirement semantics.
- The `NOT_QUALIFIED` path survives the same restart/reload boundary and preserves `ASSESSMENT_MINIMUM_SCORE`.
- Existing Domain Event trace semantics remain observable without publishing single-repository events before SQL commit.
- Domain, Application, and Repository Ports remain unchanged and persistence-framework agnostic.
- No global UnitOfWork was introduced.
- Final PR CI #144 quality job: 239 passed, 44 PostgreSQL-marked tests skipped, 98.11% coverage.
- Final PR CI #144 PostgreSQL job: 44 selected tests passed against PostgreSQL 18.6.
- Ruff, Ruff format, Pyright strict, architecture gates, migrations, Repository Contracts, UnitOfWork tests, and persistent scenarios are green.

### Refined

- Onboarding Data Mapper updates now reconcile persisted requirement rows by business code instead of recreating technical child rows after each committed update.
- Assessment Data Mapper updates now reconcile persisted question and answer rows by Domain-level question identity instead of replacing committed child rows.
- This preserves hidden SQL technical identities while keeping the Domain free of persistence IDs.
- Single-repository transaction boundaries remain a composition-root responsibility; the existing capability-specific onboarding UnitOfWork remains the only UnitOfWork justified by multi-Aggregate atomicity.
- Deferred event dispatch is explicitly an in-process post-commit mechanism, not a Transactional Outbox.

### Implementation feedback

The persistent scenario exposed a defect that shorter Repository Contract transactions could not reveal:

```text
create Aggregate
    -> save
    -> COMMIT
    -> reload
    -> mutate owned collection
    -> save
    -> COMMIT
```

Recreating every owned persistence child produced duplicate unique keys on PostgreSQL. The correct Data Mapper behavior is to reconcile persistence rows using the Domain's stable owned-object identity while keeping technical database identifiers outside the Domain model.

### Deferred / Post-Persistent-Core

- No Transactional Outbox; a process crash after database commit but before in-process publication remains a future reliability concern.
- No async SQLAlchemy / AsyncSession path.
- No generic/global UnitOfWork.
- No automatic transaction retries, savepoints, or distributed transactions.
- No API framework, broker, cache, or external SRM connector is introduced by this cycle.
- No next implementation capability is preselected before a post-persistence architecture review.

## 0.2.0a6 - 2026-10-27

### Added

- Optional `migrations` extra with Alembic 1.20.x.
- Adapter-owned Alembic configuration, migration environment, and revision template.
- Deterministic SQLAlchemy naming convention for primary keys, foreign keys, unique constraints, checks, and indexes.
- Explicit persistence metadata loader that registers the complete SQLAlchemy persistence model.
- Initial versioned migration for the 11-table Persistent Core relational schema.
- SQLite migration tests proving empty database → `upgrade head` and downgrade/re-upgrade replay.
- PostgreSQL 18 migration qualification from an empty database.
- Structural cross-checks between migrated schema and SQLAlchemy persistence metadata.

### Qualified

- An empty SQLite file database migrates reproducibly to the complete Persistent Core schema.
- The SQLite baseline can downgrade to `base` and replay to `head`.
- An empty PostgreSQL 18.6 database migrates reproducibly to the same logical Persistent Core schema.
- Re-running `alembic upgrade head` on the current PostgreSQL schema is safe.
- Existing Repository Contracts and UnitOfWork transaction semantics remain green.
- Domain, Application, and Repository Ports remain free from SQLAlchemy, Alembic, and Psycopg dependencies.
- Core consumers still have zero mandatory third-party runtime dependencies.
- Final PR CI #131 quality job: 235 passed, 42 PostgreSQL-marked tests skipped, 97.74% coverage.
- Final PR CI #131 PostgreSQL job: 42 selected tests passed against PostgreSQL 18.6.
- Ruff, Ruff format, Pyright strict, architecture gates, and full regression suite are green.

### Refined

- Foreign-key naming was shortened from `fk_<table>_<column>_<referred_table>` to `fk_<table>_<column>` after PostgreSQL exposed its 63-character identifier limit.
- Migration qualification distinguishes logical unique constraints from PostgreSQL physical backing indexes instead of requiring dialect-identical index reflection.
- `metadata.create_all()` remains valid in focused repository behavior tests; Alembic now owns schema-history/bootstrap qualification.

### Deferred

- Persistent end-to-end qualification and runtime/context reload remain in `0.2.0a7`.
- No post-baseline data migration strategy is introduced yet.
- No async migration/runtime path.
- No Transactional Outbox.

## 0.2.0a5 - 2026-10-27

### Added

- `SupplierOnboardingUnitOfWork` transaction Port.
- `InMemorySupplierOnboardingUnitOfWork` with real snapshot/restore rollback semantics.
- `SqlAlchemySupplierOnboardingUnitOfWork` owning one Session shared by Relationship and Onboarding repositories.
- Transactional `StartSupplierOnboardingHandler`.
- SQLite commit/rollback integration tests.
- PostgreSQL commit/rollback integration tests.
- Post-commit Domain Event dispatch behavior.

### Qualified

- Relationship + Onboarding commit atomically on success.
- A forced commit failure rolls both Aggregates back.
- A failed commit dispatches no `SupplierOnboardingStarted` event.
- InMemory and SQLAlchemy UnitOfWork implementations satisfy the same application-facing contract.
- Repositories remain non-committing.
- UnitOfWork remains persistence-agnostic at the Port boundary.
- Quality CI #113: 233 passed, 41 PostgreSQL-marked tests skipped, 97.73% coverage.
- PostgreSQL CI #113: 41 selected tests passed against PostgreSQL 18.6.

### Refined

- InMemory rollback snapshots are expressed as Domain state rather than private repository storage types.
- `StartSupplierOnboardingHandler` now depends on a capability-specific UnitOfWork instead of two independently supplied repositories.
- Domain Events are pulled before commit but dispatched only after commit succeeds.

### Deferred

- No global UnitOfWork across all capabilities.
- No nested transactions or savepoints.
- No automatic transaction retries.
- No Transactional Outbox.
- Alembic migration history remains in `0.2.0a6`.


## 0.2.0a4 - 2026-10-27

### Added

- SQLAlchemy persistence records for SupplierQualification.
- Owned persistence rows for ordered QualificationDecision reasons.
- Owned persistence rows for ordered failed requirements.
- Explicit SupplierQualification Domain ↔ persistence mapper.
- SqlAlchemySupplierQualificationRepository.
- SQLite execution of the existing SupplierQualification Repository Contract.
- PostgreSQL execution of the same SupplierQualification Repository Contract.
- Qualification → SupplierRelationship foreign-key constraint.
- Database check constraint preventing an empty Qualification scope.
- Database check constraint requiring persisted QualificationDecision columns to be all-present or all-absent.
- Portable partial unique index enforcing one current Qualification per Relationship + normalized Scope.
- SQLite/PostgreSQL tests proving expired history can coexist with a new current Qualification.
- SQLite test proving requested/decision timestamps and explainable decision collections survive SQL round trip.

### Qualified

- Existing Domain and Repository Port APIs remain unchanged.
- QualificationId, RelationshipId, scope dimensions, requested timestamp, status and decision survive SQL round trips.
- Explainable reasons and failed requirements preserve ordering.
- Reconstitution emits no historical Domain Events.
- Optional scope dimensions remain `None` in the Domain even though persistence uses normalized non-null strings.
- `find_current_for_scope(...)` preserves the Domain definition of currentness: statuses other than REVOKED/EXPIRED.
- SQLite enforces non-empty scope, Relationship FK, decision completeness and current-scope uniqueness.
- PostgreSQL 18 executes the same Qualification Repository Contract and current-scope uniqueness behavior.
- One SQLAlchemy Qualification repository implementation serves SQLite and PostgreSQL.
- Quality CI #100: 229 passed, 39 PostgreSQL-marked tests skipped, 98.49% coverage.
- PostgreSQL CI #100: 39 selected tests passed against PostgreSQL 18.6.

### Refined

- Qualification Repository Contract gained a no-op preparation hook so SQL adapters can prepare the required Relationship parent without teaching the repository to create Relationships.
- Optional scope dimensions are normalized to empty persistence strings so uniqueness semantics do not depend on database NULL behavior; mappers restore `None` at the Domain boundary.
- Current-scope uniqueness is represented by a partial unique index excluding REVOKED and EXPIRED rows, matching `SupplierQualification.is_current`.
- PostgreSQL CI now uses ephemeral container-local trust authentication instead of a hardcoded test password.
- PostgreSQL Qualification constraint tests use a unique module basename to avoid Pytest import-file collisions.

### Deferred

- Transaction Boundary / UnitOfWork and post-commit Domain Event dispatch remain in 0.2.0a5.
- Alembic migration history remains deferred to 0.2.0a6.
- Persistent end-to-end qualification remains deferred to 0.2.0a7.
- Async persistence remains deferred.


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
