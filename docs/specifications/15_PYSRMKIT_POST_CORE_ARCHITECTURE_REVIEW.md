# PySRMKit - Post-Core Architecture Review

**Document:** `15_PYSRMKIT_POST_CORE_ARCHITECTURE_REVIEW.md`  
**Status:** POST-CORE REVIEW / ITERATIVE DEEP DIVE  
**Review scope:** `0.1.0a1` through `0.1.0a8`  
**First-Core status:** QUALIFIED / GREEN  
**Date:** 2026-10-27

---

# 1. Purpose

This document is the first targeted architecture review created after the pre-implementation specification cut-off.

It is deliberately **not** a return to broad speculative specification.

The baseline `00 -> 14` was intended to stop once enough design existed to implement a coherent local Core. That condition has now been satisfied.

The purpose of this review is therefore:

```text
IMPLEMENTED CORE
      |
      v
OBSERVED FRICTION
      |
      v
ARCHITECTURE REVIEW
      |
      v
REAL NEXT PRESSURE
      |
      v
TARGETED NEXT SPEC
```

The governing rule remains:

> **Problem before Pattern.**

and:

> **Document again when the code reveals a new design problem.**

---

# 2. Review evidence

The review is grounded in the completed first implementation cycle:

```text
0.1.0a1  Repository Bootstrap
0.1.0a2  Supplier Core
0.1.0a3  Supplier Relationships
0.1.0a4  Relationship Lifecycle
0.1.0a5  Onboarding Core
0.1.0a6  Qualification Domain
0.1.0a7  Qualification Application Flow
0.1.0a8  Local Core Qualification
```

The final local business journey is executable:

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
        +------> QUALIFIED
        |
        +------> NOT_QUALIFIED
```

Final evidence includes:

```text
GitHub CI                     GREEN
Package install               GREEN
165 tests                     GREEN
Architecture fitness tests    GREEN
Repository contracts          GREEN
Success scenario              GREEN
Rejection scenario            GREEN
Local executable example      GREEN
Coverage                      ~99%
```

The local installation also proved that the package can be installed editable in a fresh virtual environment and execute the complete qualification example outside GitHub Actions.

---

# 3. Review questions

The roadmap defined the following architecture checkpoint after `0.1.0a8`:

```text
Did any abstraction feel forced?
Did package boundaries hold?
Did repositories remain small?
Did handlers remain thin?
Did tests expose bad assumptions?
What is the next real infrastructure pressure?
```

This document answers each question from implementation evidence.

---

# 4. Domain boundary review

## 4.1 Supplier

`Supplier` remained a cohesive canonical identity Aggregate.

It did not absorb organization-specific lifecycle, onboarding, assessment, or qualification state.

This validates the original distinction:

```text
Supplier
    = canonical supplier identity

SupplierRelationship
    = our contextual relationship with that supplier
```

This separation prevented the Supplier Aggregate from becoming a God Aggregate.

**Decision:** KEEP.

---

## 4.2 SupplierRelationship

`SupplierRelationship` proved to be an independent Aggregate Root.

It owns:

```text
Supplier relationship identity
Internal organization context
Relationship lifecycle stage
Lifecycle transitions
Relationship lifecycle events
```

It does not own onboarding requirement state, assessment state, or qualification decisions.

This boundary remained stable across the first cycle.

**Decision:** KEEP.

---

## 4.3 SupplierOnboarding

The pre-implementation model left open whether onboarding should be a separate Aggregate, Entity, or simpler object.

Implementation pressure resolved the question.

`SupplierOnboarding` now has:

```text
independent identity
relationship ownership
requirements
satisfaction state
completion invariant
completion event
repository
application use cases
```

That is enough independent lifecycle and consistency behavior to justify an Aggregate boundary.

**Decision:** KEEP as Aggregate Root.

---

## 4.4 SupplierAssessment

`SupplierAssessment` emerged only when the Qualification Application Flow required concrete assessment facts.

It owns:

```text
question snapshots
answers
mandatory-answer invariant
score computation
completion
completion event
```

The implementation deliberately avoided a generic questionnaire engine, template engine, scoring DSL, or evidence platform.

**Decision:** KEEP the current narrow Aggregate. Extend only from real assessment pressure.

---

## 4.5 SupplierQualification

`SupplierQualification` remains scoped by explicit business context rather than a global supplier flag.

The important modeling decision is:

```text
Supplier
    is not globally
    qualified = True

Qualification
    applies to
    Relationship + Scope
```

`QualificationScope` prevented a major semantic collapse and remains one of the strongest domain choices of the first cycle.

**Decision:** KEEP.

---

# 5. Aggregate isolation review

The first cycle now contains five behavior-bearing Aggregates:

```text
Supplier
SupplierRelationship
SupplierOnboarding
SupplierAssessment
SupplierQualification
```

The implementation proved that they can cooperate without direct cross-Aggregate mutation.

Examples:

```text
Assessment completion
    does not directly mutate Qualification

Qualification evaluation
    does not directly mutate Relationship

Application Handlers
    coordinate through Repository Ports
```

This is an important DDD result.

Cross-Aggregate coordination belongs in the Application Layer unless a future business invariant demonstrates otherwise.

**Decision:** KEEP current Aggregate isolation.

---

# 6. Application Layer review

## 6.1 Commands and Handlers

The CQRS-lite approach remained sufficient.

Commands express intent:

```text
RegisterSupplier
InviteSupplierRelationship
CompleteSupplierOnboarding
CompleteSupplierAssessment
EvaluateSupplierQualification
```

Handlers primarily:

```text
load state
check cross-instance preconditions
build domain inputs
call domain behavior / policy
save
dispatch events
return result
```

No Command Bus or mediator infrastructure was required.

**Decision:** KEEP direct Handler invocation.

---

## 6.2 Business logic placement

The most important application-layer validation occurred during Qualification.

The Handler does not implement:

```python
if assessment.score >= 80:
    qualification.status = QUALIFIED
```

Instead:

```text
Handler
    collects facts
        |
        v
QualificationPolicy
    decides
        |
        v
SupplierQualification
    applies decision
```

This confirms that Application coordination and Domain decision-making remain distinct.

**Decision:** KEEP.

---

# 7. QualificationPolicy review

`QualificationPolicy` is the first explicit Domain Policy carrying meaningful variable business logic.

It currently evaluates facts such as:

```text
onboarding_complete
assessment_completed
assessment_score
required_answers_complete
```

It returns an explainable `QualificationDecision`, not a boolean.

This is important because:

```text
decision
    = outcome
    + reasons
    + failed requirements
    + timestamp
```

## 7.1 Was a Strategy hierarchy needed?

No.

One concrete Policy currently exists.

Creating:

```text
AbstractQualificationPolicy
DefaultQualificationPolicy
QualificationPolicyFactory
```

would still be speculative.

The Strategy boundary is conceptually present because the Handler consumes a replaceable policy object, but implementation hierarchy should wait for actual alternative algorithms.

**Decision:** KEEP simple concrete Policy. Defer hierarchy.

---

# 8. Lifecycle modeling review

The Relationship lifecycle uses:

```text
Enum
+
explicit Aggregate behaviors
+
guards
```

This was enough for the implemented transitions.

No GoF State Pattern became necessary.

This validates the distinction:

```text
State Machine
    !=
State Pattern
```

**Decision:** KEEP Enum + guards until state-specific behavior becomes materially complex.

---

# 9. Repository review

Repository Ports remained Aggregate-specific and small.

Typical contracts contain:

```text
get
save
+ one domain-relevant lookup
```

Examples include:

```text
find_for_relationship
find_latest_for_relationship
find_current_for_scope
```

No GenericRepository abstraction was needed.

This is a positive result.

## 9.1 Contract tests

Shared Repository Contract tests became one of the strongest architecture mechanisms in the project.

They prove expected semantics independently from a concrete persistence technology.

This creates a direct path to future adapters:

```text
Repository Port
        |
        +--> InMemory Adapter
        +--> SQLAlchemy Adapter
        |       +--> SQLite engine
        |       +--> PostgreSQL engine
        |
        +--> future specialized adapter if justified
```

This is also concrete evidence of Liskov Substitution when multiple adapters satisfy the same behavioral contract.

**Decision:** KEEP Aggregate-specific Repository Ports and shared contract suites.

---

# 10. InMemory adapter review

InMemory adapters were not disposable prototypes.

They successfully proved:

```text
Repository semantics
Aggregate reconstitution
copy / snapshot behavior
application orchestration
architecture independence
deterministic tests
```

They also exposed their natural limit:

```text
process stops
    ->
state disappears
```

This is now the strongest concrete infrastructure pressure in the project.

**Finding:** Persistence is no longer hypothetical. It is the next major missing capability.

---

# 11. Domain Events review

Domain Events proved useful across the whole scenario.

The final successful trace includes:

```text
SupplierCreated
SupplierRelationshipCreated
SupplierInvited
SupplierOnboardingStarted
SupplierOnboardingCompleted
SupplierAssessmentCompleted
SupplierQualificationRequested
SupplierQualified
```

## 11.1 Repetition discovered

Several Aggregates now repeat essentially the same event-recording mechanism:

```text
_events
_record(...)
pull_events()
```

This repetition is no longer hypothetical.

It appears in:

```text
Supplier
SupplierRelationship
SupplierOnboarding
SupplierAssessment
SupplierQualification
```

This satisfies the project's own threshold for considering shared event-recording support.

## 11.2 Does this justify BaseAggregateRoot?

Not automatically.

Possible refactoring options include:

```text
A. small composition helper
B. narrowly scoped mixin
C. Aggregate event-recording base class
D. leave repetition explicit
```

The next refactoring must compare these options against:

```text
clarity
type safety
inheritance coupling
dataclass ergonomics
testability
domain readability
```

The review therefore records **real abstraction pressure**, but does not select a generic base class yet.

**Decision:** Candidate for targeted refactoring review, not automatic implementation.

---

# 12. DomainEventDispatcher review

`InProcessDomainEventDispatcher` is sufficient for the local Core.

It provides synchronous dispatch without introducing:

```text
Kafka
RabbitMQ
retry infrastructure
outbox
distributed delivery guarantees
```

No asynchronous event infrastructure is justified yet.

**Decision:** KEEP synchronous in-process dispatch for the Core.

---

# 13. UnitOfWork review

`UnitOfWork` was deliberately reconsidered several times during `a5 -> a8`.

Real pressure appeared because Application Handlers increasingly read multiple repositories and coordinate multiple capabilities.

However, the current adapters do not provide a real shared transaction resource.

Therefore:

```text
NoOpUnitOfWork
    !=
transactional UnitOfWork
```

A ceremonial UnitOfWork around dictionaries would suggest guarantees that do not exist.

## 13.1 When does UnitOfWork become justified?

When a persistence implementation provides:

```text
transaction
commit
rollback
atomicity
shared session / connection scope
```

SQLAlchemy + relational persistence is therefore the natural point to reconsider the pattern.

**Decision:** DEFER until transactional persistence exists.

---

# 14. Dependency Injection review

The complete local scenario is assembled manually in:

```text
examples/local_qualification.py
```

The composition root constructs repositories, clock, event dispatcher, policy, and handlers explicitly.

No DI framework was needed.

This proved that constructor injection is sufficient at the current scale.

**Decision:** KEEP manual composition. No DI container.

---

# 15. Package architecture review

The intended dependency rules held:

```text
domain      -> no application
domain      -> no ports
domain      -> no adapters
application -> no concrete adapters
ports       -> no adapters
domain      -> no infrastructure frameworks
```

Architecture tests made these rules executable.

The package structure remained understandable while the codebase grew from bootstrap to five Aggregates and multiple application flows.

**Decision:** KEEP current layer-first + capability-oriented hybrid.

---

# 16. Testing architecture review

The test pyramid that emerged is coherent:

```text
Domain unit tests
        |
Application tests
        |
Repository contract tests
        |
Architecture tests
        |
End-to-end local scenarios
```

The first cycle ended with 165 passing tests and approximately 99% coverage.

The high confidence comes primarily from behavior and contract coverage, not from the percentage itself.

## 16.1 Important testing lesson

Repository contracts are already prepared for a future persistence adapter.

The original testing strategy anticipated:

```text
same Repository Contract
        |
        +--> InMemory
        +--> PostgreSQL later
```

This is now ready to become executable in the next cycle.

**Decision:** KEEP tests technology-stratified. Do not move most tests to a database.

---

# 17. Tooling and local-environment review

The final local validation exposed an operational issue unrelated to PySRMKit's architecture:

```text
multiple Python environments
Conda base
Homebrew Python
.venv
```

Using bare `pytest` could select a global executable while the package was installed in the virtual environment.

The reliable project commands are therefore:

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m pytest --cov=pysrmkit --cov-report=term-missing
```

This guarantees that package installation and test execution use the same interpreter.

**Decision:** Prefer `python -m ...` project commands in contributor documentation.

---

# 18. What was deliberately avoided

The first cycle did **not** require:

```text
GenericRepository
BaseEntity
BaseValueObject
BaseService
BaseHandler
Command Bus
Query Bus
DI framework
GoF State Pattern
Specification framework
workflow engine
message broker
ORM
HTTP framework
database
cloud runtime
```

This is not missing architecture.

It is evidence that YAGNI and KISS remained effective.

---

# 19. What implementation changed in the specifications

The strongest spec feedback happened in the final scenario.

The initial `a8` roadmap omitted several operations that became real prerequisites:

```text
SatisfyOnboardingRequirement
CompleteSupplierOnboarding
RecordAssessmentAnswer
```

Implementation proved that:

```text
onboarding completion
    is a real qualification fact

assessment score
    requires real recorded answers
```

The roadmap was corrected instead of weakening the Domain rules.

This validates the intended feedback loop:

```text
SPEC
  |
  v
CODE
  |
  v
TEST
  |
  v
REALITY CHECK
  |
  +--> confirm spec
  +--> correct spec
```

---

# 20. Current architecture strengths

At the end of the first cycle, the strongest properties are:

```text
1. Domain remains framework-independent.
2. Aggregate boundaries are explicit.
3. Cross-Aggregate coordination is explicit.
4. Qualification decisions are explainable.
5. Repository Ports are minimal.
6. InMemory adapters behave like persistence boundaries.
7. Contract tests are reusable.
8. Architecture rules are executable.
9. Domain Events expose meaningful business facts.
10. Local composition requires no runtime infrastructure.
```

---

# 21. Current architecture limitations

The most important limitations are now concrete:

```text
1. State is not durable across process restart.
2. No relational transaction boundary exists.
3. UnitOfWork cannot yet provide real guarantees.
4. Event recording is repeated across Aggregates.
5. Event dispatch is process-local only.
6. No public API exists.
7. No external SRM integration exists.
8. Relationship activation after Qualification is not modeled.
9. Documents / evidence / compliance / risk remain outside the first Core.
```

These are now observed boundaries, not speculative backlog items.

---

# 22. Candidate next directions

The first-cycle roadmap explicitly left the next direction open.

Candidates are:

```text
A. Activation
B. Documents & Evidence
C. Compliance
D. Risk
E. Persistence
F. Public API
G. External SRM integration
```

The next cycle should maximize both real product value and architecture learning while solving an observed pressure.

---

# 23. Decision criteria for Cycle 2

The following criteria are used:

| Criterion | Question |
|---|---|
| Real pressure | Did the first Core expose a concrete limitation? |
| Architectural leverage | Does solving it validate existing Ports and boundaries? |
| Learning value | Does it create legitimate pressure for new concepts? |
| Product usefulness | Does it move PySRMKit toward practical use? |
| Reversibility | Can the design evolve without contaminating the Domain? |
| Dependency order | Should another concern logically come first? |

---

# 24. Candidate comparison

| Direction | Real pressure | Architecture leverage | Learning value | Immediate product value | Recommendation |
|---|---:|---:|---:|---:|---|
| Activation | Medium | Medium | Medium | High | Later business slice |
| Documents & Evidence | Medium | Medium | High | High | Later domain slice |
| Compliance | Medium | Medium | High | High | Later domain slice |
| Risk | Medium | Medium | High | High | Later domain slice |
| Persistence | **High** | **Very High** | **Very High** | **High** | **Cycle 2 candidate** |
| Public API | Medium | High | Medium | High | After persistence |
| External integration | Medium | High | Very High | High | After persistence/API boundary matures |

Persistence is the only candidate that directly attacks the strongest limitation exposed by the completed local Core while simultaneously validating Repository substitution and creating real transaction pressure.

---

# 25. Recommended Cycle 2 direction - Persistent Core

The recommended second cycle is:

```text
0.2.x - Persistent Core
```

The business model should remain substantially unchanged.

The architectural question becomes:

> **Can the exact same Domain and Application model survive replacement of InMemory persistence with real relational persistence?**

This is a stronger architecture test than immediately adding more SRM features.

---

# 26. Persistence architecture target

The desired dependency shape is:

```text
Domain
  ^
  |
Application
  |
  v
Repository Ports
  ^
  |
SQLAlchemy Persistence Adapter
  |
  +--> SQLite
  |
  +--> PostgreSQL
```

The Domain must remain unaware of:

```text
SQLAlchemy
SQLite
PostgreSQL
session
engine
migrations
```

---

# 27. Why SQLite belongs in the persistence cycle

SQLite is useful, but its role must be explicit.

It should not be treated as a substitute for PostgreSQL production validation.

Its value is:

```text
lightweight relational persistence laboratory
+
fast Repository Contract backend
+
local development database
+
mapping / transaction learning surface
```

SQLite introduces real persistence concerns absent from dictionaries:

```text
SQL mapping
constraints
foreign keys
transactions
schema lifecycle
serialization
connection lifecycle
```

without initially requiring:

```text
database server
network
credentials
container runtime
```

---

# 28. PostgreSQL role

PostgreSQL should remain the **reference production dialect**.

It is the backend that must validate concerns SQLite cannot faithfully represent, including richer transactional and concurrency behavior.

The rule should be:

> **SQLite is a lightweight persistence backend for local development and contract testing; PostgreSQL is the reference backend for production-oriented relational validation.**

---

# 29. One SQLAlchemy adapter or two database-specific repositories?

The first hypothesis should be:

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

unless implementation pressure proves the dialects require materially different repository behavior.

This follows the project's design rule:

```text
variation pressure
    before
abstraction split
```

---

# 30. Proposed persistence test layers

The next cycle should preserve the existing test architecture and add database-specific layers rather than replacing Core tests.

Candidate structure:

```text
PURE DOMAIN / APPLICATION
    no database

REPOSITORY CONTRACTS
    InMemory
    SQLite

POSTGRESQL INTEGRATION
    real PostgreSQL instance
    dialect-specific behavior
    transaction behavior

END-TO-END PERSISTENT SCENARIO
    same qualification journey
    process restart / reload
```

Conceptually:

```text
                PostgreSQL
               integration
                  /\
                 /  \
                /    \
          SQLite contracts
             /        \
            /          \
      Pure Domain / Application
```

---

# 31. UnitOfWork in Cycle 2

Persistence is also the right moment to revisit `UnitOfWork`.

With SQLAlchemy, the project can finally possess a real shared transaction boundary:

```text
SQLAlchemy Session
        |
        v
transaction
        |
        +--> commit
        +--> rollback
        +--> atomic repository operations
```

Only then does:

```text
UnitOfWork
```

have a concrete guarantee to expose.

**Cycle 2 hypothesis:** introduce UnitOfWork only when a use case actually requires coordinated atomic writes through the SQLAlchemy transaction boundary.

---

# 32. Data Mapper / ORM boundary

A critical Cycle 2 question is whether Domain Entities should remain persistence-ignorant.

The default decision is:

```text
Domain model
    !=
ORM model
```

Preferred direction:

```text
Domain Entity / Aggregate
        |
        v
Mapper / Persistence Model
        |
        v
SQLAlchemy
```

This keeps infrastructure metadata and relational concerns out of the Domain.

Whether classical mapping, explicit persistence records, or another SQLAlchemy technique is selected must be decided in the targeted persistence architecture document.

---

# 33. Migrations

Once persistent schemas exist, schema evolution becomes real.

A migration tool such as Alembic may become justified.

It should not be introduced before the persistence architecture establishes:

```text
mapping model
schema ownership
transaction boundary
database support policy
```

---

# 34. Proposed Cycle 2 milestone shape

The following is a **candidate**, not a frozen roadmap:

```text
0.2.0a1 - Persistence Architecture
        |
        v
0.2.0a2 - SQLAlchemy Mapping Foundation
        |
        v
0.2.0a3 - SQLite Repository Contracts
        |
        v
0.2.0a4 - PostgreSQL Repository Adapters
        |
        v
0.2.0a5 - Transaction Boundary / UnitOfWork checkpoint
        |
        v
0.2.0a6 - Persistent Local Qualification
```

The sequence may change once the persistence architecture is implemented and real pressure appears.

---

# 35. What should NOT happen in Cycle 2

Persistence work must not become an excuse to introduce unrelated infrastructure.

Do not automatically add:

```text
FastAPI
Kafka
Redis
Celery
cloud storage
OpenTelemetry
plugin system
generic DAO layer
generic repository framework
DI container
```

The second cycle should remain a coherent persistence vertical slice.

---

# 36. Refactoring candidates before or during Cycle 2

Two refactoring candidates are now evidence-based.

## 36.1 Common Domain Event recording support

Pressure: HIGH enough to review.

Decision: evaluate separately before introducing inheritance.

## 36.2 Persistence transaction abstraction

Pressure: EMERGING.

Decision: wait for SQLAlchemy transaction behavior before introducing UnitOfWork.

Everything else remains speculative.

---

# 37. Concepts genuinely demonstrated by the first Core

The first cycle now provides implementation evidence for:

```text
[DDD: Entity]
[DDD: Value Object]
[DDD: Aggregate Root]
[DDD: Domain Policy]
[DDD: Domain Event]

[PRINCIPLE: SRP]
[PRINCIPLE: OCP]
[PRINCIPLE: LSP]
[PRINCIPLE: ISP]
[PRINCIPLE: DIP]
[PRINCIPLE: Separation of Concerns]

[PATTERN: Repository]
[PATTERN: Strategy boundary]
[PATTERN: Adapter]

[ARCH: Ports and Adapters]
[ARCH: Hexagonal dependency direction]
[ARCH: CQRS-lite]
[ARCH: Composition Root]

[TEST: Unit Test]
[TEST: Invariant Test]
[TEST: Repository Contract]
[TEST: Architecture Fitness Function]
[TEST: Scenario Test]

[PYTHON: Protocol]
[PYTHON: dataclass]
[PYTHON: Enum]
[PYTHON: composition]
```

These labels are justified by executable evidence rather than by naming intent.

---

# 38. Patterns deliberately not introduced

The project also learned by **not** using several patterns prematurely:

```text
GoF State Pattern
Abstract Factory
Generic Repository
Specification Pattern
Command Bus
Query Bus
UnitOfWork
Transactional Outbox
Event Sourcing
DI Container
Workflow Engine
```

The absence of these patterns is part of the architectural result.

---

# 39. Architectural learning summary

The first cycle followed the intended deliberate-practice loop:

```text
real problem
    |
    v
constraint
    |
    v
simplest valid design
    |
    v
tests
    |
    v
implementation friction
    |
    v
pattern recognition
    |
    v
targeted refinement
```

Important examples:

```text
Relationship lifecycle
    -> Enum + guards
    -> no State Pattern

Qualification algorithm
    -> Domain Policy
    -> Strategy boundary emerges

Repository adapters
    -> Protocol + Contract Tests
    -> LSP becomes executable

Cross-repository coordination
    -> transaction pressure observed
    -> UnitOfWork still deferred

Repeated Aggregate event recording
    -> abstraction pressure now real
    -> refactor candidate recorded
```

---

# 40. Architecture decision

## Decision A - First Core

```text
0.1.x First Local Core
    = COMPLETE
```

No additional alpha milestone should be added merely to continue the sequence.

## Decision B - Immediate architecture work

Create targeted review/specification only for observed pressures.

## Decision C - Recommended Cycle 2

```text
0.2.x Persistent Core
```

with:

```text
SQLAlchemy persistence adapter
SQLite local / contract backend
PostgreSQL reference backend
Repository Contract reuse
transaction-boundary reassessment
persistent end-to-end qualification
```

## Decision D - Next targeted document

If the persistence direction is accepted, the next document should be:

```text
16_PYSRMKIT_PERSISTENCE_ARCHITECTURE.md
```

It should answer only the questions required to begin the persistence cycle.

---

# 41. Open questions for the Persistence Architecture document

The next targeted spec should resolve:

```text
1. SQLAlchemy 2.x mapping style?
2. Separate persistence models or classical mappings?
3. SQLite support level?
4. PostgreSQL support level?
5. Engine / Session ownership?
6. Repository construction?
7. Transaction boundary?
8. Exact UnitOfWork trigger?
9. Migration strategy?
10. Integration-test lifecycle?
11. Testcontainers or another PostgreSQL test mechanism?
12. SQLite / PostgreSQL behavioral compatibility policy?
13. Date/time and UUID storage policy?
14. Constraint ownership: Domain vs database?
15. Persistent Domain Event handling / dispatch timing?
```

These questions are now timely because the first Core has created enough evidence to answer them productively.

---

# 42. Final review verdict

The first PySRMKit implementation cycle achieved its intended purpose.

It did not prove that the architecture is final.

It proved something more useful:

```text
the domain can be modeled cleanly,
executed locally,
tested deterministically,
and extended without framework coupling.
```

The next architecture decision should therefore not maximize feature count.

It should test the most important claim that has not yet been validated:

> **Can the same Domain and Application model survive real relational persistence without leaking infrastructure concerns inward?**

That is the strongest next pressure currently visible.

---

# 43. Final rule

> **The first Core proved the architecture locally.**

> **The next cycle should prove the architecture against real persistence.**

> **SQLite should accelerate that learning locally; PostgreSQL should validate the production-oriented relational boundary.**

> **Patterns such as UnitOfWork must still emerge from real transaction pressure, not from a checklist.**
