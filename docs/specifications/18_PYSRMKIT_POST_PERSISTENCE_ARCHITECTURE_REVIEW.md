# PySRMKit - Post-Persistence Architecture Review

**Document:** `18_PYSRMKIT_POST_PERSISTENCE_ARCHITECTURE_REVIEW.md`  
**Status:** POST-PERSISTENCE REVIEW / ITERATIVE DEEP DIVE  
**Review scope:** `0.2.0a1` through `0.2.0a7`  
**Persistent Core status:** QUALIFIED / GREEN / COMPLETE  
**Date:** 2026-10-27

---

# 1. Purpose

This document is the architecture checkpoint that follows completion of the Persistent Core cycle.

It is deliberately not a new broad speculative specification.

The sequence remains:

~~~text
IMPLEMENTED SYSTEM
      |
      v
OBSERVED PRESSURE
      |
      v
ARCHITECTURE REVIEW
      |
      v
REAL NEXT PROBLEM
      |
      v
TARGETED NEXT SPEC
~~~

The governing rules remain:

> **Problem before Pattern.**

> **Implementation evidence outranks speculative elegance.**

> **Do not add infrastructure merely because the architecture can now support it.**

---

# 2. Review evidence

The review is grounded in the completed persistence cycle:

~~~text
0.2.0a1  Persistence Foundation
0.2.0a2  Supplier + Relationship SQL Persistence
0.2.0a3  Onboarding + Assessment SQL Persistence
0.2.0a4  Qualification SQL Persistence
0.2.0a5  Transaction Boundary / UnitOfWork
0.2.0a6  Alembic Migration Baseline
0.2.0a7  Persistent Local Qualification
~~~

The final Persistent Core qualification proves:

~~~text
empty database
    ↓
Alembic upgrade head
    ↓
complete Supplier qualification journey
    ↓
durable SQL commits
    ↓
destroy original Engine / Session / Repositories
    ↓
create fresh persistence context
    ↓
reload all Aggregates
    ↓
same business decision
~~~

The proof runs on:

~~~text
SQLite
PostgreSQL 18.6
~~~

Final PR qualification evidence for `0.2.0a7`:

~~~text
Ruff                         PASS
Ruff format                  PASS
Pyright strict               PASS
Pytest quality suite         239 passed
PostgreSQL selected tests    44 passed
Coverage                     98.11%
Architecture gates           PASS
Alembic bootstrap            PASS
Persistent success path      PASS
Persistent rejection path    PASS
~~~

---

# 3. Review questions

This review answers:

~~~text
Did the original Domain boundaries survive real persistence?

Did Repository Ports remain stable?

Did the single SQLAlchemy adapter-family hypothesis survive?

Did Data Mapper remain the correct ORM boundary?

Where did relational persistence force technical identities?

Was UnitOfWork introduced at the right level?

Did transaction semantics expose event-ordering problems?

Did Repository Contracts prove enough?

What did PostgreSQL reveal that SQLite did not?

Did Alembic remain infrastructure-only?

Which abstractions are now genuinely justified?

Which abstractions are still premature?

What new architecture pressure is strongest after persistence?

What should define Cycle 3?
~~~

---

# 4. Executive verdict

The Persistent Core validates the original architecture unusually strongly.

The most important result is not that SQL persistence works.

It is that persistence works **without forcing a redesign of the business model**.

Across the complete cycle:

~~~text
Domain model             remained persistence-ignorant
Application use cases    remained infrastructure-agnostic
Repository Ports         remained Aggregate-specific
InMemory adapters        remained valid
SQL repositories         remained non-committing
SQLite / PostgreSQL      shared one adapter family
Qualification semantics  remained unchanged
~~~

The persistence cycle therefore confirms the central architecture direction:

~~~text
Domain
    ↓
Application
    ↓
Ports
    ↑
Adapters
~~~

The architecture did evolve, but almost entirely inside the adapter/composition boundary where that pressure belonged.

**Overall verdict:** KEEP the architecture. Refine its runtime composition and testing seams. Do not redesign the Core.

---

# 5. Boundary survival matrix

| Boundary / decision | Before persistence | After Persistent Core | Verdict |
|---|---|---|---|
| Supplier Aggregate | qualified locally | persists/reloads unchanged | KEEP |
| SupplierRelationship Aggregate | qualified locally | persists/reloads unchanged | KEEP |
| SupplierOnboarding Aggregate | qualified locally | owned requirements persist | KEEP |
| SupplierAssessment Aggregate | qualified locally | owned questions/answers persist | KEEP |
| SupplierQualification Aggregate | qualified locally | scoped decisions persist | KEEP |
| QualificationPolicy | pure Domain Policy | unchanged | KEEP |
| Repository Ports | InMemory contracts | SQL adapters satisfy same contracts | KEEP |
| InMemory adapters | local/test adapter | still first-class | KEEP |
| SQLAlchemy | absent from Core | adapter-only | KEEP |
| Data Mapper | planned | strongly validated | KEEP |
| Generic Repository | avoided | still unnecessary | AVOID |
| Global UnitOfWork | deferred | still unnecessary | DEFER |
| Capability UnitOfWork | deferred | justified for onboarding | KEEP |
| Alembic | deferred | adapter/deployment tooling | KEEP |
| Transactional Outbox | deferred | still not justified | DEFER |
| Async persistence | deferred | still not justified | DEFER |
| DI container | avoided | manual composition still works | DEFER |
| Public facade | deferred until use cases stabilize | pressure now real | NEXT CANDIDATE |

---

# 6. Domain boundary review

## 6.1 Supplier

Persistence did not create pressure to add database identity, ORM state, timestamps, or relationship-specific state to `Supplier`.

The Aggregate remains:

~~~text
canonical Supplier identity
    ≠
organization relationship state
~~~

**Decision:** KEEP.

---

## 6.2 SupplierRelationship

The relationship Aggregate remains the correct owner of organization-specific lifecycle.

SQL persistence reinforced the boundary through a real foreign key:

~~~text
SupplierRelationship
    -> Supplier
~~~

without requiring direct ORM relationships inside the Domain.

**Decision:** KEEP.

---

## 6.3 SupplierOnboarding

The independent Aggregate decision survived persistence.

Its owned requirement collection required persistence-specific reconciliation logic, but no Domain redesign.

That distinction is important:

~~~text
Domain problem
    requirement readiness

Persistence problem
    how requirement rows are updated safely
~~~

**Decision:** KEEP as Aggregate Root.

---

## 6.4 SupplierAssessment

Persistence confirmed that Assessment requires its own Aggregate lifecycle and owned snapshots.

The database introduced technical identifiers for question rows, but those identifiers remained below the Domain boundary.

The Domain still speaks:

~~~text
question.code
answer.question_code
~~~

not:

~~~text
question_id
answer_id
~~~

**Decision:** KEEP.

---

## 6.5 SupplierQualification

The scoped Qualification model remains one of the strongest business decisions in PySRMKit.

Persistence had to normalize optional scope dimensions for SQL uniqueness, but the Domain still reconstructs:

~~~text
None
~~~

rather than leaking persistence normalization such as empty strings.

The partial unique current-scope constraint also confirmed that the database can protect the same business meaning without becoming the source of that meaning.

**Decision:** KEEP.

---

# 7. Aggregate isolation review

The five Aggregate Roots still cooperate without direct cross-Aggregate mutation:

~~~text
Supplier
SupplierRelationship
SupplierOnboarding
SupplierAssessment
SupplierQualification
~~~

Persistence did not require collapsing them into one object graph.

Instead:

~~~text
Application Handler
    loads required Aggregates
    coordinates use case
    invokes Domain behavior
    persists through Ports
~~~

The only use case that demonstrated atomic writes across two Aggregates was onboarding start.

That pressure produced one capability-specific UnitOfWork rather than a universal transaction abstraction.

**Decision:** KEEP Aggregate isolation.

---

# 8. Application Layer review

Most Application Handlers survived persistence unchanged.

This is strong evidence that they depend on useful abstractions rather than implementation details.

The major evolution was:

~~~text
StartSupplierOnboardingHandler
    old:
        two repositories

    new:
        SupplierOnboardingUnitOfWork
~~~

The change occurred because the use case acquired a real transaction invariant:

~~~text
Relationship transition
        +
Onboarding creation
        =
one atomic business operation
~~~

No other Handler was forced into that abstraction.

**Decision:** KEEP direct Handler invocation and capability-specific transaction boundaries.

---

# 9. Repository Port review

Repository Ports remained small and Aggregate-specific.

Typical shape:

~~~text
get(...)
save(...)
one domain-relevant lookup
~~~

Examples:

~~~text
find_by_external_identifier(...)
find_for_supplier_and_organization(...)
find_for_relationship(...)
find_latest_for_relationship(...)
find_current_for_scope(...)
~~~

No generic CRUD abstraction emerged.

This is important because persistence often creates pressure toward:

~~~text
GenericRepository[T]
BaseRepository
DAO
query builder leakage
Session exposure
~~~

PySRMKit did not need any of them.

**Decision:** KEEP current Repository Ports.

---

# 10. Repository substitution review

The single-adapter-family hypothesis was validated:

~~~text
Repository Port
        ^
        |
SQLAlchemy Repository
        |
        +--> SQLite
        +--> PostgreSQL
~~~

No dialect-specific Repository class was required.

The portability contract proved to be:

~~~text
same business behavior
same Repository semantics
same Domain reconstruction
~~~

not:

~~~text
identical SQL
identical reflection metadata
identical physical index representation
~~~

**Decision:** KEEP one SQLAlchemy adapter family until real dialect behavior forces divergence.

---

# 11. Data Mapper review

The explicit Data Mapper boundary is now strongly justified.

It solved three distinct classes of impedance mismatch.

## 11.1 Domain object versus ORM record

~~~text
Domain Aggregate
    persistence ignorant
        ↓
explicit mapper
        ↓
SQLAlchemy Record
~~~

No SQLAlchemy instrumentation entered Domain classes.

## 11.2 Domain identity versus persistence identity

PostgreSQL and SQLAlchemy required technical identities for relational ordering and child-row relationships.

Example:

~~~text
AssessmentQuestion.code
        =
Domain identity

question_id
        =
persistence-only surrogate identity
~~~

The technical key stayed hidden.

## 11.3 Domain collection replacement versus persistence-row reconciliation

The final persistent scenario exposed that:

~~~text
replace Domain collection
    ≠
blindly insert new persistence rows
~~~

After a real commit, owned rows already possess persistence identity.

The mappers therefore evolved from destructive replacement to reconciliation by Domain identity.

Onboarding:

~~~text
requirement.code
    -> existing requirement row
    -> update in place
~~~

Assessment:

~~~text
question.code
    -> existing question row

answer.question_code
    -> existing answer row
~~~

**Decision:** KEEP explicit Data Mapper and treat reconciliation as an adapter responsibility.

---

# 12. Data Mapper lesson

The strongest new persistence lesson is:

> **Persistence identity can exist without becoming Domain identity.**

and:

> **A Domain-owned collection may be immutable or value-oriented while its relational representation still requires stable technical row identity across commits.**

This validates:

~~~text
Separation of Concerns
Information Hiding
Data Mapper
Persistence Ignorance
~~~

The ORM must adapt to the Domain model.

The Domain model must not acquire arbitrary surrogate IDs merely to simplify ORM bookkeeping.

---

# 13. UnitOfWork review

## 13.1 What pressure actually justified it?

Only one implemented use case required atomic writes across Aggregate Roots:

~~~text
StartSupplierOnboarding
    |
    +--> SupplierRelationship
    |
    +--> SupplierOnboarding
~~~

That justified:

~~~text
SupplierOnboardingUnitOfWork
~~~

with:

~~~text
commit
rollback
shared transaction context
repository access
~~~

## 13.2 What did not happen?

No evidence justified:

~~~text
GlobalUnitOfWork
GenericUnitOfWork
ApplicationUnitOfWork
UnitOfWork containing every Repository
~~~

The final persistent scenario could still commit single-repository use cases at the composition boundary.

**Decision:** KEEP capability-specific UnitOfWork. Do not generalize yet.

---

# 14. Transaction-boundary review

One original architecture rule was strongly confirmed:

~~~text
Repository.save()
    ≠
transaction commit
~~~

Repositories correctly remain non-committing.

This gives the runtime/composition boundary control over:

~~~text
commit
rollback
event publication ordering
~~~

The architecture therefore remains:

~~~text
Repository
    stages persistence

Transaction boundary
    decides durability
~~~

**Decision:** KEEP.

---

# 15. Domain Event review

Persistence exposed a real semantic difference between local and SQL execution.

InMemory behavior could effectively treat:

~~~text
save
    -> durable enough for process-local scenario
~~~

SQL cannot.

The real sequence is:

~~~text
Domain behavior
    ↓
Repository save
    ↓
COMMIT
    ↓
publish successful business fact
~~~

This pressure produced two solutions at different scopes.

## 15.1 Multi-Aggregate onboarding

The UnitOfWork commits before the Handler publishes `SupplierOnboardingStarted`.

## 15.2 Single-repository persistent composition

`DeferredDomainEventDispatcher` buffers events until the composition root commits.

This keeps Application Handlers persistence-agnostic.

**Decision:** KEEP the deferred dispatcher as an adapter mechanism for the current in-process runtime.

---

# 16. Event-delivery limitation

The deferred dispatcher solves ordering, not durable delivery.

The remaining failure window is:

~~~text
database COMMIT succeeds
        ↓
process crashes
        ↓
buffered event never published
~~~

This is not currently a defect against the implemented product contract because:

~~~text
no external broker
no durable integration-event subscriber
no cross-process delivery guarantee
~~~

exists yet.

A Transactional Outbox becomes justified only when reliable external publication becomes a real requirement.

**Decision:** DEFER Outbox.

---

# 17. Migration architecture review

Alembic remained correctly located in persistence tooling.

The final end-to-end scenario uses:

~~~text
empty database
    ↓
alembic upgrade head
    ↓
business execution
~~~

rather than treating `metadata.create_all()` as the deployment mechanism.

At the same time, focused Repository tests may still use `create_all()` because their subject is current repository behavior rather than schema-history correctness.

That separation is useful:

~~~text
Repository contract
    tests behavior

Migration test
    tests history/bootstrap
~~~

**Decision:** KEEP.

---

# 18. Migration limitations after the baseline

Only one schema revision currently exists.

Therefore the project has proven:

~~~text
empty database -> head
~~~

but has not yet needed to prove:

~~~text
released revision N -> revision N+1
data transformation migration
rolling application/schema compatibility
zero-downtime migration
~~~

Those concerns become real only when the second migration is introduced.

**Decision:** do not build a migration-compatibility framework before revision 2 creates pressure.

---

# 19. Cross-dialect review

SQLite and PostgreSQL played different and complementary roles.

SQLite provided:

~~~text
fast relational feedback
local file persistence
normal CI execution
restart testing
foreign-key enforcement
~~~

PostgreSQL exposed:

~~~text
real identifier-length limits
ORM insert-order pressure
constraint/index reflection differences
production-oriented semantics
committed owned-row collision
~~~

This validates the testing architecture:

~~~text
SQLite
    accelerates feedback

PostgreSQL
    validates reference relational semantics
~~~

Neither backend should replace the other.

**Decision:** KEEP both.

---

# 20. PostgreSQL-specific lessons

The persistence cycle produced multiple cases where PostgreSQL changed implementation details without changing business contracts.

Examples:

~~~text
technical Assessment question identity
63-character identifier limit
UNIQUE constraint backing-index reflection
committed owned-child reconciliation
~~~

This confirms the rule:

> **Do not weaken production-oriented semantics to preserve artificial SQLite symmetry.**

**Decision:** KEEP PostgreSQL as reference backend.

---

# 21. Testing architecture review

The test architecture now contains:

~~~text
Domain unit tests
Application tests
InMemory Repository Contracts
SQLite Repository Contracts
PostgreSQL Repository Contracts
architecture fitness tests
relational constraint tests
transaction tests
migration tests
end-to-end local scenario
end-to-end persistent restart scenario
~~~

This is a strong layered testing system.

However, `0.2.0a7` exposed one real gap.

---

# 22. Repository Contract gap discovered

The shared SQL Repository Contracts correctly tested:

~~~text
save
get
reload
update
isolation
lookup semantics
~~~

but most SQL contract tests lived inside one Session/transaction lifecycle.

They did not fully exercise:

~~~text
create
    ↓
COMMIT
    ↓
new persistence state
    ↓
reload
    ↓
mutate owned collection
    ↓
save
    ↓
COMMIT
~~~

The persistent end-to-end test caught a failure that the normal contract tests could not.

This does **not** mean the shared Repository Contracts are wrong.

It means there are two distinct guarantees:

~~~text
Repository behavioral contract
        +
Durable committed lifecycle qualification
~~~

The second guarantee belongs to SQL adapter integration.

**Decision:** add focused committed-lifecycle tests when owned-collection mappers evolve. Do not pollute the generic Repository Port contract with transaction concepts.

---

# 23. Architecture fitness review

Executable architecture tests prevented persistence frameworks from entering:

~~~text
domain
application
ports
~~~

throughout the cycle.

This matters because seven persistence milestones created repeated opportunities for leakage.

The gates remained green without requiring waivers.

**Decision:** KEEP and extend architecture fitness tests whenever a new infrastructure framework is introduced.

---

# 24. Dependency-management review

The base package still has:

~~~text
dependencies = []
~~~

Persistence remains opt-in:

~~~text
pysrmkit[persistence]
pysrmkit[migrations]
pysrmkit[postgresql]
~~~

This proves that infrastructure growth did not force every consumer to install SQLAlchemy, Alembic, or Psycopg.

**Decision:** KEEP optional adapter dependencies.

---

# 25. InMemory adapter review after SQL persistence

The InMemory adapters remain first-class.

They still provide:

~~~text
fast Domain/Application tests
deterministic examples
contract reference behavior
zero-infrastructure usage
pedagogical clarity
~~~

SQL persistence did not replace them.

**Decision:** KEEP.

---

# 26. Manual composition review

Manual constructor injection still works.

There is still no evidence that PySRMKit needs a DI container.

However, the persistent composition root is materially more complex than the first local example.

It must assemble:

~~~text
Engine
Session factory
SQL repositories
UnitOfWork
Clock
Deferred dispatcher
InProcess dispatcher
QualificationPolicy
Application Handlers
commit/publish behavior
migration bootstrap
~~~

This complexity is not yet a DI-container problem.

It is a **framework consumption problem**.

Users should not need to understand every internal adapter class merely to execute stable business use cases.

This is the strongest new pressure after persistence.

---

# 27. Public package surface review

The package-level public surface is still intentionally minimal.

At the top level:

~~~python
import pysrmkit
pysrmkit.__version__
~~~

is effectively the only stable facade.

Consumers currently need deep imports such as:

~~~text
pysrmkit.application.qualification.handlers
pysrmkit.adapters.sqlalchemy.repositories.*
pysrmkit.domain.qualification.value_objects
~~~

This was acceptable while use cases were still moving.

The original package architecture explicitly deferred a public facade until use cases became stable.

That condition is now substantially satisfied for the first Supplier qualification vertical slice.

**Finding:** Public API pressure is now real.

---

# 28. What "Public API" should mean next

The next Public API problem should first be treated as a **Python framework API**, not automatically as an HTTP framework.

The first question is:

~~~text
How should a Python consumer use PySRMKit
without importing internal package structure?
~~~

before:

~~~text
How should FastAPI expose PySRMKit over HTTP?
~~~

A stable Python facade can later support:

~~~text
FastAPI
Django
CLI
Notebook
agent runtime
external SRM adapter
application service
~~~

without making any one transport the canonical interface.

---

# 29. Public API design pressure

The product-vision rule already states that a public API should prefer:

~~~text
business names
explicit types
predictable behavior
explicit errors
small interfaces
~~~

and avoid collapsing everything into:

~~~python
execute(action="X", payload={...})
~~~

The current stable vertical slice now provides enough real vocabulary to design such an API from evidence.

Potential pressure includes:

~~~text
stable imports
intentional re-exports
typed public results
typed public errors
composition helpers
runtime ownership
adapter configuration
deprecation policy
py.typed
public API tests
~~~

These are now more concrete than adding another infrastructure technology.

---

# 30. What implementation changed relative to the original persistence design

Several predictions were confirmed.

~~~text
Predicted
    SQLAlchemy remains in adapters
Observed
    CONFIRMED

Predicted
    Repository Ports survive
Observed
    CONFIRMED

Predicted
    one adapter family can serve SQLite/PostgreSQL
Observed
    CONFIRMED

Predicted
    UnitOfWork appears only under real atomicity pressure
Observed
    CONFIRMED

Predicted
    event dispatch must follow commit
Observed
    CONFIRMED

Predicted
    Alembic belongs to persistence tooling
Observed
    CONFIRMED

Predicted
    Outbox remains deferred
Observed
    CONFIRMED
~~~

Other areas were refined by reality.

~~~text
Owned collection update strategy
    had to evolve to row reconciliation

Repository Contract coverage
    needed durable restart qualification above contract level

Constraint naming
    had to respect PostgreSQL identifier limits

Schema comparison
    had to distinguish logical semantics from physical reflection
~~~

This is exactly the intended specification/code feedback loop.

---

# 31. Abstractions genuinely justified by implementation

The project now has direct evidence for:

~~~text
Aggregate Root
Value Object
Domain Policy
Domain Event
Repository
Repository Contract
Adapter
Data Mapper
UnitOfWork - capability-specific
Composition Root
Architecture Fitness Function
Migration
Deferred Event Dispatcher
~~~

These terms can now be used confidently in documentation because they describe real implementation roles.

---

# 32. Concepts still conceptually present but not implementation-justified

The following remain candidates, not mandatory architecture:

~~~text
Generic UnitOfWork
Generic Repository
Command Bus
Query Bus
Mediator
DI Container
GoF State Pattern
Specification Pattern framework
Transactional Outbox
Event Sourcing
CQRS read-model infrastructure
Async persistence
Optimistic locking
distributed transaction
cache abstraction
workflow engine
~~~

The fact that PySRMKit now has SQL persistence does not justify them automatically.

---

# 33. Current architecture strengths

At the end of the Persistent Core cycle:

~~~text
1. Domain remains framework-independent.
2. Five Aggregate boundaries survived relational persistence.
3. Repository Ports remained small and stable.
4. InMemory and SQL adapters remain substitutable at the contract level.
5. One SQLAlchemy implementation serves SQLite and PostgreSQL.
6. Data Mapper keeps persistence identity outside the Domain.
7. Database constraints protect cross-instance invariants.
8. Transaction ownership is explicit.
9. UnitOfWork exists only where demonstrated atomicity requires it.
10. Schema history is versioned through Alembic.
11. Complete business state survives persistence-context recreation.
12. Success and rejection paths are durable.
13. Architecture rules are executable.
14. Infrastructure dependencies remain optional.
15. The full Core remains usable without SQL.
~~~

---

# 34. Current architecture limitations

The strongest remaining limitations are now:

~~~text
1. No intentional stable Python public facade exists.
2. Persistent runtime composition is verbose and infrastructure-aware.
3. Single-repository commit/publish orchestration is manual at composition level.
4. In-process event publication is not crash-durable.
5. Repository Contracts do not by themselves prove committed-update lifecycles.
6. Only the first Alembic revision exists.
7. Concurrent lost-update behavior has not been qualified.
8. Infrastructure errors do not yet have a fully demonstrated public translation strategy.
9. No read-model/query architecture exists beyond Aggregate-oriented lookups.
10. No public HTTP transport exists.
11. No external SRM integration exists.
12. Relationship activation after Qualification is still absent.
13. Documents/evidence/compliance/risk remain outside the implemented Core.
14. Production observability/security hardening remains deferred.
~~~

These are limitations, not automatically the next roadmap.

---

# 35. Deferred decisions re-evaluated

## 35.1 Transactional Outbox

Pressure level: **LOW now / potentially HIGH later**

Trigger:

~~~text
reliable event delivery to external process/broker
~~~

**Decision:** DEFER.

## 35.2 Optimistic locking

Pressure level: **LOW**

No demonstrated lost-update conflict exists yet.

**Decision:** DEFER.

## 35.3 Async persistence

Pressure level: **LOW**

No async public runtime exists.

**Decision:** DEFER.

## 35.4 Global UnitOfWork

Pressure level: **LOW**

Current capability UoW solves the only demonstrated cross-Aggregate atomic transaction.

**Decision:** DEFER.

## 35.5 Query/read-model architecture

Pressure level: **LOW to MEDIUM**

No consumer has yet produced complex read/query pressure.

**Decision:** DEFER until Public API/UI consumption reveals concrete queries.

## 35.6 DI container

Pressure level: **LOW**

Manual composition works. The next problem is reducing public composition complexity, not adopting a container.

**Decision:** DEFER.

## 35.7 Migration compatibility strategy

Pressure level: **LOW now / mandatory at second schema revision**

**Decision:** revisit when migration revision 2 appears.

---

# 36. Candidate Cycle 3 directions

The candidate directions after Persistent Core are:

~~~text
A. Activation
B. Documents & Evidence
C. Compliance
D. Risk
E. Public API & Runtime Composition
F. External SRM Integration
G. Audit & Observability
H. Reliable Event Delivery / Outbox
I. Concurrency Hardening
~~~

---

# 37. Cycle 3 decision criteria

| Criterion | Question |
|---|---|
| Real pressure | Did implementation expose the limitation directly? |
| Architecture leverage | Does solving it validate or improve existing boundaries? |
| Product usefulness | Does it make PySRMKit materially easier to use? |
| Learning value | Does it create legitimate new design pressure? |
| Dependency order | Should it precede other candidates? |
| Reversibility | Can it be added without contaminating Domain semantics? |

---

# 38. Candidate comparison

| Candidate | Real pressure | Architecture leverage | Product usefulness | Dependency order | Recommendation |
|---|---:|---:|---:|---:|---|
| Activation | Medium | High | High | Medium | Strong business candidate |
| Documents & Evidence | Medium | High | High | Medium | Later domain slice |
| Compliance | Medium | High | High | Medium | After evidence/rules pressure |
| Risk | Medium | High | High | Medium | After evidence/integration pressure |
| **Public API & Runtime Composition** | **High** | **Very High** | **Very High** | **Very High** | **Cycle 3** |
| External SRM Integration | Medium | Very High | High | Lower than public boundary | After public/composition boundary |
| Audit & Observability | Low-Medium | Medium | Medium | Later | Production hardening |
| Outbox | Low | High | Low now | Depends on external events | Deferred |
| Concurrency Hardening | Low | High | Medium | Evidence-dependent | Deferred |

---

# 39. Why Public API & Runtime Composition wins

Persistence solved the previous strongest limitation:

~~~text
state disappears
~~~

The strongest new friction is now:

~~~text
the framework works
    but
using it requires knowledge of internal assembly
~~~

This is visible directly in the persistent example.

A consumer should not have to know the exact internal arrangement of:

~~~text
SqlAlchemySupplierRepository
SqlAlchemySupplierRelationshipRepository
SqlAlchemySupplierOnboardingRepository
SqlAlchemySupplierAssessmentRepository
SqlAlchemySupplierQualificationRepository
SqlAlchemySupplierOnboardingUnitOfWork
DeferredDomainEventDispatcher
Session factory
Alembic bootstrap details
~~~

to use stable Supplier business capabilities.

The next cycle can therefore validate a new boundary:

~~~text
CONSUMER
    ↓
PUBLIC PYTHON API
    ↓
RUNTIME / COMPOSITION
    ↓
APPLICATION
    ↓
PORTS
    ↓
ADAPTERS
~~~

without changing Domain semantics.

---

# 40. Cycle 3 direction

**Selected direction:**

~~~text
0.3.x - Public API & Runtime Composition
~~~

This is a direction, not yet a complete milestone roadmap.

Its first responsibility is to make the qualified Core intentionally consumable.

It should begin with Python-facing API design.

HTTP is a possible adapter later, not the foundation of the cycle.

---

# 41. Initial Cycle 3 problem statement

Today:

~~~python
from pysrmkit.adapters.sqlalchemy.repositories.qualification import (
    SqlAlchemySupplierQualificationRepository,
)
from pysrmkit.application.qualification.handlers import (
    EvaluateSupplierQualificationHandler,
)
...
~~~

works, but it exposes internal package structure to consumers.

The desired direction is closer to:

~~~text
consumer intent
    ↓
stable public PySRMKit surface
    ↓
internal composition hidden
~~~

without hiding the business language behind a generic command dictionary.

---

# 42. Cycle 3 should investigate

A targeted next specification should answer:

~~~text
Which symbols are public?

Which imports are stable?

Should PySRMKit expose a facade object?

Should public commands/results remain directly importable?

How is an InMemory runtime constructed?

How is a SQL runtime constructed?

Who owns Engine / Session lifetime?

Who owns transaction commit/publish behavior?

How are migration/bootstrap concerns exposed or kept separate?

How are infrastructure exceptions translated?

How are optional adapters selected?

Should public API return Domain objects, result DTOs, or both?

What becomes part of semantic-versioning compatibility?

Should py.typed be shipped?

How are public imports tested?

Where would a future FastAPI adapter plug in?
~~~

---

# 43. What Cycle 3 must not assume

Do not automatically introduce:

~~~text
FastAPI
Django
GraphQL
DI container
Service Locator
Command Bus
Query Bus
Generic execute(action, payload)
global UnitOfWork
async runtime
Outbox
Kafka
Redis
workflow engine
~~~

The first problem is the public Python consumption boundary.

---

# 44. Activation remains the strongest business-slice candidate

Selecting Public API & Runtime Composition does not make Activation unimportant.

Activation remains the clearest next business continuation:

~~~text
Qualification
    ↓
Activation eligibility
    ↓
ACTIVE relationship
~~~

It may become the first new business capability after the public runtime boundary is established.

This ordering has an architectural advantage:

~~~text
first
    expose stable consumption boundary

then
    extend business behavior through that boundary
~~~

The next review may reverse this order if a real Activation consumer appears first.

---

# 45. External integration ordering

Persistence is now ready for external SRM integration.

However, a direct Ivalua/SAP/Coupa adapter before a stable consumption/composition boundary risks making the first integration define internal runtime APIs accidentally.

Preferred order:

~~~text
Persistent Core
    ↓
Public API / Runtime Composition
    ↓
External Integration
~~~

An Anti-Corruption Layer can then target intentional application/public contracts.

---

# 46. Testing consequences for Cycle 3

A Public API cycle should introduce new tests at the package boundary:

~~~text
stable import tests
public symbol tests
public error tests
runtime construction tests
InMemory public scenario
SQL public scenario
side-effect-free import tests
optional-dependency tests
backward-compatibility tests for public imports
~~~

The current deep internal tests remain valuable.

Public API tests should sit above them rather than replace them.

---

# 47. Documentation consequences

The public surface becomes a compatibility promise.

Documentation must distinguish:

~~~text
public
    supported consumer contract

internal
    free to refactor

adapter-specific
    opt-in advanced surface
~~~

This will make semantic versioning meaningful beyond `__version__`.

---

# 48. Learning map - persistence cycle

~~~text
Problem
    state disappears
        ↓
Repository Ports
        ↓
SQLAlchemy adapters
        ↓
Data Mapper
        ↓
SQLite + PostgreSQL
        ↓
real transaction pressure
        ↓
capability UnitOfWork
        ↓
Alembic
        ↓
restart qualification
~~~

---

# 49. Learning map - next pressure

~~~text
Problem
    framework works
    but consumption requires internal knowledge
        ↓
Public API boundary
        ↓
stable imports
        ↓
runtime composition
        ↓
consumer-facing contracts
        ↓
future transports/integrations
~~~

---

# 50. Architecture decision summary

| Topic | Decision after Persistent Core |
|---|---|
| Domain model | KEEP |
| Aggregate boundaries | KEEP |
| QualificationPolicy | KEEP |
| Repository Ports | KEEP |
| Generic Repository | AVOID |
| InMemory adapters | KEEP |
| SQLAlchemy adapter family | KEEP |
| Data Mapper | KEEP |
| Persistence-only surrogate IDs | ALLOW inside adapter |
| Owned collection updates | RECONCILE by Domain identity |
| Repository commit | FORBIDDEN |
| Capability UnitOfWork | KEEP |
| Global UnitOfWork | DEFER |
| Deferred in-process event dispatch | KEEP for current runtime |
| Transactional Outbox | DEFER |
| Alembic | KEEP |
| SQLite | KEEP fast relational backend |
| PostgreSQL | KEEP reference backend |
| Async persistence | DEFER |
| Optimistic locking | DEFER |
| DI container | DEFER |
| Public Python API | NOW JUSTIFIED |
| HTTP API | AFTER/ON TOP OF Python public boundary |
| External SRM adapter | AFTER intentional public/composition boundary |
| Cycle 3 direction | **Public API & Runtime Composition** |

---

# 51. Next targeted document

The next document should be:

~~~text
19_PYSRMKIT_PUBLIC_API_AND_RUNTIME_COMPOSITION_ARCHITECTURE.md
~~~

Its job is not to specify every future interface.

It should define only enough to bootstrap Cycle 3:

~~~text
public-vs-internal contract
stable import philosophy
first public business surface
runtime/composition ownership
InMemory runtime
SQL runtime
transaction/event semantics
optional dependency behavior
public error boundary
public API testing strategy
first Cycle 3 milestone proposal
~~~

After that targeted document is accepted, implementation should resume.

---

# 52. Final review conclusion

The Persistent Core did not reveal a need for architectural reinvention.

It revealed that the original boundaries were strong enough to absorb:

~~~text
ORM persistence
two SQL dialects
foreign keys
uniqueness constraints
technical surrogate IDs
transactions
rollback
post-commit event ordering
schema migrations
process-context restart
~~~

while keeping the business model stable.

The major lesson is therefore:

> **The next architecture problem is no longer how PySRMKit stores its Domain. It is how consumers intentionally use the Domain and Application capabilities that are now stable.**

The selected next direction is:

~~~text
0.3.x - Public API & Runtime Composition
~~~

with a Python-first public boundary and no automatic commitment to an HTTP framework.

---

# 53. Final rule

> **Keep the Domain stable until business pressure changes it.**

> **Keep persistence complexity below the adapter boundary.**

> **Promote an abstraction only after repeated implementation pressure proves its value.**

> **The next stable contract should be the consumer-facing Python API, not another infrastructure layer.**
