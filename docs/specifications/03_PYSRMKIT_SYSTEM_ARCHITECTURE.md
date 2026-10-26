# PySRMKit — System Architecture

**Document :** `03_PYSRMKIT_SYSTEM_ARCHITECTURE.md`  
**Projet :** PySRMKit  
**Domaine :** Supplier Relationship Management  
**Type :** Architecture système et architecture logique  
**Statut :** Draft architectural initial  
**Version du document :** 0.1.0  
**Documents de référence :**
- `00_PYSRMKIT_EXPRESSION_DU_BESOIN.md`
- `01_PYSRMKIT_REQUIREMENTS_ANALYSIS.md`
- `02_PYSRMKIT_PRODUCT_VISION_AND_ARCHITECTURE_PRINCIPLES.md`
- `PYSRMKIT_SOFTWARE_DESIGN_LEARNING_CONVENTION.md`

---

# 1. Objet du document

Ce document définit l'architecture système cible de PySRMKit.

Il transforme les principes définis dans les documents précédents en une organisation logique concrète du framework.

Il répond notamment aux questions suivantes :

> Quelles sont les couches de PySRMKit ?

> Quelles responsabilités appartiennent à chacune ?

> Dans quelle direction les dépendances doivent-elles pointer ?

> Où vivent les règles métier ?

> Où vivent les cas d'utilisation ?

> Comment les systèmes externes sont-ils intégrés ?

> Comment les commandes, requêtes et événements circulent-ils ?

> Comment garder le domaine indépendant de la persistence, du réseau, du cloud, des workflows et des agents ?

> Comment matérialiser ces décisions en Python sans sur-concevoir le framework ?

Le document constitue également le premier artefact PySRMKit appliquant systématiquement la convention :

```text
PROBLEM
→ FORCES
→ DESIGN DECISION
→ DDD CONCEPT
→ PRINCIPLE
→ PATTERN
→ PYTHON MECHANISM
→ TESTING IMPLICATION
```

---

# 2. Position dans la chaîne documentaire

```text
00 — Expression du besoin
        │
        ▼
01 — Requirements Analysis
        │
        ▼
02 — Product Vision & Architecture Principles
        │
        ▼
03 — System Architecture
        │
        ▼
04 — Domain Objects
        │
        ▼
05 — Entities & Value Objects
        │
        ▼
06 — Domain Relationships & ERD
        │
        ▼
07 — Domain Invariants & Business Rules
        │
        ▼
08 — Commands, Queries & Use Cases
        │
        ▼
Detailed implementation specifications
```

Le `03` définit les **frontières structurelles**.

Les documents suivants définiront les **objets métier précis** qui habiteront ces frontières.

---

# 3. Architecture Goals

L'architecture doit satisfaire simultanément plusieurs objectifs.

## AG-001 — Domain Independence

Le Supplier Domain doit rester indépendant de :

- PostgreSQL ;
- SQLAlchemy ;
- MongoDB ;
- FastAPI ;
- Django ;
- Kafka ;
- RabbitMQ ;
- AWS ;
- Azure ;
- Ivalua ;
- SAP ;
- Coupa ;
- Ariba ;
- tout moteur d'agents ou LLM.

---

## AG-002 — Explicit Business Model

Les concepts métier doivent apparaître explicitement dans :

- les types ;
- les opérations ;
- les policies ;
- les événements ;
- les tests.

---

## AG-003 — Replaceable Infrastructure

La persistence, la messagerie et les providers externes doivent pouvoir être remplacés sans modifier le cœur métier.

---

## AG-004 — Composable Capabilities

Une application doit pouvoir utiliser :

```text
Supplier Core + Lifecycle
```

sans nécessairement utiliser :

```text
Risk + Performance + Documents + Compliance
```

---

## AG-005 — Testability

Les règles métier doivent pouvoir être testées :

```text
without database
without network
without web server
without message broker
without external provider
```

---

## AG-006 — Auditability

Les décisions critiques doivent pouvoir être reconstruites et expliquées.

---

## AG-007 — Extension without Forking

Les organisations doivent pouvoir adapter :

- qualification ;
- activation ;
- compliance ;
- risk ;
- segmentation ;
- performance ;

sans modifier directement le noyau PySRMKit.

---

## AG-008 — Agent Compatibility

Un agent doit pouvoir utiliser PySRMKit via des cas d'utilisation stables sans devenir propriétaire des règles métier.

---

# 4. Architectural Style

PySRMKit adopte une combinaison pragmatique de plusieurs idées architecturales.

```text
PRIMARY STYLE
    Hexagonal Architecture
    / Ports and Adapters

STRUCTURING PRINCIPLE
    Clean Architecture dependency rule

APPLICATION STYLE
    Command / Query separation
    CQRS-friendly, not CQRS-mandatory

INTEGRATION STYLE
    Domain Events
    Event-Driven friendly

DEPLOYMENT STYLE
    Modular Monolith friendly
    Microservice neutral
```

Aucune de ces étiquettes ne doit être interprétée comme une obligation d'utiliser toutes les techniques associées.

---

# 5. Design Concepts Applied

## Domain / DDD

- Bounded Context
- Aggregate
- Value Object
- Domain Service
- Domain Policy
- Repository
- Domain Event
- Anti-Corruption Layer

## Principles

- Single Responsibility Principle
- Open/Closed Principle
- Interface Segregation Principle
- Dependency Inversion Principle
- Separation of Concerns
- Information Hiding
- High Cohesion
- Low Coupling
- KISS
- YAGNI

## Design Patterns

- Strategy — pour les policies réellement variables
- Adapter — pour les intégrations externes
- Factory — uniquement si la création devient suffisamment complexe
- Repository — au sens DDD
- State — uniquement si le GoF State Pattern devient réellement nécessaire

## Architectural Patterns

- Hexagonal Architecture
- Ports and Adapters
- Layered Architecture
- Clean Architecture dependency direction
- CQRS-friendly organization
- Event-Driven integration
- Modular Monolith

## Python Mechanisms

- `Protocol`
- dataclasses / immutable data structures
- `Enum`
- exceptions typées
- dependency injection explicite
- composition
- typing

---

# 6. Why Hexagonal Architecture?

## Problem

PySRMKit doit être utilisable avec plusieurs technologies externes.

Exemples :

```text
Persistence:
    InMemory
    PostgreSQL
    MongoDB
    Snowflake

Supplier Platforms:
    Ivalua
    SAP
    Coupa
    Ariba

Events:
    In-process
    Kafka
    RabbitMQ
    SNS

Documents:
    Local
    S3
    Azure Blob
    DMS
```

Si le cœur métier dépend directement de ces technologies, le framework devient :

- difficile à tester ;
- difficile à réutiliser ;
- difficile à migrer ;
- difficile à comprendre.

## Decision

Placer le domaine et les cas d'utilisation au centre.

Les technologies externes se connectent au système via des **ports** et des **adapters**.

```text
             External World

      ┌───────────┬───────────┐
      │           │           │
      ▼           ▼           ▼
   API/UI       Agents       Jobs
      │           │           │
      └──────┬────┴────┬──────┘
             │
        Primary Adapters
             │
             ▼
      ┌─────────────────┐
      │ Application     │
      │ Use Cases       │
      └────────┬────────┘
               │
               ▼
      ┌─────────────────┐
      │ Domain          │
      │ Business Truth  │
      └────────┬────────┘
               │
         Output Ports
               │
      ┌────────┴─────────┐
      ▼                  ▼
Persistence          External APIs
Adapters             Adapters
```

## Concepts

```text
[ARCH: Hexagonal Architecture]
[ARCH: Ports and Adapters]
[PRINCIPLE: Dependency Inversion]
[PRINCIPLE: Separation of Concerns]
[PATTERN: Adapter]
```

---

# 7. Clean Architecture Influence

PySRMKit ne cherche pas à reproduire mécaniquement tous les anneaux d'une Clean Architecture.

Le principe retenu est surtout la **Dependency Rule** :

> Les dépendances de code doivent pointer vers les abstractions les plus stables et les plus proches du métier.

Version simplifiée :

```text
Interfaces
    │
    ▼
Application
    │
    ▼
Domain
```

L'infrastructure dépend des contrats internes :

```text
Infrastructure
    │
    ▼
Ports
```

Le domaine ne dépend jamais de l'infrastructure.

---

# 8. Architecture globale

```text
┌─────────────────────────────────────────────────────────────────┐
│                          CONSUMERS                              │
│                                                                 │
│  API │ CLI │ Supplier Portal │ ERP │ Procurement │ Agents      │
│  Jobs │ Workers │ Tests │ Notebooks                            │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INTERFACE / INPUT ADAPTERS                  │
│                                                                 │
│  API controllers │ CLI commands │ Agent tools │ Worker entry   │
│  Serializers │ Request mappers                                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       APPLICATION LAYER                         │
│                                                                 │
│ Commands │ Queries │ Handlers │ Use Cases │ Application DTOs   │
│ Transaction coordination │ Event dispatch coordination          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DOMAIN LAYER                            │
│                                                                 │
│ Supplier │ Relationship │ Lifecycle │ Qualification             │
│ Onboarding │ Documents │ Certification │ Compliance             │
│ Risk │ Assessment │ Performance │ Incident │ Segmentation       │
│                                                                 │
│ Entities │ Value Objects │ Aggregates │ Policies                │
│ Domain Services │ Invariants │ Domain Events                    │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                         defines required ports
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                              PORTS                              │
│                                                                 │
│ Repository │ Unit of Work │ Event Publisher │ Clock             │
│ Company Registry │ Risk Provider │ Document Storage             │
│ Tax Validation │ Sanctions Screening │ ERP / Procurement        │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE / ADAPTERS                    │
│                                                                 │
│ InMemory │ PostgreSQL │ MongoDB │ Ivalua │ SAP │ REST          │
│ Kafka │ RabbitMQ │ S3 │ Azure Blob │ External Compliance APIs  │
└─────────────────────────────────────────────────────────────────┘
```

---

# 9. Core Architectural Rule

La règle la plus importante est :

```text
BUSINESS LOGIC
must not know
INFRASTRUCTURE
```

Concrètement :

```text
pysrmkit.domain
```

ne doit pas importer :

```text
sqlalchemy
django
fastapi
requests
httpx
boto3
azure.*
confluent_kafka
pymongo
```

Le détail exact des dépendances autorisées pourra être protégé par des architecture tests.

---

# 10. Logical Layers

L'architecture est découpée en cinq zones logiques principales.

```text
1. Domain
2. Application
3. Ports
4. Adapters
5. Interfaces
```

Cette séparation est logique avant d'être physique.

Le futur package layout pourra matérialiser cette distinction.

---

# 11. Domain Layer

Le Domain Layer contient la vérité métier de PySRMKit.

Il doit être la partie :

- la plus stable ;
- la plus indépendante ;
- la plus testable ;
- la plus riche sémantiquement.

Il contient conceptuellement :

```text
Entities
Value Objects
Aggregates
Domain Policies
Domain Services
Business Rules
Invariants
State Transitions
Domain Events
Domain Errors
```

Il ne contient pas :

```text
HTTP
SQL
ORM
Kafka
Cloud SDK
UI
Serialization transport-specific
Agent logic
```

---

# 12. Domain Layer — Candidate Structure

Structure conceptuelle initiale :

```text
domain/
│
├── supplier/
│   ├── entities
│   ├── value_objects
│   ├── events
│   ├── policies
│   └── errors
│
├── relationship/
│
├── lifecycle/
│
├── onboarding/
│
├── qualification/
│
├── documents/
│
├── certification/
│
├── compliance/
│
├── risk/
│
├── assessment/
│
├── performance/
│
├── incident/
│
└── segmentation/
```

Cette topologie n'est pas encore définitive.

Elle exprime surtout des **boundaries fonctionnelles candidates**.

---

# 13. Domain Entities

Les Entities représentent les concepts qui possèdent une identité durable.

Candidats probables :

```text
Supplier
SupplierRelationship
Qualification
Assessment
RiskAssessment
Incident
```

La liste définitive sera établie dans :

```text
05_PYSRMKIT_ENTITIES_AND_VALUE_OBJECTS.md
```

## Design Concepts Applied

```text
[DDD: Entity]
[PRINCIPLE: Encapsulation]
[PRINCIPLE: Information Hiding]
```

---

# 14. Value Objects

Les Value Objects représentent des concepts définis par leur valeur plutôt que par une identité propre.

Candidats :

```text
SupplierId
ExternalIdentifier
Address
CountryCode
EmailAddress
QualificationScope
RiskScore
Percentage
DateRange
DocumentReference
```

Propriétés recherchées :

- validation à la construction ;
- immutabilité lorsque pertinente ;
- égalité par valeur ;
- vocabulaire métier explicite.

## Python

Mécanisme candidat :

```python
@dataclass(frozen=True)
class QualificationScope:
    organization_id: OrganizationId
    category_code: CategoryCode
```

La forme définitive reste à concevoir.

---

# 15. Aggregates

Les Aggregates devront être définis en fonction des invariants transactionnels.

La question n'est pas :

> Quels objets apparaissent ensemble sur un écran ?

La question est :

> Quels objets doivent rester cohérents ensemble lorsqu'une décision métier est appliquée ?

Candidats à étudier :

```text
Supplier Aggregate
SupplierRelationship Aggregate
Qualification Aggregate
Assessment Aggregate
RiskAssessment Aggregate
```

Le `Supplier` ne doit pas devenir automatiquement un **God Aggregate** contenant toute l'histoire fournisseur.

---

# 16. Aggregate Root Principle

Une mutation métier significative doit passer par l'Aggregate Root responsable de l'invariant.

Exemple conceptuel :

```text
Application
    │
    ▼
Supplier Aggregate Root
    │
    ├── validates transition
    ├── changes state
    └── records Domain Event
```

L'application ne doit pas modifier directement les structures internes d'un aggregate.

---

# 17. Domain Policies

Une Policy représente une règle métier variable selon le contexte ou l'organisation.

Exemples :

```text
QualificationPolicy
ActivationPolicy
CompliancePolicy
RiskPolicy
SegmentationPolicy
PerformancePolicy
DocumentRequirementPolicy
```

## Problem

Les règles varient, mais les use cases ne doivent pas dépendre de chaque implémentation concrète.

## Design Decision

Définir un contrat stable et injecter l'implémentation appropriée.

## Concepts

```text
[DDD: Domain Policy]
[PATTERN: Strategy]
[PRINCIPLE: Open/Closed Principle]
[PRINCIPLE: Dependency Inversion Principle]
[PYTHON: Protocol]
```

---

# 18. Policy Example

```python
class QualificationPolicy(Protocol):
    def evaluate(
        self,
        supplier: Supplier,
        scope: QualificationScope,
    ) -> QualificationDecision:
        ...
```

Implémentations possibles :

```text
DefaultQualificationPolicy
CybersecurityQualificationPolicy
ConstructionQualificationPolicy
OrganizationSpecificQualificationPolicy
```

Le nom métier `QualificationPolicy` est préféré à `QualificationStrategy`.

---

# 19. Domain Services

Un Domain Service doit être utilisé lorsque :

- la logique est métier ;
- elle ne relève naturellement d'aucune Entity ou Value Object ;
- elle implique plusieurs concepts du domaine.

Exemple candidat :

```text
SupplierEligibilityService
```

uniquement si la décision implique réellement plusieurs aggregates ou policies.

À éviter :

```text
SupplierService
```

comme conteneur générique de toute la logique du projet.

---

# 20. Domain Events

Un Domain Event représente un fait métier significatif déjà survenu.

Exemples :

```text
SupplierCreated
SupplierInvited
SupplierOnboardingStarted
SupplierQualified
SupplierActivated
SupplierSuspended
SupplierBlocked
SupplierReactivated
SupplierRiskChanged
SupplierAssessmentCompleted
SupplierIncidentReported
SupplierOffboarded
```

## Rule

Un événement ne doit être produit que si l'opération métier correspondante a réellement réussi.

---

# 21. Domain Event Is Not Observer

Important :

```text
Domain Event
≠
GoF Observer Pattern
```

Le Domain Event exprime un fait métier.

Le mécanisme utilisé pour distribuer ce fait peut éventuellement employer :

- Observer ;
- Event Dispatcher ;
- Message Bus ;
- broker externe.

La sémantique métier ne dépend pas de ce mécanisme.

---

# 22. Domain Errors

Les erreurs métier doivent être typées et séparées des erreurs techniques.

Exemples :

```text
InvalidLifecycleTransition
QualificationScopeRequired
SupplierAlreadyOffboarded
ActivationRequirementsNotMet
ExpiredDocumentCannotBeAccepted
InvalidCertificationPeriod
```

À distinguer de :

```text
DatabaseUnavailable
ProviderTimeout
SerializationFailure
NetworkError
```

---

# 23. Application Layer

L'Application Layer orchestre les cas d'utilisation.

Il ne définit pas la vérité métier.

Il coordonne :

```text
load
→ call domain
→ persist
→ publish
→ return
```

Exemple :

```text
ActivateSupplierHandler
    │
    ├── load Supplier
    ├── invoke activation business operation
    ├── save Supplier
    ├── commit transaction
    └── dispatch resulting events
```

---

# 24. Application Layer Responsibilities

L'Application Layer peut prendre en charge :

- command handling ;
- query handling ;
- transaction boundary ;
- repository coordination ;
- calls to external ports ;
- authorization context propagation ;
- correlation metadata ;
- event dispatch coordination ;
- DTO mapping ;
- idempotency coordination lorsque nécessaire.

Il ne doit pas :

- réimplémenter les invariants du domaine ;
- devenir une collection de règles métier procédurales.

---

# 25. Commands

Une Command représente une intention de modifier l'état du système.

Exemples :

```text
RegisterSupplier
InviteSupplier
StartSupplierOnboarding
RequestSupplierQualification
ApproveSupplierQualification
ActivateSupplier
SuspendSupplier
ReactivateSupplier
OffboardSupplier
ReportSupplierIncident
```

Une Command devrait être :

- explicite ;
- typée ;
- immutable autant que possible ;
- centrée sur une intention.

---

# 26. CQRS Command vs GoF Command

Important :

```text
CQRS Command
≠
GoF Command Pattern
```

Dans PySRMKit, le terme `Command` sera d'abord utilisé au sens :

```text
message representing intent to change state
```

Cela ne signifie pas automatiquement que le GoF Command Pattern est implémenté.

---

# 27. Command Handler

Un Handler prend en charge un cas d'utilisation applicatif.

Exemple conceptuel :

```python
class ActivateSupplierHandler:
    def __init__(
        self,
        repository: SupplierRepository,
        uow: UnitOfWork,
        policy: ActivationPolicy,
    ) -> None:
        ...
    def handle(self, command: ActivateSupplier) -> None:
        ...
```

Cette forme reste illustrative.

Les signatures finales seront définies dans le document dédié aux Commands et Use Cases.

---

# 28. Queries

Une Query représente une intention de lecture.

Exemples :

```text
GetSupplier
FindSupplierByExternalIdentifier
ListQualifiedSuppliers
ListExpiringDocuments
GetSupplierRiskProfile
GetSupplierScorecard
```

Une Query ne doit pas changer l'état métier.

---

# 29. CQRS-Friendly, Not CQRS-Mandatory

PySRMKit distingue conceptuellement :

```text
Commands
    mutate

Queries
    read
```

mais ne rend pas obligatoire :

- une base de lecture séparée ;
- deux services déployés séparément ;
- deux bases différentes ;
- un bus distribué ;
- de l'event sourcing.

Le framework est :

> **CQRS-friendly, not full-CQRS by default.**

---

# 30. Query Models

Certaines lectures pourront utiliser directement des projections.

Exemple :

```text
SupplierListItem
SupplierRiskSummary
SupplierQualificationView
SupplierScorecardView
```

Ces read models peuvent être différents des Aggregates.

Principe :

> On ne doit pas charger un Aggregate complet uniquement pour afficher une liste.

---

# 31. Ports

Un Port exprime un besoin de l'intérieur du système vers l'extérieur.

Exemples :

```text
SupplierRepository
SupplierRelationshipRepository
UnitOfWork
EventPublisher
Clock
CompanyRegistryProvider
TaxValidationProvider
SanctionsScreeningProvider
RiskDataProvider
DocumentStorageProvider
ERPProvider
ProcurementProvider
```

Un Port est défini par le besoin métier ou applicatif.

---

# 32. Port Design Principle

Un Port ne doit pas exposer les détails d'une technologie externe.

Mauvais :

```python
class SupplierRepository:
    def execute_sql(self, query: str): ...
```

Meilleur :

```python
class SupplierRepository(Protocol):
    def get(self, supplier_id: SupplierId) -> Supplier | None:
        ...

    def save(self, supplier: Supplier) -> None:
        ...
```

---

# 33. Interface Segregation for Ports

Les ports doivent rester spécialisés.

Préférer :

```text
SupplierRepository
RiskDataProvider
DocumentStorageProvider
```

à :

```text
ExternalSystemsManager
```

contenant des dizaines d'opérations non liées.

## Concepts

```text
[PRINCIPLE: Interface Segregation Principle]
[PRINCIPLE: High Cohesion]
```

---

# 34. Repository Port

Le Repository abstrait la persistence d'un Aggregate.

Il ne doit pas être conçu comme un ORM générique.

Exemple conceptuel :

```python
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

---

# 35. Repository Is Not Generic DAO

Important :

```text
DDD Repository
≠
Generic DAO
```

Le Repository parle le langage du domaine.

Il masque la technologie de persistence.

Il ne doit pas exposer par défaut :

```text
raw SQL
table names
ORM sessions
database-specific query objects
```

---

# 36. Unit of Work

Un `UnitOfWork` est un candidat architectural lorsque plusieurs opérations doivent être regroupées dans une même transaction applicative.

Responsabilités possibles :

```text
begin
commit
rollback
repository access
event collection coordination
```

Mais :

> PySRMKit ne doit pas introduire un Unit of Work abstrait uniquement par tradition.

Son introduction devra être justifiée par les besoins transactionnels réels.

---

# 37. Clock Port

Le domaine contient plusieurs règles temporelles :

- expiration de document ;
- expiration de certification ;
- qualification ;
- review date ;
- risk assessment age.

Un `Clock` explicite peut éviter de dépendre implicitement de :

```python
datetime.now()
```

Exemple conceptuel :

```python
class Clock(Protocol):
    def now(self) -> datetime:
        ...
```

## Concepts

```text
[PRINCIPLE: Explicit Dependencies]
[PRINCIPLE: Deterministic Testing]
[PYTHON: Protocol]
```

---

# 38. Adapters

Les Adapters traduisent entre PySRMKit et le monde extérieur.

Deux grandes catégories :

```text
Primary / Driving Adapters
Secondary / Driven Adapters
```

---

# 39. Primary Adapters

Les Primary Adapters déclenchent les cas d'utilisation.

Exemples :

```text
FastAPI endpoint
Django view
CLI command
Worker entrypoint
Agent tool
Notebook facade
```

Ils transforment une entrée externe en :

```text
Command
or
Query
```

---

# 40. Secondary Adapters

Les Secondary Adapters implémentent les ports utilisés par l'application.

Exemples :

```text
PostgreSQLSupplierRepository
MongoSupplierRepository
IvaluaSupplierAdapter
SapSupplierAdapter
KafkaEventPublisher
S3DocumentStorageAdapter
ExternalRiskProviderAdapter
```

---

# 41. Adapter Pattern

## Problem

Les interfaces externes ne correspondent pas au modèle interne.

## Decision

Créer un composant qui traduit explicitement les deux modèles.

## Concepts

```text
[PATTERN: Adapter]
[DDD: Anti-Corruption Layer]
[PRINCIPLE: Information Hiding]
[PRINCIPLE: Dependency Inversion]
```

---

# 42. Anti-Corruption Layer

Exemple Ivalua :

```text
IVALUA API
    │
    ▼
Ivalua DTO
    │
    ▼
Ivalua Mapper / Adapter
    │
    ▼
PySRMKit Canonical Model
```

Le JSON Ivalua ne doit pas devenir le modèle canonique PySRMKit.

Même principe pour :

```text
SAP
Coupa
Ariba
Company registries
Risk providers
Compliance providers
```

---

# 43. Mapping Boundary

Le mapping est une frontière explicite.

Les transformations peuvent distinguer :

```text
External DTO
Application DTO
Domain Object
Persistence Model
Integration Event
```

Ces représentations peuvent partager certaines données sans être le même objet conceptuel.

---

# 44. Persistence Architecture

La persistence doit rester un détail d'infrastructure.

Architecture :

```text
Domain Aggregate
      │
      ▼
Repository Port
      ▲
      │
Persistence Adapter
      │
      ▼
Database
```

Backends possibles :

```text
InMemory
SQLite
PostgreSQL
MySQL
MongoDB
DynamoDB
Snowflake
```

---

# 45. ORM Boundary

Si SQLAlchemy est utilisé ultérieurement :

```text
SQLAlchemy Model
≠
Domain Entity
```

Deux approches resteront possibles :

```text
Data Mapper
or
carefully isolated mapping layer
```

Le choix sera documenté dans une stratégie de persistence dédiée.

---

# 46. In-Memory Adapter

Un adapter InMemory est particulièrement utile pour :

- tests ;
- exemples ;
- notebooks ;
- prototypage ;
- reference implementation.

Exemple :

```text
InMemorySupplierRepository
```

Il doit respecter le même contract test que les adapters persistants.

---

# 47. Contract Testing

Chaque implémentation importante d'un Port pourra être testée avec une suite de contrat partagée.

Exemple :

```text
SupplierRepositoryContractTests
        │
        ├── InMemorySupplierRepository
        ├── PostgreSQLSupplierRepository
        └── MongoSupplierRepository
```

## Concepts

```text
[TEST: Contract Test]
[PRINCIPLE: Liskov Substitution Principle]
```

---

# 48. Event Architecture

PySRMKit distingue plusieurs niveaux.

```text
Domain Event
    │
    ▼
Application Event Handling
    │
    ▼
Integration Event
    │
    ▼
Transport
```

---

# 49. Domain Event

Exemple :

```text
SupplierActivated
```

Il appartient au langage interne du domaine.

---

# 50. Integration Event

Une application peut décider de transformer :

```text
SupplierActivated
```

en :

```text
supplier.lifecycle.activated.v1
```

destiné à des consommateurs externes.

Le contrat d'intégration doit pouvoir évoluer indépendamment du modèle interne.

---

# 51. Event Transport

Le transport est une décision d'infrastructure.

Exemples :

```text
In-process dispatcher
Kafka
RabbitMQ
SNS/SQS
Azure Service Bus
Webhook
```

PySRMKit ne dépend d'aucun de ces choix.

---

# 52. Event-Driven Friendly

PySRMKit doit permettre une architecture Event-Driven.

Il ne doit pas imposer une infrastructure Event-Driven.

La différence est importante :

```text
Domain Events
    required conceptually

External broker
    optional infrastructure
```

---

# 53. Event Sourcing Is Optional

PySRMKit ne suppose pas que l'état courant soit reconstruit à partir de tous les événements.

```text
Domain Events
≠
Event Sourcing
```

Event Sourcing pourra être étudié ultérieurement si un besoin réel le justifie.

---

# 54. Event Publication Timing

La publication externe doit idéalement intervenir après confirmation de la transaction de persistence.

Problème classique :

```text
DB commit succeeds
event publication fails
```

ou inversement.

Une application de production pourra nécessiter :

```text
Transactional Outbox
```

Mais ce pattern ne doit pas être introduit dans le core avant que la persistence distribuée le justifie.

---

# 55. Transaction Boundaries

Les frontières transactionnelles appartiennent principalement à l'Application Layer.

Exemple :

```text
Handle command
    │
    ├── load aggregate
    ├── execute domain operation
    ├── persist
    ├── commit
    └── schedule/publish events
```

Le Domain Layer ne connaît pas le mécanisme de transaction.

---

# 56. End-to-End Flow — Activate Supplier

```text
External Caller
    │
    ▼
Primary Adapter
    │
    ▼
ActivateSupplier Command
    │
    ▼
ActivateSupplierHandler
    │
    ├── SupplierRepository.get()
    │
    ▼
Supplier Aggregate
    │
    ├── check lifecycle
    ├── evaluate ActivationPolicy
    ├── enforce invariants
    ├── transition to ACTIVE
    └── record SupplierActivated
    │
    ▼
SupplierRepository.save()
    │
    ▼
UnitOfWork.commit()
    │
    ▼
Event Dispatcher
```

---

# 57. Design Concepts — Activate Supplier Flow

```text
[DDD: Aggregate]
[DDD: Domain Policy]
[DDD: Domain Event]
[PATTERN: Repository]
[PATTERN: Strategy]
[ARCH: Application Layer]
[ARCH: Ports and Adapters]
[PRINCIPLE: Dependency Inversion]
[PRINCIPLE: Encapsulation]
```

---

# 58. End-to-End Flow — Qualification

```text
RequestSupplierQualification
        │
        ▼
Application Handler
        │
        ▼
Load Supplier / Relationship context
        │
        ▼
QualificationPolicy
        │
        ▼
QualificationDecision
        │
        ├── approved
        └── rejected
        │
        ▼
Domain transition
        │
        ▼
SupplierQualified / QualificationRejected
```

La policy varie sans modifier le handler.

---

# 59. End-to-End Flow — External Compliance Check

```text
Application Use Case
       │
       ├── load Supplier context
       │
       ├── call SanctionsScreeningPort
       │          │
       │          ▼
       │    External Provider Adapter
       │          │
       │          ▼
       │    External Compliance API
       │
       ├── map result
       │
       ▼
Domain Compliance Decision
       │
       ▼
Persist state / event
```

La réponse du provider ne doit pas muter directement le domaine.

---

# 60. External Data Is Evidence, Not Business Truth

Un provider externe peut renvoyer :

```text
risk_score = 87
```

mais le domaine décide ce que ce score signifie.

Exemple :

```text
External Risk Data
        │
        ▼
RiskPolicy
        │
        ▼
Domain Risk Decision
```

Ainsi :

```text
provider data
≠
domain decision
```

---

# 61. Workflow Architecture

PySRMKit définit les règles métier.

Un moteur de workflow orchestre les étapes.

```text
PySRMKit
    says:
        qualification can be approved

PyWorkflowKit
    says:
        Compliance reviews first
        Procurement reviews second
        Finance reviews above threshold
```

---

# 62. Domain State vs Workflow State

Ces concepts ne doivent pas être confondus.

```text
Workflow State:
    WAITING_FOR_LEGAL_APPROVAL

Domain State:
    UNDER_REVIEW
```

Le workflow peut changer sans modifier le modèle métier.

---

# 63. Lifecycle State Machine

Le lifecycle est représenté comme une machine à états métier.

```text
DISCOVERED
PROSPECTIVE
INVITED
ONBOARDING
UNDER_REVIEW
QUALIFIED
ACTIVE
SUSPENDED
BLOCKED
INACTIVE
OFFBOARDED
```

Chaque transition possède potentiellement :

```text
source
target
guard
reason
event
```

---

# 64. State Machine vs State Pattern

Important :

```text
State Machine
≠
GoF State Pattern
```

La première version peut parfaitement utiliser :

```text
Enum + transition rules
```

sans créer une classe par état.

Le GoF State Pattern ne sera introduit que si le comportement par état devient suffisamment complexe pour le justifier.

## KISS / YAGNI

```text
Do not introduce State classes prematurely.
```

---

# 65. Factory Architecture

La création simple doit rester simple.

Exemple initial possible :

```python
Supplier.create(...)
```

ou constructeur contrôlé.

Une `SupplierFactory` ne sera introduite que si la construction nécessite réellement :

- plusieurs sources ;
- plusieurs policies ;
- plusieurs objets dépendants ;
- orchestration complexe ;
- invariants de construction non triviaux.

---

# 66. Factory Pattern — Evidence Required

Avant de créer une Factory, la documentation doit pouvoir répondre :

```text
Why is construction complex?
Why can't a constructor/factory method remain sufficient?
What creation variants exist?
```

Sinon :

```text
YAGNI
```

s'applique.

---

# 67. Interface Layer

L'Interface Layer connecte les consommateurs aux cas d'utilisation.

Possibles interfaces :

```text
Python Facade
CLI
REST API
GraphQL
Worker
Agent Tool
Notebook API
```

PySRMKit Core ne doit imposer aucune de ces interfaces.

---

# 68. Python-Native API

Le premier consumer du framework est Python lui-même.

Une API Python claire doit donc être possible sans serveur :

```python
service.register_supplier(...)
service.qualify_supplier(...)
```

ou :

```python
handler.handle(command)
```

selon l'API stabilisée.

---

# 69. REST Adapter

Une future intégration FastAPI pourra ressembler conceptuellement à :

```text
HTTP Request
    │
    ▼
Pydantic Request Model
    │
    ▼
Command
    │
    ▼
Application Handler
    │
    ▼
Domain
```

Le domaine ne reçoit pas directement le modèle HTTP.

---

# 70. Agent Adapter

Un agent est un Primary Adapter potentiel.

```text
Agent
   │
   ▼
Tool / Adapter
   │
   ▼
Command / Query
   │
   ▼
Application
   │
   ▼
Domain
```

L'agent ne reçoit pas un accès direct à :

```text
repository.save()supplier.status = ...
database session
```

---

# 71. Agentic Safety Boundary

L'agent peut :

- proposer ;
- expliquer ;
- rechercher ;
- comparer ;
- déclencher une commande autorisée.

Le domaine :

- valide ;
- refuse ;
- protège les invariants ;
- produit la décision finale.

```text
Agent reasoning
    ≠
Business invariant
```

---

# 72. Explainable Decisions

Les opérations critiques devraient pouvoir produire des résultats structurés.

Exemple conceptuel :

```text
ActivationDecision
├── allowed
├── reasons
├── failed_rules
└── evidence_refs
```

Cela facilite :

- UI ;
- API ;
- audit ;
- agents ;
- tests.

---

# 73. Authorization Boundary

PySRMKit n'est pas un moteur IAM.

Séparation :

```text
IAM / Application
    "Can actor X request this operation?"

Domain
    "Is this business transition valid?"
```

Une commande peut transporter :

```text
actor_id
reason
correlation_id
```

sans que le domaine implémente OAuth ou RBAC.

---

# 74. Sensitive Data Boundary

Certaines données fournisseur peuvent être sensibles.

Exemples :

- coordonnées personnelles ;
- données bancaires de référence ;
- documents ;
- fiscalité ;
- compliance findings.

Les événements et logs ne doivent pas exposer automatiquement l'ensemble du state.

Principe :

```text
minimum necessary data
```

---

# 75. Logging

Le logging est une préoccupation technique.

Un log :

```text
Supplier activated
```

ne remplace pas :

```text
SupplierActivated Domain Event
Audit Record
Lifecycle History
```

---

# 76. Observability

Les adapters et l'Application Layer peuvent être instrumentés avec :

- logs ;
- metrics ;
- traces.

Le Domain Layer ne doit pas dépendre directement de :

```text
OpenTelemetry
Datadog
Prometheus
Sentry
```

---

# 77. Correlation

Les cas d'utilisation distribués peuvent propager :

```text
correlation_id
causation_id
request_id
actor_id
```

Ces métadonnées appartiennent principalement à l'enveloppe applicative ou événementielle.

---

# 78. Configuration

La configuration doit servir :

- choix d'adapter ;
- mappings ;
- seuils de policy ;
- paramètres opérationnels.

Elle ne doit pas devenir un langage caché remplaçant le modèle métier.

---

# 79. Dependency Injection

La Dependency Injection peut être utilisée pour fournir :

```text
repository
policy
clock
provider
publisher
```

Mais :

```text
Dependency Injection
≠
Dependency Inversion Principle
```

DI est un mécanisme.

DIP est un principe de dépendance.

---

# 80. Composition Root

L'assemblage des implémentations concrètes doit se faire à l'extérieur du domaine.

Exemple :

```text
Application startup
    │
    ├── PostgreSQLSupplierRepository
    ├── DefaultQualificationPolicy
    ├── SystemClock
    ├── KafkaEventPublisher
    └── ActivateSupplierHandler
```

Cette zone peut être appelée :

```text
Composition Root
```

---

# 81. No Service Locator

Les dépendances doivent être explicites.

À éviter :

```python
repository = GlobalContainer.resolve("supplier_repository")
```

au cœur du domaine.

Préférer l'injection explicite.

---

# 82. Concurrency

Les problèmes de concurrence seront principalement pertinents au niveau persistence/application.

Exemples :

```text
two users update supplier simultaneously
duplicate activation commands
concurrent qualification reviews
```

Mécanismes possibles :

```text
optimistic locking
version field
idempotency key
transaction isolation
```

Ces choix ne doivent pas contaminer le modèle métier plus que nécessaire.

---

# 83. Optimistic Concurrency Candidate

Un aggregate persistant pourra éventuellement posséder une version technique :

```text
version
```

mais cette version doit rester clairement distincte :

- du lifecycle ;
- des business revisions ;
- de l'identité métier.

---

# 84. Idempotency

Certains commands externes peuvent être rejoués.

Exemple :

```text
ActivateSupplier
```

envoyé deux fois.

La stratégie peut combiner :

- domain-level semantic idempotency ;
- application idempotency keys ;
- infrastructure deduplication.

Le choix dépendra du use case.

---

# 85. Serialization

Le domaine ne doit pas devenir dépendant de JSON.

Flux :

```text
Domain Object
    │
    ▼
Mapper
    │
    ▼
Serializable DTO
    │
    ▼
JSON / Message / API
```

---

# 86. DTOs

Les DTOs peuvent exister à plusieurs frontières.

```text
API DTO
Application DTO
Integration DTO
Persistence DTO
```

Un DTO est une représentation de transport.

Il n'est pas automatiquement :

```text
Entity
Value Object
Aggregate
```

---

# 87. Read Model Architecture

Les read models pourront être optimisés séparément.

Exemple :

```text
SupplierSearchProjection
SupplierQualificationProjection
SupplierRiskProjection
```

Ils peuvent être construits :

- directement depuis la persistence ;
- depuis les domain events ;
- via un index de recherche.

Aucune stratégie n'est imposée à ce stade.

---

# 88. Modular Monolith Friendly

PySRMKit doit pouvoir vivre dans une application modulaire :

```text
enterprise_app/
│
├── customer/
├── supplier/
├── procurement/
├── contracts/
└── accounting/
```

sans nécessiter de microservices.

---

# 89. Microservice Neutral

PySRMKit peut aussi être utilisé derrière :

```text
Supplier Service
```

mais le framework ne suppose pas :

- réseau ;
- API ;
- service discovery ;
- container ;
- orchestration Kubernetes.

---

# 90. Bounded Context Integration

Le Supplier Domain interagit avec d'autres contexts.

```text
Customer Context
Supplier Context
Procurement Context
Contract Context
Accounting Context
IAM Context
Workflow Context
```

Chaque intégration doit préserver la frontière du modèle.

---

# 91. PyProcurementKit Integration

```text
PySRMKit
    determines supplier eligibility

PyProcurementKit
    performs sourcing and purchasing
```

Flux possible :

```text
SupplierQualified
       │
       ▼
Procurement projection / eligibility cache
```

ou query directe selon l'architecture de l'application.

---

# 92. PyAccountingKit Integration

```text
SupplierActivated
       │
       ▼
Accounting Application
       │
       ▼
Vendor Account creation
```

Le Supplier n'est pas le Vendor Ledger Account.

---

# 93. PyContractKit Integration

PySRMKit peut référencer :

```text
ContractId
```

sans embarquer :

- clauses ;
- amendments ;
- contract authoring ;
- legal lifecycle détaillé.

---

# 94. PyWorkflowKit Integration

PyWorkflowKit orchestre.

PySRMKit décide la validité métier.

```text
Workflow
    asks to activate

Domain
    accepts or refuses
```

---

# 95. PyRuntimeKit Integration

PyRuntimeKit peut exécuter :

- handlers ;
- jobs ;
- background tasks.

Mais :

```text
PyRuntimeKit executes
PySRMKit decides
```

---

# 96. PyScheduleKit Integration

Exemples de tâches planifiées :

```text
scan expiring documents
review certifications
trigger annual assessments
refresh risk
```

Le scheduling ne fait pas partie du Supplier Domain.

---

# 97. PyAgentsKit Integration

Les agents peuvent utiliser des tools exposant :

```text
GetSupplier
ListExpiringDocuments
RequestQualification
PrepareRiskReview
```

Les tools doivent passer par l'Application Layer.

---

# 98. Proposed Package Topology

Première proposition, non définitive :

```text
src/
└── pysrmkit/
    │
    ├── domain/
    │   ├── supplier/
    │   ├── relationship/
    │   ├── lifecycle/
    │   ├── onboarding/
    │   ├── qualification/
    │   ├── documents/
    │   ├── certification/
    │   ├── compliance/
    │   ├── risk/
    │   ├── assessment/
    │   ├── performance/
    │   ├── incident/
    │   └── segmentation/
    │
    ├── application/
    │   ├── commands/
    │   ├── queries/
    │   ├── handlers/
    │   ├── dto/
    │   └── services/
    │
    ├── ports/
    │   ├── repositories/
    │   ├── providers/
    │   ├── events/
    │   ├── clock/
    │   └── unit_of_work/
    │
    ├── adapters/
    │   ├── persistence/
    │   ├── integrations/
    │   ├── events/
    │   └── documents/
    │
    ├── interfaces/
    │   ├── python/
    │   ├── cli/
    │   └── optional/
    │
    └── _internal/
```

Cette proposition devra être raffinée après la définition des domain objects.

---

# 99. Alternative Package Topology

Une autre organisation possible consiste à structurer verticalement par capability :

```text
pysrmkit/
├── supplier/
│   ├── domain
│   ├── application
│   └── ports
│
├── qualification/
│   ├── domain
│   ├── application
│   └── ports
│
└── risk/
    ├── domain
    ├── application
    └── ports
```

Le choix entre :

```text
layer-first
```

et :

```text
feature-first
```

reste ouvert.

---

# 100. Package Topology Decision Criteria

Le choix devra privilégier :

- cohésion ;
- lisibilité ;
- faibles dépendances ;
- navigation simple ;
- capacité à extraire une capability si nécessaire ;
- absence de cycles.

La structure ne doit pas être choisie uniquement pour ressembler à un diagramme Clean Architecture.

---

# 101. Dependency Matrix

| From | Domain | Application | Ports | Adapters | Interfaces |
|---|---:|---:|---:|---:|---:|
| Domain | Yes | No | Minimal/No | No | No |
| Application | Yes | Yes | Yes | No | No |
| Ports | Domain types if required | No | Yes | No | No |
| Adapters | Yes if mapping needed | Possibly | Yes | Yes | No |
| Interfaces | Application | Yes | No direct infra dependency preferred | Optional composition | Yes |

Cette matrice sera raffinée lorsque la topologie physique sera figée.

---

# 102. Dependency Direction Diagram

```text
                    Interfaces
                        │
                        ▼
                    Application
                    │         │
                    ▼         ▼
                  Domain     Ports
                              ▲
                              │
                           Adapters
```

Point subtil :

Les Ports sont des abstractions définies pour les besoins internes.

Les Adapters dépendent de ces Ports.

---

# 103. Domain-to-Port Dependency

Selon le port concerné, deux stratégies sont possibles.

## Strategy A

Ports applicatifs séparés :

```text
Application → Port
```

Le Domain ne connaît aucun port.

## Strategy B

Certains concepts abstraits purement métier peuvent vivre dans le Domain.

Exemple potentiel :

```text
Clock
```

si réellement nécessaire au calcul métier.

La décision devra favoriser la simplicité et éviter de transformer `domain/` en couche d'abstractions techniques.

---

# 104. Public API Boundary

Tout ce qui existe dans le package ne doit pas être public.

Surface publique recherchée :

```text
small
stable
intentional
documented
typed
```

Les modules internes peuvent évoluer plus rapidement.

---

# 105. Stable vs Experimental API

Pendant les premières versions :

```text
domain concepts
may evolve rapidly
```

Une fois stabilisés :

```text
public imports
commands
events
ports
```

devront suivre une politique de compatibilité explicite.

---

# 106. Internal Modules

Les détails non destinés aux consumers peuvent être placés derrière :

```text
_internal
```

ou simplement non réexportés.

L'objectif est de limiter le couplage accidentel.

---

# 107. Error Boundary

Architecture d'erreurs :

```text
DomainError
├── InvalidLifecycleTransition
├── QualificationError
└── ...

ApplicationError
├── SupplierNotFound
├── Conflict
└── ...

InfrastructureError
├── PersistenceUnavailable
├── ExternalProviderUnavailable
└── ...
```

La taxonomie exacte sera définie ultérieurement.

---

# 108. Error Translation

Les Primary Adapters traduisent les erreurs vers leur protocole.

Exemple HTTP :

```text
SupplierNotFound
    ↓
404
```

Exemple CLI :

```text
SupplierNotFound
    ↓
exit code + human-readable message
```

Le Domain ne connaît pas HTTP 404.

---

# 109. Testing Architecture

La stratégie de test doit suivre les frontières.

```text
Domain Tests
    fastest / purest

Application Tests
    orchestration

Port Contract Tests
    adapter compatibility

Integration Tests
    external technologies

Architecture Tests
    dependency rules

End-to-End Tests
    selected critical paths
```

---

# 110. Domain Unit Tests

Ils testent :

- invariants ;
- transitions ;
- value objects ;
- policies ;
- domain services ;
- domain events.

Ils ne nécessitent aucune infrastructure.

---

# 111. Application Tests

Ils testent :

```text
command → handler → domain → repository port
```

avec adapters InMemory ou fakes.

---

# 112. Contract Tests

Ils garantissent qu'un adapter respecte son Port.

Exemple :

```text
SupplierRepositoryContract
```

---

# 113. Integration Tests

Ils valident :

```text
PostgreSQL mapping
Ivalua API adapter
Kafka publisher
S3 document adapter
```

Ils sont plus lents et plus ciblés.

---

# 114. Architecture Tests

Ils protègent les décisions de ce document.

Exemples :

```text
domain MUST NOT import sqlalchemy
domain MUST NOT import fastapi
domain MUST NOT import boto3
domain MUST NOT import adapters
application MUST NOT import concrete persistence adapters
```

Ces tests rendent l'architecture exécutable.

---

# 115. Architecture Fitness Functions

Candidats :

```text
AF-001
No infrastructure dependency from domain.

AF-002
No adapter dependency from application.

AF-003
Every concrete repository passes repository contract tests.

AF-004
Domain tests run without network.

AF-005
Core package installs without optional infrastructure dependencies.

AF-006
Public API imports remain explicitly controlled.
```

---

# 116. Static Analysis

Outils potentiels, à choisir plus tard :

```text
mypy / pyright
ruff
import-linter
pytest
hypothesis
```

La stratégie outil n'est pas encore figée.

---

# 117. Type System Role

Le typing doit aider à exprimer :

- contracts ;
- Value Objects ;
- command shapes ;
- port interfaces ;
- return decisions.

Le typing ne doit pas devenir une abstraction plus complexe que le domaine.

---

# 118. Protocol vs ABC

`Protocol` est un candidat naturel pour les ports et policies lorsque le structural typing est utile.

`ABC` peut être choisi lorsque :

- un comportement partagé ;
- une hiérarchie nominale ;
- ou un lifecycle explicite

le justifie.

Aucun mécanisme ne doit être utilisé par dogme.

---

# 119. Dataclasses

Les dataclasses sont des candidats naturels pour :

- Commands ;
- Events ;
- Value Objects ;
- DTOs.

Exemple :

```python
@dataclass(frozen=True)
class SupplierActivated:    supplier_id: SupplierId
    occurred_at: datetime
```

La décision finale dépendra des besoins de validation et d'ergonomie.

---

# 120. Pydantic Boundary

Pydantic pourra être utile dans les adapters API.

Mais :

```text
Pydantic model
≠
Domain model
```

Le core ne doit pas être forcé à dépendre de Pydantic pour exister.

---

# 121. Serialization Boundary

Exemple :

```text
FastAPI/Pydantic
      │
      ▼
Application Command
      │
      ▼
Domain
```

et retour :

```text
Domain / Projection
      │
      ▼
Application DTO
      │
      ▼
Pydantic Response
```

---

# 122. Performance Principle

L'architecture doit favoriser la correction et la clarté avant l'optimisation prématurée.

Les optimisations futures pourront concerner :

- read models ;
- caching ;
- batching ;
- event processing ;
- indexes ;
- lazy loading contrôlé.

Le Domain Model ne doit pas être déformé sans mesure réelle.

---

# 123. Caching

Le cache est une préoccupation externe.

Un cache peut entourer :

```text
Query Handler
Repository Adapter
External Provider Adapter
```

mais ne doit pas devenir une source implicite de vérité métier.

---

# 124. Resilience

Les retry, timeout, circuit breaker concernent principalement les appels externes.

Ils appartiennent :

- aux adapters ;
- au runtime ;
- aux application policies techniques.

Ils ne doivent pas être confondus avec les policies métier.

---

# 125. Business Policy vs Technical Policy

Exemple :

```text
QualificationPolicy
    business

RetryPolicy
    technical
```

Les deux peuvent utiliser un pattern Strategy mais n'appartiennent pas au même niveau.

---

# 126. Security Architecture

PySRMKit doit permettre :

- contextual actor ;
- audit metadata ;
- minimisation des données ;
- redaction externe ;
- authorization integration.

Mais il ne devient pas :

```text
IAM
Secrets Manager
OAuth server
```

---

# 127. Audit Architecture

Une décision importante peut produire :

```text
Domain Event
+
Audit metadata
+
History record
```

Le modèle exact d'audit reste à concevoir.

L'audit ne doit pas dépendre uniquement des logs techniques.

---

# 128. History Architecture

Deux stratégies restent possibles :

```text
Current State + explicit history
```

ou :

```text
event-sourced state
```

La première est la candidate par défaut car elle est plus simple.

Event Sourcing exige un besoin spécifique avant adoption.

---

# 129. Multi-Organization Architecture

Les structures qui varient selon l'organisation devront être contextualisées.

Exemples :

```text
SupplierRelationship
QualificationScope
Organization-specific policy
ComplianceRequirement
Segmentation
```

Le Supplier global ne doit pas absorber tout ce qui appartient à une relation locale.

---

# 130. Multi-Country Architecture

Les éléments juridictionnels doivent être extensibles.

Exemple :

```text
ExternalIdentifier
├── type
├── value
└── jurisdiction
```

Pas de dépendance universelle à :

```text
SIREN
SIRET
URSSAF
```

---

# 131. Capability Boundaries

Capabilities principales :

```text
Supplier Core
Organization
Relationship
Lifecycle
Onboarding
Qualification
Documents
Certification
Compliance
Risk
Assessment
Performance
Incident
Segmentation
History
```

Chacune doit viser :

```text
high cohesion
low coupling
```

---

# 132. Capability Dependency Principle

Une capability ne doit pas importer arbitrairement toutes les autres.

Exemple :

```text
Qualification
may depend on
Supplier Identity + Scope

Qualification
should not automatically depend on
Performance + Incident + Documents + Risk
```

Si elle en a besoin, cette dépendance doit être exprimée via :

- policy ;
- decision input ;
- domain service ;
- projection ;

selon le cas.

---

# 133. Avoid Cyclic Dependencies

Les cycles entre capabilities doivent être surveillés.

Exemple problématique :

```text
Risk → Qualification → Compliance → Risk
```

Une solution possible consiste à introduire :

```text
decision inputs
events
application orchestration
```

plutôt qu'un couplage direct.

---

# 134. Domain Event for Cross-Capability Coordination

Exemple :

```text
SupplierIncidentReported
        │
        ▼
Risk recalculation
```

La coordination entre capabilities peut passer par l'Application Layer et les events plutôt que par des appels bidirectionnels directs.

---

# 135. Synchronous vs Asynchronous

Les règles de domaine sont idéalement synchrones et déterministes.

Les interactions externes peuvent être :

```text
sync
or
async
```

La question de l'async ne doit pas contaminer tous les objets du domaine.

---

# 136. Async Ports

Les ports peuvent nécessiter une stratégie future :

```text
SyncSupplierRepository
AsyncSupplierRepository
```

ou API séparée.

Cette décision reste ouverte.

Éviter de mélanger arbitrairement sync et async dans le cœur avant usage réel.

---

# 137. Python Async Principle

`async` est un mécanisme d'I/O et de concurrence.

Il n'est pas un concept métier.

```text
async
belongs mostly near boundaries
```

---

# 138. Dependency Graph — Ideal

```text
                ┌───────────────┐
                │  Interfaces   │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ Application   │
                └───────┬───────┘
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
      ┌───────────────┐     ┌───────────────┐
      │    Domain     │     │     Ports     │
      └───────────────┘     └───────▲───────┘
                                    │
                            ┌───────┴───────┐
                            │   Adapters    │
                            └───────────────┘
```

---

# 139. Design Learning Annotation

Chaque future architecture section importante pourra contenir :

```markdown
## Design Concepts Applied

### Problem
...

### DDD
...

### Principles
...

### Pattern
...

### Python
...

### Testing
...

### Trade-offs
...
```

Cela suit la convention pédagogique du projet.

---

# 140. Example — Repository Learning Annotation

## Problem

Persistence must vary without changing domain behavior.

## DDD

Repository.

## Principles

- Dependency Inversion
- Information Hiding
- Separation of Concerns

## Pattern

Repository.

## Architecture

Port and Adapter.

## Python

Protocol.

## Testing

Contract tests.

## Trade-off

Additional mapping layer and abstraction.

---

# 141. Example — Qualification Policy Learning Annotation

## Problem

Qualification algorithms vary by organization.

## DDD

Domain Policy.

## Principles

- OCP
- DIP
- SRP

## Pattern

Strategy.

## Python

Protocol + composition.

## Testing

Shared behavior tests + implementation-specific policy tests.

## Trade-off

More types and indirection than a simple conditional.

---

# 142. Example — Ivalua Integration Learning Annotation

## Problem

Ivalua's data model must not become PySRMKit's domain model.

## DDD

Anti-Corruption Layer.

## Principles

- Information Hiding
- DIP
- SoC

## Pattern

Adapter.

## Python

Mapper + adapter class/protocol.

## Testing

Mapping tests + integration tests.

## Trade-off

Explicit translation code must be maintained.

---

# 143. Architecture Anti-Patterns

PySRMKit doit éviter les patterns négatifs suivants.

---

# 144. Anti-Pattern — ORM-Driven Domain

```text
Database table
    ↓
ORM model
    ↓
domain concept
```

Le modèle métier ne doit pas être dérivé automatiquement du schéma de base.

---

# 145. Anti-Pattern — God Supplier

Un seul objet Supplier ne doit pas porter :

- toutes les qualifications ;
- tous les incidents ;
- toute la performance ;
- tous les documents ;
- tout l'audit ;
- toutes les relations ;

si cela détruit les frontières transactionnelles.

---

# 146. Anti-Pattern — Generic Service

Éviter :

```text
SupplierService
```

avec 80 méthodes couvrant tout le domaine.

---

# 147. Anti-Pattern — Generic Repository

Éviter un repository universel exposant tout type de requête arbitraire.

---

# 148. Anti-Pattern — Framework Leakage

Éviter dans le domaine :

```text
SQLAlchemy Session
FastAPI Request
Pydantic HTTP model
Kafka Message
AWS object
```

---

# 149. Anti-Pattern — Boolean State Explosion

Éviter :

```text
is_active
is_suspended
is_blocked
is_offboarded
is_onboarding
```

sans modèle d'état cohérent.

---

# 150. Anti-Pattern — Hidden Side Effects

Une méthode métier ne doit pas implicitement :

- écrire en base ;
- envoyer un email ;
- publier Kafka ;
- appeler une API externe.

---

# 151. Anti-Pattern — Pattern-Driven Design

Éviter :

```text
"We need Observer, where can we put it?"
```

Toujours :

```text
Problem before Pattern
```

---

# 152. Anti-Pattern — Premature Distributed Architecture

Ne pas introduire prématurément :

- microservices ;
- distributed sagas ;
- Kafka obligatoire ;
- event sourcing ;
- service mesh.

Le core doit d'abord démontrer son modèle métier.

---

# 153. Anti-Pattern — Agent Bypass

Un agent ne doit pas manipuler directement :

```text
supplier.status
repository
database
```

en dehors des use cases.

---

# 154. Phase 1 Architecture Scope

Supplier Core :

```text
Supplier
Identity
Organization
Contacts
Locations
Categories
Capabilities
Lifecycle
Domain Events
History minimal
Repository Ports
InMemory Adapter
```

Architecture nécessaire :

```text
Domain
Application
Ports
InMemory adapters
Tests
```

Pas besoin initialement de broker ou de base production.

---

# 155. Phase 2 Architecture Scope

Onboarding & Qualification :

```text
Commands
Policies
Assessments
Scoped qualification
Decision objects
```

Patterns particulièrement pertinents :

```text
Strategy
Domain Policy
Application Service
Repository
```

---

# 156. Phase 3 Architecture Scope

Trust & Control :

```text
Documents
Certifications
Compliance
Risk
```

Nouvelles frontières :

```text
DocumentStoragePort
ComplianceProvider
RiskDataProvider
Clock
Evidence references
```

Adapter / ACL devient central.

---

# 157. Phase 4 Architecture Scope

Relationship Intelligence :

```text
Performance
Scorecards
Incidents
Segmentation
Relationships
```

Nouvelles préoccupations :

```text
time-series data
read models
projections
aggregation
query optimization
```

---

# 158. MVP Architecture

Le MVP architectural minimum doit pouvoir démontrer :

```text
Pure Domain
+
Application Use Cases
+
Repository Port
+
InMemory Adapter
+
Domain Events
+
Policy Extension
+
Architecture Tests
```

Si cela fonctionne proprement, la base architecturale est saine.

---

# 159. MVP End-to-End Demonstration

Scénario :

```text
Create Supplier
    │
    ▼
Invite
    │
    ▼
Start Onboarding
    │
    ▼
Request Qualification
    │
    ▼
Apply QualificationPolicy
    │
    ▼
Qualify
    │
    ▼
Activate
    │
    ▼
Inspect Domain Events
```

Tout cela doit pouvoir fonctionner :

```text
without database
without network
without web framework
without message broker
```

---

# 160. Architecture Acceptance Criteria

L'architecture est acceptable si :

1. `domain` peut être importé sans infrastructure ;
2. les règles métier sont testables en mémoire ;
3. les transitions lifecycle sont encapsulées ;
4. les policies sont injectables/remplaçables ;
5. les repositories sont des ports ;
6. les adapters implémentent les ports ;
7. aucune API externe ne fuite directement dans le domain model ;
8. les domain events existent sans message broker ;
9. les Commands et Queries sont distinguables ;
10. les Queries ne nécessitent pas toujours le chargement d'un Aggregate ;
11. les agents passent par l'Application Layer ;
12. les tests d'architecture protègent les dépendances ;
13. les integrations optionnelles ne sont pas des dépendances du core ;
14. les capabilities restent composables ;
15. la structure permet multi-organisation et multi-pays.

---

# 161. Design Quality Criteria

Une nouvelle abstraction doit pouvoir justifier :

```text
What problem?
What variation?
What responsibility?
What coupling does it reduce?
What does it cost?
```

Si ces questions n'ont pas de réponse convaincante, l'abstraction doit être reconsidérée.

---

# 162. Architectural Decision Checklist

Avant d'introduire une nouvelle brique :

```text
[ ] Is this domain or infrastructure?
[ ] Is the responsibility clear?
[ ] Does a simpler solution exist?
[ ] Is there real variation?
[ ] Is an interface actually needed?
[ ] Does the dependency direction remain inward?
[ ] Can this be tested without infrastructure?
[ ] Does the name express domain intent?
[ ] Are we confusing two concepts with similar names?
[ ] Are KISS and YAGNI still respected?
```

---

# 163. Open Question — Aggregate Boundaries

À résoudre dans les prochains documents :

```text
Is Supplier one aggregate root?
Is SupplierRelationship separate?
Is Qualification autonomous?
Where does lifecycle live?
```

---

# 164. Open Question — Layer-first vs Feature-first Packages

À décider après le domain modeling.

---

# 165. Open Question — Sync vs Async Ports

À décider selon les intégrations réelles.

---

# 166. Open Question — Unit of Work

À introduire uniquement si les transactions applicatives le justifient.

---

# 167. Open Question — Event Dispatcher

Première implémentation possible :

```text
simple in-process dispatcher
```

avant tout broker externe.

---

# 168. Open Question — Persistence Mapping

Options futures :

```text
Data Mapper
ORM mapping
explicit persistence model
```

---

# 169. Open Question — Domain History

Choix futur :

```text
audit records
temporal tables
event stream
hybrid
```

---

# 170. Open Question — Public Facade

PySRMKit pourra fournir une façade ergonomique au-dessus des handlers.

Exemple :

```python
srm.activate_supplier(...)
```

mais cette décision doit être compatible avec la transparence des use cases.

---

# 171. Architecture Decision Records

Les décisions structurantes devront progressivement être capturées sous forme d'ADR.

Premiers ADR candidats :

```text
ADR-001 — Adopt Hexagonal Architecture
ADR-002 — Keep Domain Infrastructure-Free
ADR-003 — Use Protocols for Selected Ports
ADR-004 — Commands and Queries Separation
ADR-005 — Domain Events Independent from Transport
ADR-006 — No Mandatory ORM
ADR-007 — No Mandatory Workflow Engine
ADR-008 — Agent Access Through Application Layer
```

---

# 172. Suggested Architecture Documentation Tree

```text
docs/
├── architecture/
│   ├── system/
│   ├── domain/
│   ├── decisions/
│   ├── integration/
│   └── testing/
│
├── domain/
│
├── guides/
│
└── learning/```

Cette organisation reste indicative.

---

# 173. Architecture Learning Map

Le `03` introduit concrètement les concepts suivants :

```text
DOMAIN-DRIVEN DESIGN
├── Bounded Context
├── Entity
├── Value Object
├── Aggregate
├── Domain Service
├── Domain Policy
├── Domain Event
├── Repository
└── Anti-Corruption Layer

PRINCIPLES
├── SRP
├── OCP
├── LSP
├── ISP
├── DIP
├── SoC
├── Information Hiding
├── KISS
└── YAGNI

DESIGN PATTERNS
├── Strategy
├── Adapter
├── Repository
└── Factory [conditional]

ARCHITECTURAL PATTERNS
├── Hexagonal
├── Ports and Adapters
├── Layered
├── Clean dependency rule
├── CQRS-friendly
├── Event-Driven friendly
└── Modular Monolith

PYTHON
├── Protocol
├── dataclass
├── Enum
├── exceptions
├── typing
└── composition

TESTING
├── Domain Unit Tests
├── Contract Tests
├── Integration Tests
└── Architecture Tests
```

---

# 174. From Business to Runtime

La descente d'abstraction de PySRMKit devient :

```text
SUPPLIER BUSINESS PROBLEM
        │
        ▼
DOMAIN MODEL
        │
        ▼
APPLICATION USE CASE
        │
        ▼
PORT
        │
        ▼
ADAPTER
        │
        ▼
PYTHON IMPLEMENTATION
        │
        ▼
RUNTIME
        │
        ▼
DATABASE / NETWORK / OS
```

Le métier reste au sommet de la chaîne de décision.

---

# 175. Example Full Traceability

Prenons :

```text
Supplier Qualification
```

## Business problem

Les critères varient selon le contexte.

## Domain concept

```text
Qualification
QualificationScope
QualificationDecision
```

## DDD

```text
Domain Policy
```

## Principle

```text
OCP
DIP
SRP
```

## Pattern

```text
Strategy
```

## Python

```text
Protocol
```

## Application

```text
RequestQualification
ApproveQualification
```

## Port

```text
SupplierRepository
```

## Adapter

```text
InMemorySupplierRepository
PostgreSQLSupplierRepository
```

## Test

```text
Policy Test
Invariant Test
Repository Contract Test
```

Cette trace est exactement le type de répétition recherché par la convention pédagogique.

---

# 176. Architecture North Star

```text
                        CONSUMERS
                            │
                            ▼
                    INPUT ADAPTERS
                            │
                            ▼
                    APPLICATION LAYER
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
         DOMAIN MODEL                  PORTS
              │                           ▲
              │                           │
              │                     OUTPUT ADAPTERS
              │                           │
              └──────── business ─────────┘
```

Avec une règle :

> **The Supplier Domain owns business truth.**

---

# 177. Architectural Summary

PySRMKit est conçu comme :

```text
A DOMAIN-CENTRIC
HEXAGONAL
COMPOSABLE
CQRS-FRIENDLY
EVENT-DRIVEN-FRIENDLY
TECHNOLOGY-AGNOSTIC
PYTHON FRAMEWORK
```

avec :

```text
Domain
    owns business rules

Application
    orchestrates use cases

Ports
    define external needs

Adapters
    implement technologies

Interfaces
    expose capabilities
```

---

# 178. What This Architecture Does Not Mean

Elle ne signifie pas automatiquement :

```text
microservices
Kafka
event sourcing
separate read database
complex DI container
one class per state
one interface per class
repository for every object
factory for every creation
```

Ces techniques ne seront introduites que lorsqu'un besoin les justifie.

---

# 179. Problem Before Pattern — Architecture Edition

La règle de la convention reste applicable à l'architecture :

```text
Need to isolate infrastructure
    → Ports and Adapters

Need varying qualification logic
    → Strategy candidate

Need to translate Ivalua model
    → Adapter / ACL

Need transaction consistency
    → Aggregate boundary

Need read optimization
    → Projection / CQRS candidate

Need reliable event publication
    → Outbox candidate
```

Le pattern vient **après** la pression de conception.

---

# 180. Next Documents

Le prochain ensemble de documents doit maintenant préciser le modèle interne.

Ordre recommandé :

```text
04_PYSRMKIT_DOMAIN_OBJECTS.md
05_PYSRMKIT_ENTITIES_AND_VALUE_OBJECTS.md
06_PYSRMKIT_DOMAIN_RELATIONSHIPS_AND_ERD.md
07_PYSRMKIT_DOMAIN_INVARIANTS_AND_BUSINESS_RULES.md
08_PYSRMKIT_COMMANDS_QUERIES_AND_USE_CASES.md
```

Le `04` devra identifier les principaux objets métier sans encore surcharger leurs détails d'implémentation.

---

# 181. Conclusion

PySRMKit adopte une architecture centrée sur le domaine fournisseur.

Le framework sépare explicitement :

```text
Business Truth
from
Application Orchestration
from
External Technologies
```

Cette séparation permet :

- de protéger les invariants ;
- de tester le domaine indépendamment ;
- de remplacer l'infrastructure ;
- de réutiliser le framework ;
- de construire plusieurs interfaces ;
- de brancher des systèmes externes ;
- de supporter des agents ;
- de faire évoluer le domaine sans être prisonnier d'une stack.

L'architecture choisie n'est cependant pas un exercice académique.

Elle doit rester soumise aux règles :

> **Problem before Pattern.**

> **Domain before Technology.**

> **Explicit dependencies before hidden magic.**

> **Composition before unnecessary inheritance.**

> **KISS and YAGNI before architectural ceremony.**

Enfin, ce document matérialise l'objectif pédagogique de PySRMKit :

```text
problème réel
→ concept
→ principe
→ pattern
→ Python
→ test
→ répétition
→ intuition
```

L'architecture devient ainsi à la fois :

- une structure de production ;
- une protection du domaine ;
- un vocabulaire partagé ;
- et un support de pratique délibérée de la conception logicielle.