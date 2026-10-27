# PySRMKit - Public API and Runtime Composition Architecture

**Document:** `19_PYSRMKIT_PUBLIC_API_AND_RUNTIME_COMPOSITION_ARCHITECTURE.md`  
**Status:** TARGETED CYCLE 3 ARCHITECTURE SPECIFICATION  
**Architecture cycle:** `0.3.x - Public API & Runtime Composition`  
**Previous checkpoint:** `18_PYSRMKIT_POST_PERSISTENCE_ARCHITECTURE_REVIEW.md`  
**Date:** 2026-10-27

---

# 1. Purpose

This document defines the architecture boundary for the third PySRMKit implementation cycle.

The Persistent Core is complete.

PySRMKit can now:

~~~text
model Supplier business concepts
execute the complete qualification journey
persist that journey
commit it transactionally
migrate an empty database
destroy the original persistence context
reload durable business state
produce the same qualification decision
~~~

The strongest remaining pressure is no longer persistence.

It is **consumption**.

Today the framework works, but a consumer who wants to execute the stable Supplier qualification use cases must understand too many internal modules:

~~~text
Application Handlers
Commands
Repository adapters
SQLAlchemy Engine
Session factory
UnitOfWork
Clock
Event dispatcher
Deferred event dispatcher
QualificationPolicy
transaction commit/publish choreography
~~~

This document defines the next architecture boundary:

~~~text
Consumer
    ↓
Public Python API
    ↓
Runtime / Composition
    ↓
Application
    ↓
Ports
    ↓
Adapters
~~~

The goal is not to hide the Domain.

The goal is to expose it intentionally.

---

# 2. Governing rules

The Cycle 3 rules remain:

> **Problem before Pattern.**

> **Public API before transport API.**

> **Stable business language before generic execution abstractions.**

> **Runtime composition may hide infrastructure wiring; it must not hide business meaning.**

> **Do not make internal package structure part of the consumer contract accidentally.**

---

# 3. Evidence from the current implementation

The current local scenario manually assembles:

~~~text
InMemorySupplierRepository
InMemorySupplierRelationshipRepository
InMemorySupplierOnboardingRepository
InMemorySupplierAssessmentRepository
InMemorySupplierQualificationRepository
FixedClock
InProcessDomainEventDispatcher
QualificationPolicy
Application Handlers
~~~

The persistent scenario additionally assembles:

~~~text
Alembic bootstrap
SQLAlchemy Engine
Session factory
SqlAlchemySupplierRepository
SqlAlchemySupplierRelationshipRepository
SqlAlchemySupplierOnboardingRepository
SqlAlchemySupplierAssessmentRepository
SqlAlchemySupplierQualificationRepository
SqlAlchemySupplierOnboardingUnitOfWork
DeferredDomainEventDispatcher
commit / rollback / publish choreography
~~~

That assembly is valuable as an architecture qualification artifact.

It is too infrastructure-aware to be the normal consumer experience.

---

# 4. Problem statement

The framework currently has two properties:

~~~text
internally coherent
    +
externally verbose
~~~

A consumer who only wants to:

~~~text
register Supplier
create Relationship
invite Relationship
start Onboarding
complete Onboarding
record Assessment
request Qualification
evaluate Qualification
~~~

should not have to import concrete repositories or manage a SQLAlchemy Session directly.

The Public API cycle must therefore solve:

~~~text
stable consumer imports
stable business operations
runtime construction
transaction ownership
event publication ordering
optional persistence selection
public result types
public error types
lifecycle ownership
~~~

---

# 5. Non-goals

This cycle does **not** automatically introduce:

~~~text
FastAPI
Django
GraphQL
CLI framework
Command Bus
Query Bus
Mediator
Service Locator
DI container
global UnitOfWork
AsyncSession
async runtime
Transactional Outbox
Kafka
RabbitMQ
Redis
workflow engine
generic CRUD service
generic execute(action, payload)
~~~

These remain separate decisions.

---

# 6. Public API is not HTTP API

The first Public API is a Python API.

The dependency direction is:

~~~text
Python consumer
      ↓
PySRMKit public API
      ↓
Application use cases
      ↓
Ports
      ↓
Adapters
~~~

A future transport adapter may then depend on that stable surface:

~~~text
FastAPI
Django
CLI
Notebook
Agent
External Integration
      ↓
Public PySRMKit API
~~~

HTTP must not become the canonical business interface merely because it is familiar.

---

# 7. Public surface design objectives

The public API should be:

~~~text
small
stable
intentional
documented
typed
business-named
predictable
adapter-agnostic by default
~~~

It should avoid requiring knowledge of:

~~~text
repository concrete classes
SQLAlchemy records
SQLAlchemy Session
Engine internals
mapper functions
Alembic Config objects
adapter package layout
test-only composition details
~~~

---

# 8. Public versus internal contract

Cycle 3 introduces an explicit distinction.

## Public

A symbol is public when PySRMKit intentionally supports consumer use of it.

Public symbols become compatibility-sensitive.

Examples may include:

~~~text
PySRMKit
create_in_memory_runtime
create_sql_runtime
public command input types
public result types
public view types
public business IDs
public enums
public errors
selected Domain Events
~~~

## Internal

A symbol may be importable without being public.

Examples:

~~~text
SqlAlchemySupplierRepository
SupplierOnboardingUnitOfWork implementation
mapper helper
PersistenceBase
SQLAlchemy Record
private composition helper
internal Handler factory
~~~

Internal modules may evolve more freely during `0.x`.

---

# 9. Public namespace strategy

The package should expose a deliberately small top-level surface.

Target direction:

~~~python
from pysrmkit import PySRMKit
from pysrmkit import create_in_memory_runtime
~~~

Adapter-specific construction should remain explicit:

~~~python
from pysrmkit.runtime.sql import create_sql_runtime
~~~

The base package must not import SQLAlchemy merely because:

~~~python
import pysrmkit
~~~

was executed.

This preserves the existing optional-dependency architecture.

---

# 10. Why not export everything from `pysrmkit`

A very broad top-level namespace creates accidental compatibility promises.

Avoid:

~~~python
from pysrmkit import (
    Supplier,
    SupplierRelationship,
    SupplierQualification,
    SqlAlchemySupplierRepository,
    SupplierOnboardingUnitOfWork,
    ...
)
~~~

as the default strategy.

The top-level namespace should expose the smallest stable entry points.

Capability-specific public types may live below intentional public modules.

---

# 11. Proposed public package shape

Candidate Cycle 3 shape:

~~~text
src/pysrmkit/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── suppliers.py
│   ├── relationships.py
│   ├── onboarding.py
│   ├── assessments.py
│   ├── qualifications.py
│   ├── events.py
│   └── errors.py
├── runtime/
│   ├── __init__.py
│   ├── in_memory.py
│   └── sql.py
├── domain/
├── application/
├── ports/
└── adapters/
~~~

This is an architecture direction, not a requirement to move every existing type immediately.

---

# 12. Why a separate `api/` namespace

The current package layout reflects implementation layers.

Consumers need a business-oriented stable surface.

The `api/` namespace may therefore re-export or wrap selected stable types without forcing the internal layer structure to become permanent public contract.

Conceptually:

~~~text
internal package layout
    may evolve

public API namespace
    remains stable
~~~

This is an application of Information Hiding at package level.

---

# 13. Public facade decision

Cycle 3 should introduce a root facade:

~~~text
PySRMKit
~~~

The facade is justified now because:

~~~text
use cases are implemented
persistence is qualified
runtime wiring is repetitive
consumer pressure is real
~~~

The facade must not become a God Object containing arbitrary infrastructure behavior.

Its role is:

~~~text
stable access point
to capability-oriented public APIs
~~~

---

# 14. Capability-oriented facade

Prefer:

~~~python
srm.suppliers.register(...)
srm.relationships.create(...)
srm.relationships.invite(...)
srm.onboarding.satisfy_requirement(...)
srm.onboarding.complete(...)
srm.assessments.create(...)
srm.assessments.record_answer(...)
srm.assessments.complete(...)
srm.qualifications.request(...)
srm.qualifications.evaluate(...)
~~~

over one flat root object containing dozens of unrelated methods.

This preserves the domain vocabulary already present in the internal architecture.

---

# 15. Why not `execute(action, payload)`

Avoid making the canonical API:

~~~python
srm.execute(
    action="evaluate_qualification",
    payload={...},
)
~~~

because this would erase:

~~~text
typing
discoverability
business intent
specific results
specific errors
capability vocabulary
~~~

A future generic integration adapter may translate external messages into explicit public operations.

The public API itself should remain explicit.

---

# 16. Commands versus facade methods

The existing Application Commands remain useful implementation types.

Cycle 3 should support two consumer levels.

## Primary surface

Capability methods:

~~~python
srm.suppliers.register(...)
~~~

## Advanced explicit surface

Selected public command/result types may be re-exported:

~~~python
from pysrmkit.api.suppliers import RegisterSupplier
~~~

This allows framework-style and explicit application-style use without forcing internal module imports.

---

# 17. Do Commands become stable API?

Not automatically every existing Command.

The rule should be:

~~~text
public command
    =
explicitly re-exported
documented
covered by public API tests
~~~

An internal Application Command remains internal unless promoted intentionally.

This prevents accidental API freezing.

---

# 18. Domain types in the public API

Some Domain types are already natural consumer vocabulary.

Examples:

~~~text
SupplierId
SupplierRelationshipId
AssessmentId
QualificationId
InternalOrganizationId
QualificationScope
QualificationStatus
SupplierLifecycleStage
CategoryCode
CountryCode
~~~

These should be reviewed individually for public promotion.

Promotion criteria:

~~~text
appears in stable use-case inputs/outputs
business meaning is clear
not persistence-specific
not implementation-only
unlikely to be replaced by infrastructure detail
~~~

---

# 19. Domain Aggregates as public return values

The primary public API should not require returning mutable Aggregate Roots from every operation.

Reasons:

~~~text
Aggregate behavior may evolve
internal event buffers exist
direct mutation can bypass runtime transaction ownership
consumer could save nothing after mutation
persistence lifecycle becomes ambiguous
~~~

Preferred default:

~~~text
commands
    -> explicit public result

queries
    -> immutable public view / snapshot
~~~

Aggregate objects may remain available to advanced internal consumers, but they should not be the default facade contract.

---

# 20. Command result strategy

Existing Application results should be reused where they already represent stable use-case outcomes.

Example shape:

~~~text
RegisterSupplierResult
    supplier_id

CreateSupplierRelationshipResult
    relationship_id

CreateSupplierAssessmentResult
    assessment_id

RequestSupplierQualificationResult
    qualification_id
~~~

If an existing result already has the correct public semantics, re-export it.

Do not create duplicate DTOs merely to rename the same information.

---

# 21. Query result strategy

Public query methods should prefer immutable views.

Example candidate:

~~~text
SupplierQualificationView
├── qualification_id
├── relationship_id
├── scope
├── status
├── approved
├── reasons
├── failed_requirements
└── decided_at
~~~

The view represents consumer-readable state.

It should not contain:

~~~text
SQLAlchemy Record
Session
lazy relationship
query object
ORM proxy
~~~

---

# 22. CQRS posture

The project already uses a CQRS-lite style.

Cycle 3 should preserve:

~~~text
commands
    change business state

queries
    return read-oriented views
~~~

This does **not** justify:

~~~text
Command Bus
Query Bus
separate read database
projection infrastructure
event-driven read models
~~~

The public API can express command/query separation directly.

---

# 23. Public error boundary

The public API must not leak raw infrastructure exceptions as its normal contract.

Avoid exposing:

~~~text
sqlalchemy.exc.IntegrityError
sqlalchemy.exc.OperationalError
psycopg.Error
DBAPIError
~~~

directly to a normal PySRMKit consumer.

The public boundary should translate infrastructure failures when stable meaning exists.

---

# 24. Error categories

The smallest useful public taxonomy is likely:

~~~text
PySRMKitError
├── Domain / business errors
├── Application use-case errors
└── Infrastructure-facing stable errors
~~~

Existing Domain and Application errors should not be wrapped gratuitously if they already express correct consumer semantics.

Infrastructure errors need a stable public representation only where the consumer must react.

---

# 25. Public persistence errors

Candidate minimal types:

~~~text
PersistenceError
PersistenceUnavailable
PersistenceConflict
~~~

Do not add a large hierarchy before concrete cases justify it.

Examples:

~~~text
database unreachable
    -> PersistenceUnavailable

known relational uniqueness conflict
that maps to a business conflict
    -> existing Application conflict

unexpected persistence failure
    -> PersistenceError
~~~

---

# 26. Error translation location

Infrastructure translation belongs in:

~~~text
runtime / adapter boundary
~~~

not in:

~~~text
Domain
Repository Port
business Aggregate
~~~

A SQL runtime may catch infrastructure exceptions because it knows the technology.

The Application layer should not import SQLAlchemy exception classes.

---

# 27. Runtime concept

A Runtime is the assembled execution environment for public PySRMKit use cases.

Conceptually:

~~~text
PySRMKit Runtime
├── business facade
├── repositories/adapters
├── clock
├── policies
├── transaction strategy
└── event dispatch strategy
~~~

The runtime owns wiring.

The Domain remains unaware that a runtime exists.

---

# 28. Runtime is not a DI container

The Runtime has a specific purpose:

~~~text
assemble the known PySRMKit application
~~~

It is not a generic object registry.

Avoid:

~~~python
runtime.resolve(SupplierRepository)
runtime.get_service("qualification")
runtime.container["repository"]
~~~

unless a future integration genuinely requires such behavior.

Constructor composition should remain explicit internally.

---

# 29. Runtime variants

Cycle 3 needs two runtime families because they already correspond to qualified behavior.

~~~text
InMemory Runtime
SQL Runtime
~~~

Both must expose the same primary public capability surface.

This is the consumer-level equivalent of the existing Repository substitution strategy.

---

# 30. InMemory Runtime

Candidate creation:

~~~python
from pysrmkit import create_in_memory_runtime

with create_in_memory_runtime() as srm:
    ...
~~~

The InMemory Runtime owns:

~~~text
InMemory repositories
Clock
QualificationPolicy
InProcessDomainEventDispatcher
capability API objects
~~~

It requires no database.

---

# 31. Why keep InMemory public

InMemory is useful beyond tests.

It supports:

~~~text
examples
notebooks
teaching
prototyping
local deterministic scenarios
consumer integration tests
framework evaluation
~~~

Making SQL the only public runtime would discard a proven capability.

---

# 32. SQL Runtime

Candidate creation:

~~~python
from pysrmkit.runtime.sql import create_sql_runtime

with create_sql_runtime(
    database_url="postgresql+psycopg://..."
) as srm:
    ...
~~~

The SQL Runtime owns infrastructure composition so the normal consumer does not have to assemble repositories manually.

---

# 33. Optional dependency rule

The following must remain valid without SQL dependencies:

~~~python
import pysrmkit
from pysrmkit import create_in_memory_runtime
~~~

Importing these must not require:

~~~text
SQLAlchemy
Alembic
Psycopg
~~~

Only SQL runtime modules may require the optional persistence extras.

---

# 34. SQL Runtime and Engine ownership

Initial Cycle 3 direction:

~~~text
create_sql_runtime(database_url)
    ↓
runtime creates Engine
    ↓
runtime owns Engine lifecycle
~~~

The runtime therefore disposes the Engine when closed.

This gives the public API one clear ownership model.

---

# 35. External Engine injection

Supporting:

~~~python
create_sql_runtime(engine=my_engine)
~~~

may become useful for host applications.

It should not be mandatory in the first milestone.

Reason:

~~~text
external Engine ownership
pool ownership
disposal responsibility
host framework integration
~~~

introduce extra lifecycle semantics.

**Initial decision:** URL-owned runtime first. Revisit external Engine injection when a real host application requires it.

---

# 36. SQL Runtime and Session scope

The public SQL Runtime should not expose one long-lived mutable Session as its business execution context.

Preferred default:

~~~text
one command
    ↓
one application transaction
    ↓
one Session scope
    ↓
commit / rollback
    ↓
close Session
~~~

Queries similarly receive short-lived Session scopes.

This reduces persistence-context leakage into the facade.

---

# 37. Session-per-use-case rule

For ordinary single-transaction commands:

~~~text
public capability method
    ↓
open Session
    ↓
construct SQL repositories
    ↓
construct Handler
    ↓
execute Handler
    ↓
commit
    ↓
publish buffered events
    ↓
close Session
~~~

This runtime choreography should replace the manual pattern visible in `examples/persistent_qualification.py`.

---

# 38. Repository lifetime

SQL Repository objects are use-case-scoped.

They should not become long-lived facade fields holding a Session indefinitely.

Conceptually:

~~~text
PySRMKit runtime
    long-lived

Session
    short-lived

Repository instances
    short-lived with Session
~~~

---

# 39. Capability UnitOfWork inside SQL Runtime

`StartSupplierOnboarding` already has its own justified transaction boundary.

The runtime should reuse:

~~~text
SqlAlchemySupplierOnboardingUnitOfWork
~~~

rather than bypassing it.

The facade should not care whether a command internally uses:

~~~text
one Repository
or
capability UnitOfWork
~~~

The public operation contract remains business-oriented.

---

# 40. Global UnitOfWork remains unnecessary

Runtime composition does not justify replacing every operation with a global UnitOfWork.

The runtime can orchestrate:

~~~text
single-repository command
    -> Session transaction

multi-Aggregate onboarding command
    -> capability UnitOfWork
~~~

This keeps the existing evidence-driven design.

---

# 41. Transaction success semantics

For SQL commands:

~~~text
Handler succeeds
    +
database commit succeeds
        =
public operation succeeds
~~~

If commit fails:

~~~text
rollback
discard buffered events
translate infrastructure error if appropriate
raise public error
~~~

The public facade must never report successful completion before durability is known.

---

# 42. Event publication semantics

The SQL Runtime should preserve:

~~~text
Domain behavior
    ↓
Repository save
    ↓
database COMMIT
    ↓
publish in-process Domain Events
~~~

For single-repository operations:

~~~text
DeferredDomainEventDispatcher
~~~

may remain the runtime mechanism.

For the onboarding UnitOfWork, runtime behavior must preserve the existing post-commit ordering.

---

# 43. Event subscription surface

Cycle 3 may expose public subscription for selected Domain Events.

Candidate direction:

~~~python
srm.events.subscribe(SupplierQualified, handler)
~~~

but event subscription should not block the first runtime milestone.

Events promoted to public subscription contracts must be explicitly documented and tested.

---

# 44. Event compatibility

A public Domain Event becomes a consumer contract.

Therefore changing:

~~~text
event name
event fields
field meaning
delivery timing
~~~

becomes compatibility-sensitive.

Do not re-export every internal event automatically.

---

# 45. Outbox remains outside Runtime v1

The public runtime must document that event delivery is:

~~~text
in-process
post-commit
non-durable across process crash
~~~

Do not imply:

~~~text
at-least-once
exactly-once
durable broker delivery
~~~

unless a future Outbox/integration cycle implements those guarantees.

---

# 46. Clock ownership

The Runtime owns the default Clock adapter.

Production default:

~~~text
SystemClock
~~~

Tests/examples may inject:

~~~text
FixedClock
~~~

Clock injection is useful because deterministic qualification timestamps are already proven in tests.

---

# 47. Public clock configuration

The first runtime API may allow an advanced optional Clock override:

~~~python
create_in_memory_runtime(clock=my_clock)
~~~

and equivalent SQL construction.

The type exposed should be the technology-agnostic Clock Port, not a concrete infrastructure concept.

This is one Port with demonstrated consumer/testing value.

---

# 48. QualificationPolicy ownership

The Runtime owns the default QualificationPolicy configuration.

Current stable fact:

~~~text
minimum_assessment_score
~~~

The public runtime may accept a policy or policy configuration explicitly.

Do not introduce a Policy Factory hierarchy until multiple real policies exist.

---

# 49. Policy customization

Two possible public forms exist:

~~~text
A. inject QualificationPolicy
B. pass Qualification configuration
~~~

Initial preference:

~~~text
inject explicit policy object
~~~

because a real replaceable policy object already exists.

Avoid speculative configuration DSL.

---

# 50. Migration ownership

Runtime construction must not silently run Alembic migrations.

Avoid:

~~~text
create_sql_runtime(...)
    -> mutates schema automatically
~~~

Reasons:

~~~text
runtime startup
deployment
migration permissions
schema change
application execution
~~~

are different responsibilities.

---

# 51. Explicit migration operation

Schema migration remains an explicit deployment/administration operation.

The first public SQL Runtime may assume:

~~~text
required schema already exists
~~~

The existing Alembic command remains valid.

A later adapter-specific public helper may be introduced if repeated consumer pressure appears.

---

# 52. Runtime schema validation

Do not add elaborate schema-version negotiation in the first Cycle 3 milestone.

If runtime startup needs a simple compatibility check later, introduce it from real failure pressure.

For now:

~~~text
migration responsibility
    explicit

runtime responsibility
    execute business operations
~~~

---

# 53. Runtime context-manager semantics

Both runtime families should support:

~~~python
with create_in_memory_runtime() as srm:
    ...

with create_sql_runtime(...) as srm:
    ...
~~~

This gives a consistent lifecycle model.

For InMemory:

~~~text
close
    minimal/no-op cleanup
~~~

For SQL:

~~~text
close
    dispose owned Engine
    release runtime resources
~~~

---

# 54. Explicit `close()`

A context manager should not prevent explicit lifecycle management.

Candidate contract:

~~~python
srm.close()
~~~

Runtime close should be:

~~~text
safe
idempotent if practical
not silently commit pending business work
~~~

---

# 55. No hidden global Runtime

Avoid:

~~~text
module-level singleton runtime
global Engine
global Session
global current PySRMKit
~~~

Runtime construction must remain explicit.

This preserves:

~~~text
test isolation
multi-runtime usage
clear ownership
no import side effects
~~~

---

# 56. Multiple runtimes

It should be valid to create:

~~~text
one InMemory Runtime
one SQLite Runtime
one PostgreSQL Runtime
~~~

inside the same Python process.

No global mutable configuration should make them interfere.

---

# 57. Thread-safety posture

Do not promise Runtime thread safety before it is qualified.

Session-per-use-case avoids one obvious shared-Session problem, but full thread-safety guarantees require explicit testing.

**Initial contract:** no stronger concurrency guarantee than tested.

---

# 58. Async posture

Cycle 3 Public API is synchronous.

Do not create:

~~~text
async def facade methods
AsyncEngine
AsyncSession
dual sync/async API
~~~

until a real asynchronous consumer requires it.

Adding an async mirror prematurely doubles the public compatibility surface.

---

# 59. Public ID types

Strong IDs should remain strong across the public boundary.

Prefer:

~~~python
SupplierId
SupplierRelationshipId
QualificationId
~~~

over reducing everything to untyped:

~~~python
str
~~~

inside the Python API.

Transport adapters may serialize them later.

---

# 60. Public enum types

Public Python consumers should receive meaningful enums such as:

~~~text
QualificationStatus
SupplierLifecycleStage
~~~

rather than database strings.

This preserves domain language and type safety.

---

# 61. Primitive-friendly input convenience

The facade may accept simple Python primitives for ergonomics when ambiguity is low.

Example candidate:

~~~python
srm.suppliers.register(
    legal_name="ACME",
    country_code="FR",
)
~~~

Internally it may build explicit command/value objects.

Do not force every simple consumer to manually construct every Value Object if the facade can validate the same semantics.

---

# 62. Where strong input types remain necessary

Use explicit Value Objects where primitive input would lose meaning.

Examples:

~~~text
QualificationScope
SupplierRelationshipId
CategoryCode
InternalOrganizationId
~~~

The API should balance ergonomics with semantic precision.

---

# 63. Public capability: Suppliers

First stable capability surface should cover the already-qualified Supplier use cases.

Candidate:

~~~text
SuppliersAPI
├── register(...)
└── get(...)
~~~

Do not invent update/search capabilities that do not yet have qualified Application use cases.

---

# 64. Public capability: Relationships

Candidate:

~~~text
RelationshipsAPI
├── create(...)
├── invite(...)
└── get(...)
~~~

`start_onboarding(...)` may remain under Relationships because the intent is a Relationship lifecycle transition, even though it creates an Onboarding Aggregate.

That mirrors the current Application command.

---

# 65. Public capability: Onboarding

Candidate:

~~~text
OnboardingAPI
├── get_for_relationship(...)
├── satisfy_requirement(...)
└── complete(...)
~~~

The API should expose business operations rather than direct collection mutation.

---

# 66. Public capability: Assessments

Candidate:

~~~text
AssessmentsAPI
├── create(...)
├── record_answer(...)
├── complete(...)
└── get(...)
~~~

No generic questionnaire engine is introduced.

---

# 67. Public capability: Qualifications

Candidate:

~~~text
QualificationsAPI
├── request(...)
├── evaluate(...)
├── get(...)
└── get_current_for_scope(...)
~~~

The stable outcome must preserve explainable decision data.

---

# 68. Public queries must not leak Repository abstractions

Avoid requiring consumers to call:

~~~python
srm.repositories.qualifications.find_current_for_scope(...)
~~~

Repository language remains internal architecture.

Public queries should use business capability vocabulary.

---

# 69. Public views

Candidate immutable public views:

~~~text
SupplierView
SupplierRelationshipView
OnboardingView
AssessmentView
QualificationView
~~~

Each view should contain only consumer-relevant state.

Views should be:

~~~text
immutable
typed
serializable by normal adapters
ORM-independent
free of lazy loading
~~~

---

# 70. View construction

Views may be built from Domain Aggregates at the public boundary.

Conceptually:

~~~text
Repository
    ↓
Domain Aggregate
    ↓
public view mapper
    ↓
Consumer
~~~

Do not build views directly from ORM rows in the primary runtime if that bypasses Domain reconstruction semantics without demonstrated performance pressure.

---

# 71. Query optimization is deferred

The first public views may use Aggregate repositories.

If later UI/API workloads expose:

~~~text
large lists
cross-Aggregate search
reporting
pagination
sorting
analytics
N+1 pressure
~~~

then a dedicated query/read-model architecture may become justified.

Do not introduce it before those queries exist.

---

# 72. Public API and semantic versioning

Cycle 3 is still `0.x`, but public symbols should nonetheless be treated intentionally.

A public API change must be classified as:

~~~text
additive
compatible refinement
breaking
deprecated
removed
~~~

This creates discipline before `1.0`.

---

# 73. Internal imports remain unsupported

Documentation should state that:

~~~text
pysrmkit.adapters.*
pysrmkit.application.*
internal mapper modules
SQLAlchemy records
~~~

are implementation surfaces unless explicitly documented otherwise.

Advanced users may still import them during `0.x`, but they should not expect the same compatibility guarantees.

---

# 74. Deprecation posture

Before `1.0`, deprecation can remain lightweight.

For intentionally public symbols:

~~~text
prefer deprecation warning
document replacement
keep at least one alpha/minor transition when practical
~~~

Do not build a complex deprecation framework now.

---

# 75. Typing contract

The public API should remain fully typed under Pyright strict.

Consumer-facing signatures should avoid:

~~~text
Any
dict[str, object] as generic payload
untyped callback
untyped error details
~~~

when the business type is known.

---

# 76. `py.typed`

Cycle 3 should ship:

~~~text
src/pysrmkit/py.typed
~~~

once the public typed surface is introduced.

This declares that installed type information is intentional for type checkers.

---

# 77. Public API tests

Add a dedicated test layer:

~~~text
tests/public_api/
~~~

It should validate:

~~~text
documented imports
top-level exports
public capability methods
public result types
public errors
runtime lifecycle
optional dependency behavior
no import side effects
~~~

---

# 78. Stable import tests

Examples:

~~~python
from pysrmkit import PySRMKit
from pysrmkit import create_in_memory_runtime
from pysrmkit.api.qualifications import QualificationStatus
~~~

These imports become executable compatibility contracts.

---

# 79. Negative public-surface tests

Where practical, tests should ensure top-level imports do not accidentally expose technology-specific internals.

For example:

~~~text
top-level public package
    should not require SQLAlchemy
~~~

A pure-core installation must remain usable.

---

# 80. InMemory public scenario

Cycle 3 qualification must reproduce the existing successful and rejected qualification journeys using only public imports.

The test must not import:

~~~text
internal repositories
internal handlers
internal mapper modules
~~~

Expected shape:

~~~text
create public InMemory Runtime
    ↓
execute public business operations
    ↓
QUALIFIED / NOT_QUALIFIED
~~~

---

# 81. SQL public scenario

A SQL Runtime qualification must reproduce the same journey using only:

~~~text
public PySRMKit API
adapter-specific SQL runtime constructor
public business types
~~~

The test must not manually assemble repositories.

---

# 82. Persistent restart through public Runtime

The final SQL public scenario should still prove:

~~~text
Runtime A
    ↓
business journey
    ↓
close Runtime A
    ↓
Runtime B
    ↓
reload views
    ↓
same decision
~~~

This ensures the facade does not accidentally weaken the Persistent Core proof.

---

# 83. PostgreSQL public Runtime qualification

PostgreSQL remains required for the final persistent public runtime qualification.

SQLite-only green is not enough for the SQL Runtime milestone.

The same public consumer code should operate against:

~~~text
SQLite
PostgreSQL
~~~

with only the database URL differing.

---

# 84. Public event tests

If public event subscription is introduced, tests must prove:

~~~text
event type
event order
post-commit timing
rejection versus success distinction
no event after failed commit
~~~

This is a compatibility contract, not merely internal behavior.

---

# 85. Runtime failure tests

SQL runtime tests should include at least:

~~~text
commit failure
rollback
buffered event discard
runtime cleanup
public persistence error translation
~~~

These already have lower-level evidence and should remain true through the public facade.

---

# 86. Optional dependency tests

The package should be tested in two installation modes.

## Pure

~~~text
pysrmkit
~~~

Expected:

~~~text
import works
InMemory Runtime works
SQL runtime import/use fails clearly only when selected
~~~

## Persistence

~~~text
pysrmkit[persistence]
or
pysrmkit[postgresql]
~~~

Expected:

~~~text
SQL Runtime available
~~~

---

# 87. Missing optional dependency error

If a consumer tries to select SQL runtime without SQLAlchemy installed, avoid an obscure deep import traceback if practical.

Prefer a clear message explaining the required extra.

Example conceptual behavior:

~~~text
SQL runtime requires PySRMKit persistence dependencies.
Install pysrmkit[persistence].
~~~

The exact exception type can be defined during implementation.

---

# 88. Configuration boundary

Runtime configuration belongs at composition level.

Allowed inputs may include:

~~~text
database URL
Clock override
QualificationPolicy override
event subscriber registration
safe SQL engine options when justified
~~~

Domain and Application modules must not read environment variables directly.

---

# 89. Environment variables

The Runtime constructor should not require environment-variable access internally.

A host application may do:

~~~python
database_url = os.environ["DATABASE_URL"]
srm = create_sql_runtime(database_url=database_url)
~~~

This keeps configuration acquisition outside the framework Core.

---

# 90. Credentials and logging

The SQL Runtime must not log full database URLs containing credentials by default.

Existing security principles remain.

No new observability dependency is needed.

---

# 91. Logging posture

The public Runtime may use standard Python logging later if useful.

Do not make logging configuration a first milestone requirement.

The host application should retain control over logging policy.

---

# 92. Runtime observability

Do not add metrics/tracing abstractions before a production consumer requires them.

A future primary adapter may wrap the public API with:

~~~text
logging
metrics
tracing
audit
~~~

without forcing those concerns into Domain behavior.

---

# 93. Public API and framework adapters

A future FastAPI adapter should depend on:

~~~text
Public PySRMKit API
~~~

not:

~~~text
SQLAlchemy repositories directly
internal Handlers directly
ORM records directly
~~~

This prevents transport architecture from bypassing the intentional consumer contract.

---

# 94. Future Django integration

The same principle applies to Django.

A Django application may use the Python public API while selecting a persistence/runtime strategy.

PySRMKit must not redesign the Domain around Django ORM merely to support a web framework.

---

# 95. External SRM integration

A future Ivalua/SAP/Coupa Anti-Corruption Layer should target public application/business operations where possible.

Conceptually:

~~~text
External SRM payload
    ↓
ACL mapper
    ↓
public PySRMKit operation
    ↓
Domain/Application
~~~

This reduces coupling to internal Handler package structure.

---

# 96. Agent integration

A future agent can also consume the public API.

The agent should not receive raw repository access as its normal tool surface.

Potential tool exposure:

~~~text
register supplier
request qualification
get qualification
evaluate qualification
~~~

This is another reason to keep the public API explicit and business-named.

---

# 97. Notebook usage

The InMemory Runtime should make notebook exploration straightforward:

~~~python
srm = create_in_memory_runtime()
...
~~~

No database setup should be necessary for first exploration.

This preserves the pedagogical value established by the first Core.

---

# 98. Public facade lifecycle state

The facade should know whether its Runtime is open or closed.

Using a closed runtime should fail clearly.

Do not silently recreate infrastructure after explicit close.

---

# 99. Runtime ownership matrix

| Resource | InMemory Runtime | SQL Runtime |
|---|---|---|
| repositories | owns | creates per use case |
| clock | owns/reference | owns/reference |
| policy | owns/reference | owns/reference |
| in-process event dispatcher | owns | owns |
| deferred dispatcher | unnecessary/default direct | use-case scoped |
| Engine | none | owns initially |
| Session factory | none | owns |
| Session | none | use-case scoped |
| Alembic migration | none | not automatic |
| database credentials | none | provided by host |
| transaction commit | logical adapter semantics | runtime / capability UoW |
| close | lightweight | dispose Engine |

---

# 100. Dependency direction with Runtime

The Runtime belongs outside the Core layers.

Target direction:

~~~text
runtime
    ↓
application
    ↓
ports

runtime
    ↓
adapters

domain
    does not depend on runtime

application
    does not depend on runtime

ports
    do not depend on runtime
~~~

This is composition, not business logic.

---

# 101. Runtime package architecture rule

Architecture fitness tests should enforce that:

~~~text
domain
application
ports
~~~

do not import:

~~~text
pysrmkit.runtime
~~~

The Runtime may import inward.

The Core must never import outward.

---

# 102. Public API package dependency rule

`pysrmkit.api` may re-export Domain/Application-facing types but should not depend on SQLAlchemy adapter modules.

This preserves:

~~~text
public business API
    independent from
optional SQL infrastructure
~~~

---

# 103. Avoid duplicate business logic in facade

Facade methods must orchestrate existing Application Handlers.

Do not reimplement:

~~~text
lifecycle guards
qualification score rules
onboarding completeness rules
duplicate relationship rules
qualification uniqueness rules
~~~

inside public API classes.

The facade is an adapter/composition boundary.

---

# 104. Avoid bypassing Application Handlers

The primary public facade should not mutate Aggregates directly merely to reduce code.

Preferred:

~~~text
public operation
    ↓
Application Handler
    ↓
Domain
~~~

This keeps cross-instance rules and orchestration in the existing Application layer.

---

# 105. Public transaction runner candidate

Repeated SQL runtime choreography may create pressure for a small internal helper:

~~~text
run_in_transaction(...)
~~~

Such a helper may be justified internally if repetition appears.

It should not automatically become a public abstraction.

The public contract is the business operation, not the transaction runner.

---

# 106. Composition helper versus DI framework

If Handler construction becomes repetitive, use explicit internal factories/composition helpers first.

Example conceptual:

~~~text
build_supplier_api(runtime_context)
build_qualification_api(runtime_context)
~~~

Do not jump directly to a container.

---

# 107. Runtime configuration object

A configuration dataclass may become useful if constructor parameters grow.

Do not introduce one in `0.3.0a1` merely for symmetry.

Introduce it when real runtime options exceed a clear direct signature.

---

# 108. Public facade object graph

Candidate:

~~~text
PySRMKit
├── suppliers: SuppliersAPI
├── relationships: RelationshipsAPI
├── onboarding: OnboardingAPI
├── assessments: AssessmentsAPI
├── qualifications: QualificationsAPI
└── events: EventsAPI? [optional milestone]
~~~

Each capability API is small.

The root facade coordinates lifecycle only.

---

# 109. Capability API implementation status

Capability API classes are primary adapters.

They translate consumer calls into existing Application Commands/Handlers.

They should contain:

~~~text
input normalization
handler invocation
result/view mapping
public error translation
~~~

They should not contain Domain policy.

---

# 110. Public API naming rules

Use domain verbs already proven by Commands.

Examples:

~~~text
register
create
invite
start_onboarding
satisfy_requirement
complete
record_answer
request
evaluate
get
get_current_for_scope
~~~

Avoid generic:

~~~text
process
execute
run_action
perform
manage
~~~

unless the domain meaning truly requires them.

---

# 111. Public API method granularity

One facade method should normally represent one Application use case.

Avoid methods that silently perform the entire onboarding/qualification workflow unless a real higher-level business use case requires it.

The existing full journey remains a scenario, not automatically one transaction or one API operation.

---

# 112. Batch operations

No bulk registration, bulk qualification, or batch API is introduced in the first public cycle.

Bulk behavior has different transaction, error, and performance semantics.

Defer until real pressure exists.

---

# 113. Idempotency

The public API does not promise generic idempotency yet.

Where existing business uniqueness rules naturally reject duplicates, preserve those semantics.

Do not add global idempotency keys before external retry pressure appears.

---

# 114. Concurrency

The public facade must not imply conflict-safe concurrent updates beyond existing database constraints and transaction semantics.

Optimistic versioning remains deferred.

A later concurrent consumer may create the pressure.

---

# 115. Public API security boundary

The Python API does not implement authorization by itself in Cycle 3.

Authorization depends on host/application context that does not yet exist.

A future primary adapter may enforce:

~~~text
who may register
who may evaluate
who may activate
~~~

without moving identity-provider concerns into Domain models.

---

# 116. Audit boundary

Public Runtime execution may later become a useful interception point for audit.

Do not implement a generic audit framework yet.

The current Domain Events already expose meaningful business facts.

---

# 117. Serialization

The public Python API should use Python types.

JSON serialization is a transport concern.

Do not force public results into raw dictionaries merely to anticipate HTTP.

Future adapters can serialize:

~~~text
dataclasses
Value Objects
Enums
datetime
UUID
~~~

appropriately.

---

# 118. Date/time contract

Public timestamps should remain timezone-aware.

Persistence already normalizes UTC semantics.

The public API must not regress to naive datetimes.

---

# 119. Public callbacks

If event subscription is exposed, callback typing must be explicit.

Avoid:

~~~python
Callable[..., Any]
~~~

when the event type is known.

This aligns with the strict typing posture.

---

# 120. Public documentation structure

Cycle 3 documentation should eventually provide:

~~~text
Quickstart
InMemory runtime guide
SQL runtime guide
Public API reference
Error reference
Persistence setup
Migration setup
Event semantics
Advanced adapter usage
Internal API warning
~~~

The architecture spec itself does not replace user documentation.

---

# 121. Public examples

Add examples that use only public imports.

Candidate:

~~~text
examples/public_in_memory_qualification.py
examples/public_sql_qualification.py
~~~

The existing low-level examples can remain as architecture-learning references if useful.

---

# 122. Existing examples after Cycle 3

Do not delete:

~~~text
local_qualification.py
persistent_qualification.py
~~~

immediately.

They remain valuable for showing the internal composition behind the facade.

Documentation should distinguish:

~~~text
consumer example
architecture/composition example
~~~

---

# 123. Internal composition remains testable

Hiding composition from ordinary consumers must not hide it from maintainers.

Internal tests should continue validating:

~~~text
Repository Contracts
UnitOfWork
Data Mapper
migrations
transaction rollback
event ordering
~~~

The facade adds a layer; it does not replace lower-level tests.

---

# 124. Architecture learning convention

Cycle 3 should name the concepts actually implemented.

Likely concepts:

~~~text
Facade
Composition Root
Primary Adapter
Application Service boundary
DTO / View Model
Dependency Injection by constructor
Information Hiding
Stable Public API
Semantic Versioning boundary
Context Manager
~~~

Do not label something a pattern merely because its class name resembles one.

---

# 125. Facade pattern qualification

If `PySRMKit` presents a simplified interface over multiple subsystems, calling it a **Facade** is justified.

The problem it solves is real:

~~~text
consumer otherwise coordinates
many internal application/infrastructure objects
~~~

This is now implementation-driven pattern pressure.

---

# 126. Composition Root qualification

Runtime constructors are explicit Composition Roots.

They decide:

~~~text
which repositories
which dispatcher
which clock
which policy
which transaction implementation
~~~

The rest of the Core should not construct these dependencies itself.

---

# 127. Primary Adapter qualification

Capability APIs are primary/driving adapters.

They receive external Python calls and invoke Application use cases.

SQL repositories remain secondary/driven adapters.

Conceptually:

~~~text
Python consumer
    ↓
Primary Adapter
    ↓
Application
    ↓
Port
    ↓
Secondary Adapter
~~~

This makes the Hexagonal influence explicit without forcing a framework.

---

# 128. Public API stability rule

A symbol is considered part of the stable public API only if all are true:

~~~text
documented as public
imported from an intentional public module
covered by public API tests
used in a public example or reference
included in compatibility review
~~~

Importability alone is not enough.

---

# 129. `__all__` usage

Public modules should define intentional exports where useful.

`__all__` can document and test the intended namespace.

Do not use it as the only public/private mechanism; documentation and package structure still matter.

---

# 130. Top-level `__init__.py`

The top-level package should remain lightweight.

Likely initial exports:

~~~text
__version__
PySRMKit
create_in_memory_runtime
~~~

Potential additions should be reviewed carefully.

SQL runtime construction should remain in its optional module to avoid base import coupling.

---

# 131. Public API import cost

Importing the base package must not:

~~~text
connect to database
read credentials
run migration
start threads
load external services
import optional SQL dependencies
~~~

This existing smoke-test principle becomes part of the public contract.

---

# 132. Runtime startup cost

Creating an InMemory Runtime should remain cheap.

Creating a SQL Runtime may create an Engine but should avoid opening a database transaction until an operation requires one, unless connection validation is explicitly requested later.

---

# 133. Eager database connectivity

Do not silently test connectivity at SQL Runtime creation unless defined as part of the constructor contract.

Lazy connectivity follows SQLAlchemy Engine behavior and keeps construction predictable.

A future `health_check()` may be introduced if needed.

---

# 134. Health check

No public health-check abstraction is required for the first milestone.

A deployment framework can test database connectivity separately.

Add only when runtime hosting pressure appears.

---

# 135. Runtime cloning

No cloning/copying semantics are required.

A runtime owns resources and should be created explicitly.

---

# 136. Runtime serialization

A runtime is not serializable state.

Do not pickle or persist the facade/runtime.

Persist business state through repositories.

---

# 137. Runtime equality

No meaningful value equality is required for Runtime or API facade objects.

They represent execution contexts, not Domain values.

---

# 138. Public views equality

Immutable view/result dataclasses may support structural equality naturally.

This is useful for tests and consumer assertions.

---

# 139. Query not found semantics

Public query methods should choose consistent semantics.

Candidate:

~~~text
get(...)
    -> view or None
~~~

or:

~~~text
get(...)
    -> view
    -> raise public NotFound error
~~~

The first Cycle 3 implementation should select one convention and apply it consistently.

Do not mix silently across capabilities.

---

# 140. Command not found semantics

Commands that target an expected existing object should keep existing Application errors.

Example:

~~~text
Invite unknown Relationship
    -> SupplierRelationshipNotFound
~~~

These are meaningful command failures, not query absence.

---

# 141. Public conflict semantics

Known business conflicts remain explicit.

Examples:

~~~text
duplicate Supplier external identifier
duplicate Supplier/organization Relationship
duplicate current Qualification for same Scope
~~~

The runtime should not reduce them to generic `PersistenceError` when the Application already defines business meaning.

---

# 142. Database constraint conflict translation

Database constraints remain last-line protection against races.

If a constraint violation corresponds to an existing public business conflict, the SQL Runtime may need adapter-specific translation.

This translation should be added case by case.

Do not map every IntegrityError to one generic Conflict without understanding the violated constraint.

---

# 143. Public error causality

Infrastructure-facing public errors may preserve the original exception as Python exception cause:

~~~python
raise PersistenceUnavailable(...) from exc
~~~

This supports debugging without making the DB exception the public type contract.

---

# 144. Public API result mutation

Result and view objects should preferably be immutable.

Consumers should issue new commands to change business state.

This aligns with the existing command-oriented Application layer.

---

# 145. Runtime extension points

The first runtime should expose only extension points already justified.

Strong candidates:

~~~text
Clock
QualificationPolicy
event subscribers
database URL
~~~

Weak candidates to defer:

~~~text
custom repository registry
custom Session class
custom transaction runner
service container hooks
middleware chain
plugin manager
~~~

---

# 146. Custom repositories

Advanced consumers may eventually want custom Repository adapters.

The Ports already make this possible internally.

Do not make custom runtime repository injection a first-milestone public requirement unless a real external adapter consumer appears.

---

# 147. Custom persistence backend

Cycle 3 does not promise an arbitrary persistence plugin system.

The known public runtimes are:

~~~text
InMemory
SQLAlchemy SQL
~~~

New backends should first satisfy existing Repository contracts and then motivate a runtime integration path.

---

# 148. Public Ports

Repository Ports do not automatically become public stable API.

Most normal consumers should not need them.

Ports may remain advanced/internal until a custom-adapter use case proves public value.

---

# 149. Public Clock Port

Clock is an exception candidate because deterministic runtime injection is already useful.

Even so, the promotion should be explicit and tested.

---

# 150. Public Domain Events

Events are another exception candidate because subscribers may intentionally consume them.

Promotion must be selective.

---

# 151. Adapter-specific public surface

Some public APIs are necessarily technology-specific.

Example:

~~~text
pysrmkit.runtime.sql
~~~

This surface may publicly mention:

~~~text
database URL
SQL runtime
persistence setup
~~~

but should still avoid exposing internal SQLAlchemy Records.

---

# 152. SQLAlchemy objects in advanced API

Do not prohibit all advanced SQLAlchemy access forever.

A future advanced module may expose controlled integration hooks.

But the primary runtime contract should not require:

~~~text
Engine
Session
Mapped
DeclarativeBase
~~~

types.

---

# 153. Runtime and migrations package boundary

Potential long-term shape:

~~~text
pysrmkit.runtime.sql
    business runtime

pysrmkit.migrations
    explicit database lifecycle tooling
~~~

Do not create the latter until there is consumer pressure beyond direct Alembic usage.

---

# 154. Runtime and test fixtures

Public runtime factories may simplify downstream consumer tests.

This is positive.

However PySRMKit should not ship pytest fixtures as mandatory public API in Cycle 3.

Consumers can construct runtimes directly.

---

# 155. Runtime reset

InMemory Runtime may eventually benefit from explicit reset for tests.

Do not add it initially.

Creating a fresh runtime is clearer and preserves isolation.

---

# 156. SQL test isolation

Public SQL runtime integration tests should continue using isolated test databases/files.

The runtime itself should not expose destructive reset helpers intended only for PySRMKit's test suite.

---

# 157. Public API and performance

The first priority remains correctness and usability.

Do not bypass Domain/Application layers for performance without evidence.

Measure before introducing optimized query paths.

---

# 158. Public facade overhead

A thin capability facade adds negligible conceptual cost relative to the wiring it removes.

Its value is not performance.

Its value is:

~~~text
stable contract
discoverability
encapsulation
composition ownership
~~~

---

# 159. Public API and backward compatibility during `0.3.x`

The first alpha milestones may refine names.

Each milestone should record:

~~~text
new public symbols
changed public symbols
deprecated symbols
removed symbols
~~~

This makes the public surface evolution visible.

---

# 160. Architecture fitness additions

Cycle 3 should add tests for:

~~~text
domain -> no runtime imports
application -> no runtime imports
ports -> no runtime imports
api -> no SQLAlchemy/Alembic/Psycopg imports
top-level import -> no optional SQL dependency requirement
runtime SQL imports -> allowed adapter dependencies
~~~

---

# 161. Public API dependency diagram

~~~text
                       ┌────────────────────────┐
                       │   Python Consumer      │
                       └───────────┬────────────┘
                                   │
                                   ▼
                       ┌────────────────────────┐
                       │   Public API / Facade  │
                       └───────────┬────────────┘
                                   │
                      ┌────────────┴────────────┐
                      │                         │
                      ▼                         ▼
             ┌────────────────┐       ┌────────────────┐
             │ Application    │       │ Runtime        │
             │ Use Cases      │       │ Composition    │
             └───────┬────────┘       └───────┬────────┘
                     │                        │
                     ▼                        ▼
             ┌────────────────┐       ┌────────────────┐
             │ Ports          │◄──────│ Adapters       │
             └───────┬────────┘       └────────────────┘
                     │
                     ▼
             ┌────────────────┐
             │ Domain         │
             └────────────────┘
~~~

The arrows are conceptual; implementation dependencies must still obey the inward Core dependency rules.

---

# 162. Runtime execution diagram - InMemory

~~~text
Consumer
    ↓
SuppliersAPI.register(...)
    ↓
RegisterSupplierHandler
    ↓
Supplier Domain
    ↓
InMemorySupplierRepository
    ↓
InProcessDomainEventDispatcher
    ↓
Result
~~~

No transaction framework is invented.

---

# 163. Runtime execution diagram - SQL

~~~text
Consumer
    ↓
SuppliersAPI.register(...)
    ↓
SQL Runtime opens Session
    ↓
SqlAlchemySupplierRepository
    ↓
RegisterSupplierHandler
    ↓
Domain behavior
    ↓
Repository stages state
    ↓
Session COMMIT
    ↓
DeferredDomainEventDispatcher.publish()
    ↓
Result
    ↓
Session closes
~~~

---

# 164. Multi-Aggregate SQL execution diagram

~~~text
Consumer
    ↓
RelationshipsAPI.start_onboarding(...)
    ↓
StartSupplierOnboardingHandler
    ↓
SqlAlchemySupplierOnboardingUnitOfWork
    ├── Relationship Repository
    └── Onboarding Repository
    ↓
COMMIT
    ↓
event buffered by runtime dispatcher
    ↓
publish
    ↓
Result
~~~

The facade does not need to expose the UnitOfWork concept.

---

# 165. First Cycle 3 public journey

The reference public journey remains the qualified Supplier qualification path.

~~~text
srm.suppliers.register
        ↓
srm.relationships.create
        ↓
srm.relationships.invite
        ↓
srm.relationships.start_onboarding
        ↓
srm.onboarding.satisfy_requirement
        ↓
srm.onboarding.complete
        ↓
srm.assessments.create
        ↓
srm.assessments.record_answer
        ↓
srm.assessments.complete
        ↓
srm.qualifications.request
        ↓
srm.qualifications.evaluate
        ↓
srm.qualifications.get
~~~

This ensures Cycle 3 validates the same business model rather than inventing new Domain scope.

---

# 166. Success exit state

The public journey must still be able to prove:

~~~text
Relationship stage     ONBOARDING
Onboarding complete    True
Assessment complete    True
Assessment score       90
Qualification status   QUALIFIED
approved               True
failed requirements    ()
~~~

---

# 167. Rejection exit state

The public journey must also prove:

~~~text
Assessment score       60
Qualification status   NOT_QUALIFIED
approved               False
failed requirements    ASSESSMENT_MINIMUM_SCORE
~~~

The public facade must not collapse explainability into a boolean.

---

# 168. Runtime implementation order

Do not implement the entire public architecture in one commit.

The runtime cycle should progress incrementally.

Recommended order:

~~~text
public type boundary
    ↓
InMemory facade
    ↓
SQL runtime
    ↓
public views/errors
    ↓
public qualification scenario
~~~

---

# 169. Cycle 3 milestone proposal

Proposed implementation roadmap:

~~~text
0.3.0a1 - Public API Foundation
0.3.0a2 - InMemory Runtime Composition
0.3.0a3 - SQL Runtime Composition
0.3.0a4 - Public Views and Error Boundary
0.3.0a5 - Public Event Surface
0.3.0a6 - Public Runtime Qualification
~~~

This roadmap remains iterative.

Implementation pressure may refine it.

---

# 170. `0.3.0a1 - Public API Foundation`

Scope:

~~~text
api package boundary
PySRMKit facade skeleton
intentional public exports
public capability interfaces/surfaces
public business IDs/enums review
py.typed
public import tests
architecture fitness updates
no SQL runtime yet
~~~

Exit gate:

> **A consumer can import an intentional typed PySRMKit public surface without importing implementation layers or optional persistence dependencies.**

---

# 171. `0.3.0a2 - InMemory Runtime Composition`

Scope:

~~~text
create_in_memory_runtime
runtime lifecycle
capability API implementation
existing Application Handler reuse
SystemClock default
optional Clock override
QualificationPolicy composition
public success/rejection local scenario
~~~

Exit gate:

> **The complete local qualification journey can be executed through public API imports without direct Repository or Handler construction.**

---

# 172. `0.3.0a3 - SQL Runtime Composition`

Scope:

~~~text
create_sql_runtime(database_url)
runtime-owned Engine
Session-per-use-case
SQL repository composition
capability UnitOfWork reuse
commit / rollback
deferred event publication
SQLite qualification
PostgreSQL qualification
optional-dependency behavior
~~~

Migration execution remains explicit and outside runtime startup.

Exit gate:

> **The same public business operations run durably on SQLite and PostgreSQL without the consumer constructing SQLAlchemy repositories or Sessions.**

---

# 173. `0.3.0a4 - Public Views and Error Boundary`

Scope:

~~~text
immutable public state views
public query methods
consistent not-found semantics
selected public business errors
persistence error translation
no raw SQLAlchemy/DBAPI exception contract
view mapping tests
~~~

Exit gate:

> **Consumers can read the qualified Supplier state and react to stable public errors without depending on internal Aggregates, ORM rows, or infrastructure exceptions.**

---

# 174. `0.3.0a5 - Public Event Surface`

Scope only if still justified after `a4`:

~~~text
selected public Domain Events
typed subscription
post-commit semantics
event compatibility tests
explicit non-durable delivery documentation
~~~

If no consumer pressure exists, this milestone may be deferred and the cycle can proceed directly to final qualification.

---

# 175. `0.3.0a6 - Public Runtime Qualification`

Final scenario:

~~~text
PUBLIC IMPORTS ONLY
        ↓
InMemory success
InMemory rejection
        ↓
SQLite migrated database
        ↓
public success/rejection
        ↓
close runtime
        ↓
recreate runtime
        ↓
same public views
        ↓
PostgreSQL public success/rejection
~~~

No internal Handler/Repository import should appear in the consumer scenario.

Exit gate:

> **PySRMKit's qualified Supplier Core can be consumed through a small typed Python API with explicit runtime ownership while preserving all Domain, transaction, persistence, and event-ordering semantics.**

---

# 176. Cycle 3 Definition of Done

~~~text
[ ] top-level public surface is intentional
[ ] py.typed shipped
[ ] public import tests exist
[ ] pure package import requires no persistence dependency
[ ] PySRMKit facade exists
[ ] capability APIs are business-oriented
[ ] InMemory Runtime works
[ ] SQL Runtime works
[ ] SQL consumer does not construct Session
[ ] SQL consumer does not construct repositories
[ ] one command = one transaction by default
[ ] capability UnitOfWork remains intact
[ ] commit failure rolls back
[ ] failed commit publishes no success event
[ ] migrations are not run implicitly
[ ] public views expose business state
[ ] raw ORM records never cross primary public boundary
[ ] raw SQLAlchemy/DBAPI errors are not normal public contract
[ ] InMemory success path green
[ ] InMemory rejection path green
[ ] SQLite success/rejection green
[ ] persistence restart through public runtime green
[ ] PostgreSQL success/rejection green
[ ] Domain/Application/Ports do not depend on Runtime
[ ] architecture fitness tests green
[ ] regression suite green
~~~

---

# 177. Failure signs

Cycle 3 should stop and reconsider if implementation produces:

~~~text
Domain importing runtime
Application importing SQLAlchemy
public API returning ORM records
Facade duplicating business rules
Facade becoming generic service locator
one giant execute(action, payload)
global mutable Runtime
global Session
automatic migration on package import
automatic migration hidden in normal command execution
raw DB exceptions becoming public contract
public SQL runtime required for InMemory use
FastAPI becoming a Core dependency
global UnitOfWork introduced without new atomicity pressure
~~~

---

# 178. Decisions intentionally not frozen

The following details should still be allowed to evolve during implementation:

~~~text
exact facade constructor signature
exact capability API class names
exact public query not-found convention
exact public view fields
whether public event surface stays in Cycle 3
whether external Engine injection is needed
whether runtime configuration dataclass becomes useful
which existing Commands are re-exported
which Domain Errors become direct public exports
~~~

The architecture direction is frozen.

The smallest ergonomic surface should still be implementation-driven.

---

# 179. Decisions frozen by this document

~~~text
Cycle 3 is Python-first Public API & Runtime Composition.
Public API is not synonymous with HTTP.
A root PySRMKit facade is justified.
Facade remains capability-oriented.
Base import remains persistence-optional.
InMemory remains a public runtime.
SQL runtime hides normal Session/Repository assembly.
SQL runtime uses short-lived use-case Sessions.
Repositories still do not commit.
Existing capability UnitOfWork remains.
Global UnitOfWork remains deferred.
Event publication remains post-commit.
Outbox remains deferred.
Runtime startup does not silently run migrations.
Primary public queries return public views rather than ORM rows.
Runtime/composition remains outside Domain/Application/Ports.
~~~

---

# 180. Architecture concept map

~~~text
Problem
    consumer must understand internal wiring
        ↓
Facade
        ↓
capability-oriented Public API
        ↓
Runtime Composition
        ↓
Application Handlers
        ↓
Ports
        ↓
Adapters
~~~

---

# 181. Learning map - Facade

~~~text
many internal subsystems
    create consumer complexity
        ↓
one intentional entry point
        ↓
PySRMKit
        ↓
capability APIs
~~~

Pattern name:

~~~text
Facade
~~~

justified by real composition complexity.

---

# 182. Learning map - Composition Root

~~~text
dependencies must be selected somewhere
        ↓
Runtime factory
        ↓
repositories
clock
policy
dispatcher
transactions
        ↓
constructed once at application boundary
~~~

Pattern/concept:

~~~text
Composition Root
~~~

---

# 183. Learning map - Primary and Secondary Adapters

~~~text
Consumer
    ↓
Capability API
    =
Primary Adapter

Application
    ↓
Repository Port
    ↓
SQL/InMemory Repository
    =
Secondary Adapter
~~~

This makes the Hexagonal architecture vocabulary observable in code.

---

# 184. Learning map - DTO / View Model

~~~text
Domain Aggregate
    optimized for business behavior
        ↓
Public View
    optimized for consumer reading
~~~

This prevents ORM leakage without forcing the Aggregate itself to become a presentation object.

---

# 185. Learning map - Information Hiding

~~~text
consumer
    knows:
        business operations
        business IDs
        views
        errors

consumer
    does not need:
        mapper internals
        Session lifecycle
        technical child IDs
        Repository implementation
~~~

This is package-level Information Hiding.

---

# 186. Relationship with Clean Architecture

The new boundary follows the dependency rule:

~~~text
outer runtime
    depends inward

inner business layers
    do not depend outward
~~~

Runtime and facade are replaceable delivery/composition concerns.

The Domain remains central.

---

# 187. Relationship with Hexagonal Architecture

Cycle 3 clarifies both sides of the hexagon.

Before:

~~~text
Ports + secondary adapters
    were most visible
~~~

After:

~~~text
Primary Adapter
    Public API

Application Core

Secondary Adapters
    InMemory / SQL
~~~

This makes the architecture symmetrical from a consumer perspective.

---

# 188. Relationship with Dependency Inversion

Application behavior continues to depend on abstract Ports.

The Runtime selects concrete implementations.

~~~text
Application
    -> Port

Runtime
    -> Concrete Adapter
~~~

The public API must not reverse this by letting Handlers instantiate SQL repositories.

---

# 189. Relationship with Separation of Concerns

~~~text
Domain
    business truth

Application
    use-case orchestration

Public API
    consumer-facing interaction

Runtime
    dependency/resource composition

Adapter
    technology implementation

Migration
    schema lifecycle
~~~

Each concern has a distinct reason to change.

---

# 190. Relationship with KISS

The proposed architecture deliberately avoids:

~~~text
container
bus
middleware framework
plugin manager
async mirror
generic command envelope
~~~

The first public runtime should be explicit Python objects and functions.

---

# 191. Relationship with YAGNI

The project now has evidence for:

~~~text
Facade
Runtime
public views
public error boundary
~~~

It still lacks evidence for:

~~~text
Outbox
optimistic locking
async runtime
global UnitOfWork
transport framework
generic plugin system
~~~

The latter remain deferred.

---

# 192. Public API review checkpoint

After the final Cycle 3 milestone, stop again.

Review:

~~~text
Did the facade reduce real consumer complexity?

Did capability grouping remain clear?

Did any public type feel forced?

Did runtime ownership remain understandable?

Did SQL runtime hide too much?

Did error translation preserve business meaning?

Did public views duplicate Domain unnecessarily?

Did event subscription prove useful?

Did external consumers need Port-level customization?

What is the next real pressure?
~~~

---

# 193. Likely post-Cycle-3 candidates

Only after the review:

~~~text
Activation
Documents & Evidence
Compliance
Risk
HTTP API adapter
External SRM integration
Outbox
Concurrency hardening
Observability
~~~

No candidate is automatically selected by this document beyond Cycle 3.

---

# 194. Why Activation is still deferred

Activation remains the strongest next business continuation.

However, Public API & Runtime Composition is selected first because it creates a stable way to consume both:

~~~text
current Qualification
and
future Activation
~~~

This avoids building a second business slice on top of accidental internal import contracts.

---

# 195. Why HTTP remains deferred

A FastAPI layer built before the public Python boundary risks turning:

~~~text
HTTP schemas
route handlers
dependency injection
status codes
~~~

into de facto application architecture.

The Python public contract should exist first.

Then HTTP can translate:

~~~text
HTTP
    ↔
Public PySRMKit API
~~~

---

# 196. Why external SRM integration remains deferred

An Ivalua/SAP/Coupa adapter should not need to know internal Repository wiring.

After Cycle 3 it can target:

~~~text
public business operations
stable IDs
public errors
public views
~~~

while keeping external payload semantics inside an Anti-Corruption Layer.

---

# 197. Why Outbox remains deferred

The first public runtime still publishes only in-process events.

There is no external delivery contract yet.

Outbox pressure begins when a real requirement states:

~~~text
database state
and
external event delivery
must survive process failure together
~~~

That requirement does not yet exist in the implemented Core.

---

# 198. Why optimistic locking remains deferred

PostgreSQL persistence introduced concurrent-write possibility but has not demonstrated lost-update failures in a real use case.

Database uniqueness and transaction boundaries currently protect the implemented invariants.

Add versioning only after a concrete conflict scenario appears.

---

# 199. Why async remains deferred

No current consumer requires asynchronous execution.

A sync-first public API is simpler to stabilize.

A future async surface should be justified by a real async host or workload rather than symmetry.

---

# 200. Final architecture statement

> **Cycle 1 proved the Domain locally.**

> **Cycle 2 proved the same Domain against durable relational persistence.**

> **Cycle 3 will prove that the qualified Domain and Application capabilities can be consumed through a small, stable, typed Python interface without exposing infrastructure assembly as the normal user experience.**

The intended progression is:

~~~text
0.1.x
LOCAL CORE
    ✅
    ↓
0.2.x
PERSISTENT CORE
    ✅
    ↓
0.3.x
PUBLIC API & RUNTIME COMPOSITION
    NEXT
~~~

---

# 201. Next implementation action

After this document is accepted, the next action is:

~~~text
0.3.0a1 - Public API Foundation
~~~

Implement only the first public boundary:

~~~text
intentional api package
minimal PySRMKit facade skeleton
public symbol decisions
public import tests
py.typed
architecture fitness updates
zero SQL runtime implementation beyond what is needed for import boundaries
~~~

Do not implement the entire runtime cycle inside `0.3.0a1`.

---

# 202. Final rule

> **The consumer should learn Supplier Relationship Management concepts before learning PySRMKit internals.**

> **The facade may hide wiring; it must not hide business meaning.**

> **The Runtime owns infrastructure composition; the Domain remains unaware of the Runtime.**

> **Public API stability is an intentional contract, never an accidental consequence of importability.**


---

# 203. Document qualification evidence

~~~text
Pull request     #21
Final PR CI      #151
Quality job      PASS
PostgreSQL job   PASS
Merge commit     0e40640ccb5d868fdd3ac552de54697e03c9f680
Target branch    main
~~~

The Cycle 3 architecture specification is therefore accepted as the implementation baseline for:

~~~text
0.3.0a1 - Public API Foundation
~~~
