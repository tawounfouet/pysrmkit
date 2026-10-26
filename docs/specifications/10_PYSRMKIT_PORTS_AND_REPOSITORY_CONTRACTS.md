# PySRMKit — Ports and Repository Contracts

**Document :** `10_PYSRMKIT_PORTS_AND_REPOSITORY_CONTRACTS.md`  
**Projet :** PySRMKit  
**Domaine :** Supplier Relationship Management  
**Type :** Architecture / Ports / Persistence Contracts  
**Statut :** Baseline pré-implémentation  
**Version du document :** 0.1.0  

**Documents de référence :**
- `03_PYSRMKIT_SYSTEM_ARCHITECTURE.md`
- `04_PYSRMKIT_DOMAIN_OBJECTS.md`
- `05_PYSRMKIT_ENTITIES_AND_VALUE_OBJECTS.md`
- `06_PYSRMKIT_DOMAIN_RELATIONSHIPS_AND_ERD.md`
- `07_PYSRMKIT_DOMAIN_INVARIANTS_AND_BUSINESS_RULES.md`
- `08_PYSRMKIT_COMMANDS_QUERIES_AND_USE_CASES.md`
- `09_PYSRMKIT_DOMAIN_EVENTS_AND_EVENT_MODEL.md`
- `PYSRMKIT_SOFTWARE_DESIGN_LEARNING_CONVENTION.md`
- `PYSRMKIT_PRE_IMPLEMENTATION_SPECIFICATION_CUTOFF_AND_ITERATIVE_DOCUMENTATION_STRATEGY.md`

---

# 1. Objet du document

Ce document définit les **Ports et Repository Contracts nécessaires au premier Core PySRMKit**.

Il répond notamment aux questions suivantes :

> De quelles abstractions la couche Application a-t-elle réellement besoin ?

> Quels Aggregate Roots nécessitent un Repository ?

> Quelles opérations doivent être exposées par ces Repositories ?

> Quelles opérations ne doivent surtout pas être ajoutées ?

> Comment garantir qu’un futur adapter PostgreSQL se comporte comme l’adapter InMemory ?

> Quelle est la place de `Clock`, du dispatcher de Domain Events et du `UnitOfWork` ?

> Où placer les frontières entre Command side, Query side et infrastructure ?

> Comment appliquer concrètement Dependency Inversion, Liskov Substitution et Ports & Adapters en Python ?

Le document reste volontairement centré sur :

```text
LOCAL CORE
+
IN-MEMORY ADAPTERS
+
CONTRACT TESTS
```

Il ne définit pas encore :

```text
SQLAlchemy mapping
PostgreSQL schema
MongoDB strategy
distributed locks
transactional outbox
async repository API
external event broker
```

---

# 2. Position dans le baseline pré-bootstrap

```text
08 — Commands / Queries / Use Cases
        │
        ▼
09 — Domain Events
        │
        ▼
10 — PORTS & REPOSITORY CONTRACTS   ← ce document
        │
        ▼
11 — Repository & Package Architecture
        │
        ▼
12 — Testing Strategy
        │
        ▼
13 — Implementation Roadmap
        │
        ▼
14 — Bootstrap Plan
        │
        ▼
IMPLEMENTATION
```

Le `10` définit les **contrats**.

Le `11` décidera précisément **où ces contrats vivent dans le repository Python**.

---

# 3. Architecture de référence

```text
┌───────────────────────────────┐
│       Application Layer       │
│ Commands / Handlers / Queries │
└───────────────┬───────────────┘
                │
                │ depends on
                ▼
┌───────────────────────────────┐
│             PORTS             │
│                               │
│ SupplierRepository            │
│ RelationshipRepository        │
│ QualificationRepository       │
│ AssessmentRepository          │
│ Clock                         │
│ DomainEventDispatcher         │
│ UnitOfWork?                   │
└───────────────▲───────────────┘
                │
                │ implements
                │
┌───────────────┴───────────────┐
│           ADAPTERS            │
│                               │
│ InMemory...Repository         │
│ SystemClock                   │
│ InProcessEventDispatcher      │
│ NoOpUnitOfWork?               │
└───────────────────────────────┘
```

---

# 4. Définition d’un Port

Dans PySRMKit, un **Port** exprime :

> **un besoin de l’intérieur du système envers une capacité extérieure ou interchangeable.**

Un Port est donc défini depuis le point de vue du Domain/Application Core.

Exemples :

```text
SupplierRepository
Clock
DomainEventDispatcher
RiskDataProvider
DocumentStorageProvider
```

---

# 5. Port ≠ Adapter

```text
Port
    = contract

Adapter
    = implementation
```

Exemple :

```text
SupplierRepository
        ▲
        │
        ├── InMemorySupplierRepository
        └── PostgreSQLSupplierRepository
```

Le Core dépend du Port.

L’Adapter dépend du Port.

---

# 6. Dependency Inversion appliqué

Mauvais :

```text
RegisterSupplierHandler
        │
        ▼
PostgreSQLSupplierRepository
```

Bon :

```text
RegisterSupplierHandler
        │
        ▼
SupplierRepository
        ▲
        │
PostgreSQLSupplierRepository
```

Concepts appliqués :

```text
[PRINCIPLE: Dependency Inversion Principle]
[ARCH: Ports and Adapters]
[DDD: Repository]
```

---

# 7. Ports requis pour le premier Core

Ports obligatoires pour aller jusqu’à une qualification locale :

```text
SupplierRepository
SupplierRelationshipRepository
SupplierQualificationRepository
SupplierAssessmentRepository
Clock
DomainEventDispatcher
```

Port candidat :

```text
UnitOfWork
```

Ports différés :

```text
RiskDataProvider
SanctionsScreeningProvider
DocumentStorageProvider
CompanyRegistryProvider
TaxValidationProvider
IntegrationEventPublisher
```

---

# 8. Repository — définition retenue

Un Repository représente une collection orientée domaine d’Aggregate Roots.

Il fournit l’illusion conceptuelle :

```text
load aggregate
save aggregate
find aggregate using domain-relevant identity
```

Il ne doit pas exposer la technologie de persistence.

---

# 9. Repository ≠ DAO générique

Important :

```text
DDD Repository
≠
Generic DAO
```

Éviter :

```python
repository.create(table, payload)
repository.update(table, filters, values)
repository.execute_sql(...)
repository.find_all(filters: dict)
```

Préférer :

```python
supplier = repository.get(supplier_id)
repository.save(supplier)
```

---

# 10. Repository ≠ Query God Object

Un Repository Command-side ne doit pas absorber toutes les lectures possibles du produit.

Éviter :

```text
SupplierRepository
    search_by_name_country_category_risk_status(...)
    dashboard(...)
    scorecard(...)
    report(...)
```

Ces besoins appartiennent plutôt au Query side :

```text
Read Models
Query Services
Search Ports
Projections
```

---

# 11. Repository per Aggregate Root

Heuristique retenue :

```text
one Repository contract
per Aggregate Root
```

et non :

```text
one Repository
per class
```

Pas de Repository pour :

```text
SupplierId
Address
QualificationScope
RiskScore
AssessmentScore
```

---

# 12. Aggregate Roots du premier Core

Le premier Core utilise :

```text
Supplier
SupplierRelationship
SupplierQualification
SupplierAssessment
```

Donc :

```text
SupplierRepository
SupplierRelationshipRepository
SupplierQualificationRepository
SupplierAssessmentRepository
```

---

# 13. Repository API — principe de minimalité

Chaque méthode doit répondre à un use case réel.

La règle est :

> **No repository method without a use-case reason.**

Cela évite :

```text
premature generic API
```

---

# 14. Repository API — conventions

Convention recommandée :

```text
get(...)
save(...)
```

et quelques méthodes de recherche métier ciblées.

`save()` signifie :

> persister l’état courant d’un Aggregate valide.

Il ne signifie pas :

> appliquer arbitrairement un patch de fields.

---

# 15. Repository `get`

Convention :

```text
get(id) -> Aggregate | None
```

Le Repository ne lève pas automatiquement :

```text
SupplierNotFound
```

Cette erreur appartient généralement à l’Application Layer.

Exemple :

```text
supplier = repository.get(command.supplier_id)

if supplier is None:
    raise SupplierNotFound(...)
```

---

# 16. Pourquoi retourner `None`

Avantages :

- contract simple ;
- absence représentée explicitement ;
- Repository reste indépendant des use cases ;
- Application décide quelle erreur exposer.

---

# 17. Repository `save`

Convention :

```text
save(aggregate) -> None
```

Le Repository reçoit un Aggregate déjà valide.

Il ne doit pas :

- décider les invariants métier ;
- modifier le lifecycle ;
- produire des Domain Events métier ;
- commit automatiquement de manière cachée si un UoW existe.

---

# 18. Add vs Save

Deux styles étaient possibles :

```text
add(new)
save(existing)
```

ou :

```text
save(new_or_existing)
```

Pour le premier Core, la baseline privilégie :

```text
save(...)
```

pour réduire la surface API.

Un split `add/save` pourra être introduit si la persistence réelle le justifie.

---

# 19. Delete — volontairement absent

Le Core ne fournit pas par défaut :

```text
delete(...)
```

pour les Aggregate Roots métier.

Raisons :

- audit ;
- historique ;
- offboarding ≠ suppression ;
- qualification revoked/expired ≠ delete ;
- assessment history.

La suppression technique éventuelle sera traitée plus tard.

---

# 20. SupplierRepository

Contrat principal :

```text
get(supplier_id)
save(supplier)
find_by_external_identifier(identifier)
```

---

# 21. SupplierRepository — Python candidate

```python
from typing import Protocol

class SupplierRepository(Protocol):
    def get(self, supplier_id: SupplierId) -> Supplier | None:
        ...

    def save(self, supplier: Supplier) -> None:
        ...

    def find_by_external_identifier(
        self,
        identifier: ExternalIdentifier,
    ) -> Supplier | None:
        ...
```

Illustratif, mais suffisamment proche de la baseline cible.

---

# 22. Pourquoi `find_by_external_identifier`

Use cases :

```text
RegisterSupplier
FindSupplierByExternalIdentifier
duplicate detection
external system reconciliation
```

La méthode possède donc une justification métier réelle.

---

# 23. SupplierRepository — méthodes non retenues au MVP

Pas encore :

```text
list_all()
search(...)
find_by_country(...)
find_by_category(...)
paginate(...)
delete(...)
bulk_save(...)
```

Les besoins de recherche seront servis par le Query side.

---

# 24. SupplierRepository invariant cross-instance

Certaines contraintes dépassent un seul Aggregate.

Exemple :

```text
same canonical external identifier
should not map to conflicting Suppliers
```

Le Handler peut utiliser :

```text
find_by_external_identifier(...)
```

avant création.

---

# 25. SupplierRelationshipRepository

Contrat principal :

```text
get(relationship_id)
save(relationship)
find_for_supplier_and_organization(...)
```

---

# 26. Python candidate

```python
class SupplierRelationshipRepository(Protocol):
    def get(
        self,
        relationship_id: SupplierRelationshipId,
    ) -> SupplierRelationship | None:
        ...

    def save(
        self,
        relationship: SupplierRelationship,
    ) -> None:
        ...

    def find_for_supplier_and_organization(
        self,
        supplier_id: SupplierId,
        organization_id: InternalOrganizationId,
    ) -> SupplierRelationship | None:
        ...
```

---

# 27. Pourquoi `find_for_supplier_and_organization`

Use case :

```text
CreateSupplierRelationship
```

doit pouvoir vérifier l’unicité contextuelle d’une relation.

Ce check traverse les instances.

Il ne peut pas être réalisé uniquement par un nouvel Aggregate isolé.

---

# 28. RelationshipRepository — méthode optionnelle future

Si plusieurs relationships par organisation/type deviennent autorisées :

```text
find_current(...)
```

ou une méthode incluant :

```text
relationship_type
```

pourra remplacer le contrat initial.

Ne pas anticiper avant besoin.

---

# 29. SupplierQualificationRepository

Contrat principal :

```text
get(qualification_id)
save(qualification)
find_current_for_scope(...)
```

---

# 30. Python candidate

```python
class SupplierQualificationRepository(Protocol):
    def get(
        self,
        qualification_id: QualificationId,
    ) -> SupplierQualification | None:
        ...

    def save(
        self,
        qualification: SupplierQualification,
    ) -> None:
        ...

    def find_current_for_scope(
        self,
        relationship_id: SupplierRelationshipId,
        scope: QualificationScope,
    ) -> SupplierQualification | None:
        ...
```

---

# 31. Pourquoi `find_current_for_scope`

Use cases :

```text
RequestSupplierQualification
IsSupplierQualified
prevent conflicting current qualifications
renew/re-evaluate later
```

Le terme `current` doit être défini par les invariants :

- non superseded ;
- non historical ;
- active request/current outcome.

La sémantique exacte sera alignée avec le `07`.

---

# 32. Qualification Repository — historique

Le Repository Command-side ne doit pas nécessairement fournir :

```text
list_history(...)
```

Une Query dédiée pourra le faire via un Read Model.

---

# 33. SupplierAssessmentRepository

Contrat principal :

```text
get(assessment_id)
save(assessment)
```

Éventuellement :

```text
find_open_for_relationship_and_type(...)
```

si un invariant interdit plusieurs assessments ouverts identiques.

---

# 34. Python candidate

```python
class SupplierAssessmentRepository(Protocol):
    def get(
        self,
        assessment_id: AssessmentId,
    ) -> SupplierAssessment | None:
        ...

    def save(
        self,
        assessment: SupplierAssessment,
    ) -> None:
        ...
```

Le MVP commence volontairement minimal.

---

# 35. Assessment lookup methods — différés

Ne pas ajouter immédiatement :

```text
find_by_score
find_by_status
list_completed
list_by_year
```

Ces besoins sont Query-side.

---

# 36. Repository return semantics

Les Repositories retournent :

```text
Domain Aggregates
```

et non :

```text
ORM models
database rows
dict
Pydantic models
```

---

# 37. Persistence mapping boundary

Future adapter :

```text
PostgreSQL Row / ORM Model
        │
        ▼
Mapper
        │
        ▼
Domain Aggregate
```

Le Repository Contract ne change pas.

---

# 38. Repository exception semantics

Le contrat du Core évite les exceptions pour :

```text
not found
```

mais peut laisser remonter une erreur technique abstraite si la persistence échoue.

Cependant la taxonomie d’infrastructure est différée.

---

# 39. Repository should not validate domain rules

Mauvais :

```text
repository.save()
    rejects Supplier because lifecycle invalid
```

Le domaine doit déjà être valide avant persistence.

---

# 40. Repository should preserve Aggregate identity

Contract :

```text
save(x)
get(x.id)
```

doit reconstruire un Aggregate représentant la même Entity.

---

# 41. Repository round-trip principle

Pour toute implémentation :

```text
aggregate
    ↓ save
repository
    ↓ get
equivalent aggregate state
```

Cette propriété sera testée.

---

# 42. Equality caution

Une Entity n’est pas forcément comparée structurellement.

Les contract tests doivent vérifier :

- ID ;
- state pertinent ;
- Value Objects ;

plutôt que dépendre aveuglément de `==` si celui-ci n’est pas défini.

---

# 43. InMemory Repository role

Les adapters InMemory sont les premières implémentations concrètes.

Ils servent :

```text
local execution
unit/application tests
contract verification
examples
```

Ils ne sont pas du code jetable.

---

# 44. InMemorySupplierRepository

Candidate implementation structure :

```text
dict[SupplierId, Supplier]
```

avec index secondaire possible :

```text
ExternalIdentifier → SupplierId
```

---

# 45. InMemoryRelationshipRepository

Candidate :

```text
dict[SupplierRelationshipId, SupplierRelationship]
```

plus recherche contextuelle.

---

# 46. InMemoryQualificationRepository

Candidate :

```text
dict[QualificationId, SupplierQualification]
```

plus lookup :

```text
relationship + scope
```

---

# 47. InMemoryAssessmentRepository

Candidate :

```text
dict[AssessmentId, SupplierAssessment]
```

---

# 48. Copy semantics InMemory

Question importante :

```text
Does get() return the same mutable object reference?
```

Si oui, les tests peuvent masquer l’absence de `save()`.

Recommendation :

> **The InMemory adapter should mimic persistence boundaries closely enough not to hide lifecycle mistakes.**

Deux stratégies :

```text
deep copy on save/get
```

ou :

```textexplicit state cloning/serialization
```

Pour le premier Core, `deepcopy` peut être acceptable si les objets le permettent.

---

# 49. Why avoid shared-reference illusion

Mauvais test :

```text
aggregate = repo.get(id)
aggregate.suspend()

# test passes even without repo.save()
```

si le dict contient exactement la même instance.

Cela ne reproduit pas une vraie persistence.

---

# 50. InMemory realism principle

L’InMemory adapter n’a pas besoin d’émuler PostgreSQL.

Mais il doit éviter de fausser les contrats fondamentaux :

```text
load
mutate
save
reload
```

---

# 51. Repository Contract Tests

Chaque Repository possède une suite de tests commune.

Exemple :

```text
SupplierRepositoryContract
```

qui pourra être exécutée contre :

```text
InMemorySupplierRepository
PostgreSQLSupplierRepository
MongoSupplierRepository
```

si ces adapters apparaissent plus tard.

---

# 52. Liskov Substitution Principle

Si deux adapters implémentent le même Port :

> un consumer ne doit pas avoir besoin de connaître lequel est utilisé pour obtenir un comportement contractuel correct.

Le contract testing rend LSP concret.

---

# 53. SupplierRepository Contract Tests

Tests minimum :

```text
save then get returns same logical Supplier
unknown id returns None
save updated Supplier replaces persisted state
find_by_external_identifier resolves Supplier
unknown external identifier returns None
multiple Suppliers remain isolated
```

---

# 54. SupplierRelationshipRepository Contract Tests

```text
save/get round-trip
unknown id returns None
find_for_supplier_and_organization resolves relationship
unrelated organization does not match
multiple Suppliers remain isolated
updated lifecycle persists after save
```

---

# 55. SupplierQualificationRepository Contract Tests

```text
save/get round-trip
unknown id returns None
find_current_for_scope returns expected qualification
different scopes do not collide
different relationships do not collide
updated qualification status persists
```

---

# 56. SupplierAssessmentRepository Contract Tests

```text
save/get round-trip
unknown id returns None
answers/scores survive persistence
completed assessment state survives reload
multiple assessments remain isolated
```

---

# 57. Shared contract test style

Possible pattern :

```python
class SupplierRepositoryContract:
    def make_repository(self) -> SupplierRepository:
        raise NotImplementedError

    def test_save_and_get(self):
        repository = self.make_repository()
        ...
```

Puis :

```python
class TestInMemorySupplierRepository(
    SupplierRepositoryContract
):
    def make_repository(self):
        return InMemorySupplierRepository()
```

Illustratif.

---

# 58. Contract Test ≠ Mock Test

Un Contract Test vérifie :

```text
real implementation
against
shared behavioral contract
```

Un Mock Test vérifie principalement des interactions.

Ne pas confondre.

---

# 59. Clock Port

Le Core nécessite un temps déterministe.

Port :

```text
Clock
```

---

# 60. Clock contract

```python
class Clock(Protocol):
    def now(self) -> datetime:
        ...
```

Contract :

```text
returns timezone-aware datetime
represents current logical time
```

Recommendation :

```text
UTC
```

pour le Core.

---

# 61. SystemClock Adapter

Production/local runtime adapter :

```python
class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
```

---

# 62. FixedClock / FakeClock

Tests :

```python
class FixedClock:
    def __init__(self, value: datetime) -> None:
        self._value = value

    def now(self) -> datetime:
        return self._value
```

Peut être étendu :

```text
advance(...)
```

si besoin.

---

# 63. Why Clock is a Port

Parce que le temps est une dépendance externe/non déterministe.

Le domaine doit pouvoir tester :

```text
expiration
qualification validity
assessment timestamps
event occurred_at
```

sans dépendre de l’horloge réelle.

---

# 64. DomainEventDispatcher Port

Le Core local a besoin d’un mécanisme de dispatch.

Port candidat :

```text
DomainEventDispatcher
```

---

# 65. Dispatcher contract

Deux options :

```text
dispatch(event)
```

ou :

```text
dispatch_all(events)
```

Baseline recommandée :

```python
class DomainEventDispatcher(Protocol):
    def dispatch_all(
        self,
        events: tuple[DomainEvent, ...],
    ) -> None:
        ...
```

afin de préserver explicitement l’ordre d’un batch local.

---

# 66. Dispatcher responsibility

Il doit :

- recevoir des Domain Events ;
- les dispatcher aux handlers enregistrés ;
- préserver l’ordre fourni ;
- faire remonter les erreurs au MVP.

Il ne doit pas :

- commit ;
- modifier l’Aggregate ;
- décider les invariants ;
- sérialiser Kafka ;
- effectuer retries durables.

---

# 67. InProcessDomainEventDispatcher

Premier adapter concret :

```text
InProcessDomainEventDispatcher
```

avec structure simple :

```text
event_type
→ list[callable]
```

---

# 68. Dispatcher contract tests

```text
zero handlers does not corrupt dispatch
registered handler receives event
multiple handlers receive event
events are delivered in order
handler error behavior is deterministic
```

---

# 69. Fail-fast policy

Pour le Core local :

```text
event handler exception
→ dispatch fails visibly
```

Pourquoi :

- débogage simple ;
- tests explicites ;
- aucune fausse impression de fiabilité.

Retry durable plus tard.

---

# 70. Event Handler is not a Port by default

Un event handler applicatif peut être un simple callable/class.

Pas besoin de créer :

```text
DomainEventHandler Protocol
```

tant que cela n’apporte pas de valeur.

KISS.

---

# 71. UnitOfWork — statut

**Status :** CANDIDATE PORT

Il peut être utile pour définir explicitement :

```text
transaction boundary
commit
rollback
```

Mais le premier Core InMemory ne doit pas sur-concevoir ce mécanisme.

---

# 72. Pourquoi envisager UnitOfWork

Use case :

```text
handler
    loads Aggregate
    saves Aggregate
    commits transaction
    dispatches events
```

Un UoW rend le commit explicite.

---

# 73. Minimal UnitOfWork contract

Candidate :

```python
class UnitOfWork(Protocol):
    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
```

Mais cette forme ne contrôle pas encore les repositories.

---

# 74. Rich UnitOfWork — deferred

Ne pas introduire avant besoin :

```text
uow.suppliers
uow.relationships
uow.qualifications
context manager
nested transaction
savepoint
```

---

# 75. Core decision for UoW

Baseline :

> **Support the concept, but allow the first implementation to use a minimal or NoOp UnitOfWork.**

Le document `11/13` pourra décider si `0.1.0a1` inclut déjà ce Port.

---

# 76. NoOpUnitOfWork

Pour InMemory :

```text
commit()
    no-op

rollback()
    no-op or state reset if snapshot semantics implemented
```

À ne pas prétendre fournir de vraies transactions si ce n’est pas le cas.

---

# 77. Commit ownership

Si UoW existe :

```text
Repository.save()
```

ne doit pas commit automatiquement.

Le Handler orchestre :

```text
save
commit
dispatch
```

---

# 78. Without UoW

Pour un tout premier MVP :

```text
repository.save()
dispatcher.dispatch_all(...)
```

peut suffire.

Mais le code doit être structuré pour qu’un UoW puisse être introduit sans déplacer la logique métier.

---

# 79. Query-side Ports

Le Core local qualification n’a pas encore besoin d’un Query architecture riche.

Possibles futurs ports :

```text
SupplierReader
SupplierRelationshipReader
QualificationReader
SupplierSearchPort
```

---

# 80. Why defer Query ports

Le premier scénario peut lire les Aggregates directement dans les tests/examples.

Le Query side doit émerger avec les vrais besoins de projection.

---

# 81. Query side ≠ Repository side

Quand `GetSupplier360` apparaîtra :

```text
Supplier360Reader
```

ou une projection spécialisée sera préférable à un Repository géant.

---

# 82. External Provider Ports — deferred

Ces ports sont identifiés mais non obligatoires :

```text
CompanyRegistryProvider
TaxValidationProvider
SanctionsScreeningProvider
RiskDataProvider
DocumentStorageProvider
```

Ils seront créés lorsque les capacités correspondantes seront implémentées.

---

# 83. Port naming convention

Préférer des noms exprimant la capacité :

```text
SupplierRepository
Clock
RiskDataProvider
DocumentStorage
```

à :

```text
SupplierRepositoryInterface
IClock
IRiskProvider
AbstractSupplierRepository
```

Python n’a pas besoin du préfixe `I`.

---

# 84. Adapter naming convention

Implémentation concrète :

```text
InMemorySupplierRepository
PostgreSQLSupplierRepository
SystemClock
FixedClock
InProcessDomainEventDispatcher
```

Le nom expose clairement la technologie de l’adapter.

---

# 85. Port methods use domain types

Bon :

```python
get(supplier_id: SupplierId)
```

Mauvais :

```python
get(supplier_id: str)
```

si le Core manipule déjà un `SupplierId`.

---

# 86. Port methods avoid infrastructure types

Mauvais :

```python
save(session: Session, supplier: Supplier)
```

```python
find(query: Select)
```

```python
get(document: MongoDocument)
```

---

# 87. Port errors avoid vendor semantics

Le Port ne doit pas exposer :

```text
SQLAlchemyError
psycopg exception
MongoError
```

à l’Application Layer comme contrat normal.

La traduction technique sera définie dans l’adapter.

---

# 88. Sync-first contract

Le premier Core est :

```text
synchronous
```

Donc les Ports initiaux sont synchrones.

Ne pas écrire :

```python
async def get(...)
```

sans besoin d’I/O async réel.

---

# 89. Why sync first

- réduit la complexité ;
- facilite les tests ;
- garde le domaine pédagogique ;
- InMemory n’a aucun intérêt à être async ;
- permet de comprendre les frontières avant la concurrence.

---

# 90. Async later

Si une API async ou une persistence async apparaît :

- API parallèle ;
- adapters séparés ;
- refactoring ciblé ;

seront étudiés.

Ne pas contaminer le Core aujourd’hui.

---

# 91. Repository identity map — not required

Le Core ne requiert pas :

```text
Identity Map
```

comme pattern explicite.

Un ORM futur pourra en fournir une.

Ne pas l’introduire prématurément.

---

# 92. Generic Repository — rejected

PySRMKit n’adopte pas pour le Core :

```python
Repository[T, ID]
```

comme abstraction principale.

Pourquoi :

- masque les opérations métier spécifiques ;
- encourage CRUD générique ;
- réduit la lisibilité pédagogique ;
- peut forcer un plus petit dénominateur commun.

---

# 93. Common helper base — possible later

Les adapters peuvent partager une utility interne.

Mais les **Ports publics restent explicites**.

---

# 94. Specification Pattern — not required in Repository

Éviter :

```python
repository.find(specification)
```

avant pression réelle.

Les méthodes métier ciblées suffisent pour le Core.

---

# 95. Repository isolation

Un Repository ne doit pas utiliser un autre Repository pour appliquer une règle métier.

Coordination :

```text
Application Handler
```

---

# 96. Example — Relationship creation

```text
CreateSupplierRelationshipHandler
    │
    ├── suppliers.get(supplier_id)
    ├── relationships.find_for_supplier_and_organization(...)
    ├── SupplierRelationship.create(...)
    └── relationships.save(...)
```

Pas :

```text
SupplierRelationshipRepository
    internally checks SupplierRepository
```

---

# 97. Example — Qualification request

```text
RequestSupplierQualificationHandler
    │
    ├── relationships.get(...)
    ├── qualifications.find_current_for_scope(...)
    ├── SupplierQualification.create(...)
    └── qualifications.save(...)
```

---

# 98. Example — Assessment completion

```text
CompleteSupplierAssessmentHandler
    │
    ├── assessments.get(...)
    ├── assessment.complete(...)
    └── assessments.save(...)
```

---

# 99. Port granularity

Un Port doit être suffisamment petit et cohésif.

Mais éviter une fragmentation artificielle :

```text
SupplierGetter
SupplierSaver
SupplierFinder
```

si `SupplierRepository` reste cohésif.

---

# 100. Interface Segregation applied

Le consumer ne doit dépendre que des opérations pertinentes.

Un Repository Core de 3 à 5 méthodes respecte mieux ISP qu’un Repository universel de 30 méthodes.

---

# 101. Repository public mutability

Le Repository retourne un Aggregate qui peut évoluer via ses business methods.

Il ne doit pas fournir une API de mutation champ par champ.

---

# 102. Snapshot semantics

Les read models futurs peuvent être immuables.

Le Repository Command-side, lui, reconstruit un Aggregate mutable de façon contrôlée.

---

# 103. Transaction boundaries

Repository Contract :

```text
persistence operation
```

UoW/Handler :

```text
transaction orchestration
```

Ne pas mélanger.

---

# 104. Event extraction and Repository

Un Repository ne doit pas automatiquement supprimer les Domain Events pending.

La collecte est une responsabilité explicite de l’Application/UoW.

---

# 105. Event publication and Repository

Repository ne publie pas les Domain Events.

Éviter :

```text
save()
    → publish()
```

comme side effect caché.

---

# 106. Why keep save pure

Cela rend possible :

```text
save
commit
dispatch
```

et prépare correctement un futur Outbox.

---

# 107. Clock and event timestamps

Le Handler peut obtenir :

```text
now = clock.now()
```

et le transmettre au Domain behavior.

Cela garde :

```text
event occurred_at
```

déterministe.

---

# 108. IDs generation — no port initially

Le premier Core n’a pas besoin de :

```text
SupplierIdGenerator
RelationshipIdGenerator
```

si les IDs peuvent être générés localement avec UUID.

YAGNI.

---

# 109. Future deterministic IDs in tests

Les tests peuvent construire explicitement les IDs.

Aucun generator global n’est requis.

---

# 110. Repository contract and optimistic concurrency

Différé.

Un futur adapter pourra utiliser :

```text
version
```

et lever une erreur abstraite :

```text
ConcurrentModification
```

Mais le Port du MVP n’intègre pas encore `expected_version`.

---

# 111. Repository contract and pagination

Non pertinent au Command-side MVP.

Pagination appartient aux Queries.

---

# 112. Repository contract and sorting

Non pertinent au Core Command side.

---

# 113. Repository contract and bulk operations

Non retenu :

```text
save_all
bulk_update
bulk_delete
```

avant besoin.

---

# 114. Repository contract and transactions

Le Repository n’expose pas :

```text
begin
commitrollback
```

Ces concepts appartiennent au UnitOfWork.

---

# 115. InMemory adapter data isolation

Chaque instance de Repository doit posséder son propre store par défaut.

Éviter des dictionaries globaux partagés entre tests.

---

# 116. Test determinism

Les adapters InMemory doivent permettre :

```text
fresh instance
→ clean state
```

pour chaque test.

---

# 117. Adapter seeding

Pour les tests :

```text
repository.save(fixture)
```

est suffisant.

Pas besoin d’une API spéciale `seed()` publique.

---

# 118. Inspection helpers

Un adapter InMemory peut posséder des helpers privés/test-only.

Ils ne doivent pas élargir le Port public.

---

# 119. Contract-first implementation order

Ordre recommandé :

```text
1. define Port Protocol
2. write shared contract tests
3. implement InMemory adapter
4. run contract tests
5. use in Handler tests
```

---

# 120. Why contract-first

Cela transforme immédiatement le Port en :

```text
executable architecture contract
```

plutôt qu’en interface décorative.

---

# 121. Testing layers for Ports

```text
PORT CONTRACT TEST
    shared behavior

ADAPTER UNIT TEST
    adapter-specific detail

APPLICATION TEST
    consumer behavior through Port

ARCHITECTURE TEST
    dependency direction
```

---

# 122. Architecture test candidates

```text
domain must not import adapters
application must not import concrete repository adapters
ports must not import SQLAlchemy
ports must not import FastAPI
memory adapters may import domain + ports only
```

---

# 123. Port placement rule

Le `11` tranchera package path exact.

Principe logique :

```text
Ports belong to the inside.
Adapters belong to the outside.
```

---

# 124. Domain or Application ownership of Repository Ports

Deux options classiques :

```text
domain/ports
```

ou :

```text
application/ports
```

Pour PySRMKit, recommandation :

> Repository Ports are consumed by Application Handlers and represent persistence needs of Domain Aggregates.

Le `11` pourra donc privilégier :

```text
application/ports
```

ou un package top-level :

```text
ports/
```

sans changer la règle de dépendance.

---

# 125. Repository port should import Domain Types

C’est acceptable :

```text
SupplierRepository
    imports Supplier
    imports SupplierId
```

Le Port existe pour manipuler les Aggregates du domaine.

---

# 126. Domain should not import Repository

Important :

```text
Supplier
```

ne connaît pas :

```text
SupplierRepository
```

Les Entities/Aggregates restent persistence ignorant.

---

# 127. Handler owns Repository coordination

C’est l’Application Layer qui sait :

```text
which repository
when to load
when to save
```

---

# 128. Query side future topology

Future possible :

```text
application/queries/
application/readers/
ports/read_models/
adapters/read_models/
```

Mais hors scope bootstrap initial.

---

# 129. Contract documentation convention

Chaque Port doit documenter :

```text
Purpose
Consumer
Input semantics
Return semantics
Absence semantics
Mutation semantics
Transaction semantics
Ordering if relevant
Error semantics
```

---

# 130. SupplierRepository docstring candidate

```python
class SupplierRepository(Protocol):
    """
    Persistence port for the Supplier aggregate.

    DDD role:
        Repository.

    Consumers:
        Supplier application handlers.

    Contract:
        - get() returns None when the Supplier is absent;
        - save() persists the current valid aggregate state;
        - find_by_external_identifier() resolves canonical Supplier identity.
    """
```

---

# 131. Comments convention

Éviter :

```python
# Repository pattern
```

Préférer :

```python
# Duplicate detection spans aggregate instances, so the application
# queries the repository before creating a new Supplier.
```

---

# 132. Learning Map — Repository

```text
Problem
    Domain state must survive use cases
        │
        ▼
DDD
    Repository
        │
        ▼
Architecture
    Output Port
        │
        ▼
SOLID
    Dependency Inversion
        │
        ▼
Python
    Protocol
        │
        ▼
Adapter
    InMemorySupplierRepository
        │
        ▼
Testing
    Shared Contract Tests
```

---

# 133. Learning Map — LSP

```text
SupplierRepository Contract
        │
        ├── InMemory adapter
        └── PostgreSQL adapter later
                 │
                 ▼
same behavioral tests
                 │
                 ▼
Liskov Substitution made executable
```

---

# 134. Learning Map — Clock

```text
Problem
    system time is non-deterministic
        │
        ▼
Port
    Clock
        │
        ├── SystemClock
        └── FixedClock
        │
        ▼
Deterministic domain tests
```

---

# 135. Learning Map — Event Dispatcher

```text
Domain Event
    │
    ▼
Application commit
    │
    ▼
Dispatcher Port
    │
    ▼
InProcess adapter
```

Le transport externe reste différé.

---

# 136. Learning Map — Unit of Work

```text
Problem
    multiple persistence operations need one transaction boundary
        │
        ▼
Candidate pattern
    Unit of Work
        │
        ▼
Introduce only when transactional pressure is real
```

---

# 137. Design Patterns explicitly applied

## Repository Pattern

Oui.

Justification réelle :

```text
persist/retrieve Aggregates independent of technology
```

## Adapter Pattern

Oui, côté implémentations.

```text
InMemory adapter
future PostgreSQL adapter
```

## Strategy

Non concerné directement par les Repository Ports.

## Factory

Non requis.

---

# 138. Architectural Principles Applied

```text
Dependency Inversion
Interface Segregation
Liskov Substitution
Separation of Concerns
Information Hiding
High Cohesion
Low Coupling
KISS
YAGNI
```

---

# 139. Anti-pattern — GenericRepository[T]

Rejeté pour le Core.

---

# 140. Anti-pattern — ORM Repository leakage

Éviter :

```text
SupplierRepository.get_session()
SupplierRepository.query()
SupplierRepository.model
```

---

# 141. Anti-pattern — Auto commit

Éviter un `save()` qui commit automatiquement si le système adopte ensuite UoW.

---

# 142. Anti-pattern — Repository emits Domain Event

Domain Events sont produits par le domaine.

---

# 143. Anti-pattern — Repository mutates Aggregate

Le Repository reconstruit/persiste.

Il ne doit pas :

```text
auto-qualify
auto-suspend
auto-normalize business state
```

---

# 144. Anti-pattern — Repository returns DTO

Command-side Repository retourne l’Aggregate.

---

# 145. Anti-pattern — Repository per Value Object

Aucun :

```text
AddressRepository
CountryCodeRepository
QualificationScopeRepository
```

---

# 146. Anti-pattern — hidden global store

InMemory adapter ne doit pas utiliser un singleton global invisible.

---

# 147. Anti-pattern — InMemory semantics too weak

L’InMemory adapter ne doit pas masquer l’oubli de `save()` en exposant toujours la même référence mutable sans réflexion.

---

# 148. Anti-pattern — Async everywhere

Pas d’`async` sans besoin.

---

# 149. Anti-pattern — Port per method

Éviter la micro-fragmentation artificielle.

---

# 150. Anti-pattern — Future-proofing everything

Ne pas ajouter :

```text
tenant_id
version
shard_key
transaction_id
retry_token
```

dans chaque Port tant qu’un besoin réel ne l’exige pas.

---

# 151. MVP Port Catalog

Baseline minimale :

```text
SupplierRepository
SupplierRelationshipRepository
SupplierQualificationRepository
SupplierAssessmentRepository
Clock
DomainEventDispatcher
```

Candidate :

```text
UnitOfWork
```

---

# 152. MVP Adapter Catalog

```text
InMemorySupplierRepository
InMemorySupplierRelationshipRepository
InMemorySupplierQualificationRepository
InMemorySupplierAssessmentRepository

SystemClock
FixedClock

InProcessDomainEventDispatcher

NoOpUnitOfWork?  [conditional]
```

---

# 153. MVP scenario dependency map

```text
RegisterSupplierHandler
    → SupplierRepository
    → Clock
    → DomainEventDispatcher

CreateSupplierRelationshipHandler
    → SupplierRepository
    → SupplierRelationshipRepository
    → Clock
    → DomainEventDispatcher

Create/CompleteAssessmentHandler
    → SupplierAssessmentRepository
    → Clock
    → DomainEventDispatcher

Request/EvaluateQualificationHandler
    → SupplierRelationshipRepository
    → SupplierQualificationRepository
    → SupplierAssessmentRepository
    → QualificationPolicy
    → Clock
    → DomainEventDispatcher
```

Exact dependencies will be refined during implementation.

---

# 154. Event dispatch placement in Handler

Candidate flow:

```text
aggregate = repo.get(...)
aggregate.do_business_action(now=clock.now())

repo.save(aggregate)

if uow:
    uow.commit()

dispatcher.dispatch_all(
    aggregate.pull_events()
)
```

---

# 155. Event collection caveat

Si plusieurs Aggregates sont modifiés dans un use case, les events doivent être collectés depuis chacun.

Le premier Core doit garder ce mécanisme explicite.

Pas encore besoin d’un global event collector.

---

# 156. Future UoW event collection

Un UnitOfWork plus riche pourra plus tard collecter automatiquement les events des Aggregates tracked.

Mais cette abstraction doit émerger de répétition réelle.

---

# 157. Contract versioning

Les Protocols internes peuvent évoluer pendant `0.x`.

Mais toute modification doit :

- mettre à jour les contract tests ;
- mettre à jour tous les adapters ;
- rester cohérente avec les handlers.

---

# 158. Public API status

Les Ports ne sont pas encore forcément surface publique stable.

Le document Public API ultérieur décidera des réexports.

---

# 159. Port type variance

Pas besoin de generics avancés au MVP.

Préférer des signatures explicites.

---

# 160. Typing acceptance

Les Ports doivent être suffisamment typés pour que :

```text
SupplierId
```

ne soit pas confondu avec :

```text
QualificationId
```

---

# 161. Static checking

`pyright` ou `mypy` pourra vérifier les implementations structurelles des Protocols.

Le choix outil sera figé au bootstrap.

---

# 162. Runtime isinstance checks

Pas requis.

Un Protocol peut être purement structurel.

---

# 163. `@runtime_checkable`

Ne pas ajouter sans besoin de vérification runtime.

---

# 164. Protocol vs ABC

Baseline :

```text
Protocol preferred
```

pour les Ports simples.

Pourquoi :

- structural typing ;
- faible cérémonie ;
- adapters faciles à écrire ;
- bon fit Python.

---

# 165. Quand préférer ABC plus tard

Si besoin de :

- comportement partagé ;
- lifecycle commun ;
- enforcement nominal ;
- hooks concrets.

Aucun besoin actuel.

---

# 166. Repository method naming

Standardiser :

```text
get
save
find_...
```

Éviter de mélanger :

```text
fetch
load
retrieve
read
```

sans raison.

---

# 167. Query method naming

`find_...` signifie :

```text
zero or one expected
```

Si plusieurs résultats deviennent légitimes :

```text
list_...
```

sur un Query Port, pas nécessairement sur Repository.

---

# 168. `exists(...)`

À éviter si `find(...)` fournit déjà l’information nécessaire et l’objet peut être utile.

Ajouter `exists` uniquement pour performance réelle plus tard.

---

# 169. Repository contracts and duplicate detection

Le Repository ne décide pas :

```text
duplicate = error
```

Il fournit l’information.

Le Handler/Domain rule décide.

---

# 170. Repository contracts and normalization

Un ExternalIdentifier doit déjà être normalisé/validé par son Value Object avant lookup.

Le Repository ne doit pas appliquer une normalisation métier secrète.

---

# 171. Persistence adapter normalization

Une normalisation purement technique de storage keys est acceptable en interne si elle ne change pas la sémantique.

---

# 172. Multi-organization

`SupplierRelationshipRepository` utilise :

```text
InternalOrganizationId
```

comme type explicite.

Cela protège le scope relationnel.

---

# 173. Multi-country

`SupplierRepository.find_by_external_identifier(...)` reçoit un Value Object pouvant porter :

```text
jurisdiction
```

Le Port n’a pas besoin d’une méthode française :

```text
find_by_siret(...)
```

dans le Core générique.

---

# 174. Local qualification readiness

Après implémentation de ce document, le Core doit pouvoir persister en mémoire :

```text
Supplier
SupplierRelationship
SupplierAssessment
SupplierQualification
```

et exécuter plusieurs handlers successifs sans dépendance technique externe.

---

# 175. Contract test acceptance criteria

Chaque adapter Repository est accepté si :

```text
[ ] all shared contract tests pass
[ ] aggregate IDs remain stable
[ ] state survives save/reload
[ ] unrelated aggregates remain isolated
[ ] domain-specific lookup semantics are correct
[ ] absence returns None
[ ] no infrastructure type leaks through contract
```

---

# 176. Clock acceptance criteria

```text
[ ] now() returns timezone-aware datetime
[ ] FixedClock is deterministic
[ ] domain tests do not need system time
```

---

# 177. Dispatcher acceptance criteria

```text
[ ] dispatches all supplied events
[ ] preserves supplied order
[ ] supports multiple handlers
[ ] handler failures are visible
[ ] requires no broker
```

---

# 178. UnitOfWork acceptance criteria — if included

```text
[ ] commit boundary is explicit
[ ] repository does not commit implicitly
[ ] local implementation remains simple
[ ] no fake distributed transaction claims
```

---

# 179. Architecture acceptance criteria

```text
[ ] Domain imports no repository adapters
[ ] Application depends only on Ports
[ ] InMemory adapters implement Port contracts
[ ] Ports use Domain types
[ ] Ports contain no SQL/HTTP/cloud types
[ ] Query concerns do not inflate repositories
```

---

# 180. Core implementation sequence enabled by this doc

```text
1. create domain IDs/value objects
2. create Supplier Aggregate
3. define SupplierRepository Protocol
4. write SupplierRepository contract tests
5. implement InMemorySupplierRepository
6. repeat for Relationship
7. repeat for Assessment
8. repeat for Qualification
9. implement Clock
10. implement local Event Dispatcher
11. wire application handlers
12. run local qualification scenario
```

---

# 181. Deferred Port Catalog

À créer uniquement lorsque les capabilities correspondantes arrivent :

```text
SupplierDocumentRepository
SupplierCertificationRepository
ComplianceCheckRepository
RiskAssessmentRepository
SupplierIncidentRepository
PerformanceMeasurementRepository? 
```

Même ici, un Repository ne sera créé que si l’objet est confirmé Aggregate Root.

---

# 182. Deferred External Ports

```text
CompanyRegistryProvider
SanctionsScreeningProvider
TaxValidationProvider
RiskDataProvider
DocumentStorageProvider
IntegrationEventPublisher
NotificationPort
WorkflowPort
```

---

# 183. Deferred technical concerns

```text
Connection Pool
Database Session
Transaction Manager
Retry Policy
Circuit Breaker
Cache
Message Producer
```

Ces détails appartiennent aux adapters/infrastructure.

---

# 184. Documentation update rule

Si l’implémentation révèle que :

```text
find_current_for_scope(...)
```

est mal défini ou que l’Aggregate boundary change :

1. modifier le modèle ;
2. modifier ce document ;
3. modifier les contract tests ;
4. modifier les adapters.

La spec reste vivante.

---
# 185. Problem Before Pattern — Repository edition

```text
Need aggregate persistence abstraction
    → Repository

Need interchangeable implementations
    → Port + Adapter

Need common implementation behavior
    → Contract Tests

Need atomic transaction across repositories
    → Unit of Work candidate

Need complex read aggregation
    → Query Port / Projection
```

---

# 186. Pedagogical objective

Après ce Core, il doit devenir naturel de reconnaître :

```text
"my use case needs an Aggregate persisted independently"
    → Repository candidate
```

```text
"my application should not depend on PostgreSQL"
    → Port
```

```text
"I need to prove adapters are substitutable"
    → Contract Test
```

```text
"I need deterministic time"
    → Clock Port
```

---

# 187. Final contract summary

## SupplierRepository

```text
get
save
find_by_external_identifier
```

## SupplierRelationshipRepository

```text
get
save
find_for_supplier_and_organization
```

## SupplierQualificationRepository

```text
get
save
find_current_for_scope
```

## SupplierAssessmentRepository

```text
get
save
```

## Clock

```text
now
```

## DomainEventDispatcher

```text
dispatch_all
```

## UnitOfWork

```text
commit
rollback
```

**Candidate, minimal, optional for first bootstrap.**

---

# 188. Final rules

> **Repositories persist Aggregate Roots, not arbitrary classes.**

> **Ports describe Core needs, not infrastructure APIs.**

> **Adapters implement Ports.**

> **Application depends on abstractions.**

> **Repositories do not own business rules.**

> **Repositories do not publish Domain Events.**

> **Query needs must not turn Repositories into God Objects.**

> **InMemory adapters must satisfy the same behavioral contracts as future persistent adapters.**

> **Contract Tests make substitution executable.**

---

# 189. Next mandatory document

Le prochain document du baseline pré-bootstrap est :

> **`11_PYSRMKIT_REPOSITORY_AND_PACKAGE_ARCHITECTURE.md`**

Il devra figer :

```text
repository layout
src layout
test layout
capability boundaries
module naming
dependency directions
public/internal packages
placement of Ports
placement of InMemory adapters
placement of contract tests
```

avant le premier bootstrap.

---

# 190. Conclusion

PySRMKit dispose maintenant des contrats minimaux permettant d’implémenter son Core local sans couplage à une base de données.

La première architecture exécutable est :

```text
Application Handler
        │
        ▼
Repository Port
        ▲
        │
InMemory Repository Adapter
```

avec :

```text
Clock
```

pour le temps déterministe

et :

```text
DomainEventDispatcher
```

pour le dispatch événementiel local.

Cette baseline permet de démontrer concrètement :

```text
DDD Repository
Dependency Inversion
Interface Segregation
Liskov Substitution
Ports & Adapters
Contract Testing
```

avant même d’introduire PostgreSQL.

La philosophie reste :

> **Define the contract from the Core.  
> Implement the technology outside the Core.  
> Prove substitutability with tests.**