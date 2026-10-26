# PySRMKit — Domain Events and Event Model

**Document :** `09_PYSRMKIT_DOMAIN_EVENTS_AND_EVENT_MODEL.md`  
**Projet :** PySRMKit  
**Domaine :** Supplier Relationship Management  
**Type :** Domain Modeling / Event Model  
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
- `PYSRMKIT_SOFTWARE_DESIGN_LEARNING_CONVENTION.md`
- `PYSRMKIT_PRE_IMPLEMENTATION_SPECIFICATION_CUTOFF_AND_ITERATIVE_DOCUMENTATION_STRATEGY.md`

---

# 1. Objet du document

Ce document définit le **modèle événementiel du Core PySRMKit**.

Il précise :

- ce qu’est un Domain Event dans PySRMKit ;
- quand un Domain Event doit être créé ;
- comment il est nommé ;
- quelles informations il transporte ;
- quel Aggregate en est propriétaire ;
- comment il est enregistré ;
- comment il est collecté ;
- comment il est dispatché localement ;
- comment il participe à l’audit et à la coordination cross-aggregate ;
- ce qui relève du Domain Event et ce qui relève plus tard des Integration Events.

Le document fixe uniquement ce qui est nécessaire au **Core local**.

Il ne spécifie pas encore :

```text
Kafka
RabbitMQ
Transactional Outbox
Schema Registry
Event Streaming Platform
Distributed Event Bus
Exactly-once delivery
Event Store
Event Sourcing
```

Ces sujets sont volontairement différés.

---

# 2. Position dans la chaîne de conception

```text
Business Need
    │
    ▼
Domain Model
    │
    ▼
Aggregates
    │
    ▼
Invariants
    │
    ▼
Commands / Use Cases
    │
    ▼
DOMAIN EVENTS   ← ce document
    │
    ▼
Ports / Repositories
    │
    ▼
Implementation
```

Le Event Model relie :

```text
business state change
```

à :

```text
observable business fact
```

---

# 3. Définition retenue

Un **Domain Event** représente :

> **un fait métier significatif qui vient de se produire dans le domaine.**

Il est formulé au passé.

Exemples :

```text
SupplierCreated
SupplierRelationshipCreated
SupplierInvited
SupplierOnboardingStarted
SupplierQualificationRequested
SupplierQualified
SupplierQualificationRejected
SupplierActivated
SupplierSuspended
SupplierOffboarded
```

Un Domain Event ne demande pas une action.

Il constate un fait.

---

# 4. Command vs Domain Event

```text
Command
    = intention

Domain Event
    = fait accompli
```

Exemple :

```text
ActivateSupplierRelationship
```

demande :

```text
activate this relationship
```

Puis, si le domaine accepte :

```text
SupplierActivated
```

signifie :

```text
the relationship has been activated
```

---

# 5. Query vs Domain Event

Une Query :

```text
GetSupplierRelationship
```

lit le système.

Elle ne produit pas de Domain Event métier sauf si une opération métier réelle a effectivement eu lieu, ce qui serait généralement un mauvais signe pour une Query.

---

# 6. Domain Event vs Integration Event

Important :

```text
Domain Event
≠
Integration Event
```

## Domain Event

Langage interne du domaine.

Exemple :

```text
SupplierQualified
```

## Integration Event

Contrat exposé vers l’extérieur.

Exemple futur :

```text
supplier.qualification.completed.v1
```

ou :

```text
SupplierQualificationCompletedV1
```

Le mapping :

```text
Domain Event
    ↓
Integration Event
```

appartient à la couche application/integration.

---

# 7. Domain Event vs Event Sourcing

Important :

```text
Domain Events
≠
Event Sourcing
```

PySRMKit peut :

- produire des Domain Events ;
- conserver un état courant ;
- persister normalement ses Aggregates ;

sans reconstruire chaque Aggregate depuis un journal complet d’événements.

Le Core local n’est **pas event-sourced**.

---

# 8. Domain Event vs Observer Pattern

Important :

```text
Domain Event
≠
GoF Observer Pattern
```

Un Domain Event exprime une sémantique métier.

Le mécanisme de distribution peut être :

```text
simple dispatcher
event handler registry
message bus
```

et éventuellement utiliser une structure proche d’Observer.

Mais le concept métier reste indépendant du mécanisme.

---

# 9. Domain Event vs Audit Record

Important :

```text
Domain Event
≠
Audit Record
```

Un Domain Event dit :

```text
what happened in the business
```

Un Audit Record peut ajouter :

```text
who
when
source
request
before/after
technical metadata
```

Les deux peuvent être liés.

Ils ne doivent pas être confondus.

---

# 10. Pourquoi PySRMKit a besoin de Domain Events

Les Domain Events permettent notamment de :

- rendre visibles les changements métier ;
- coordonner plusieurs Aggregates sans couplage direct ;
- alimenter l’audit ;
- mettre à jour des projections ;
- déclencher des use cases secondaires ;
- préparer les futures intégrations ;
- exposer clairement le résultat d’un comportement d’Aggregate.

---

# 11. Cas d’usage cross-aggregate

Exemple :

```text
SupplierIncidentReported
        │
        ├──► ReassessSupplierRisk
        ├──► ReviewSupplierQualification
        └──► ConsiderSupplierSuspension
```

L’Incident Aggregate ne modifie pas directement les autres Aggregates.

Il exprime un fait.

L’Application Layer orchestre les réactions.

---

# 12. Event Ownership

Un Domain Event appartient conceptuellement à l’Aggregate qui a produit le changement.

Exemples :

```text
Supplier
    → SupplierCreated
    → SupplierInformationUpdated

SupplierRelationship
    → SupplierRelationshipCreated
    → SupplierInvited
    → SupplierActivated
    → SupplierSuspended
    → SupplierOffboarded

SupplierQualification
    → SupplierQualificationRequested
    → SupplierQualified
    → SupplierQualificationRejected
    → SupplierQualificationRevoked

SupplierIncident
    → SupplierIncidentReported
```

---

# 13. Event naming convention

Les événements doivent être nommés :

```text
Past Tense
```

Bon :

```text
SupplierCreated
SupplierQualified
SupplierActivated
```

Mauvais :

```text
CreateSupplier
QualifySupplier
ActivateSupplier
```

Ces derniers sont des Commands.

---

# 14. Event naming — semantic precision

Préférer un nom métier précis.

Bon :

```text
SupplierQualificationRevoked
```

plutôt que :

```text
SupplierStatusChanged
```

si la sémantique métier réelle est la révocation d’une qualification.

---

# 15. Avoid generic events

Éviter :

```text
EntityUpdated
StatusChanged
ObjectModified
```

sauf si aucune sémantique métier plus riche n’existe.

Un événement générique masque le langage du domaine.

---

# 16. Event payload principle

Un Domain Event doit transporter :

> **suffisamment d’informations pour exprimer le fait métier, mais pas un snapshot complet arbitraire de l’Aggregate.**

---

# 17. Minimal event metadata

Le Core peut standardiser un minimum :

```text
event_id
occurred_at
aggregate_id
```

éventuellement :

```text
correlation_id
causation_id
actor_reference
```

mais ces derniers peuvent rester hors du Domain Event strict ou dans une envelope applicative.

---

# 18. EventId

**Classification :** Value Object candidate

Responsabilités possibles :

- identifier une occurrence d’événement ;
- déduplication future ;
- audit ;
- tracing.

Pour le Core local :

```text
UUID
```

est suffisant.

---

# 19. occurred_at

Chaque event métier doit porter un temps explicite.

Éviter :

```text
event created at dispatch time
```

si le fait métier s’est produit plus tôt.

Le temps de l’événement doit correspondre au moment logique de la transition.

---

# 20. aggregate_id

Un event doit permettre d’identifier l’Aggregate qui l’a émis.

Exemple :

```text
SupplierActivated
    relationship_id
```

plutôt que seulement :

```text
supplier_id
```

si l’activation est relationship-scoped.

---

# 21. Event payload should use domain vocabulary

Exemple :

```text
SupplierQualified
├── qualification_id
├── relationship_id
├── qualification_scope
└── occurred_at
```

plutôt que :

```text
record_id
status_code
payload
```

---

# 22. Event payload should avoid technical objects

Ne pas inclure :

```text
SQLAlchemy Session
ORM model
HTTP Request
Kafka Message
Pydantic transport model
Cloud SDK object
```

---

# 23. Event immutability

Un Domain Event représente le passé.

Il doit donc être immuable.

Candidate Python representation :

```python
@dataclass(frozen=True, slots=True)
class SupplierCreated:
    event_id: EventId
    supplier_id: SupplierId
    occurred_at: datetime
```

Illustratif.

---

# 24. Event base class — optional

Une base commune est possible :

```python
class DomainEvent(Protocol):
    ...
```

ou :

```python
@dataclass(frozen=True)
class DomainEvent:
    ...
```

Mais elle n’est pas obligatoire si elle n’apporte qu’un marquage décoratif.

---

# 25. Marker Protocol candidate

Un `Protocol` ou type commun peut devenir utile pour :

```text
dispatcher typing
event collection
tests
```

Mais la solution la plus simple doit être privilégiée.

---

# 26. Aggregate event recording

Une Aggregate Root peut enregistrer ses événements dans une collection interne.

Conceptuellement :

```text
Aggregate
    ├── state
    └── pending_domain_events
```

---

# 27. Event recording rule

Un event est enregistré :

```text
after
```

que l’invariant métier ait été validé et que la transition ait effectivement été appliquée dans l’Aggregate.

---

# 28. Invalid operation must not emit event

Exemple :

```text
OFFBOARDED
→ ACTIVE
```

si interdit :

```text
raise InvalidLifecycleTransition
```

et :

```text
NO SupplierActivated event
```

---

# 29. Event recording example

Conceptuel :

```python
def activate(self, decision, occurred_at):
    if not decision.allowed:
        raise ActivationRequirementsNotMet(...)

    self._stage = SupplierLifecycleStage.ACTIVE

    self._record_event(
        SupplierActivated(
            ...
        )
    )
```

---

# 30. Event collection access

L’Aggregate peut exposer un mécanisme tel que :

```text
pull_events()
```

ou :

```text
collect_events()
```

qui retourne puis vide la collection interne.

---

# 31. pull_events semantics

Exemple :

```text
events = aggregate.pull_events()
```

doit idéalement :

1. retourner les events pending ;
2. vider la collection ;
3. préserver l’ordre d’enregistrement.

---

# 32. Event ordering

Pour un Aggregate donné, l’ordre local doit être préservé.

Exemple :

```text
SupplierQualificationRequested
SupplierQualified
```

ne doit pas être inversé.

Le Core local ne définit pas d’ordre global distribué entre tous les Aggregates.

---

# 33. Global ordering — deferred

Ne pas introduire :

```text
global sequence number
distributed total ordering
```

avant besoin réel.

---

# 34. Local event sequence — optional

Un Aggregate peut éventuellement avoir :

```text
aggregate_version
event_sequence
```

mais ce mécanisme doit attendre le besoin de concurrency/event transport.

---

# 35. Event dispatch flow

Flux local recommandé :

```text
Command Handler
    │
    ▼
Load Aggregate
    │
    ▼
Domain operation
    │
    ▼
Aggregate records event
    │
    ▼
Repository.save()
    │
    ▼
Commit
    │
    ▼
Collect events
    │
    ▼
In-process dispatcher
```

---

# 36. Commit-before-dispatch principle

Recommandation :

```text
persist / commit
BEFORE
external side-effect dispatch
```

afin d’éviter :

```text
event published
but
business state rollbacked
```

---

# 37. Core local dispatch

Pour le Core local :

```text
InProcessDomainEventDispatcher
```

est suffisant.

Il peut être extrêmement simple.

---

# 38. Event Dispatcher responsibility

Le dispatcher :

- reçoit un event ;
- trouve les handlers enregistrés ;
- appelle les handlers ;
- conserve l’ordre local si nécessaire.

Il ne décide pas la validité métier.

---

# 39. Event Handler

Un Event Handler représente une réaction applicative à un Domain Event.

Exemple :

```text
SupplierQualified
    ↓
EvaluateRelationshipActivationReadiness
```

---

# 40. Event Handler naming

Préférer un nom orienté action.

Exemple :

```text
EvaluateActivationAfterSupplierQualified
```

plutôt que :

```text
SupplierQualifiedHandler
```

si plusieurs réactions différentes existent.

---

# 41. Multiple handlers

Un Domain Event peut avoir plusieurs consumers.

Exemple :

```text
SupplierQualified
    ├── update qualification projection
    ├── evaluate activation readiness
    └── create integration event later
```

---

# 42. Event Handler must not hide domain mutation

Un handler ne doit pas faire :

```text
load unrelated aggregate
mutate fields directly
save
```

sans passer par un use case/behavior explicite.

Préférer :

```text
event handler
    → sends/invokes command
    → command handler
    → domain
```

pour les réactions métier importantes.

---

# 43. Event Handler and recursive flows

Il faut surveiller :

```text
Event A
→ Command B
→ Event B
→ Command A
```

Les cycles doivent être explicites et testés.

---

# 44. Synchronous local dispatch

Le premier dispatcher peut être synchrone.

Avantages :

- simple ;
- déterministe ;
- facile à tester ;
- aucune infrastructure.

---

# 45. Async dispatch — deferred

Le besoin d’async doit être traité plus tard.

Ne pas rendre tout le Domain Event model `async` dès le Core.

---

# 46. Event handling failure

Question importante :

```text
What if an event handler fails after commit?
```

Pour le Core local :

- l’état métier principal reste committed ;
- l’erreur peut remonter/logguer ;
- les mécanismes de retry durable seront différés.

---

# 47. Reliable delivery — deferred

La résolution durable de :

```text
DB commit succeeded
event processing failed
```

pourra mener plus tard à :

```text
Transactional Outbox
durable queue
retry
dead-letter queue
```

Pas avant le besoin réel.

---

# 48. Event idempotency

Un Event Handler devrait être pensé pour supporter potentiellement un retry.

Le Core local n’a pas besoin d’un framework d’idempotence complet.

Mais les handlers ne doivent pas supposer aveuglément :

```text
this event can never be delivered twice
```
---

# 49. Event deduplication — deferred

Un futur système distribué peut utiliser :

```text
event_id
```

pour dédupliquer.

Le Core local peut simplement inclure l’ID sans implémenter de store de déduplication.

---

# 50. CorrelationId

Un `correlation_id` peut relier :

```text
Command
→ Domain Event
→ secondary Command
→ Integration Event
```

Mais il appartient souvent mieux à une Event Envelope applicative qu’au payload métier.

---

# 51. CausationId

Même distinction.

```text
causation_id
```

identifie l’événement ou commande qui a causé un nouvel event.

Utile plus tard pour tracing.

Pas obligatoire pour le premier Domain Event dataclass.

---

# 52. ActorReference

Certaines décisions critiques peuvent nécessiter :

```text
who triggered the change
```

Mais :

```text
actor identity
```

peut rester dans le command/audit context.

Le Domain Event ne doit pas dépendre du système IAM.

---

# 53. Event Envelope — future candidate

Une envelope applicative peut contenir :

```text
event
event_id
occurred_at
correlation_id
causation_id
actor_reference
metadata
```

Mais le Core peut commencer plus simplement.

---

# 54. Core Event Shape

Minimum recommandé :

```text
event_id
occurred_at
aggregate identity
business-specific payload
```

---

# 55. Supplier Aggregate Events

## SupplierCreated

Déclenché lorsque l’identité Supplier est créée avec succès.

Payload candidat :

```text
event_id
supplier_id
occurred_at
```

Optionnel :

```text
primary_external_identifier
```

mais éviter de recopier toute l’identité.

---

# 56. SupplierInformationUpdated

Candidate event.

Utiliser seulement si une mise à jour master est significative pour des consumers.

Éviter un event générique sur chaque petit changement si personne n’en a besoin.

---

# 57. SupplierExternalIdentifierAdded

Candidate event.

Peut être utile si les integrations dépendent de l’ajout d’identifiants.

Pas obligatoire pour le MVP qualification.

---

# 58. SupplierRelationship Events

Core events :

```text
SupplierRelationshipCreated
SupplierInvited
SupplierOnboardingStarted
SupplierActivated
SupplierSuspended
SupplierBlocked
SupplierReactivated
SupplierOffboarded
```

---

# 59. SupplierRelationshipCreated

Payload candidat :

```text
event_id
relationship_id
supplier_id
organization_id
occurred_at
```

---

# 60. SupplierInvited

Payload candidat :

```text
event_id
relationship_id
supplier_id
occurred_at
```

L’email d’invitation ou son contenu n’appartient pas au Domain Event.

---

# 61. SupplierOnboardingStarted

Payload candidat :

```text
event_id
relationship_id
onboarding_id?
occurred_at
```

selon frontière finale de l’Onboarding.

---

# 62. SupplierActivated

Payload candidat :

```text
event_id
relationship_id
supplier_id
occurred_at
```

Peut inclure :

```text
activation_reason?
```

si c’est réellement utile métier.

---

# 63. SupplierSuspended

Payload candidat :

```text
event_id
relationship_id
supplier_id
reason
occurred_at
```

Le `reason` est fortement pertinent pour audit et métier.

---

# 64. SupplierBlocked

Distinct de :

```text
SupplierSuspended
```

si le domaine distingue réellement les deux situations.

---

# 65. SupplierReactivated

Payload candidat :

```text
relationship_id
occurred_at
reason?
```

---

# 66. SupplierOffboarded

Payload candidat :

```text
relationship_id
supplier_id
reason
occurred_at
```

Offboarding :

```text
does not mean
Supplier deleted
```

---

# 67. Qualification Events

Core candidates :

```text
SupplierQualificationRequested
SupplierQualified
SupplierQualificationRejected
SupplierQualificationRevoked
SupplierQualificationExpired
SupplierQualificationRenewed
```

---

# 68. SupplierQualificationRequested

Payload candidat :

```text
event_id
qualification_id
relationship_id
scope
occurred_at
```

---

# 69. SupplierQualified

Payload candidat :

```text
event_id
qualification_id
relationship_id
scope
occurred_at
valid_until?
```

Le payload ne doit pas exposer toute la policy ou tous les documents utilisés.

---

# 70. SupplierQualificationRejected

Payload candidat :

```text
qualification_id
relationship_id
scope
decision_reasons
occurred_at
```

Les reasons peuvent être :

- codes ;
- structured values ;

plutôt qu’un long texte libre.

---

# 71. SupplierQualificationRevoked

Distinct de rejet initial.

Il représente :

```text
a previously valid qualification
is no longer valid because of a business decision.
```

---

# 72. SupplierQualificationExpired

Distinct de révocation.

Expiration :

```text
time-based validity ended
```

Révocation :

```text
explicit business decision
```

---

# 73. Assessment Events

Candidates :

```text
SupplierAssessmentCreated
SupplierAssessmentCompleted
SupplierAssessmentCancelled
```

Pour le Core qualification :

```text
SupplierAssessmentCompleted
```

peut être particulièrement utile.

---

# 74. SupplierAssessmentCompleted

Payload candidat :

```text
assessment_id
supplier_id
relationship_id?
assessment_type
occurred_at
decision?
```

---

# 75. Documents Events

Candidates for later iteration :

```text
SupplierDocumentRegistered
SupplierDocumentVerified
SupplierDocumentRejected
SupplierDocumentSuperseded
SupplierDocumentExpired
```

---

# 76. Certification Events

Candidates :

```text
SupplierCertificationRegistered
SupplierCertificationVerified
SupplierCertificationRevoked
SupplierCertificationExpired
```

---

# 77. Compliance Events

Candidates :

```text
SupplierComplianceCheckRecorded
SupplierComplianceApproved
SupplierComplianceFailed
SupplierComplianceReviewRequired
```

Le modèle exact dépendra du document Compliance détaillé.

---

# 78. Risk Events

Candidates :

```text
SupplierRiskAssessed
SupplierRiskChanged
SupplierHighRiskDetected
```

Éviter de produire deux events redondants pour le même fait sans consumer réel.

---

# 79. Incident Events

Candidates :

```text
SupplierIncidentReported
SupplierIncidentEscalated
SupplierIncidentResolved
SupplierIncidentClosed
```

---

# 80. Performance Events

Candidates :

```text
SupplierPerformanceRecorded
SupplierScorecardPublished
```

si ces faits ont une utilité métier.

---

# 81. Segmentation Events

Candidate :

```text
SupplierSegmentChanged
```

utile si la segmentation influence d’autres processus.

---

# 82. MVP Event Catalog

Pour le premier Core jusqu’à qualification, le minimum peut être :

```text
SupplierCreated
SupplierRelationshipCreated
SupplierInvited
SupplierOnboardingStarted
SupplierAssessmentCompleted
SupplierQualificationRequested
SupplierQualified
SupplierQualificationRejected
```

Optionnel :

```text
SupplierActivated
```

si l’activation est intégrée juste après.

---

# 83. MVP Event Flow

```text
RegisterSupplier
    │
    ▼
SupplierCreated

CreateSupplierRelationship
    │
    ▼
SupplierRelationshipCreated

InviteSupplierRelationship
    │
    ▼
SupplierInvited

StartSupplierOnboarding
    │
    ▼
SupplierOnboardingStarted

CompleteSupplierAssessment
    │
    ▼
SupplierAssessmentCompleted

RequestSupplierQualification
    │
    ▼
SupplierQualificationRequested

EvaluateSupplierQualification
    │
    ├──► SupplierQualified
    └──► SupplierQualificationRejected
```

---

# 84. Event recording location

La préférence est :

```text
Aggregate records event
```

lorsque l’event correspond à un changement d’état de l’Aggregate.

---

# 85. Application-generated events

Un Event purement applicatif peut exister.

Mais il ne doit pas être appelé Domain Event si le fait n’appartient pas au domaine.

Exemple :

```text
SupplierImportBatchCompleted
```

peut être un Application Event.

---

# 86. Integration-generated events

Un Adapter peut recevoir un événement externe.

Il doit être mappé vers :

```text
Command
```

ou :

```text
Application input
```

avant d’entrer dans le domaine.

---

# 87. Event state transition invariant

Si un event affirme :

```text
SupplierQualified
```

alors l’état de l’Aggregate après l’opération doit être cohérent avec ce fait.

---

# 88. Event atomicity concept

Conceptuellement :

```text
state change
+
record Domain Event
```

doivent être une seule décision métier dans l’Aggregate.

---

# 89. Event persistence — Core

Le Core local peut simplement garder les events en mémoire jusqu’au dispatch.

Il n’a pas besoin de table `domain_events`.

---

# 90. Event persistence — future

Une future infrastructure pourra stocker :

```text
event outbox
audit event log
event store
```

mais ce sont des concerns distincts.

---

# 91. Event replay — not required

Le Core n’a pas besoin de :

```text
replay domain events to rebuild state
```

---

# 92. Event versioning — Core

Pour les Domain Events internes au même package :

```text
semantic versioning of Python API
```

est suffisant initialement.

Pas besoin :

```text
SupplierQualifiedV1
```

dans le Core tant qu’il n’existe pas de contrat externe durable.

---

# 93. Integration Event versioning — future

Les Integration Events devront probablement être versionnés explicitement :

```text
SupplierQualifiedV1
```

ou :

```text
supplier.qualified.v1
```

mais dans un document dédié ultérieur.

---

# 94. Domain Event public API

Question :

Les Domain Event classes doivent-elles faire partie de la surface publique stable ?

Recommendation initiale :

```text
selected core domain events
may be public
```

si les consumers Python ont besoin de les observer.

La décision sera liée à la Public API strategy.

---

# 95. Event dispatcher port

Port candidat :

```text
DomainEventDispatcher
```

ou :

```text
EventPublisher
```

Le naming doit refléter le fait qu’il s’agit d’un dispatch interne.

---

# 96. EventPublisher naming caution

`EventPublisher` peut être interprété comme :

```text
external broker publisher
```

Pour le Core local :

```text
DomainEventDispatcher
```

est plus précis.

---

# 97. Minimal dispatcher protocol

Illustration :

```python
class DomainEventDispatcher(Protocol):
    def dispatch(self, event: DomainEvent) -> None:
        ...
```

ou :

```python
def dispatch_all(events: Iterable[DomainEvent]) -> None:
    ...
```

La forme finale sera fixée dans le document Ports.

---

# 98. Event handler protocol

Un handler peut être :

```python
Callable[[DomainEvent], None]
```

sans base class.

KISS.

---

# 99. Event registry

Pour le Core local :

```text
dict[event_type, list[handler]]
```

peut suffire.

Ne pas créer un framework de bus interne complexe.

---

# 100. Event dispatch testing

Tests nécessaires :

```text
event recorded after valid transition
no event on invalid transition
events preserve order
pull_events clears pending queue
dispatcher calls registered handlers
multiple handlers receive event
```

---

# 101. Domain event tests

Exemple :

```python
def test_qualified_event_is_recorded_after_successful_qualification():
    ...
```

---

# 102. Invalid transition event test

```python
def test_invalid_activation_does_not_record_supplier_activated():
    ...
```

---

# 103. Event payload tests

Tester la sémantique :

```text
correct aggregate id
correct scope
correct occurred_at
correct reason
```

Pas l’ordre des attributs de dataclass.

---

# 104. Dispatcher unit tests

Tester :

```text
registered handler called once
unregistered event harmless or explicit error
order preserved
handler failure behavior explicit
```

---

# 105. Event handler application tests

Exemple :

```text
SupplierQualified
    → activation-readiness handler invoked
```

avec fakes/in-memory.

---

# 106. Architecture tests

Exemples :

```text
domain events must not import adapters
domain events must not import Kafka
domain events must not import HTTP models
```

---

# 107. Event naming tests — optional

Pas nécessaire d’automatiser au MVP.

Naming review suffit.

---

# 108. Event payload privacy

Un event ne doit pas embarquer inutilement :

```text
personal contact data
bank details
raw compliance evidence
full documents
```

Les payloads doivent respecter :

```text
minimum necessary data
```

---

# 109. Event payload stability

Plus un event est consommé largement, plus son payload doit être stable.

Le Core local peut évoluer rapidement.

Une Integration Event publique devra être plus contrôlée.

---

# 110. Event size

Domain Events doivent rester petits.

Éviter :

```text
full Supplier snapshot
full Assessment questionnaire
full Document bytes
```

---

# 111. Event evidence references

Si un event doit référencer une preuve :

```text
EvidenceReference
```

est préférable à une copie complète.

---

# 112. Event causality

Une chaîne :

```text
SupplierAssessmentCompleted
    → EvaluateSupplierQualification
    → SupplierQualified
```

doit rester conceptuellement traçable.

Même si `causation_id` n’est pas encore obligatoire.

---

# 113. Event chains

Exemple Core :

```text
SupplierOnboardingStarted
        │        ▼
Assessment completed
        │
        ▼
SupplierAssessmentCompleted
        │
        ▼
Qualification requested
        │
        ▼
SupplierQualificationRequested
        │
        ▼
Qualification evaluated
        │
        ▼
SupplierQualified
```

---

# 114. Avoid implicit cascades

Ne pas faire :

```text
SupplierAssessment.complete()
```

qui qualifierait directement le Supplier dans la même méthode.

Cela créerait un couplage d’Aggregates.

---

# 115. Use case reaction

Préférer :

```text
Assessment Aggregate
    records SupplierAssessmentCompleted
        │
        ▼
Application reacts
        │
        ▼
Qualification use case
```

---

# 116. Event-driven does not mean asynchronous

Important :

```text
Event-Driven
≠
Async
```

Le Core peut être :

```text
event-driven
+
fully synchronous
```

---

# 117. Event-driven does not mean distributed

Important :

```text
Event-Driven
≠
Microservices
```

Un monolithe Python peut utiliser Domain Events proprement.

---

# 118. Event-driven does not mean Kafka

Important :

```text
Domain Event
≠
Kafka topic
```

---

# 119. Event-driven does not mean Event Sourcing

Rappel volontaire car la confusion est fréquente.

---

# 120. Domain Event pattern vs Observer

La ressemblance structurelle ne suffit pas à dire :

```text
we use Observer Pattern
```

Pour appliquer la convention pédagogique, on n’étiquettera Observer que si :

- subjects maintain observers ;
- observers subscribe directly ;
- notification relationship corresponds réellement au pattern.

Un dispatcher de Domain Events peut exister sans revendiquer Observer.

---

# 121. Event handler coupling

Les handlers doivent dépendre :

```text
on event contract
```

et éventuellement :

```text
on command/application port
```

Pas sur l’Aggregate émetteur lui-même si ce n’est pas nécessaire.

---

# 122. Event loops

Les chaînes event → command → event doivent être surveillées.

Le Core doit éviter les loops infinies.

Un test de scenario doit détecter les cycles accidentels.

---

# 123. Event fan-out

Un event peut provoquer plusieurs réactions.

Mais chaque handler doit rester cohésif.

Exemple :

```text
SupplierQualified
```

handlers :

```text
UpdateQualificationProjection
EvaluateActivationReadiness
PrepareIntegrationNotification
```

---

# 124. Event handler side-effect separation

Un handler qui :

- envoie email ;
- met à jour projection ;
- appelle ERP ;

ne devrait pas nécessairement tout faire dans une même classe.

SRP.

---

# 125. Event handler failure isolation — future

Dans le Core synchrone :

```text
one handler failure
may stop dispatch
```

selon implementation.

Plus tard, un bus durable pourra isoler les failures.

---

# 126. Dispatcher failure policy

Le document Ports devra définir la première politique.

Recommendation Core :

```text
fail fast in tests/local
```

pour rendre les erreurs visibles.

---

# 127. Event processing transaction

Ne pas démarrer automatiquement une nouvelle transaction métier dans le dispatcher.

Chaque réaction importante doit posséder son propre use case/handler.

---

# 128. Event to Command mapping

Exemple :

```text
SupplierAssessmentCompleted
    ↓
RequestSupplierQualification
```

ou :

```text
EvaluateSupplierQualification
```

selon workflow retenu.

---

# 129. Event to Query update

Exemple :

```text
SupplierQualified
    ↓
QualificationSummaryProjection updated
```

---

# 130. Event to Integration Event

Future :

```text
SupplierQualified
    ↓
SupplierQualifiedV1
    ↓
external transport
```

---

# 131. Event to Audit

Possible :

```text
Domain Event
    ↓
Audit Recorder
```

qui enrichit avec :

- actor ;
- correlation ;
- source ;
- technical timestamp.

---

# 132. Domain Event storage for audit

Le système peut stocker certains Domain Events à des fins d’audit sans devenir Event Sourced.

---

# 133. Domain Event history

Une vue :

```text
GetSupplierRelationshipHistory
```

peut être construite depuis :

- audit records ;
- events ;
- explicit history table.

Le Core ne fixe pas encore la persistence.

---

# 134. Event serialization

Le Domain Event Python n’a pas besoin d’être directement JSON-ready.

Un mapper peut le transformer plus tard.

---

# 135. Datetime policy

Recommandation :

```text
timezone-aware UTC datetime
```

pour les event timestamps.

La conversion locale appartient aux interfaces.

---

# 136. Clock dependency

Le Domain Event ne doit pas appeler lui-même :

```python
datetime.now()
```

si le domaine doit rester déterministe.

Le `occurred_at` peut être fourni par :

- Handler via Clock ;
- Aggregate operation input ;
- factory.

---

# 137. EventId generation

Même principe :

- application-generated ;
- domain local UUID generation ;
- injected generator ;

sont possibles.

Pour le MVP :

```text
UUID4 locally
```

est acceptable.

---

# 138. Event schema design

Un event doit être suffisamment spécifique pour rester utile.

Mauvais :

```text
SupplierStateChanged(old, new)
```

si plusieurs transitions ont des significations très différentes.

---

# 139. Event granularity

Ne pas émettre un event pour chaque modification triviale.

Émettre lorsque :

- un fait métier significatif s’est produit ;
- un autre process peut légitimement réagir ;
- l’audit doit distinguer l’action.

---

# 140. Event granularity example

Peut être inutile :

```text
SupplierTradingNameWhitespaceNormalized
```

Utile :

```text
SupplierQualified
```

---

# 141. Domain Event catalog governance

La liste des events doit évoluer avec les use cases réels.

Ne pas créer un catalogue exhaustif de futurs events avant implémentation.

---

# 142. Event deprecation

Si un Domain Event public devient stable, sa suppression devra suivre la stratégie de versioning du package.

Avant 1.0, davantage d’évolution est acceptable.

---

# 143. Event public imports

Candidate future API :

```python
from pysrmkit.domain.events import SupplierQualified
```

ou exports par capability.

À trancher dans Public API doc.

---

# 144. Event organization by capability

Candidate layout :

```text
domain/
├── supplier/
│   └── events.py
├── relationship/
│   └── events.py
├── qualification/
│   └── events.py
├── assessment/
│   └── events.py
└── incident/
    └── events.py
```

Alternative :

```text
domain/events/
```

La décision finale appartient au package architecture doc.

---

# 145. Event co-location principle

Avantage de co-locating :

```text
Aggregate
+
its Events
```

dans la même capability :

- meilleure cohésion ;
- navigation plus simple ;
- évite un énorme module events.

---

# 146. Central event module risk

Un :

```text
domain/events.py
```

global peut devenir trop volumineux.

---

# 147. Event base types location

Les types communs peuvent vivre dans :

```text
domain/common/events.py
```

si nécessaire.

---

# 148. Event learning map

```text
Business transition
        │
        ▼
Aggregate invariant passes
        │
        ▼
State changes
        │
        ▼
Domain Event recorded
        │
        ▼
Application commits
        │
        ▼
Dispatcher reacts
```

---

# 149. Design Concepts Applied

## DDD

```text
Aggregate
Domain Event
Application Service
Repository
Domain Policy
```

## Principles

```text
Low Coupling
High Cohesion
Separation of Concerns
Information Hiding
Explicit Dependencies
SRP
KISS
YAGNI
```

## Architecture

```text
Event-Driven friendly
Ports & Adapters
Application orchestration
Eventual Consistency
```

## Python

```text
immutable dataclass
typed IDs
Protocol / Callable
composition
```

---

# 150. Pattern classification

Le Event Model ne revendique pas automatiquement :

```text
Observer
Mediator
Event Sourcing
Command
```

Simple existence d’un dispatcher ≠ preuve d’un GoF pattern.

---

# 151. Core event implementation minimalism

Le premier code peut se limiter à :

```text
DomainEvent type
Aggregate event list
_record_event(...)
pull_events()
simple dispatcher
event handler registration
```

Rien de plus.

---

# 152. Suggested minimal abstractions

```text
DomainEvent
DomainEventDispatcher
DomainEventHandler
```

Même ces abstractions peuvent être réduites si Python callables suffisent.

---

# 153. Implementation sketch

Conceptuel :

```python
@dataclass(frozen=True, slots=True)
class SupplierQualified:
    event_id: EventId
    qualification_id: QualificationId
    relationship_id: SupplierRelationshipId
    scope: QualificationScope
    occurred_at: datetime
```

---

# 154. Aggregate event list sketch

```python
class Aggregate:
    def __init__(self) -> None:
        self._domain_events = []

    def _record_event(self, event) -> None:
        self._domain_events.append(event)

    def pull_events(self):
        events = tuple(self._domain_events)
        self._domain_events.clear()
        return events
```

Illustratif, pas normatif.

---

# 155. Avoid generic base too early

Un `Aggregate` base class n’est pas obligatoire.

Chaque Aggregate peut gérer ses events explicitement au début.

Si la répétition devient réelle :

```text
extract common mechanism
```

plus tard.

---

# 156. Refactoring trigger

Introduire une base commune si plusieurs Aggregates répètent exactement :

```text
event recording
event pulling
aggregate version
```

et que cette abstraction apporte une valeur réelle.

---

# 157. MVP Event Tests

Le premier milestone event model doit inclure :

```text
test_supplier_created_event
test_relationship_created_event
test_supplier_invited_event
test_onboarding_started_event
test_assessment_completed_event
test_qualification_requested_event
test_qualification_approved_event
test_qualification_rejected_event
test_invalid_transition_records_no_event
test_pull_events_preserves_order
test_pull_events_clears_queue
```

---

# 158. Scenario test

Scénario :

```text
register supplier
create relationship
invite
start onboarding
complete assessment
request qualification
evaluate qualification
```

Puis vérifier l’ordre logique des events produits par chaque Aggregate/use case.

---

# 159. Event tracing in examples

Le script :

```text
examples/local_qualification.py
```

peut afficher les Domain Events pour rendre visible la mécanique.

Exemple :

```text
[EVENT] SupplierCreated
[EVENT] SupplierRelationshipCreated
[EVENT] SupplierInvited
[EVENT] SupplierOnboardingStarted
[EVENT] SupplierAssessmentCompleted
[EVENT] SupplierQualificationRequested
[EVENT] SupplierQualified
```

Cela renforce l’objectif pédagogique.

---

# 160. No external broker in example

Le scénario local ne doit pas démarrer :

```text
Kafka
Redis
RabbitMQ
```

---

# 161. Event model acceptance criteria

Le document est suffisamment implémentable si :

```text
[ ] Domain Event definition is clear
[ ] Command/Event distinction is clear
[ ] Domain/Integration distinction is clear
[ ] Event naming convention is fixed
[ ] Minimal metadata is known
[ ] Aggregate ownership is defined
[ ] Recording happens only after valid transition
[ ] Invalid operations emit no success event
[ ] pull_events semantics are defined
[ ] local ordering is preserved
[ ] in-process dispatch is sufficient for MVP
[ ] broker/outbox/event sourcing are explicitly deferred
```

---

# 162. Core Event Catalog acceptance criteria

Pour le Core qualification :

```text
SupplierCreated
SupplierRelationshipCreated
SupplierInvited
SupplierOnboardingStarted
SupplierAssessmentCompleted
SupplierQualificationRequested
SupplierQualified
SupplierQualificationRejected
```

doivent être suffisants pour raconter le scénario métier principal.

---

# 163. Deferred event topics

À traiter plus tard :

```text
Integration Event versioning
Transactional Outbox
Durable retries
Dead-letter queues
Exactly-once semantics
External schemas
Broker partitioning
Consumer offsets
Event retention
Event replay
Schema Registry
Distributed tracing metadata
```

---

# 164. Documentation rule after bootstrap

Un nouveau mécanisme événementiel ne sera spécifié que si le code rencontre réellement le besoin.

Exemple :

```text
Need reliable external publication
    → Outbox spec

Need event replay
    → Event Store research

Need cross-service contracts
    → Integration Event versioning spec
```

---

# 165. Pedagogical distinction matrix

| Concept | Meaning |
|---|---|
| Command | Intention |
| Domain Event | Business fact |
| Integration Event | External contract |
| Event Handler | Application reaction |
| Event Dispatcher | Delivery mechanism |
| Audit Record | Traceability record |
| Event Sourcing | Persistence model from events |
| Observer | GoF behavioral pattern |

---

# 166. Learning objective

Après l’implémentation du Core, il doit devenir naturel de reconnaître :

```text
"Something meaningful just happened"
    → Domain Event
```

et non :

```text
"Something changed in the database"
    → Event
```

Le Domain Event doit venir du métier, pas de la persistence.

---

# 167. Event model North Star

```text
COMMAND
    │
    ▼
AGGREGATE
    │
    ├── validate invariants
    ├── change state
    └── record DOMAIN EVENT
            │
            ▼
        COMMIT
            │
            ▼
    LOCAL DISPATCHER
            │
            ├── application reaction
            ├── projection update
            └── future integration mapping
```

---

# 168. Final principles

> **Events describe facts, not intentions.**

> **Events are emitted by business behavior, not by database triggers.**

> **A successful event must correspond to a successful domain transition.**

> **Domain Events remain independent from brokers.**

> **Cross-aggregate reactions are orchestrated explicitly.**

> **The Core starts synchronous and in-process.**

> **Durability and distributed delivery are deferred until they become real problems.**

---

# 169. Implementation scope after this document

Après ce document, l’implémentation doit être capable de concevoir :

```text
immutable Domain Event objects
aggregate-local pending event collection
pull_events()
simple in-process dispatch
event-driven application reactions
```

sans définir encore :

```text
external integration transport
```

---

# 170. Next mandatory document

Le prochain document du baseline pré-bootstrap est :

> **`10_PYSRMKIT_PORTS_AND_REPOSITORY_CONTRACTS.md`**

Il devra préciser les abstractions nécessaires au premier Core :

```text
SupplierRepository
SupplierRelationshipRepository
SupplierQualificationRepository
SupplierAssessmentRepository
Clock
DomainEventDispatcher
UnitOfWork candidate
```

et leurs contracts de test.

---

# 171. Conclusion

Le Event Model de PySRMKit est volontairement simple.

Il repose sur une idée centrale :

> **Lorsqu’un Aggregate accepte une transition métier significative, il enregistre un fait métier immuable.**

Ce fait peut ensuite :

- être observé ;
- déclencher un autre use case ;
- alimenter une projection ;
- participer à l’audit ;
- être transformé plus tard en Integration Event.

Le premier Core n’a besoin ni de Kafka, ni d’Event Sourcing, ni de Transactional Outbox.

Il a besoin de :

```text
Domain Events
+
Aggregate event recording
+
Application commit boundary
+
In-process dispatch
+
Tests
```
Cette simplicité permet de pratiquer concrètement :

```text
DDD Domain Events
Aggregate boundaries
Low Coupling
Event-Driven Architecture
Application orchestration
Eventual Consistency
```

tout en respectant :

```text
KISS
YAGNI
Problem Before Pattern
```

La règle finale est :

> **Model the business fact first.  
> Choose the transport later.**