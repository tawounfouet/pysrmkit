# PySRMKit - Persistence Architecture

**Document:** `16_PYSRMKIT_PERSISTENCE_ARCHITECTURE.md`  
**Status:** ITERATIVE DEEP DIVE / CYCLE 2 BASELINE  
**Target cycle:** `0.2.x - Persistent Core`  
**Predecessor:** `15_PYSRMKIT_POST_CORE_ARCHITECTURE_REVIEW.md`  
**Date:** 2026-10-27

---

# 1. Purpose

This document defines the minimum persistence architecture required to begin the second PySRMKit implementation cycle.

It exists because the first local Core exposed a concrete limitation:

```text
process stops
    ->
all InMemory state disappears
```

The architectural question is now:

> **Can the same Domain and Application model survive real relational persistence without leaking infrastructure concerns inward?**

This document is intentionally narrower than the pre-implementation baseline.

It specifies only the persistence decisions that are now timely.

---

# 2. Problem statement

The qualified `0.1.x` Core already proves:

```text
Domain model
Application handlers
Repository Ports
InMemory adapters
Domain Events
Qualification Policy
Contract tests
Architecture tests
End-to-end local scenario
```

What it does not prove is:

```text
durable state
relational mapping
database constraints
database transactions
schema evolution
adapter substitution against SQL
transaction-safe event dispatch ordering
restart / reload persistence
```

The persistence cycle must validate these concerns without contaminating the Domain.

---

# 3. Persistence north star

```text
DOMAIN
    remains persistence ignorant
        |
        v
APPLICATION
    depends on Repository Ports
        |
        v
PORTS
    expose Aggregate persistence needs
        ^
        |
SQLALCHEMY ADAPTER
        |
        +--> SQLite
        |
        +--> PostgreSQL
```

The Core must continue to execute against InMemory adapters.

Persistence is an additional adapter family, not a replacement for the architecture.

---

# 4. Governing principles

The persistence architecture follows:

```text
Problem Before Pattern
Dependency Inversion
Separation of Concerns
Information Hiding
Liskov Substitution
KISS
YAGNI
Explicit transaction boundaries
Contract-first adapters
```

Persistence technology belongs outside the Domain.

---

# 5. Non-goals

The persistence cycle does not automatically introduce:

```text
FastAPI
GraphQL
Kafka
RabbitMQ
Redis
Celery
Transactional Outbox
Event Sourcing
cloud deployment
generic DAO framework
generic repository framework
DI container
async application runtime
```

These concerns remain deferred until separate pressure appears.

---

# 6. Ecosystem checkpoint - 2026-10-27

The architecture targets the modern SQLAlchemy stack rather than legacy APIs.

Current external reference state at the time of this document:

```text
SQLAlchemy 2.1.x    current major/minor family
Alembic 1.20.x     current migration tool family
Psycopg 3          current PostgreSQL Python adapter generation
PostgreSQL 18      current PostgreSQL release family
SQLite             standard-library-accessible local relational backend
```

Exact patch versions are implementation/release concerns rather than architectural commitments.

Reference documentation:

- https://docs.sqlalchemy.org/en/21/
- https://alembic.sqlalchemy.org/en/latest/
- https://www.psycopg.org/psycopg3/docs/
- https://www.postgresql.org/docs/current/
- https://www.sqlite.org/docs.html

---

# 7. SQLAlchemy decision

**Decision:** use SQLAlchemy as the relational persistence toolkit for Cycle 2.

Reasons:

```text
mature dialect abstraction
typed modern Python API
Session / transaction model
SQLite support
PostgreSQL support
migration ecosystem via Alembic
clear separation between Core and persistence adapter
```

The Domain must not import SQLAlchemy.

The Application Layer must not import SQLAlchemy.

The Repository Ports must not import SQLAlchemy.

Only persistence adapters and persistence-specific tests may depend on it.

---

# 8. Sync-first decision

The existing Application Layer is synchronous.

Therefore the first persistence implementation uses:

```text
SQLAlchemy Session
not AsyncSession

Psycopg sync driver
not async driver usage
```

Async persistence would currently add two execution models without solving a demonstrated problem.

**Decision:** synchronous persistence first. Async remains deferred.

---

# 9. Persistence model vs Domain model

**Decision:** keep Domain Aggregates persistence ignorant and separate from SQLAlchemy persistence records.

Preferred shape:

```text
Domain Aggregate
        ^
        | reconstruct / extract
        |
Mapper
        |
        v
SQLAlchemy persistence record
        |
        v
Database row(s)
```

Rejected initial shape:

```text
@mapped
class Supplier(DomainAggregate):
    ...
```

Why rejected:

- SQLAlchemy instrumentation would enter the Domain model;
- persistence concerns would affect dataclass design;
- lazy-loading semantics could leak into business behavior;
- Domain tests would become persistence-aware;
- the existing architecture fitness rules would be weakened.

This is a Data Mapper style boundary.

---

# 10. SQLAlchemy mapping style

Persistence records should use modern SQLAlchemy typed declarative mapping:

```text
DeclarativeBase
Mapped[...]
mapped_column(...)
relationship(...) only inside persistence models
```

Domain classes remain ordinary Python classes/dataclasses.

Mapping functions should be explicit enough to make conversion semantics visible.

Example conceptual direction:

```text
SupplierRecord
    -> supplier_id
    -> legal_name
    -> trading_name
    -> country_code

SupplierExternalIdentifierRecord
    -> supplier_id FK
    -> kind
    -> value
    -> source_system
```

---

# 11. Adapter package topology

Recommended first topology:

```text
src/pysrmkit/adapters/sqlalchemy/
├── __init__.py
├── metadata.py
├── session.py
├── types.py
├── models/
│   ├── supplier.py
│   ├── relationship.py
│   ├── onboarding.py
│   ├── assessment.py
│   └── qualification.py
├── mappers/
│   ├── supplier.py
│   ├── relationship.py
│   ├── onboarding.py
│   ├── assessment.py
│   └── qualification.py
└── repositories/
    ├── supplier.py
    ├── relationship.py
    ├── onboarding.py
    ├── assessment.py
    └── qualification.py
```

`unit_of_work.py` is added only when the UnitOfWork decision becomes executable.

Do not create separate top-level `sqlite/` and `postgresql/` repository packages unless real dialect divergence appears.

---

# 12. One SQLAlchemy repository family

First hypothesis:

```text
SupplierRepository Port
        ^
        |
SqlAlchemySupplierRepository
        |
        +--> SQLite Engine
        +--> PostgreSQL Engine
```

not:

```text
SQLiteSupplierRepository
PostgreSQLSupplierRepository
```

The repository implementation should vary only when behavior actually differs.

Dialect-specific configuration may exist below the repository layer.

---

# 13. SQLite role

SQLite is an officially useful backend for Cycle 2, but with a limited role.

SQLite provides:

```text
fast relational Repository Contract tests
local persistence
mapping validation
foreign-key validation
transaction experiments
schema bootstrapping
file-backed restart / reload scenario
```

SQLite is **not** considered evidence that PostgreSQL-specific behavior is correct.

---

# 14. SQLite operating modes

Two modes are useful:

## 14.1 In-memory SQLite

```text
sqlite:///:memory:
```

Use for:

```text
fast repository contracts
mapper tests
adapter behavior tests
```

## 14.2 Temporary file SQLite

Use for:

```text
process/repository recreation
persistent restart scenario
schema migration experiments
```

File-backed SQLite proves durability in a way that `:memory:` cannot.

---

# 15. SQLite foreign keys

SQLite foreign-key enforcement must be enabled explicitly for every connection.

Required adapter behavior:

```text
PRAGMA foreign_keys = ON
```

This configuration belongs to the SQLite engine setup, not to repositories or Domain code.

Tests must fail if relational constraints are accidentally disabled.

---

# 16. PostgreSQL role

PostgreSQL is the **reference production-oriented relational backend**.

It validates concerns SQLite cannot fully represent:

```text
real client/server behavior
PostgreSQL transaction semantics
MVCC
concurrent writes
locking
native UUID support
PostgreSQL constraint/index behavior
driver integration
connection pooling behavior
```

The initial CI reference target may use one current PostgreSQL version rather than promising broad version compatibility.

Broad support policy can be defined after the adapter stabilizes.

---

# 17. PostgreSQL driver

**Decision:** Psycopg 3 is the preferred PostgreSQL DBAPI driver.

Rationale:

```text
current generation
modern Python support
static typing support
sync and async capabilities
PostgreSQL-focused feature support
```

The first cycle uses synchronous Psycopg through SQLAlchemy.

---

# 18. Engine ownership

`Engine` creation belongs to the outer persistence/composition boundary.

Repositories must not create Engines themselves.

Conceptual flow:

```text
Composition Root
    -> create Engine
    -> create sessionmaker
    -> create Session / transaction scope
    -> create repositories bound to Session
    -> invoke use case
```

No Engine is created at package import time.

---

# 19. Session ownership

**Decision:** one SQLAlchemy `Session` is scoped to one application transaction/use-case boundary.

Rules:

```text
no global Session
no module-level Session singleton
no Session stored in Domain objects
no Session exposed through Repository Ports
```

Repositories participating in the same use case must share the same Session when atomicity is required.

---

# 20. Repository transaction semantics

Repository methods must not call:

```text
session.commit()
session.rollback()
```

`save()` means:

> stage the current valid Aggregate state in the current persistence context.

Commit/rollback belongs to the transaction boundary above repositories.

This preserves the existing Port semantics and prevents one repository from committing another repository's work.

---

# 21. Flush semantics

Repositories should not rely on implicit commits.

`flush()` may be used only when required to:

```text
materialize a database constraint failure
synchronize pending SQL before a dependent query
obtain database-generated persistence values
```

PySRMKit Domain identifiers are already generated before persistence, so generated primary keys are not a reason to flush.

Default posture:

```text
save
    -> stage state
transaction boundary
    -> flush/commit
```

---

# 22. Domain identifiers

Domain identifiers remain application-generated UUID Value Objects.

The database must not replace them with auto-increment integers as Domain identity.

Recommended SQLAlchemy persistence type:

```text
Uuid(as_uuid=True)
```

This allows native UUID storage where supported and emulation where needed.

Repository mappers reconstruct the existing Domain ID wrappers.

---

# 23. Date/time policy

Domain time remains timezone-aware.

Persistence policy:

```text
normalize business timestamps to UTC
persist through SQLAlchemy datetime/timestamp types
reconstruct timezone-aware UTC datetime values
```

PostgreSQL should use timezone-capable timestamp semantics.

SQLite does not provide equivalent native timezone behavior, so mapper/type handling must preserve the Domain contract explicitly.

Repository contract tests must verify timezone-aware round trips.

---

# 24. Enum policy

Initial persistence should favor portable string representation for Domain `StrEnum` values.

Preferred direction:

```text
Domain Enum
    <-> string column
```

rather than PostgreSQL-native ENUM types in the first cycle.

Reasons:

```text
SQLite portability
simpler migrations
less dialect coupling
easier enum evolution during alpha
```

Database CHECK constraints may be added where they increase integrity without making evolution brittle.

---

# 25. Value Object persistence

Value Objects should be flattened into meaningful relational columns and reconstructed through their constructors.

Example:

```text
QualificationScope
    -> organization_id nullable
    -> category_code nullable
    -> country_code nullable
```

Do not default to opaque JSON blobs for first-Core state.

JSON may be introduced only when the data is genuinely document-shaped or schemaless by business nature.

---

# 26. Aggregate persistence shape

Each Aggregate Root gets one primary table plus child tables only where collection state requires it.

Candidate relational shape:

```text
suppliers
supplier_external_identifiers

supplier_relationships

supplier_onboardings
supplier_onboarding_requirements

supplier_assessments
supplier_assessment_questions
supplier_assessment_answers

supplier_qualifications
```

This is a starting model, not an immutable database contract.

---

# 27. Aggregate loading rule

A Repository must return a Domain Aggregate that is ready to execute its current business behaviors.

Therefore:

```text
Repository.get(...)
    -> load required persistence records
    -> reconstruct full Aggregate state
    -> return Domain Aggregate
```

Domain objects must not contain lazy SQLAlchemy relationships or Session-backed proxies.

Lazy loading must not occur from inside Domain behavior.

---

# 28. Save strategy

Repository `save()` must preserve the current Aggregate snapshot semantics already qualified by the InMemory adapters.

Conceptually:

```text
Domain Aggregate
    -> extract persistence state
    -> insert or update root record
    -> synchronize owned child records
```

Exact implementation may use explicit SELECT/UPDATE/INSERT logic or SQLAlchemy ORM state operations.

The observable contract matters more than the internal mechanism.

---

# 29. Database constraints

Database constraints complement Domain/Application invariants; they do not replace them.

Use database constraints for:

```text
primary keys
foreign keys
non-null structural requirements
cross-row uniqueness
race-condition protection
```

Keep behavioral rules such as lifecycle transitions in the Domain.

---

# 30. Cross-instance uniqueness

Several first-Core rules span Aggregate instances.

Examples:

```text
Supplier external identifier uniqueness
Supplier + organization Relationship uniqueness
current Qualification uniqueness for Relationship + Scope
```

Application pre-checks remain useful for clear errors.

Relational constraints must also protect these invariants against concurrent writers.

The persistence implementation must define constraint-to-application error translation without leaking raw SQLAlchemy/DBAPI exceptions through Core-facing APIs.

Exact exception taxonomy is deferred until the first real constraint failure is implemented.

---

# 31. Qualification current-scope uniqueness

`find_current_for_scope(...)` currently defines currentness through Domain status.

A persistent adapter must preserve the semantic rule:

```text
one current Qualification
per
Relationship + QualificationScope
```

Possible relational enforcement includes a partial unique index where supported.

SQLite and PostgreSQL both need contract/integration evidence before this design is frozen.

Do not weaken the Domain semantics merely to avoid a dialect-specific index detail.

---

# 32. Delete semantics

The current Repository Ports expose no general delete operation.

Therefore the persistence architecture does not invent one.

No hard-delete, soft-delete, cascade-delete, or archival policy is introduced until a real use case requires deletion or retention behavior.

---

# 33. Audit columns

Do not automatically add generic:

```text
created_at
updated_at
deleted_at
created_by
updated_by
```

to every table.

Persist Domain timestamps that already exist.

Technical audit metadata may be introduced later when an audit/compliance requirement appears.

---

# 34. Transaction boundary

**Decision:** one command/use-case execution is the default transaction boundary.

Conceptually:

```text
begin transaction
    -> load Aggregates
    -> execute Domain behavior
    -> save affected Aggregates
    -> commit
    -> dispatch in-process Domain Events
```

If any operation fails before commit:

```text
rollback
no post-commit event dispatch
```

---

# 35. Why transaction pressure is now real

`StartSupplierOnboardingHandler` already persists two Aggregate Roots:

```text
SupplierRelationship
+
SupplierOnboarding
```

InMemory repositories could not provide meaningful atomicity.

With SQL persistence, partial success is no longer acceptable.

Example invalid outcome:

```text
Relationship committed as ONBOARDING
but
SupplierOnboarding insert failed
```

Cycle 2 must prevent this.

---

# 36. UnitOfWork trigger

UnitOfWork is now a **legitimate candidate**, but its exact API should emerge from the first SQL-backed multi-repository use case.

Trigger condition:

> **The first persistent use case that must atomically coordinate more than one Repository requires an Application-visible transaction abstraction that does not expose SQLAlchemy.**

The likely trigger is `StartSupplierOnboarding`.

Required guarantees if UnitOfWork is introduced:

```text
explicit transaction scope
shared persistence context
commit
rollback
repositories participate in the same transaction
no SQLAlchemy types leak inward
```

Do not introduce nested transactions, savepoints, or distributed transactions unless separately justified.

---

# 37. UnitOfWork API - intentionally not frozen yet

Possible shapes include:

```text
A. UnitOfWork owns repositories
B. UnitOfWork owns only transaction boundary while repositories share context
C. application transaction runner wraps existing handlers
```

This document does not choose the final surface before the SQL adapter exists.

The invariant is fixed; the API remains iterative.

---

# 38. Domain Event dispatch ordering

Persistence exposes a real ordering issue that InMemory execution could ignore.

Current local handlers can dispatch events immediately after `save()` because there is no later database commit.

With SQL persistence:

```text
save
    !=
commit
```

Therefore the required ordering becomes:

```text
Domain behavior
    -> record event

Repository save
    -> stage persistence

COMMIT SUCCESS
    -> persistence is durable

THEN
    -> dispatch in-process Domain Events
```

If commit fails, events must not be dispatched as successful business facts.

This is a required Cycle 2 refactoring pressure.

---

# 39. Outbox decision

A Transactional Outbox is still deferred.

Why:

```text
current dispatcher = in-process
no external broker
no durable integration event delivery requirement
```

If later:

```text
database commit
+
external event publication
```

must be made reliable together, an Outbox deep dive becomes justified.

---

# 40. Concurrency policy

Cycle 2 introduces real concurrent-write possibility through PostgreSQL.

Initial posture:

```text
database uniqueness constraints
+
transaction boundaries
+
application preconditions
```

Optimistic locking/version columns are **not** introduced automatically.

They become justified when concurrent updates to the same Aggregate create demonstrated lost-update pressure.

Qualification double-evaluation and lifecycle concurrent transitions should be observed explicitly in integration tests before a versioning mechanism is selected.

---

# 41. Isolation level

Do not select SERIALIZABLE globally by default.

Initial PostgreSQL persistence should begin with normal database defaults and explicit constraints.

Escalate isolation only when a specific invariant cannot be protected adequately by:

```text
constraints
locking
atomic transaction design
retry on serialization/conflict
```

Isolation level is a use-case property, not a badge of correctness.

---

# 42. Connection pooling

Use SQLAlchemy Engine pooling behavior before inventing a PySRMKit connection-pool abstraction.

SQLite and PostgreSQL may require different adapter configuration.

No pool tuning milestone exists until measurements or deployment constraints justify it.

---

# 43. Configuration

Database configuration belongs to the composition/runtime boundary.

Candidate inputs:

```text
DATABASE_URL
engine options
echo/logging option for development
test database URL
```

Rules:

```text
Domain does not read environment variables
Application does not construct Engines
imports do not connect to databases
credentials never appear in logs
```

---

# 44. Dependency packaging

The base PySRMKit package should remain lightweight.

Persistence dependencies should be optional extras rather than mandatory dependencies for users who only need the pure Core.

Candidate direction:

```text
pysrmkit
    -> zero mandatory third-party runtime dependencies

pysrmkit[persistence]
    -> SQLAlchemy

pysrmkit[postgresql]
    -> SQLAlchemy + Psycopg 3
```

Alembic belongs to persistence development/deployment tooling rather than Domain runtime semantics.

Exact extra names and version ranges are implementation details to finalize in the first persistence milestone.

---

# 45. Migration strategy

**Decision:** use Alembic once the first persistent schema is introduced.

Roles:

```text
development schema evolution
repeatable database bootstrap
upgrade history
production-oriented migration path
```

For ephemeral adapter contract tests, `metadata.create_all()` may still be used when testing repository behavior rather than migration history.

Migration correctness needs separate tests.

---

# 46. Migration rules

Each schema change should provide:

```text
forward migration
deterministic upgrade path
reviewed generated SQL
compatibility with target backend policy
```

Automatic Alembic generation is a starting point, not an unquestioned source of truth.

Downgrade support is desirable during alpha but is not automatically a production rollback strategy.

---

# 47. SQLite migration posture

SQLite has DDL limitations compared with PostgreSQL.

Do not distort the production schema design merely to make every migration identical.

When Alembic requires SQLite-specific batch operations, keep them in persistence/migration concerns.

Repository behavior, not identical DDL, is the cross-dialect contract.

---

# 48. PostgreSQL migration posture

PostgreSQL migration tests are the reference for production-oriented schema evolution.

Migration validation should eventually prove:

```text
empty database -> head
previous released schema -> head
application repository contracts -> green after migration
```

---

# 49. Testing layers

Cycle 2 adds persistence tests without moving Domain tests to a database.

Target structure:

```text
tests/
├── unit/
├── application/
├── contracts/repositories/
├── architecture/
├── scenarios/
└── integration/
    ├── sqlite/
    └── postgresql/
```

Domain/Application tests remain fast and database-free.

---

# 50. Repository Contract reuse

Every SQLAlchemy repository must satisfy the same shared behavioral contract already used by InMemory adapters.

Example:

```text
SupplierRepositoryContract
        |
        +--> InMemorySupplierRepository
        +--> SqlAlchemySupplierRepository + SQLite
        +--> SqlAlchemySupplierRepository + PostgreSQL
```

This makes Liskov Substitution executable across persistence technologies.

---

# 51. SQLite test gate

SQLite repository contracts should be fast enough to run in the normal developer test suite.

Expected gate:

```text
python -m pytest
    -> pure tests
    -> InMemory contracts
    -> SQLite contracts
```

unless runtime cost proves significant.

---

# 52. PostgreSQL integration gate

PostgreSQL tests should be separated explicitly.

Candidate marker/job:

```text
pytest -m postgresql
```

CI can provide a PostgreSQL service container.

Local developers may point tests to an explicit test database URL.

Do not require Testcontainers as the first solution unless it materially improves lifecycle management.

---

# 53. PostgreSQL test database safety

Integration tests must never accept an arbitrary production-like database silently.

Recommended safeguards:

```text
explicit test URL
database/schema name assertion
isolated credentials
destructive reset allowed only for test target
```

---

# 54. Test isolation

Repository tests require fresh state.

Candidate strategies:

```text
SQLite
    -> fresh Engine/database per test or test class

PostgreSQL
    -> transaction rollback fixture
    -> isolated schema/database for migration tests
```

SQLAlchemy's ability to join Sessions to an external test transaction may be used where it simplifies rollback isolation.

---

# 55. Persistent restart scenario

The persistence cycle exit scenario must prove more than save/reload in one Session.

Required final shape:

```text
empty database
    -> run qualification journey
    -> commit
    -> dispose Session / repositories
    -> create new Session / repositories
    -> reload Supplier
    -> reload Relationship
    -> reload Onboarding
    -> reload Assessment
    -> reload Qualification
    -> business state preserved
```

Run this first against SQLite file persistence and finally against PostgreSQL.

---

# 56. Architecture fitness updates

New architecture tests should enforce:

```text
domain must not import sqlalchemy
domain must not import alembic
domain must not import psycopg

application must not import sqlalchemy
application must not import alembic
application must not import psycopg

ports must not import sqlalchemy
ports must not import alembic
ports must not import psycopg
```

SQLAlchemy imports belong under adapters and persistence tests.

---

# 57. Error translation boundary

Raw infrastructure exceptions such as:

```text
IntegrityError
OperationalError
DBAPIError
```

must not become part of the public Repository Port contract.

The adapter/application boundary must translate failures into stable meanings when the Core needs to react.

Do not design a large persistence exception hierarchy before the first real failure cases appear.

---

# 58. Logging and observability

Persistence instrumentation is useful but remains secondary.

Initial rules:

```text
no credential logging
no raw sensitive supplier data in debug logs by default
SQL echo only opt-in for development
no observability framework dependency yet
```

Production observability remains a later deep dive.

---

# 59. Security posture

Database credentials are runtime configuration.

Never:

```text
hard-code credentials
commit local passwords
log full database URLs with secrets
reuse production credentials in tests
```

TLS, secret management, IAM database authentication, and rotation are deployment concerns to specify when a production runtime exists.

---

# 60. Performance posture

Do not optimize persistence before measuring.

Initial priorities:

```text
correct Aggregate reconstruction
correct transactions
correct constraints
correct contract semantics
```

Avoid accidental N+1 behavior by making repository loading explicit.

Indexes should first support known identity/lookup/uniqueness requirements.

---

# 61. Initial index candidates

Likely useful indexes derive from existing Repository queries:

```text
external identifier lookup
supplier + organization relationship lookup
onboarding by relationship
latest assessment by relationship
qualification by relationship + scope
```

Exact DDL is deferred to mapping implementation.

---

# 62. Public API impact

The persistence cycle should not force a public HTTP API.

Consumer configuration may eventually expose persistence composition helpers, but Core public APIs should not return SQLAlchemy models, Sessions, Engines, Rows, or query objects.

---

# 63. InMemory adapter status after persistence

InMemory adapters remain first-class test/local adapters.

They are not deprecated by SQL persistence.

They continue to provide:

```text
fast application tests
pure local examples
contract reference behavior
low-noise domain learning
```

---

# 64. Cross-dialect compatibility rule

The portability contract is **business behavior and Repository semantics**, not byte-identical SQL.

Therefore:

```text
same Repository Port
same shared contract
same Domain reconstruction
same business result
```

must hold across SQLite and PostgreSQL.

Dialect-specific SQL may differ where required.

---

# 65. PostgreSQL-specific behavior rule

If a feature is required for correct production behavior and cannot be represented faithfully in SQLite:

```text
keep production correctness
+
add PostgreSQL-specific integration test
```

Do not weaken the production model to preserve artificial SQLite symmetry.

---

# 66. SQLAlchemy type strategy

Prefer backend-agnostic SQLAlchemy types where semantics remain correct:

```text
Uuid
String
Integer
Boolean
DateTime / TIMESTAMP with explicit UTC handling
```

Introduce dialect-specific types only when their semantics are required.

This preserves the single-adapter hypothesis.

---

# 67. Schema naming

Initial convention:

```text
snake_case
plural table names
explicit foreign-key names where useful
stable constraint/index names for migrations
```

Database names are persistence concerns and should not leak into Domain terminology.

---

# 68. Schema ownership

SQLAlchemy metadata and Alembic migrations are owned by the persistence adapter layer.

The Domain owns business semantics.

The database owns relational integrity mechanisms.

The Application owns use-case coordination.

These responsibilities must remain distinct.

---

# 69. Event persistence

Domain Events are **not** persisted as an event store in Cycle 2.

The system remains state-based persistence plus transient Domain Events.

Event Sourcing would be a separate architectural decision with substantially different semantics.

---

# 70. Current Domain Event storage decision

No `domain_events` table is introduced merely because a relational database now exists.

If reliable external publication later requires durable pending events, evaluate Transactional Outbox rather than conflating it with Domain Event history.

---

# 71. Cycle 2 milestone proposal

The persistence cycle can now be refined into:

```text
0.2.0a1 - Persistence Foundation
    SQLAlchemy dependency boundary
    adapter package
    Engine / Session factories
    architecture gates

0.2.0a2 - Supplier + Relationship SQL Persistence
    mappings
    SQLite contracts
    first PostgreSQL contracts

0.2.0a3 - Onboarding + Assessment SQL Persistence
    child collections
    completion state

0.2.0a4 - Qualification SQL Persistence
    scope mapping
    current-scope uniqueness

0.2.0a5 - Transaction Boundary / UnitOfWork
    atomic StartSupplierOnboarding
    commit / rollback
    post-commit event dispatch

0.2.0a6 - Alembic Migration Baseline
    initial schema history
    migration tests

0.2.0a7 - Persistent Local Qualification
    SQLite restart scenario
    PostgreSQL persistent scenario
```

This roadmap remains iterative and may be adjusted by implementation pressure.

---

# 72. Why persistence foundation precedes API

An HTTP interface before durable state would prove transport but not operational persistence.

The chosen order is:

```text
Core
    -> Persistence
    -> Public API
```

unless a real consumer creates stronger pressure for a different order.

---

# 73. Why persistence precedes external SRM integration

External integrations become more meaningful once PySRMKit can preserve its canonical state.

Future shape:

```text
Ivalua / SAP / Coupa
        |
        v
Anti-Corruption Layer
        |
        v
PySRMKit Application
        |
        v
Persistent Domain State
```

---

# 74. Architecture acceptance criteria

The persistence architecture is implemented successfully when:

```text
[ ] Domain imports no SQLAlchemy/Alembic/Psycopg
[ ] Application imports no SQLAlchemy/Alembic/Psycopg
[ ] Repository Ports remain unchanged unless real semantics require change
[ ] InMemory contracts remain green
[ ] SQLite implementations pass shared Repository Contracts
[ ] PostgreSQL implementations pass shared Repository Contracts
[ ] Aggregate state survives Session/repository recreation
[ ] cross-instance uniqueness survives concurrency-safe persistence
[ ] multi-repository use case has atomic transaction semantics
[ ] repositories never commit independently
[ ] events dispatch only after successful commit
[ ] migration baseline can build an empty database
[ ] persistent end-to-end qualification succeeds
[ ] rejection path remains correct
[ ] architecture tests remain green
```

---

# 75. Explicitly deferred decisions

Deferred until pressure appears:

```text
async SQLAlchemy
AsyncSession
connection-pool tuning
optimistic version columns
SERIALIZABLE default isolation
savepoints
nested UnitOfWork
distributed transactions
read replicas
sharding
multi-tenancy schema strategy
database encryption architecture
outbox
event sourcing
cache layer
query/read-model architecture
```

---

# 76. Learning map - persistence

```text
Problem
    state disappears
        |
        v
Repository Port already exists
        |
        v
SQLAlchemy Adapter
        |
        +--> SQLite
        +--> PostgreSQL
        |
        v
same Repository Contracts
        |
        v
Liskov Substitution
```

---

# 77. Learning map - transaction

```text
Problem
    multiple Aggregate writes
    must be atomic
        |
        v
SQLAlchemy Session transaction
        |
        v
Application transaction abstraction
        |
        v
UnitOfWork candidate
        |
        v
commit / rollback tests
```

---

# 78. Learning map - Data Mapper

```text
Domain Aggregate
    persistence ignorant
        |
        v
Mapper
        |
        v
SQLAlchemy Record
        |
        v
Relational tables
```

This preserves Separation of Concerns and Dependency Inversion.

---

# 79. Learning map - migrations

```text
Schema changes over time
        |
        v
Alembic migration history
        |
        v
upgrade tests
        |
        v
reproducible persistent runtime
```

---

# 80. Design decisions summary

| Topic | Decision |
|---|---|
| Persistence toolkit | SQLAlchemy |
| SQLAlchemy style | modern typed declarative persistence models |
| Domain mapping | separate persistence records + explicit mapping |
| Initial execution model | synchronous |
| SQLite | local + fast contract backend |
| PostgreSQL | reference production-oriented backend |
| PostgreSQL driver | Psycopg 3 |
| Repository split by dialect | no, unless real divergence appears |
| Repository commit | forbidden |
| Session scope | one application transaction/use case |
| IDs | Domain-generated UUIDs |
| Domain enums | portable string persistence initially |
| Domain timestamps | timezone-aware, normalized to UTC |
| Migrations | Alembic |
| UnitOfWork | introduce when SQL multi-repository atomicity requires it |
| Event dispatch | after successful commit |
| Outbox | deferred |
| Async persistence | deferred |
| Optimistic locking | deferred until conflict pressure |
| DI container | not required |

---

# 81. Next implementation action

After this document is accepted, the next action is **not another broad specification**.

It is:

```text
0.2.0a1 - Persistence Foundation
```

which should implement only:

```text
optional SQLAlchemy dependency
adapters/sqlalchemy package
metadata/base
Engine factory
Session factory
SQLite foreign-key configuration
architecture dependency tests
first persistence smoke test
```

No Aggregate repository needs to be fully migrated in the foundation milestone.

---

# 82. Final rule

> **The Domain must not know that SQL exists.**

> **Repository behavior must remain stable while adapters change.**

> **SQLite accelerates relational learning; PostgreSQL validates production-oriented semantics.**

> **Repositories stage persistence; transaction boundaries commit it.**

> **Domain Events describe business facts; successful commit determines when those facts may be dispatched.**

> **UnitOfWork becomes a pattern only when the transaction actually needs it.**
