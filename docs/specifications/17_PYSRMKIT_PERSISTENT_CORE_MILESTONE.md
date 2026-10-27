# PySRMKit - Persistent Core Milestone

**Document:** `17_PYSRMKIT_PERSISTENT_CORE_MILESTONE.md`  
**Status:** ACTIVE CYCLE / ITERATIVE MILESTONE BASELINE  
**Cycle:** `0.2.x - Persistent Core`  
**Predecessors:**  
- `15_PYSRMKIT_POST_CORE_ARCHITECTURE_REVIEW.md`
- `16_PYSRMKIT_PERSISTENCE_ARCHITECTURE.md`

**Date:** 2026-10-27

---

# 1. Purpose

This document defines the complete **PERSISTENT CORE** milestone for PySRMKit.

It is the umbrella milestone for the second implementation cycle:

```text
0.2.x - Persistent Core
```

The first implementation cycle proved that PySRMKit could execute the complete supplier qualification journey locally with:

```text
Domain
Application
Ports
InMemory Adapters
Domain Events
Tests
```

The second cycle must prove a stronger architectural claim:

> **The same Domain and Application model can survive real relational persistence without allowing infrastructure concerns to leak into the Core.**

This document defines:

```text
why the cycle exists
what it must prove
what it explicitly excludes
which milestones compose it
which architecture invariants must remain true
how SQLite and PostgreSQL are used
when UnitOfWork becomes justified
how migrations enter the architecture
how Repository Contracts are reused
how the persistent end-to-end scenario is qualified
when the cycle is considered complete
```

---

# 2. Relationship with documents 15 and 16

The three post-Core documents have different responsibilities.

```text
15_PYSRMKIT_POST_CORE_ARCHITECTURE_REVIEW.md
        |
        | asks:
        | "What did 0.1.x actually teach us?"
        v
Decision:
Persistence is the strongest next pressure.


16_PYSRMKIT_PERSISTENCE_ARCHITECTURE.md
        |
        | asks:
        | "How should relational persistence fit into the architecture?"
        v
Decision:
SQLAlchemy + SQLite + PostgreSQL,
Core remains persistence-ignorant.


17_PYSRMKIT_PERSISTENT_CORE_MILESTONE.md
        |
        | asks:
        | "How do we execute and qualify the full persistence cycle?"
        v
Cycle:
0.2.0a1 -> 0.2.0a7
```

Therefore:

```text
15 = WHY
16 = HOW
17 = EXECUTION CYCLE
```

---

# 3. Business sentence

Every implementation cycle must be explainable without architecture jargon.

The business sentence for the Persistent Core is:

> **PySRMKit can preserve the supplier qualification journey durably and recover the same business state after the process and persistence context are recreated.**

The technical sentence is:

> **The existing Domain and Application layers can operate against SQL-backed Repository adapters while preserving the same business behavior and architecture boundaries qualified by the InMemory Core.**

---

# 4. Starting point

The Persistent Core begins from the qualified first Core:

```text
Supplier
    |
    v
SupplierRelationship
    |
    v
Relationship Lifecycle
    |
    v
SupplierOnboarding
    |
    v
SupplierAssessment
    |
    v
SupplierQualification
```

The complete local scenario already works:

```text
RegisterSupplier
        |
        v
CreateSupplierRelationship
        |
        v
InviteSupplierRelationship
        |
        v
StartSupplierOnboarding
        |
        v
SatisfyOnboardingRequirement
        |
        v
CompleteSupplierOnboarding
        |
        v
CreateSupplierAssessment
        |
        v
RecordAssessmentAnswer
        |
        v
CompleteSupplierAssessment
        |
        v
RequestSupplierQualification
        |
        v
EvaluateSupplierQualification
        |
        +--> QUALIFIED
        |
        +--> NOT_QUALIFIED
```

The first cycle proved:

```text
business correctness
domain boundaries
application orchestration
repository contracts
domain events
in-memory adapters
architecture fitness rules
local composition
```

What it did not prove is durability.

---

# 5. Core problem

With only InMemory repositories:

```text
process starts
    |
    v
business state created
    |
    v
process stops
    |
    v
state disappears
```

This is now a real limitation.

The second cycle changes that to:

```text
process starts
    |
    v
business state created
    |
    v
transaction committed
    |
    v
process / Session / repositories destroyed
    |
    v
new persistence context created
    |
    v
state reloaded
    |
    v
same business meaning preserved
```

The cycle therefore tests whether persistence is truly an Adapter concern.

---

# 6. Main architectural hypothesis

The central hypothesis is:

```text
Domain
Application
Ports
```

should remain substantially unchanged while:

```text
InMemory Adapters
```

are complemented by:

```text
SQLAlchemy Adapters
```

The intended shape is:

```text
                 DOMAIN
                    ^
                    |
              APPLICATION
                    |
                    v
             REPOSITORY PORTS
                    ^
                    |
        +-----------+------------+
        |                        |
        |                        |
   InMemory Adapters       SQLAlchemy Adapters
                                 |
                       +---------+----------+
                       |                    |
                     SQLite             PostgreSQL
```

If the Domain must become SQLAlchemy-aware for this cycle to succeed, the architecture has failed its main test.

---

# 7. Cycle objective

The Persistent Core must make the following statement true:

> **A complete supplier qualification journey can be committed to relational persistence, the runtime can be recreated, and the same Domain Aggregates and qualification decision can be reconstructed correctly.**

This requires more than "SQLAlchemy connects successfully."

It requires:

```text
mapping
repository behavior
constraints
transactions
rollback
schema evolution
restart/reload
cross-adapter contract compatibility
event dispatch ordering
```

---

# 8. Non-goal: rewriting the Domain

The Persistent Core is not a second Domain redesign.

The default position is:

```text
Supplier                    KEEP
SupplierRelationship        KEEP
SupplierOnboarding          KEEP
SupplierAssessment          KEEP
SupplierQualification       KEEP
QualificationPolicy         KEEP
Commands                    KEEP
Handlers                    KEEP unless transaction pressure requires coordination change
Repository Ports            KEEP unless real semantics require adjustment
```

Persistence should adapt to the Core.

The Core should not adapt itself to an ORM.

---

# 9. Persistence technology decisions

The cycle uses:

```text
SQLAlchemy
    relational persistence toolkit

SQLite
    lightweight local and contract-test backend

PostgreSQL
    reference production-oriented relational backend

Psycopg 3
    PostgreSQL Python driver

Alembic
    schema migration history
```

These tools live outside the Domain and Application layers.

---

# 10. Runtime dependency policy

The pure PySRMKit Core remains lightweight.

Desired packaging model:

```text
pysrmkit
    Core
    no mandatory third-party runtime dependency

pysrmkit[persistence]
    SQLAlchemy persistence capability

pysrmkit[postgresql]
    SQLAlchemy + Psycopg

pysrmkit[dev]
    tests + lint + typing + persistence qualification tools
```

Persistence is optional for consumers that only need the pure Core.

---

# 11. SQLite role

SQLite is part of the Persistent Core for a precise reason.

It provides:

```text
real SQL
real tables
real foreign keys
real uniqueness constraints
real transactions
real relational mapping
fast Repository Contract execution
local file-backed durability
```

without requiring:

```text
database server
network
credentials
container runtime
```

SQLite is therefore:

> **a lightweight relational persistence laboratory and contract backend.**

It is not:

> **a substitute for PostgreSQL production validation.**

---

# 12. PostgreSQL role

PostgreSQL is the reference production-oriented relational backend.

It validates concerns that SQLite cannot fully represent:

```text
client/server behavior
MVCC
concurrent writes
locking
PostgreSQL constraint behavior
native UUID semantics
driver integration
connection pooling
real transaction behavior
```

The compatibility rule is:

```text
same Domain behavior
same Repository contract
same business outcome
```

not:

```text
identical SQL
identical DDL
identical dialect behavior
```

---

# 13. SQLAlchemy adapter strategy

The first hypothesis is one repository family:

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

Separate repository implementations are justified only if real dialect divergence appears.

---

# 14. Data Mapper boundary

The Persistent Core uses a persistence-ignorant Domain.

Therefore:

```text
Domain Aggregate
        !=
SQLAlchemy persistence record
```

The preferred flow is:

```text
Domain Aggregate
        ^
        |
        | reconstitute / map
        |
Persistence Mapper
        ^
        |
        v
SQLAlchemy Persistence Record
        |
        v
Database
```

This is a Data Mapper style boundary.

---

# 15. Persistence record rule

SQLAlchemy persistence records may contain:

```text
table names
columns
foreign keys
indexes
constraints
relationships
SQLAlchemy type information
```

Domain Aggregates may not.

Persistence records are infrastructure representations.

They are not business Entities.

---

# 16. Repository semantics

Repository Ports already exist and remain the behavioral source of truth.

A SQL repository must preserve semantics such as:

```text
get(...)
save(...)
find_by_external_identifier(...)
find_for_supplier_and_organization(...)
find_for_relationship(...)
find_latest_for_relationship(...)
find_current_for_scope(...)
```

`save()` means:

> **Stage the current valid Aggregate state in the active persistence context.**

It does not mean:

> **Commit the database transaction.**

---

# 17. Repository commit rule

SQL repositories must never call:

```text
session.commit()
session.rollback()
```

The reason is architectural.

If repositories commit independently:

```text
Repository A save
    -> commit

Repository B save
    -> fails
```

the use case can leave the system partially updated.

Transaction ownership therefore belongs above repositories.

---

# 18. Session scope

The default model is:

```text
one application transaction
        =
one SQLAlchemy Session scope
```

Rules:

```text
no global Session
no module-level Session singleton
no Session inside Domain objects
no Session exposed by Repository Ports
no Engine created by repositories
```

The composition boundary owns Engine and Session creation.

---

# 19. Aggregate loading rule

A Repository must return a fully usable Domain Aggregate.

Therefore:

```text
Repository.get(...)
    -> query persistence state
    -> load required owned records
    -> reconstruct Value Objects
    -> reconstruct Aggregate
    -> return persistence-ignorant Domain object
```

No Domain behavior may trigger lazy SQL queries.

---

# 20. Aggregate save rule

Conceptually:

```text
Domain Aggregate
        |
        v
extract current state
        |
        v
map to persistence records
        |
        v
synchronize root row
        |
        v
synchronize owned child rows
        |
        v
Session contains staged changes
```

The Repository Contract defines the observable semantics.

Internal ORM mechanics remain adapter details.

---

# 21. Identity policy

Domain-generated UUID identities remain canonical.

Do not replace:

```text
SupplierId
SupplierRelationshipId
OnboardingId
AssessmentId
QualificationId
```

with auto-increment integers as business identities.

The database may use technical surrogate keys only for owned child rows when they do not become Domain identity.

---

# 22. Value Object persistence

Value Objects should normally be flattened into explicit relational columns.

Examples:

```text
SupplierIdentity
    -> legal_name
    -> trading_name
    -> supplier_type
    -> country_code

ExternalIdentifier
    -> kind
    -> value
    -> source_system
    -> jurisdiction

QualificationScope
    -> organization_id
    -> category_code
    -> country_code
```

Opaque JSON storage is not the default.

---

# 23. Enum persistence

Domain `StrEnum` values should initially be persisted as portable strings.

Example:

```text
SupplierLifecycleStage.ONBOARDING
        |
        v
"ONBOARDING"
```

This avoids premature coupling to PostgreSQL-native enum types.

---

# 24. Time persistence

Business timestamps remain timezone-aware.

Policy:

```text
Domain time
    timezone-aware

Persistence
    normalized to UTC

Reload
    timezone-aware UTC datetime
```

Repository Contract and integration tests must prove round-trip semantics.

---

# 25. Relational constraints

Database constraints complement Domain and Application invariants.

Use the database for:

```text
primary keys
foreign keys
non-null structural constraints
cross-row uniqueness
race-condition protection
```

Keep behavior such as lifecycle transition rules in the Domain.

---

# 26. Cross-instance invariants

The Persistent Core must protect first-Core invariants that span Aggregate instances.

Examples:

```text
ExternalIdentifier uniqueness

Supplier + Organization Relationship uniqueness

Current Qualification uniqueness
    per Relationship + QualificationScope
```

Application pre-checks remain valuable for clear business errors.

Database constraints protect against concurrent writers.

---

# 27. Error translation

Raw persistence errors such as:

```text
IntegrityError
OperationalError
DBAPIError
```

must not become part of the public Core-facing contract.

The adapter/application boundary should translate them only when a stable business/application meaning exists.

Do not create a large generic persistence-error hierarchy before concrete failures require it.

---

# 28. Transaction boundary

Default rule:

```text
one Command / use case
        =
one transaction boundary
```

Conceptually:

```text
BEGIN
  |
  +--> load Aggregates
  |
  +--> execute Domain behavior
  |
  +--> save Aggregates
  |
  +--> flush as required
  |
COMMIT
  |
  +--> success -> dispatch Domain Events
  |
  +--> failure -> rollback, no success dispatch
```

---

# 29. Why transaction pressure is real

The first Core already contains a multi-Aggregate write use case:

```text
StartSupplierOnboarding
        |
        +--> SupplierRelationship
        |
        +--> SupplierOnboarding
```

With relational persistence, this invalid outcome must be impossible:

```text
Relationship stage committed as ONBOARDING
        +
SupplierOnboarding insert failed
```

Therefore the persistence cycle introduces real atomicity pressure.

---

# 30. UnitOfWork trigger

UnitOfWork is not introduced because the architecture textbook says so.

It becomes justified when this condition is true:

> **A SQL-backed use case must coordinate multiple repositories atomically without exposing SQLAlchemy to the Application Layer.**

The likely first trigger is:

```text
StartSupplierOnboarding
```

At that moment UnitOfWork must provide real guarantees:

```text
shared Session / transaction
commit
rollback
atomicity
repository participation
no SQLAlchemy leakage
```

---

# 31. UnitOfWork API is not pre-frozen

Possible shapes remain open:

```text
A. UnitOfWork owns repositories

B. UnitOfWork owns transaction only,
   repositories receive shared persistence context

C. transaction runner wraps application use case execution
```

The invariant is defined now.

The exact API should emerge from implementation pressure.

---

# 32. Domain Event ordering

Persistence changes the meaning of `save()`.

InMemory:

```text
save
    ~= durable enough for local process
```

SQL:

```text
save
    !=
commit
```

Therefore event ordering becomes:

```text
Domain behavior
    -> event recorded

Repository.save
    -> SQL state staged

COMMIT SUCCESS
    -> state durable

THEN
    -> Domain Event dispatch
```

If commit fails:

```text
rollback
no success event dispatch
```

---

# 33. Outbox boundary

Transactional Outbox remains deferred.

Current event transport is:

```text
InProcessDomainEventDispatcher
```

There is no external message broker delivery requirement yet.

Outbox becomes relevant when PySRMKit must guarantee:

```text
database commit
+
external event publication
```

together.

---

# 34. Migration strategy

Persistent schema evolution requires migration history.

The cycle adopts:

```text
Alembic
```

once the first schema is stable enough to establish a baseline.

Migration concerns include:

```text
initial schema
incremental upgrades
constraint changes
index changes
cross-version compatibility
migration tests
```

`metadata.create_all()` may still be used for fast ephemeral Repository Contract tests.

It is not the production migration strategy.

---

# 35. Schema ownership

Responsibilities are:

```text
Domain
    owns business semantics

Persistence records
    own relational representation

Database
    owns relational integrity enforcement

Alembic
    owns schema evolution history

Application
    owns use-case coordination
```

---

# 36. Persistent Core test architecture

The cycle extends the existing test stack.

```text
Pure Domain Tests
        |
        v
Application Tests
        |
        v
Repository Contracts
        |
        +--> InMemory
        |
        +--> SQLite
        |
        +--> PostgreSQL
        |
        v
Persistence Integration Tests
        |
        v
Persistent Scenario Tests
```

Pure Domain tests remain database-free.

---

# 37. Repository Contract strategy

The same behavioral contract should execute against multiple adapters.

Example:

```text
SupplierRepositoryContract
        |
        +--> InMemorySupplierRepository
        |
        +--> SqlAlchemySupplierRepository + SQLite
        |
        +--> SqlAlchemySupplierRepository + PostgreSQL
```

This is a direct executable demonstration of:

```text
Repository Pattern
Adapter Pattern
Dependency Inversion
Liskov Substitution
```

---

# 38. SQLite contract tests

SQLite is expected to run quickly enough for the normal developer suite.

Target:

```bash
python -m pytest
```

may include:

```text
pure tests
InMemory contracts
SQLite contracts
SQLite adapter smoke tests
```

as long as feedback remains fast.

---

# 39. PostgreSQL integration tests

PostgreSQL tests should be explicit.

Candidate:

```bash
python -m pytest -m postgresql
```

They validate:

```text
real PostgreSQL dialect
foreign keys
unique constraints
transactions
locking/concurrency behavior where relevant
Psycopg integration
schema migrations
```

CI should provide an isolated PostgreSQL service.

---

# 40. Test database safety

PostgreSQL integration tests must never silently target an arbitrary database.

Required safeguards:

```text
explicit test database URL
test database naming check
isolated credentials
destructive operations allowed only on test target
no production credentials
```

---

# 41. Persistence architecture fitness functions

The architecture suite must enforce:

```text
domain
    must not import sqlalchemy
    must not import alembic
    must not import psycopg

application
    must not import sqlalchemy
    must not import alembic
    must not import psycopg

ports
    must not import sqlalchemy
    must not import alembic
    must not import psycopg
```

Persistence imports belong to:

```text
adapters/sqlalchemy
integration tests
migration tooling
outer composition
```

---

# 42. Package topology target

Target architecture:

```text
src/pysrmkit/
├── domain/
├── application/
├── ports/
└── adapters/
    ├── memory/
    ├── events/
    ├── clock/
    └── sqlalchemy/
        ├── metadata.py
        ├── engine.py
        ├── session.py
        ├── models/
        ├── mappers/
        └── repositories/
```

Later, only if justified:

```text
unit_of_work.py
```

---

# 43. Cycle milestone map

The Persistent Core is decomposed into seven alpha milestones.

```text
0.2.0a1
Persistence Foundation
        |
        v
0.2.0a2
Supplier + Relationship SQL Persistence
        |
        v
0.2.0a3
Onboarding + Assessment SQL Persistence
        |
        v
0.2.0a4
Qualification SQL Persistence
        |
        v
0.2.0a5
Transaction Boundary / UnitOfWork
        |
        v
0.2.0a6
Alembic Migration Baseline
        |
        v
0.2.0a7
Persistent Local Qualification
```

---

# 44. `0.2.0a1 - Persistence Foundation`

## Goal

Create the relational infrastructure boundary without persisting business Aggregates yet.

## Scope

```text
optional SQLAlchemy dependency
adapters/sqlalchemy package
DeclarativeBase / metadata
Engine factory
Session factory
SQLite foreign-key configuration
architecture dependency gates
relational smoke tests
```

## Explicit non-scope

```text
SupplierRecord
RelationshipRecord
SQL business repositories
UnitOfWork
Alembic migrations
PostgreSQL adapter qualification
AsyncSession
```

## Exit gate

> **The relational persistence boundary exists, is executable, typed, and remains outside the Core.**

---

# 45. `0.2.0a2 - Supplier + Relationship SQL Persistence`

## Business sentence

> **We can preserve supplier master data and supplier-organization relationships in relational persistence without changing the Domain contract.**

## Scope

```text
SupplierRecord
SupplierExternalIdentifierRecord
SupplierRelationshipRecord

Supplier mapper
Relationship mapper

SqlAlchemySupplierRepository
SqlAlchemySupplierRelationshipRepository

SQLite Repository Contract execution
relational FK constraints
relational uniqueness constraints
```

## Key proof

```text
same SupplierRepositoryContract
        |
        +--> InMemory
        +--> SQLite SQLAlchemy
```

and:

```text
same SupplierRelationshipRepositoryContract
        |
        +--> InMemory
        +--> SQLite SQLAlchemy
```

## Exit gate

> **Supplier and SupplierRelationship can be substituted between InMemory and SQL persistence through the same Repository Ports and contracts.**

---

# 46. `0.2.0a3 - Onboarding + Assessment SQL Persistence`

## Business sentence

> **Onboarding readiness and assessment evidence survive relational persistence.**

## Scope

```text
SupplierOnboarding persistence
owned OnboardingRequirement persistence

SupplierAssessment persistence
question snapshots
answers
completion state
score
decision

SQLite contracts
PostgreSQL contracts when infrastructure is ready
```

## Main learning pressure

Owned collections and Aggregate reconstruction become more complex.

## Exit gate

> **Onboarding and Assessment can be fully reconstructed with their invariants and completion state preserved.**

---

# 47. `0.2.0a4 - Qualification SQL Persistence`

## Business sentence

> **Scoped qualification decisions survive relational persistence without losing explainability.**

## Scope

```text
SupplierQualification persistence
QualificationScope flattening
QualificationDecision persistence
status persistence
decision reasons
failed requirements
current-scope lookup
cross-instance uniqueness
```

## Main challenge

Protect:

```text
one current Qualification
per
Relationship + Scope
```

under real database concurrency.

## Exit gate

> **A qualification can be requested, evaluated, saved, reloaded, and explained from relational persistence.**

---

# 48. `0.2.0a5 - Transaction Boundary / UnitOfWork`

## Business sentence

> **A multi-Aggregate business operation either commits completely or leaves no partial durable state.**

## Primary candidate

```text
StartSupplierOnboarding
```

## Scope

```text
shared transaction boundary
commit
rollback
multi-repository atomicity
post-commit event dispatch
failure tests
```

## UnitOfWork decision

This milestone may introduce UnitOfWork if implementation pressure proves it is the smallest clean abstraction.

## Exit gate

> **A failure during a multi-repository use case cannot leave a partially committed business transition.**

---

# 49. `0.2.0a6 - Alembic Migration Baseline`

## Business sentence

> **The Persistent Core schema can be created and evolved reproducibly.**

## Scope

```text
Alembic configuration
initial migration baseline
constraint/index naming
SQLite migration compatibility where useful
PostgreSQL migration validation
migration test strategy
```

## Exit gate

> **An empty supported database can be migrated reproducibly to the schema required by the Persistent Core.**

---

# 50. `0.2.0a7 - Persistent Local Qualification`

## Business sentence

> **The complete supplier qualification journey survives runtime and persistence-context recreation.**

## Scenario

```text
empty database
    |
    v
RegisterSupplier
    |
    v
CreateSupplierRelationship
    |
    v
Invite
    |
    v
Start + complete Onboarding
    |
    v
Create + complete Assessment
    |
    v
Request + evaluate Qualification
    |
    v
COMMIT
    |
    v
destroy Session/repositories
    |
    v
create new Session/repositories
    |
    v
reload complete business state
    |
    v
same final QualificationDecision
```

## Backends

```text
SQLite file-backed scenario
PostgreSQL scenario
```

## Exit gate

> **The first Core business narrative remains correct after durable relational persistence and reload.**

---

# 51. Cycle dependency graph

```text
0.2.0a1 Foundation
      |
      v
0.2.0a2 Supplier + Relationship
      |
      v
0.2.0a3 Onboarding + Assessment
      |
      v
0.2.0a4 Qualification
      |
      v
0.2.0a5 Transactions / UnitOfWork
      |
      v
0.2.0a6 Migrations
      |
      v
0.2.0a7 Persistent Scenario
```

Each milestone may refine earlier design when implementation pressure reveals a wrong assumption.

---

# 52. Why this order

The order follows dependency and learning pressure.

```text
Foundation
    before
business mappings

simple Aggregates
    before
owned collections

individual persistence
    before
cross-repository transactions

working schema
    before
migration history

all parts
    before
persistent end-to-end scenario
```

---

# 53. Cycle architecture checkpoints

Explicit review points should occur after:

```text
a2
    Are Repository Ports truly substitutable?

a3
    Are owned child collections mapped without leaking ORM behavior?

a4
    Does scoped qualification remain relationally expressible?

a5
    Is UnitOfWork actually justified and minimal?

a6
    Can schema evolution remain adapter-owned?

a7
    Did the original Domain/Application model survive real persistence?
```

---

# 54. Persistent Core success criteria

At the end of the cycle:

```text
[ ] Core remains SQLAlchemy-free
[ ] Core remains Alembic-free
[ ] Core remains Psycopg-free

[ ] InMemory adapters remain green
[ ] SQLite adapters pass shared contracts
[ ] PostgreSQL adapters pass shared contracts

[ ] Supplier persists and reloads
[ ] Relationship persists and reloads
[ ] Onboarding persists and reloads
[ ] Assessment persists and reloads
[ ] Qualification persists and reloads

[ ] Value Objects round-trip correctly
[ ] lifecycle state round-trips correctly
[ ] timezone-aware timestamps round-trip correctly
[ ] Domain identifiers remain stable

[ ] FK constraints are enforced
[ ] uniqueness constraints are enforced
[ ] concurrent cross-instance invariants are protected

[ ] repositories never auto-commit
[ ] transaction boundary is explicit
[ ] rollback is proven
[ ] multi-repository atomicity is proven

[ ] Domain Events dispatch only after successful commit

[ ] migration baseline creates the full schema
[ ] migration tests are green

[ ] persistent success scenario passes
[ ] persistent rejection scenario passes
[ ] reload after runtime recreation passes
```

---

# 55. Definition of Done - adapter

A persistence adapter item is done when:

```text
[ ] Domain mapping is explicit
[ ] Repository Port semantics preserved
[ ] shared Repository Contract passes
[ ] SQL-specific constraints tested
[ ] no commit inside Repository
[ ] no SQLAlchemy leakage into Core
[ ] mapper/reconstitution tests pass
[ ] types pass
[ ] lint passes
[ ] architecture tests pass
```

---

# 56. Definition of Done - milestone

A Persistent Core milestone is done when:

```text
[ ] scoped persistence capability implemented
[ ] InMemory regression remains green
[ ] SQLite contract/integration tests green
[ ] PostgreSQL tests green when milestone scope includes PostgreSQL
[ ] architecture gates green
[ ] failure paths tested
[ ] spec updated when implementation changed assumptions
[ ] qualification document records exact CI evidence
```

---

# 57. Definition of Done - cycle

The Persistent Core cycle is done when:

> **PySRMKit can execute the complete qualification journey using relational persistence, commit it atomically, recreate its persistence context, reload all required Aggregates, and produce the same business meaning without any persistence dependency inside Domain, Application, or Repository Ports.**

---

# 58. Quality gate matrix

| Milestone | Pure Core | InMemory contracts | SQLite | PostgreSQL | Transactions | Migrations | Persistent scenario |
|---|---:|---:|---:|---:|---:|---:|---:|
| `a1` Foundation | regression | regression | smoke | - | - | - | - |
| `a2` Supplier + Relationship | regression | required | required | progressive | - | - | partial |
| `a3` Onboarding + Assessment | regression | required | required | required | observation | - | partial |
| `a4` Qualification | regression | required | required | required | observation | - | partial |
| `a5` Transaction / UoW | regression | required | required | required | **required** | - | partial |
| `a6` Alembic | regression | required | required | required | required | **required** | partial |
| `a7` Persistent Qualification | **all** | **all** | **all** | **all** | **all** | **all** | **required** |

---

# 59. Coverage philosophy

Do not chase database coverage percentages mechanically.

Priority is:

```text
Repository Contract semantics
mapper round trips
constraint failures
transaction rollback
cross-instance uniqueness
event dispatch ordering
restart/reload scenario
```

A line coverage metric cannot substitute for these behaviors.

---

# 60. Failure-driven tests

The persistence cycle must intentionally test failure.

Examples:

```text
missing FK target
duplicate external identifier
duplicate Supplier + Organization relationship
invalid current Qualification duplication
commit failure
rollback
multi-repository partial-write prevention
migration failure
reload after process-context destruction
```

A persistence layer that only tests the happy path is not qualified.

---

# 61. Concurrency posture

Do not introduce optimistic locking everywhere automatically.

Start with:

```text
database constraints
transaction boundaries
clear business preconditions
```

Observe:

```text
lost update
double transition
double qualification
concurrent duplicate creation
```

Only then decide whether version columns, row locks, or stronger isolation are required.

---

# 62. Isolation-level posture

Do not set SERIALIZABLE globally.

Use the database defaults first.

Escalate only when a concrete invariant cannot be protected adequately through:

```text
constraints
atomic transaction design
locking
conflict handling
```

---

# 63. Performance posture

Performance optimization is not a primary cycle objective.

Initial priorities:

```text
correct mapping
correct reconstruction
correct constraints
correct transactions
correct contracts
```

Avoid accidental N+1 behavior by keeping Aggregate loading explicit.

Measure before optimizing.

---

# 64. Index strategy

Indexes should derive from real Repository lookups.

Likely candidates:

```text
external identifier lookup
Supplier + Organization relationship lookup
Onboarding by Relationship
latest Assessment by Relationship
Qualification by Relationship + Scope
```

No speculative indexing catalog is required.

---

# 65. Delete policy

The existing Repository Ports do not expose generic delete.

Therefore the Persistent Core does not invent:

```text
hard delete
soft delete
archive flag
generic delete()
```

Deletion/retention enters only when a business use case requires it.

---

# 66. Audit policy

Do not add generic:

```text
created_at
updated_at
created_by
updated_by
deleted_at
```

to every table automatically.

Persist Domain timestamps that already exist.

Technical audit metadata should emerge from audit/compliance requirements.

---

# 67. Event persistence policy

The Persistent Core is not Event Sourcing.

It persists current business state.

Domain Events remain transient facts emitted by Aggregate behavior.

No generic:

```text
domain_events
```

event-store table is introduced.

---

# 68. Security baseline

Persistence credentials belong to outer runtime configuration.

Never:

```text
hard-code credentials
commit passwords
log secret-bearing database URLs
reuse production credentials in tests
```

Production secret management remains a deployment concern.

---

# 69. Configuration baseline

Expected outer configuration:

```text
DATABASE_URL
optional engine settings
development SQL echo flag
test database URL
```

Rules:

```text
Domain reads no environment variables
Application constructs no Engine
module imports connect to no database
```

---

# 70. Local developer workflow

The cycle should preserve a simple development experience.

Pure/local development:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

Persistence-focused development:

```bash
python -m pytest tests/contracts
python -m pytest tests/integration/sqlite
```

PostgreSQL qualification later:

```bash
python -m pytest -m postgresql
```

Prefer:

```text
python -m ...
```

to avoid interpreter/tool mismatch across Conda, Homebrew Python, and project virtual environments.

---

# 71. CI evolution

The CI pipeline should evolve gradually.

Initial:

```text
lint
format
typing
full pytest
architecture tests
SQLite tests
```

Later:

```text
PostgreSQL service
    |
    v
postgresql integration job
    |
    v
migration tests
    |
    v
persistent scenario
```

Do not introduce complex CI orchestration before the corresponding runtime capability exists.

---

# 72. Documentation strategy

The Persistent Core does not restart broad upfront documentation.

The rule remains:

```text
implementation
    |
    v
real friction
    |
    v
targeted document update
```

This document is the cycle baseline.

Future deep dives should exist only for newly observed design pressure.

---

# 73. Architecture learning goals

The Persistent Core should make the following concepts executable rather than theoretical:

```text
Data Mapper
Repository substitution
Liskov Substitution
Dependency Inversion
relational constraints
transaction boundary
UnitOfWork
migration
Session lifecycle
database adapter
cross-dialect testing
post-commit event dispatch
```

---

# 74. Design patterns expected to emerge

Expected and already justified:

```text
Repository
Adapter
Data Mapper
```

Potentially justified later in the cycle:

```text
UnitOfWork
```

Still not automatically justified:

```text
Generic Repository
DAO framework
Active Record
Service Locator
DI Container
Outbox
Event Sourcing
Specification framework
```

---

# 75. Persistence anti-patterns to avoid

Do not introduce:

```text
SQLAlchemy models as Domain entities

Session access inside Aggregate methods

Repository.commit()

Repository-created Engine

global Session singleton

lazy database access from Domain behavior

raw SQLAlchemy exceptions as public application errors

database-specific logic inside Repository Ports

SQLite-only assumptions presented as PostgreSQL guarantees

generic CRUD repositories that erase Aggregate semantics
```

---

# 76. Cycle risk register

| Risk | Consequence | Mitigation |
|---|---|---|
| ORM leaks into Domain | architecture erosion | fitness tests |
| Repository auto-commit | broken atomicity | transaction tests |
| SQLite hides PostgreSQL differences | false confidence | PostgreSQL integration gate |
| Duplicate mapping code | maintenance cost | targeted mapper helpers only after repetition |
| Over-generic repository abstraction | lost domain semantics | keep Aggregate-specific Ports |
| Premature UnitOfWork | ceremony | introduce only at multi-repository atomicity pressure |
| Migration drift | unreproducible schema | Alembic baseline + migration tests |
| Lazy loading leaks | hidden SQL in Domain | explicit Aggregate reconstruction |
| Constraint mismatch | race-condition bugs | SQL-specific integration tests |
| CI becomes slow | poor feedback | stratified test suite |
| Persistence rewrites Domain | cycle failure | Domain remains source of business semantics |

---

# 77. Architecture decision log for the cycle

The Persistent Core begins with these decisions:

```text
ADR-PERSIST-001
SQLAlchemy for relational persistence.

ADR-PERSIST-002
Domain and SQLAlchemy persistence models remain separate.

ADR-PERSIST-003
SQLite is a local/contract backend.

ADR-PERSIST-004
PostgreSQL is the production-oriented reference backend.

ADR-PERSIST-005
One SQLAlchemy repository family is preferred across dialects.

ADR-PERSIST-006
Repositories never commit.

ADR-PERSIST-007
One Session is scoped to one application transaction.

ADR-PERSIST-008
UnitOfWork waits for real multi-repository transaction pressure.

ADR-PERSIST-009
Domain Events dispatch only after successful commit.

ADR-PERSIST-010
Alembic owns relational schema migration history.

ADR-PERSIST-011
Pure Core remains usable without persistence dependencies.
```

---

# 78. Current implementation status

At the time this cycle document is created:

```text
0.2.0a1 - Persistence Foundation
    QUALIFIED

0.2.0a2 - Supplier + Relationship SQL Persistence
    IN PROGRESS

0.2.0a3 - Onboarding + Assessment SQL Persistence
    PLANNED

0.2.0a4 - Qualification SQL Persistence
    PLANNED

0.2.0a5 - Transaction Boundary / UnitOfWork
    PLANNED

0.2.0a6 - Alembic Migration Baseline
    PLANNED

0.2.0a7 - Persistent Local Qualification
    PLANNED
```

This status is informative.

Each milestone qualification document remains the authoritative implementation evidence.

---

# 79. Milestone progress model

Each alpha milestone follows:

```text
Read cycle/spec decisions
        |
        v
Implement minimum scoped capability
        |
        v
Run shared contracts
        |
        v
Run SQL-specific failure tests
        |
        v
Run architecture gates
        |
        v
Observe friction
        |
        v
refine design/spec only if necessary
        |
        v
qualify milestone
        |
        v
merge to main
```

---

# 80. Cycle product narrative

The Persistent Core tells a simple story:

```text
We already know the supplier business journey.
        |
        v
Now we preserve it durably.
        |
        v
We prove repository substitution.
        |
        v
We add real relational constraints.
        |
        v
We make multi-Aggregate operations atomic.
        |
        v
We make the schema reproducible.
        |
        v
We restart the runtime.
        |
        v
The same business state comes back.
```

---

# 81. Final persistent scenario - success

The final success scenario should prove:

```text
Supplier registered
Relationship created
Relationship invited
Onboarding started
mandatory requirement satisfied
Onboarding completed
Assessment created
answer recorded
Assessment completed
Qualification requested
Qualification evaluated
final status = QUALIFIED
transaction committed
runtime persistence context destroyed
new persistence context created
all relevant Aggregates reloaded
qualification decision still QUALIFIED
decision reasons/state preserved
```

---

# 82. Final persistent scenario - rejection

The final rejection scenario should prove:

```text
same persistent journey
        |
        v
insufficient assessment evidence
        |
        v
QualificationDecision.approved = False
        |
        v
NOT_QUALIFIED
        |
        v
commit
        |
        v
reload
        |
        v
same failed requirements preserved
```

---

# 83. Final persistent event semantics

The cycle must preserve meaningful event ordering.

Successful path:

```text
business transition
    |
    v
event recorded
    |
    v
database state staged
    |
    v
commit succeeds
    |
    v
event dispatched
```

Failure path:

```text
business transition
    |
    v
event recorded
    |
    v
database operation fails
    |
    v
rollback
    |
    v
event NOT dispatched
```

---

# 84. End-of-cycle architecture review questions

At the end of `0.2.0a7`, review:

```text
Did Domain stay persistence-ignorant?

Did Repository Ports survive unchanged?

Did SQLite and PostgreSQL fit one SQLAlchemy adapter family?

Did any dialect require a real adapter split?

Did UnitOfWork become justified?

Did transaction boundaries remain clear?

Did event dispatch ordering remain correct?

Did migrations remain infrastructure-owned?

Did contract tests catch adapter divergence?

Did persistent reload preserve business meaning?

Did any new abstraction feel forced?

What is the next real product pressure?
```

---

# 85. Candidate post-Persistent-Core directions

Only after the cycle is complete should the next direction be selected.

Candidates may include:

```text
Activation
Documents & Evidence
Compliance
Risk
Public API
External SRM integration
Audit
Observability
```

No next cycle is preselected here.

---

# 86. What would count as cycle failure

The Persistent Core should be considered architecturally unsuccessful if implementation requires any of the following without compelling evidence:

```text
Domain imports SQLAlchemy

Application manipulates Session directly

Repository Ports expose SQLAlchemy types

Domain behavior triggers lazy SQL

Repositories commit independently

SQLite tests replace PostgreSQL validation completely

business invariants are removed from Domain only to satisfy ORM limitations

generic CRUD abstractions replace Aggregate-specific Repository semantics
```

If such pressure appears, stop and review rather than normalize the leak.

---

# 87. What would count as cycle success

Cycle success is not:

```text
"SQLAlchemy works."
```

It is:

```text
"The original business architecture still works
after real relational persistence is introduced."
```

That means:

```text
same Domain
same Application intent
same Repository Ports
same business invariants
same qualification meaning
new durable Adapter
real transaction semantics
reproducible schema
```

---

# 88. Persistent Core Definition of Done

```text
PERSISTENT CORE
|
+-- Domain remains persistence-ignorant
|
+-- SQLAlchemy adapter family complete
|
+-- SQLite Repository Contracts green
|
+-- PostgreSQL Repository Contracts green
|
+-- Supplier persisted
|
+-- Relationship persisted
|
+-- Onboarding persisted
|
+-- Assessment persisted
|
+-- Qualification persisted
|
+-- relational constraints proven
|
+-- multi-repository atomicity proven
|
+-- rollback proven
|
+-- post-commit event dispatch proven
|
+-- Alembic baseline proven
|
+-- restart/reload scenario proven
|
+-- success and rejection paths proven
|
+-- full architecture gates green
|
+-- full regression suite green
|
`-- persistent end-to-end qualification green
```

---

# 89. Exit gate

The Persistent Core cycle exits only when:

> **PySRMKit can run the complete qualification journey against relational persistence, commit it safely, recreate its runtime persistence context, reload the required Aggregates, and preserve the same final business decision while Domain, Application, and Repository Ports remain free from persistence-framework dependencies.**

---

# 90. Final principle

> **The first Core proved the business architecture in memory.**

> **The Persistent Core must prove the same architecture under durable relational constraints.**

> **SQLite accelerates the learning loop.**

> **PostgreSQL validates production-oriented relational behavior.**

> **Repository Contracts prove substitution.**

> **Transactions create the real pressure for UnitOfWork.**

> **Migrations make persistence reproducible.**

> **The Domain must still not know that SQL exists.**