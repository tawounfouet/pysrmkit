# PySRMKit — Implementation Roadmap

**Document :** `13_PYSRMKIT_IMPLEMENTATION_ROADMAP.md`  
**Projet :** PySRMKit  
**Domaine :** Supplier Relationship Management  
**Type :** Implementation Roadmap / Milestones / Qualification Gates  
**Statut :** Baseline pré-implémentation  
**Version du document :** 0.1.0  

**Documents de référence :**
- `00_PYSRMKIT_EXPRESSION_DU_BESOIN.md`
- `01_PYSRMKIT_REQUIREMENTS_ANALYSIS.md`
- `02_PYSRMKIT_PRODUCT_VISION_AND_ARCHITECTURE_PRINCIPLES.md`
- `03_PYSRMKIT_SYSTEM_ARCHITECTURE.md`
- `04_PYSRMKIT_DOMAIN_OBJECTS.md`
- `05_PYSRMKIT_ENTITIES_AND_VALUE_OBJECTS.md`
- `06_PYSRMKIT_DOMAIN_RELATIONSHIPS_AND_ERD.md`
- `07_PYSRMKIT_DOMAIN_INVARIANTS_AND_BUSINESS_RULES.md`
- `08_PYSRMKIT_COMMANDS_QUERIES_AND_USE_CASES.md`
- `09_PYSRMKIT_DOMAIN_EVENTS_AND_EVENT_MODEL.md`
- `10_PYSRMKIT_PORTS_AND_REPOSITORY_CONTRACTS.md`
- `11_PYSRMKIT_REPOSITORY_AND_PACKAGE_ARCHITECTURE.md`
- `12_PYSRMKIT_TESTING_STRATEGY.md`
- `PYSRMKIT_SOFTWARE_DESIGN_LEARNING_CONVENTION.md`
- `PYSRMKIT_PRE_IMPLEMENTATION_SPECIFICATION_CUTOFF_AND_ITERATIVE_DOCUMENTATION_STRATEGY.md`

---

# 1. Objet du document

Ce document transforme le baseline de conception PySRMKit en une séquence d’implémentation concrète, versionnée et qualifiable.

Il définit :

- les milestones du premier cycle de développement ;
- le périmètre fonctionnel de chaque version ;
- les dépendances entre milestones ;
- les objets métier à implémenter ;
- les Commands, Handlers, Ports et Adapters à introduire ;
- les tests obligatoires ;
- les quality gates ;
- les critères de sortie ;
- les non-objectifs de chaque étape ;
- le scénario final de qualification locale.

La roadmap s’arrête volontairement à :

> **un Core Python local capable d’aller jusqu’à une décision de qualification fournisseur.**

Elle n’inclut pas encore :

```text
PostgreSQL
SQLAlchemy
FastAPI
Kafka
RabbitMQ
Transactional Outbox
Ivalua
SAP
Coupa
S3
Azure Blob
OpenTelemetry
Production deployment
```

Ces sujets seront traités dans des itérations ultérieures uniquement lorsqu’un besoin réel apparaîtra.

---

# 2. Principe de roadmap

La roadmap suit la règle :

> **Each milestone must deliver a coherent capability, not just more files.**

Chaque milestone doit produire :

```text
Business capability
+
Domain model
+
Application flow
+
Port/Adapter support where needed
+
Tests
+
Architecture compliance
+
Green qualification gate
```

---

# 3. Versioning strategy for the first cycle

Le premier cycle utilise des versions alpha :

```text
0.1.0a1
0.1.0a2
0.1.0a3
0.1.0a4
0.1.0a5
0.1.0a6
0.1.0a7
0.1.0a8
```

Ces versions représentent des étapes internes qualifiées.

Elles ne signifient pas nécessairement qu’elles doivent être publiées sur PyPI.

---

# 4. Roadmap overview

```text
0.1.0a1 — Repository Bootstrap
        │
        ▼
0.1.0a2 — Supplier Core
        │
        ▼
0.1.0a3 — Supplier Relationships
        │
        ▼
0.1.0a4 — Relationship Lifecycle
        │
        ▼
0.1.0a5 — Onboarding Core
        │
        ▼
0.1.0a6 — Qualification Domain
        │
        ▼
0.1.0a7 — Qualification Application Flow
        │
        ▼
0.1.0a8 — Local Core Qualification
```

---

# 5. Final target of the cycle

À la fin de `0.1.0a8`, PySRMKit doit pouvoir exécuter localement :

```text
RegisterSupplier
        │
        ▼
SupplierCreated
        │
        ▼
CreateSupplierRelationship
        │
        ▼
SupplierRelationshipCreated
        │
        ▼
InviteSupplierRelationship
        │
        ▼
SupplierInvited
        │
        ▼
StartSupplierOnboarding
        │
        ▼
SupplierOnboardingStarted
        │
        ▼
CreateSupplierAssessment
        │
        ▼
CompleteSupplierAssessment
        │
        ▼
SupplierAssessmentCompleted
        │
        ▼
RequestSupplierQualification
        │
        ▼
SupplierQualificationRequested
        │
        ▼
QualificationPolicy.evaluate()
        │
        ▼
QualificationDecision
        │
        ├── QUALIFIED
        │       └── SupplierQualified
        │
        └── NOT_QUALIFIED
                └── SupplierQualificationRejected
```

---

# 6. Global constraints

Throughout the first cycle:

```text
Pure Python Core
No database
No network
No external service
No framework runtime
No message broker
No cloud dependency
```

The allowed execution model is:

```text
Domain
+
Application
+
Ports
+
InMemory Adapters
+
Tests
```

---

# 7. Global quality gates

Every milestone must keep the following green:

```text
ruff
type checker
pytest
architecture tests
coverage threshold
```

Candidate command set:

```bash
ruff check .
pyright
pytest
```

Exact commands will be finalized in the Bootstrap Plan.

---

# 8. Global architecture gates

The following rules must remain true during all milestones:

```text
domain ↛ application
domain ↛ ports
domain ↛ adapters
application ↛ concrete adapters
ports ↛ adapters
domain ↛ infrastructure frameworks
```

---

# 9. Milestone definition template

Each milestone is defined by:

```text
Goal
Business capability
Domain scope
Application scope
Ports/Adapters
Events
Tests
Acceptance criteria
Non-goals
Learning focus
Exit gate
```

---

# 10. `0.1.0a1 — Repository Bootstrap`

## Goal

Créer un repository Python minimal, installable, testable et architecturalement prêt à accueillir le Domain Core.

---

# 11. Scope — `0.1.0a1`

Create:

```text
pyproject.toml
src/pysrmkit/
tests/
docs/specifications/
examples/
.github/workflows/ci.yml
README.md
LICENSE
CHANGELOG.md
```

---

# 12. Source skeleton

Minimum:

```text
src/pysrmkit/
├── __init__.py
├── domain/
├── application/
├── ports/
└── adapters/
```

Sans créer toutes les capabilities futures.

---

# 13. Test skeleton

```text
tests/
├── unit/
├── application/
├── contracts/
├── architecture/
└── scenarios/
```

---

# 14. Tooling

Configure:

```text
pytest
pytest-cov
ruff
pyright or mypy
```

Optional architecture tool if justified:

```text
import-linter
```

Otherwise use custom import tests.

---

# 15. Packaging

Requirements:

```text
src layout
package import works
version available
editable installation works
```

Smoke test:

```python
import pysrmkit
```

---

# 16. Architecture tests

First executable rules:

```text
domain must not import adapters
application must not import adapters
ports must not import adapters
```

Even if packages are nearly empty.

---

# 17. `0.1.0a1` tests

Minimum:

```text
package import smoke test
architecture rule tests
tooling smoke test
```

---

# 18. `0.1.0a1` acceptance criteria

```text
[ ] package installs locally
[ ] import pysrmkit succeeds
[ ] pytest executes
[ ] ruff executes
[ ] type checker executes
[ ] architecture tests execute
[ ] CI executes same baseline
[ ] no runtime dependency required for Core
```

---

# 19. `0.1.0a1` non-goals

Do not implement yet:

```text
Supplier
Repositories
Handlers
Qualification
Domain Events
```

except minimal common primitives needed by bootstrap.

---

# 20. Learning focus — `0.1.0a1`

```text
src layout
Python packaging
architecture fitness functions
dependency direction
CI basics
```

---

# 21. Exit gate — `0.1.0a1`

```text
Repository is structurally ready
+
all baseline quality gates green
```

---

# 22. `0.1.0a2 — Supplier Core`

## Goal

Implémenter la première véritable Aggregate Root :

```text
Supplier
```

et son identité canonique.

---

# 23. Domain scope — `0.1.0a2`

Implement core Value Objects:

```text
SupplierId
SupplierIdentity
ExternalIdentifier
CountryCode
Address
CategoryCode
CapabilityCode
```

Implement Entity/Aggregate:

```text
Supplier
```

Possibly:

```text
SupplierContact
SupplierLocation
```

only if needed for this milestone.

---

# 24. Supplier behaviors

Minimum:

```text
create/register supplier
add external identifier
prevent duplicate identifier within Aggregate
update allowed identity information
```

---

# 25. Domain Errors

Candidates:

```text
InvalidSupplierIdentity
DuplicateExternalIdentifier
InvalidExternalIdentifier
```

Exact naming follows `07`.

---

# 26. Domain Event

Implement:

```text
SupplierCreated
```

Optionally:

```text
SupplierExternalIdentifierAdded
SupplierInformationUpdated
```

only if used by a real use case.

---

# 27. Repository Port

Implement:

```text
SupplierRepository
```

Contract:

```text
get
save
find_by_external_identifier
```

---

# 28. Adapter

Implement:

```text
InMemorySupplierRepository
```

with semantics close enough to persistence not to hide missing `save()`.

---

# 29. Clock

Implement:

```text
Clock
SystemClock
FixedClock
```

if not already done in bootstrap.

---

# 30. Event model primitive

Implement minimal:

```text
DomainEvent
event recording
pull_events()
```

No external dispatcher required yet if not needed until Application flow.

---

# 31. Application scope — `0.1.0a2`

Implement:

```text
RegisterSupplier
RegisterSupplierHandler
RegisterSupplierResult
```

Potential:

```text
AddSupplierExternalIdentifier
```

if kept in same milestone.

---

# 32. Tests — `0.1.0a2`

Required:

```text
SupplierId Value Object tests
ExternalIdentifier tests
Supplier Aggregate tests
SupplierCreated event tests
SupplierRepository contract tests
InMemorySupplierRepository contract execution
RegisterSupplier Handler tests
architecture tests
```

---

# 33. Supplier Repository contract tests

Must include:

```text
save/get
unknown id
update/save/reload
find_by_external_identifier
isolation
```

---

# 34. `0.1.0a2` acceptance criteria

```text
[ ] Supplier can be created
[ ] Supplier has stable SupplierId
[ ] Supplier can hold external identifier
[ ] duplicate internal identifier is rejected
[ ] SupplierCreated is recorded
[ ] SupplierRepository contract exists
[ ] InMemorySupplierRepository passes contract
[ ] RegisterSupplier works through Handler
[ ] architecture remains green
```

---

# 35. `0.1.0a2` non-goals

No:

```text
relationship
onboarding
qualification
database
query projections
```

---

# 36. Learning focus — `0.1.0a2`

```text
Entity
Aggregate Root
Value Object
Domain Event
Repository Pattern
Protocol
DIP
Contract Testing
```

---

# 37. Exit gate — `0.1.0a2`

A Supplier can be registered via Application Handler and reloaded via InMemory Repository with all tests green.

---

# 38. `0.1.0a3 — Supplier Relationships`

## Goal

Introduire la relation entre un Supplier canonique et une organisation interne.

---

# 39. Domain scope — `0.1.0a3`

Implement:

```text
SupplierRelationshipId
InternalOrganizationId
SupplierRelationship
```

Initial state according to invariant baseline:

```text
DISCOVERED
```

or whichever `07` defines.

---

# 40. Repository Port

Implement:

```text
SupplierRelationshipRepository
```

Methods:

```text
get
save
find_for_supplier_and_organization
```

---

# 41. Adapter

Implement:

```text
InMemorySupplierRelationshipRepository
```

---

# 42. Application scope

Implement:

```text
CreateSupplierRelationship
CreateSupplierRelationshipHandler
```

---

# 43. Relationship creation rules

At minimum:

```text
Supplier must exist
organization id required
duplicate relationship rule enforced
```

---

# 44. Domain Event

Implement:

```text
SupplierRelationshipCreated
```

---

# 45. Tests — `0.1.0a3`

Required:

```text
Relationship ID tests
Relationship creation tests
Supplier/Organization uniqueness tests
Relationship event tests
Repository contract tests
Handler tests
Multi-organization isolation test
Architecture tests
```

---

# 46. Multi-organization invariant test

Must prove:

```text
same Supplier
+
Org A
+
Org B
```

can produce independent relationships.

---

# 47. `0.1.0a3` acceptance criteria

```text
[ ] relationship can be created for existing Supplier
[ ] relationship references SupplierId
[ ] relationship references InternalOrganizationId
[ ] duplicate relationship is handled according to rules
[ ] relationship is persisted independently
[ ] SupplierRelationshipCreated is recorded
[ ] InMemory repository passes shared contract
```

---

# 48. `0.1.0a3` learning focus

```text
Association Entity
Aggregate boundary
Cross-Aggregate reference by ID
Application orchestration
Repository cross-instance lookup
```

---

# 49. Exit gate — `0.1.0a3`

A Supplier can have independently persisted Relationships across multiple internal organizations.

---

# 50. `0.1.0a4 — Relationship Lifecycle`

## Goal

Implémenter le lifecycle fournisseur au niveau `SupplierRelationship`.

---

# 51. Domain scope — `0.1.0a4`

Implement:

```text
SupplierLifecycleStage
LifecycleTransitionReason
lifecycle transition rules
```

Core stages needed for qualification path:

```text
DISCOVERED
INVITED
ONBOARDING
UNDER_REVIEW
QUALIFIED?
ACTIVE?  [depending on model]
```

The exact lifecycle remains aligned with `07`.

---

# 52. Minimum behaviors

Implement:

```text
invite
start_onboarding
move_to_review if needed
```

Do not implement every future transition unless required.

---

# 53. Commands

Implement:

```text
InviteSupplierRelationship
StartSupplierOnboarding
```

Possibly:

```text
MoveSupplierRelationshipToReview
```

only if the invariant model requires it.

---

# 54. Handlers

Implement matching handlers.

---

# 55. Domain Events

Implement:

```text
SupplierInvited
SupplierOnboardingStarted
```

Potential:

```text
SupplierRelationshipMovedToReview
```

only if useful.

---

# 56. State machine tests

Required:

```text
allowed transitions
forbidden transitions
no event on forbidden transition
event on successful transition
```

---

# 57. Transition matrix gate

All transitions needed by the local qualification flow must be executable and tested.

---

# 58. Tests — `0.1.0a4`

```text
LifecycleStage tests
valid transition matrix
invalid transition matrix
event emission
Handler persistence
Handler not-found errors
architecture tests
```

---

# 59. `0.1.0a4` acceptance criteria
```text
[ ] relationship starts in valid initial stage
[ ] invite transition works
[ ] onboarding transition works
[ ] forbidden transitions fail
[ ] successful transitions emit events
[ ] failed transitions emit no success event
[ ] state survives repository round-trip
```

---

# 60. Learning focus — `0.1.0a4`

```text
State Machine
Enum vs State Pattern
Guard
Domain Error
Domain Event
Transition testing
```

---

# 61. Exit gate — `0.1.0a4`

A SupplierRelationship can move from creation to onboarding through explicit, tested domain transitions.

---

# 62. `0.1.0a5 — Onboarding Core`

## Goal

Introduire un onboarding minimal permettant de préparer une qualification sans créer un workflow engine.

---

# 63. Domain scope — `0.1.0a5`

Implement only what qualification path requires.

Candidate:

```text
SupplierOnboarding
OnboardingId
OnboardingStage
OnboardingRequirement
OnboardingProgress
```

But keep minimal.

---

# 64. MVP onboarding decision

Preferred implementation:

```text
SupplierOnboarding
```

as Entity or child/aggregate according to `07`.

The roadmap must not force a separate Aggregate if implementation pressure shows it unnecessary.

---

# 65. Minimum onboarding behaviors

Possible:

```text
create/start onboarding
record requirement satisfaction
complete onboarding readiness
```

Only implement requirements used by qualification flow.

---

# 66. Onboarding is not Workflow

Do not implement:

```text
task assignment
reminders
timers
human inbox
escalation
workflow DSL
```

---

# 67. Application scope

Commands may include:

```text
CreateSupplierOnboarding
SatisfyOnboardingRequirement
CompleteSupplierOnboarding
```

If lifecycle command already creates onboarding, avoid duplicate command.

---

# 68. Domain Events

Potential:

```text
SupplierOnboardingStarted
SupplierOnboardingCompleted
```

Avoid duplicate `Started` if already emitted from Relationship milestone unless semantics differ.

---

# 69. Tests — `0.1.0a5`

Required:

```text
onboarding creation
requirement completion
missing requirement behavior
onboarding completion
relationship isolation
events if used
Handler tests
```

---

# 70. `0.1.0a5` acceptance criteria

```text
[ ] onboarding exists in required business scope
[ ] qualification prerequisites can reference onboarding state
[ ] required information can be marked satisfied
[ ] incomplete onboarding cannot be treated as complete
[ ] no workflow infrastructure introduced
```

---

# 71. Learning focus — `0.1.0a5`

```text
Entity lifecycle
Aggregate boundary reassessment
YAGNI
Domain vs Workflow responsibility
```

---

# 72. Exit gate — `0.1.0a5`

A relationship can reach a domain-valid onboarding state usable by later qualification rules.

---

# 73. `0.1.0a6 — Qualification Domain`

## Goal

Implémenter la capability métier centrale de qualification indépendamment des Handlers finaux.

---

# 74. Domain scope — `0.1.0a6`

Implement:

```text
QualificationId
QualificationScope
QualificationStatus
QualificationDecision
SupplierQualification
QualificationPolicy
```

---

# 75. Core statuses

Candidates:

```text
PENDING
QUALIFIED
NOT_QUALIFIED
REVOKED
EXPIRED
```

Only those required for first vertical slice must be fully implemented.

---

# 76. QualificationScope

Must represent the domain perimeter explicitly.

At minimum candidate dimensions:

```text
organization?
category?
country?
```

According to `07`.

---

# 77. QualificationDecision

Must be explicit and explainable.

Candidate fields:

```text
approved
resulting_status
reasons
failed_requirements
```

Avoid:

```text
bool only
```

---

# 78. QualificationPolicy

Implement a first deterministic policy.

Candidate name:

```text
DefaultQualificationPolicy
```

Only if multiple implementations are expected later.

Otherwise:

```text
QualificationPolicy
```

may itself be the concrete policy.

---

# 79. Policy inputs

The policy can consume a dedicated context:

```text
QualificationContext
```

only if this improves clarity.

Avoid generic dictionary inputs.

---

# 80. SupplierQualification Aggregate

Implement behaviors:

```text
request
apply_decision
approve/qualify
reject
```

Exact method names follow domain vocabulary.

---

# 81. Domain Events

Implement:

```text
SupplierQualificationRequested
SupplierQualified
SupplierQualificationRejected
```

---

# 82. Repository Port

Implement:

```text
SupplierQualificationRepository
```

Methods:

```text
get
save
find_current_for_scope
```

---

# 83. Adapter

Implement:

```text
InMemorySupplierQualificationRepository
```

---

# 84. Qualification Domain tests

Required:

```text
QualificationId
QualificationScope equality/validation
QualificationDecision
Policy success
Policy rejection
Policy explainability
Aggregate request
Aggregate approve
Aggregate reject
invalid state transitions
event emission
repository contract
```

---

# 85. Policy branch gate

All decision branches required for:

```text
QUALIFIED
NOT_QUALIFIED
```

must be tested.

---

# 86. `0.1.0a6` acceptance criteria

```text
[ ] valid scope can be created
[ ] invalid/empty scope rejected according to rules
[ ] qualification can be requested
[ ] policy returns explicit decision
[ ] accepted decision produces QUALIFIED
[ ] rejected decision produces NOT_QUALIFIED
[ ] decision reasons are accessible
[ ] correct events emitted
[ ] repository contract passes
```

---

# 87. Learning focus — `0.1.0a6`

```text
Strategy Pattern
Domain Policy
Decision Object
Value Object
Aggregate lifecycle
Explainability
Repository Contract
```

---

# 88. Exit gate — `0.1.0a6`

The Qualification Domain can be fully tested without any Application Handler.

---

# 89. `0.1.0a7 — Qualification Application Flow`

## Goal

Connecter Assessment, Relationship et Qualification via Commands/Handlers sans déplacer la logique métier dans l’Application Layer.

---

# 90. Assessment domain minimum

If not already sufficiently implemented, add:

```text
AssessmentId
AssessmentType
AssessmentQuestion
AssessmentAnswer
AssessmentScore
AssessmentDecision
SupplierAssessment
```

Only minimal functionality required by qualification.

---

# 91. Assessment repository

Implement:

```text
SupplierAssessmentRepository
InMemorySupplierAssessmentRepository
```

---

# 92. Assessment Commands

Minimum:

```text
CreateSupplierAssessment
RecordAssessmentAnswer
CompleteSupplierAssessment
```

Simplify if a smaller API satisfies the first qualification scenario.

---

# 93. Assessment event

Implement:

```text
SupplierAssessmentCompleted
```

---

# 94. Qualification Commands

Implement:

```text
RequestSupplierQualification
EvaluateSupplierQualification
```

---

# 95. Request Handler

Responsibilities:

```text
load Relationship
verify scope/context
check current qualification conflict
create qualification
save
commit if applicable
dispatch events
```

---

# 96. Evaluate Handler

Responsibilities:

```text
load Qualification
load Assessment facts
build qualification input/context
invoke QualificationPolicy
apply decision to Aggregate
save
dispatch events
```

---

# 97. Important boundary

Handler must not contain:

```python
if assessment.score >= 80:
    qualification.status = QUALIFIED
```

The Policy and Aggregate own the business decision.

---

# 98. DomainEventDispatcher

Implement/complete:

```text
DomainEventDispatcher
InProcessDomainEventDispatcher
```

if not already used.

---

# 99. UnitOfWork decision checkpoint

At this milestone, evaluate actual repetition.

If handlers clearly need:

```text
save
commit
dispatch
```

across several repositories, introduce minimal:

```text
UnitOfWork
```

Otherwise defer.

This is a deliberate checkpoint, not an automatic requirement.

---

# 100. Handler tests — `0.1.0a7`

Required:

```text
request qualification success
duplicate current scope rejection
relationship not found
assessment completion
policy used by evaluate handler
qualification persisted
qualified event dispatched
rejected event dispatched
FixedClock used
```

---

# 101. Cross-capability tests

Prove:

```text
Assessment does not directly mutate Qualification
Qualification does not directly mutate Relationship
Application coordinates explicitly
```

---

# 102. `0.1.0a7` acceptance criteria

```text
[ ] Assessment can be created/completed
[ ] Qualification can be requested via Handler
[ ] Qualification can be evaluated via Handler
[ ] Policy is invoked explicitly
[ ] Qualification state is persisted
[ ] Domain Events are dispatched
[ ] no infrastructure dependency introduced
```

---

# 103. Learning focus — `0.1.0a7`

```text
Application Service
Command
Handler
Application orchestration
Domain Policy delegation
Cross-Aggregate coordination
Event dispatch
```

---

# 104. Exit gate — `0.1.0a7`

All individual use cases required by the final local scenario operate correctly through Application Handlers.

---

# 105. `0.1.0a8 — Local Core Qualification`

## Goal

Qualifier l’architecture complète par un scenario end-to-end local.

---

# 106. Deliverable

Create:

```text
examples/local_qualification.py
```

and:

```text
tests/scenarios/test_local_supplier_qualification.py
```

---

# 107. Composition root

The example manually assembles:

```text
InMemorySupplierRepository
InMemorySupplierRelationshipRepository
InMemorySupplierAssessmentRepository
InMemorySupplierQualificationRepository
FixedClock or SystemClock
InProcessDomainEventDispatcher
QualificationPolicy
Application Handlers
```

No DI container.

---

# 108. Success scenario

Must execute:

```text
RegisterSupplier
CreateSupplierRelationship
InviteSupplierRelationship
StartSupplierOnboarding
SatisfyOnboardingRequirement
CompleteSupplierOnboarding
CreateSupplierAssessment
RecordAssessmentAnswer
CompleteSupplierAssessment
RequestSupplierQualification
EvaluateSupplierQualification
```

Final:

```text
QUALIFIED
```

---

# 109. Rejection scenario

A second test must prove:

```text
insufficient business evidence
→ QualificationDecision rejected
→ qualification NOT_QUALIFIED
→ SupplierQualificationRejected event
```

---

# 110. Event trace

The example may print:

```text
[EVENT] SupplierCreated
[EVENT] SupplierRelationshipCreated
[EVENT] SupplierInvited
[EVENT] SupplierOnboardingStarted
[EVENT] SupplierOnboardingCompleted
[EVENT] SupplierAssessmentCompleted
[EVENT] SupplierQualificationRequested
[EVENT] SupplierQualified
```

This is useful pedagogically.

---

# 111. Scenario assertions

At minimum verify:

```text
Supplier exists
Relationship exists
Relationship reached expected stage
Onboarding is completed
Assessment is completed
Qualification exists
Qualification scope correct
Decision correct
Final qualification status correct
Expected events observed
```

---

# 112. Full regression gate

Before declaring `0.1.0a8` complete:

```text
all unit tests
all application tests
all contract tests
all architecture tests
all scenario tests
lint
type check
coverage
```

must be green.

---

# 113. `0.1.0a8` acceptance criteria

```text
[ ] success scenario passes locally
[ ] rejection scenario passes locally
[ ] no network required
[ ] no database required
[ ] no framework runtime required
[ ] all repository contracts green
[ ] all architecture rules green
[ ] all Domain Events correct
[ ] package import remains side-effect free
[ ] example script runs locally
```

---

# 114. Learning focus — `0.1.0a8`

This milestone consolidates:

```text
DDD
SOLID
Strategy
Repository
Ports & Adapters
CQRS-lite
Domain Events
Application Services
Contract Testing
Architecture Fitness Functions
```

---

# 115. Exit gate — `0.1.0a8`

The first implementation cycle is complete when:

> **PySRMKit can qualify or reject a SupplierRelationship locally through its Domain and Application layers using only InMemory adapters.**

---

# 116. Milestone dependency graph

```text
a1 Bootstrap
   │
   ▼
a2 Supplier
   │
   ▼
a3 Relationship
   │
   ▼
a4 Lifecycle
   │
   ▼
a5 Onboarding
   │
   ▼
a6 Qualification Domain
   │
   ▼
a7 Application Flow
   │
   ▼
a8 Local Scenario
```

---

# 117. Why this order

The order follows increasing domain dependency.

```text
Qualification
```

depends conceptually on:

```text
Supplier
Relationship
Lifecycle
Onboarding/Assessment context
```

Therefore Qualification should not be the first Aggregate implemented.

---

# 118. Dependency rule between milestones

A milestone may refine previous objects, but should not require a future milestone to make its own acceptance criteria meaningful.

---

# 119. Vertical slices vs horizontal scaffolding

The roadmap intentionally avoids:

```text
implement all Value Objects first
implement all Repositories second
implement all Handlers third
```

Instead each milestone adds a coherent capability.

---

# 120. Architecture evolution checkpoints

Explicit checkpoints occur after:

```text
a2 Supplier
a4 Lifecycle
a6 Qualification Domain
a8 Local Qualification
```

At each checkpoint ask:

```text
Did any abstraction feel forced?
Did package boundaries hold?
Did repositories remain small?
Did handlers remain thin?
Did tests expose bad assumptions?
```

---

# 121. Spec feedback loop

If implementation contradicts a spec:

```text
code friction
    │
    ▼
re-evaluate design
    │
    ▼
update spec
    │
    ▼
update tests
    │
    ▼
refactor code
```

The roadmap does not freeze incorrect assumptions.

---

# 122. Deferred decisions to observe during cycle

Observe, but do not pre-implement:

```text
Need for base Aggregate class
Need for UnitOfWork
Need for generic event envelope
Need for Command Bus
Need for Query Bus
Need for Specification Pattern
Need for builder test utilities
Need for ApplicationContext
```

---

# 123. Refactoring triggers

Introduce abstraction only after repeated pressure.

Examples:

```text
3+ Aggregates duplicate event handling
    → consider common Aggregate event support

3+ Handlers repeat transaction orchestration
    → consider UnitOfWork/application helper

multiple Qualification algorithms
    → stronger Strategy abstraction

complex qualification rules
    → consider Specification/Rule objects
```

---

# 124. Non-goals of first cycle

Explicitly excluded:

```text
production database
ORM
REST API
GraphQL
CLI product
message broker
external connector
document storage
security provider
observability stack
distributed processing
async API
plugin system
```

---

# 125. Why exclude them

The first cycle must answer:

> **Is the Core domain architecture correct and executable?**

not:

> **Can we deploy a complete supplier platform?**

---

# 126. Local-only runtime

The only runtime dependencies should be Python itself and minimal package dependencies if absolutely necessary.

---
# 127. Mandatory runtime dependency target

Preferred:

```text
0 mandatory third-party runtime dependencies
```

for Core.

Dev dependencies remain acceptable.

---

# 128. Quality gate matrix

| Milestone | Domain | Application | Contract | Architecture | Scenario |
|---|---:|---:|---:|---:|---:|
| a1 Bootstrap | minimal | — | — | required | — |
| a2 Supplier | required | required | required | required | optional |
| a3 Relationship | required | required | required | required | optional |
| a4 Lifecycle | required | required | repository regression | required | partial |
| a5 Onboarding | required | required | as needed | required | partial |
| a6 Qualification Domain | required | limited | required | required | partial |
| a7 Application Flow | regression | required | regression | required | partial |
| a8 Local Qualification | all | all | all | all | required |

---

# 129. Coverage philosophy

Milestones must not game coverage numbers.

Priority:

```text
critical invariants
all lifecycle branches
all policy branches
all repository contracts
```

Candidate global threshold:

```text
>= 90%
```

to be finalized during bootstrap.

---

# 130. Branch coverage priorities

Particularly important for:

```text
lifecycle transitions
qualification policy
guards
decision branches
```

---

# 131. Commit strategy

Each milestone can be broken into small commits.

Example `a2`:

```text
feat(domain): add SupplierId and ExternalIdentifier
feat(domain): add Supplier aggregate
feat(events): add SupplierCreated
feat(ports): add SupplierRepository
feat(adapter): add in-memory supplier repository
feat(application): add RegisterSupplier
test: qualify Supplier Core
```

Exact conventions may be refined later.

---

# 132. Branching strategy

Not mandated by this document.

Simple GitHub flow is sufficient for initial local development:

```text
main
feature branches
pull request
CI
merge
```

No complex GitFlow required for Core bootstrap.

---

# 133. Definition of Done — code item

A code item is done when:

```text
[ ] behavior implemented
[ ] tests added
[ ] types pass
[ ] lint passes
[ ] architecture rules pass
[ ] docs/docstrings updated when behavior is architectural
```

---

# 134. Definition of Done — milestone

A milestone is done when:

```text
[ ] all scoped capabilities work
[ ] milestone tests pass
[ ] full regression suite passes
[ ] no known architecture violation
[ ] no deferred TODO required for milestone correctness
[ ] spec updated if design changed
```

---

# 135. Documentation rule during implementation

Do not stop coding to produce a major new spec unless:

```text
a concrete design problem
```

is encountered.

Small clarifications can be added directly to existing docs.

---

# 136. Learning log — optional

A lightweight document could later record:

```text
design friction
pattern recognized
decision changed
lesson learned
```

but it is not required for the bootstrap cycle.

---

# 137. Pattern discipline

Patterns intentionally practiced in first cycle:

```text
Repository
Strategy
Adapter
```

Patterns explicitly not forced:

```text
Factory
Builder
Observer
Mediator
Command GoF
State GoF
Specification
Saga
Singleton
```

unless implementation pressure justifies them.

---

# 138. DDD concepts practiced

```text
Entity
Value Object
Aggregate Root
Domain Event
Repository
Domain Policy
Domain Error
Association Entity
```

---

# 139. SOLID concepts practiced

```text
SRP
OCP
LSP
ISP
DIP
```

---

# 140. Architecture concepts practiced

```text
Hexagonal Architecture
Ports & Adapters
Application Layer
CQRS-lite
Architecture Fitness Functions
```

---

# 141. Python concepts practiced

```text
dataclass
Enum
Protocol
typing
composition
immutable objects
typed exceptions
```

---

# 142. Testing concepts practiced

```text
unit tests
parametrized tests
contract tests
fakes
architecture tests
scenario tests
branch coverage
```

---

# 143. Milestone summary table

| Version | Milestone | Main outcome |
|---|---|---|
| `0.1.0a1` | Repository Bootstrap | installable/testable skeleton |
| `0.1.0a2` | Supplier Core | canonical Supplier Aggregate |
| `0.1.0a3` | Supplier Relationships | Supplier ↔ Organization relation |
| `0.1.0a4` | Relationship Lifecycle | controlled state transitions |
| `0.1.0a5` | Onboarding Core | qualification-ready onboarding context |
| `0.1.0a6` | Qualification Domain | policy + decision + aggregate |
| `0.1.0a7` | Qualification Application Flow | handlers orchestrate qualification |
| `0.1.0a8` | Local Core Qualification | full local success/rejection scenarios |

---

# 144. Milestone risk table

| Risk | Mitigation |
|---|---|
| Over-modeling | YAGNI checkpoints |
| God Aggregate | Aggregate isolation tests |
| Thin/anemic domain | behavior-focused Aggregates |
| Business logic in Handler | Policy/Aggregate tests |
| Repository inflation | minimal Port contracts |
| InMemory hides persistence mistakes | contract + copy semantics |
| Event over-engineering | synchronous in-process only |
| Architecture drift | fitness tests from a1 |
| Too much documentation | stop-spec rule after 14 |
| Premature infra | explicit non-goals |

---

# 145. Architecture decision checkpoints

## After `a2`

Question:

```text
Is Supplier aggregate cohesive?
```

## After `a3`

Question:

```text
Is SupplierRelationship truly independent?
```

## After `a4`

Question:

```text
Is lifecycle correctly relationship-scoped?
```

## After `a5`

Question:

```text
Is Onboarding an Entity/Aggregate or simpler concept?
```

## After `a6`

Question:

```text
Is QualificationPolicy sufficient or are rule objects emerging?
```

## After `a7`

Question:

```text
Is UnitOfWork justified by repetition?
```

## After `a8`

Question:

```text
What is the next real infrastructure pressure?
```

---

# 146. Post-`0.1.0a8` decision point

After local qualification, stop and review.

Possible next directions:

```text
A. Activation
B. Documents & Evidence
C. Compliance
D. Risk
E. PostgreSQL persistence
F. Public API
G. Ivalua integration
```

No next direction is preselected by this roadmap.

---

# 147. Possible Iteration A — Activation

If business priority:

```text
ActivationContext
ActivationPolicy
ActivateSupplierRelationship
SupplierActivated
```

This may become:

```text
0.1.0a9 / 0.1.0b1
```

depending on versioning strategy.

---

# 148. Possible Iteration B — Persistence

If persistence is next pressure:

```text
Persistence Architecture spec
PostgreSQL adapter
SQLAlchemy mapping
UnitOfWork
migrations
integration tests
```

Repository contracts remain unchanged where possible.

---

# 149. Possible Iteration C — Trust & Control

Could add:

```text
Documents
Certifications
Compliance
Risk
```

in vertical slices.

---

# 150. Possible Iteration D — External integration

Could add:

```text
Ivalua
SAP
Coupa
```

via Anti-Corruption Layers.

---

# 151. No guaranteed future sequence

The post-Core roadmap must be driven by:

```text
real product need
+
implementation pressure
+
learning priority
```

not by the desire to complete every possible architecture document.

---

# 152. Roadmap visual

```text
FOUNDATION
┌────────────────────────────────────────┐
│ 0.1.0a1 Repository Bootstrap          │
└───────────────────┬────────────────────┘
                    ▼
MASTER DATA
┌────────────────────────────────────────┐
│ 0.1.0a2 Supplier Core                 │
└───────────────────┬────────────────────┘
                    ▼
RELATIONSHIP
┌────────────────────────────────────────┐
│ 0.1.0a3 Supplier Relationships        │
│ 0.1.0a4 Relationship Lifecycle        │
└───────────────────┬────────────────────┘
                    ▼
READINESS
┌────────────────────────────────────────┐
│ 0.1.0a5 Onboarding Core               │
└───────────────────┬────────────────────┘
                    ▼
QUALIFICATION
┌────────────────────────────────────────┐
│ 0.1.0a6 Qualification Domain          │
│ 0.1.0a7 Qualification App Flow        │
└───────────────────┬────────────────────┘
                    ▼
QUALIFICATION GATE
┌────────────────────────────────────────┐
│ 0.1.0a8 Local Core Qualification      │
└────────────────────────────────────────┘
```

---

# 153. Roadmap philosophy

This roadmap deliberately optimizes for:

```text
clarity
feedback
testability
learning
reversibility
```

rather than:

```text
maximum feature count
production infrastructure
premature scale
```

---

# 154. Milestone learning rhythm

For each milestone:

```text
Read spec
    │
    ▼
Write/adjust tests
    │
    ▼
Implement simplest valid design
    │
    ▼
Run quality gates
    │
    ▼
Refactor
    │
    ▼
Review pattern/principle usage
    │
    ▼
Update spec only if reality changed
```

---

# 155. No milestone without a business sentence

Every milestone must be explainable without technical jargon.

Examples:

```text
a2:
"We can register a supplier."

a3:
"We can create our relationship with that supplier."

a4:
"We can progress that relationship through its lifecycle."

a6:
"We can decide whether the supplier is qualified for a scope."

a8:
"We can run the whole qualification journey locally."
```

---

# 156. No milestone defined only by architecture

Avoid milestones such as:

```text
"Add abstractions"
"Create base classes"
"Introduce patterns"
```

unless they unlock a real capability.

---

# 157. First-cycle product narrative

```text
We know who the supplier is.
        ↓
We know our relationship with the supplier.
        ↓
We control the relationship lifecycle.
        ↓
We collect enough onboarding/assessment context.
        ↓
We evaluate qualification.
        ↓
We produce an explainable qualification decision.
```

---

# 158. Final qualification checklist

At the end of the cycle:

```text
[ ] Supplier identity works
[ ] Relationship context works
[ ] Lifecycle works
[ ] Onboarding context works
[ ] Assessment works
[ ] Qualification scope works
[ ] Qualification policy works
[ ] Decision explainability works
[ ] Domain Events work
[ ] Repository Ports work
[ ] InMemory Adapters work
[ ] Handler orchestration works
[ ] Architecture tests work
[ ] Success scenario works
[ ] Rejection scenario works
```

---

# 159. Final technical checklist

```text
[ ] package installs
[ ] import is side-effect free
[ ] no runtime infrastructure dependency
[ ] ruff green
[ ] type checker green
[ ] pytest green
[ ] architecture tests green
[ ] repository contracts green
[ ] coverage acceptable
```

---

# 160. Final non-goal checklist

The first cycle is successful even if none of these exist:

```text
[ ] PostgreSQL
[ ] SQLAlchemy
[ ] FastAPI
[ ] Docker
[ ] Kafka
[ ] Redis
[ ] Ivalua
[ ] SAP
[ ] cloud deployment
[ ] PyPI release
```

Their absence is intentional.

---

# 161. Roadmap completion criterion

The roadmap is complete when:

> **The first real vertical slice proves that PySRMKit’s Domain, Application, Ports, Adapters and Testing Architecture work together coherently.**

---

# 162. Next mandatory document

The final mandatory document before bootstrap is:

> **`14_PYSRMKIT_IMPLEMENTATION_BOOTSTRAP_PLAN.md`**

It must translate `0.1.0a1` into an exact execution plan:

```text
repository creation
files to create
pyproject configuration
tooling
CI
initial architecture tests
initial commit sequence
first local commands
```

After `14`:

```text
STOP GENERAL SPECS
START IMPLEMENTATION
```

---

# 163. Final principles

> **Milestones deliver capabilities, not architecture theater.**

> **Each milestone has an executable qualification gate.**

> **The first cycle stays local and infrastructure-free.**

> **The architecture is validated through code and tests, not only documents.**

> **Abstractions are introduced only when real repetition justifies them.**

> **The roadmap ends where real implementation pressure begins.**

---

# 164. Conclusion

The first PySRMKit implementation cycle is intentionally narrow.

It starts from an empty but disciplined Python repository and ends with a meaningful supplier-domain capability:

```text
Supplier
→ Relationship
→ Lifecycle
→ Onboarding
→ Assessment
→ Qualification
```

The final proof is not a diagram, a database schema or an API.

It is a local, executable and fully tested business scenario capable of producing either:

```text
QUALIFIED
```

or:

```text
NOT_QUALIFIED
```

with explicit Domain Events and an explainable `QualificationDecision`.

This roadmap therefore converts the project’s architectural doctrine into an implementation sequence that is:

```text
incremental
testable
reversible
pedagogical
domain-driven
```

The final rule is:

> **Build the smallest coherent Core that can prove the architecture through a real business journey.**