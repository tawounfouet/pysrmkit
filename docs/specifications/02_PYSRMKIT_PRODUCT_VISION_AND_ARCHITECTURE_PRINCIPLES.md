# PySRMKit — Product Vision and Architecture Principles

**Document :** `02_PYSRMKIT_PRODUCT_VISION_AND_ARCHITECTURE_PRINCIPLES.md`  
**Projet :** PySRMKit  
**Domaine :** Supplier Relationship Management  
**Type :** Vision produit et principes d'architecture  
**Statut :** Draft initial  
**Version du document :** 0.1.0  
**Documents de référence :**
- `00_PYSRMKIT_EXPRESSION_DU_BESOIN.md`
- `01_PYSRMKIT_REQUIREMENTS_ANALYSIS.md`

---

# 1. Objet du document

Ce document fixe la **vision produit** de PySRMKit et les **principes d'architecture** qui devront guider sa conception et son évolution.

Il se situe entre :

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
04+ — Domain Model / Detailed Design
```

Le document répond principalement aux questions suivantes :

> Quel produit PySRMKit cherche-t-il à devenir ?

> Quelles responsabilités appartiennent réellement au framework ?

> Quelles responsabilités doivent rester à l'extérieur ?

> Quels principes doivent rester vrais indépendamment des choix techniques futurs ?

> Comment préserver un domaine SRM riche sans construire un monolithe Source-to-Pay ?

> Comment rendre le framework extensible sans perdre ses invariants ?

> Comment permettre l'utilisation depuis des applications classiques, des APIs ou des agents sans coupler le domaine à ces canaux ?

Ce document ne définit pas encore :

- l'arborescence exacte du repository ;
- les classes finales ;
- les signatures finales des APIs ;
- les schémas de persistence ;
- les adapters concrets ;
- le choix exact des bibliothèques ;
- le protocole d'événements ;
- la stratégie de packaging définitive.

---

# 2. Vision produit

PySRMKit a vocation à devenir :

> **un Supplier Domain Engine Python, technology-agnostic, composable et extensible, fournissant les primitives métier nécessaires pour représenter, gouverner et faire évoluer la relation fournisseur.**

Sa vocation n'est pas de reproduire une plateforme SRM existante.

PySRMKit doit constituer une **primitive logicielle métier**.

```text
Applications
    │
    ▼
Supplier Use Cases
    │
    ▼
PySRMKit
    │
    ▼
Supplier Domain Rules
```

Le framework doit pouvoir être utilisé comme noyau métier par :

```text
Supplier Portal
Procurement Platform
ERP
Source-to-Pay Platform
Vendor Management System
Risk Platform
Compliance Platform
Contract Platform
Marketplace B2B
API
Microservice
Batch
CLI
Notebook
Agent
Agentic Enterprise Platform
```

---

# 3. Product statement

## 3.1 Formulation longue

> **PySRMKit is a technology-agnostic Python domain framework for modeling and managing supplier identity, organization, lifecycle, onboarding, qualification, compliance, risk, assessments, performance, incidents and supplier relationships through explicit business rules, policies, domain events and integration ports.**

## 3.2 Formulation courte

> **PySRMKit is the Supplier Domain Engine for Python applications.**

## 3.3 Formulation française

> **PySRMKit est un moteur métier Python du domaine fournisseur, destiné à modéliser et gouverner la relation fournisseur indépendamment des technologies et plateformes utilisées autour de lui.**

---

# 4. Proposition de valeur

La valeur de PySRMKit réside dans cinq propriétés principales.

## 4.1 Canonical Supplier Model

Le framework fournit un modèle métier fournisseur indépendant des systèmes externes.

```text
ERP Vendor
Ivalua Supplier
SAP Vendor
Accounting Vendor Account
Marketplace Seller
External Registry Company
           │
           ▼
      Canonical Model
           │
           ▼
        Supplier
```

Le Supplier Domain ne doit pas être défini par l'identifiant d'un ERP.

---

## 4.2 Explicit Business Rules

Les décisions critiques ne doivent pas être dispersées dans :

- des controllers ;
- des vues Web ;
- des workflows BPM ;
- des scripts ;
- des intégrations ;
- des jobs ;
- des agents ;
- des procédures SQL.

Elles doivent être exprimées dans le domaine.

```text
supplier.activate(...)
supplier.suspend(...)
qualification.approve(...)
document.is_valid(...)
risk_policy.evaluate(...)
```

La syntaxe exacte sera définie ultérieurement.

Le principe est :

> **Business meaning must be visible in the model.**

---

## 4.3 Full Supplier Lifecycle

PySRMKit doit permettre de représenter le fournisseur depuis sa découverte jusqu'à son offboarding.

```text
DISCOVERED
    │
    ▼
PROSPECTIVE
    │
    ▼
INVITED
    │
    ▼
ONBOARDING
    │
    ▼
UNDER_REVIEW
    │
    ▼
QUALIFIED
    │
    ▼
ACTIVE
    │
    ├──► SUSPENDED
    ├──► BLOCKED
    │
    ▼
INACTIVE
    │
    ▼
OFFBOARDED
```

Ce lifecycle doit être **contrôlé par le métier** et non réduit à un champ libre.

---

## 4.4 Composable Supplier Capabilities

Le framework doit permettre d'adopter uniquement les capacités utiles.

```text
Application A
Supplier Master
+ Lifecycle
+ Qualification

Application B
Supplier Master
+ Documents
+ Compliance
+ Risk

Application C
Supplier Master
+ Performance
+ Scorecards

Application D
Full Supplier Domain
```

PySRMKit ne doit pas imposer une plateforme intégrée tout-ou-rien.

---

## 4.5 Integration-Ready Domain

Le framework doit être conçu pour s'intégrer naturellement à d'autres domaines sans les absorber.

```text
PyCRMKit
    │
PySRMKit
    │
PyProcurementKit
    │
PyContractKit
    │
PyAccountingKit
```

L'intégration se fait notamment par :

- domain events ;
- application services ;
- ports ;
- serialized representations ;
- adapters externes.

---

# 5. Principe fondamental : Domain First

Le modèle métier précède les choix technologiques.

La question principale ne doit pas être :

> Comment stocker un Supplier ?

mais :

> Qu'est-ce qu'un Supplier ?

La question ne doit pas être :

> Quelle table pour la qualification ?

mais :

> Que signifie être qualifié dans un contexte donné ?

La question ne doit pas être :

> Quel workflow pour suspendre un fournisseur ?

mais :

> Quelles conditions métier autorisent ou interdisent une suspension ?

Architecture mentale attendue :

```text
Business Concepts
        │
        ▼
Business Rules
        │
        ▼
Application Use Cases
        │
        ▼
Ports
        │
        ▼
Infrastructure
```

et non :

```text
Database Schema
        │
        ▼
ORM Models
        │
        ▼
Business Logic
```

---

# 6. Ubiquitous Language

PySRMKit doit adopter un vocabulaire métier explicite et stable.

Termes centraux :

```text
Supplier
Supplier Identity
Supplier Organization
Supplier Relationship
Supplier Lifecycle
Supplier Onboarding
Supplier Qualification
Supplier Capability
Supplier Document
Supplier Certification
Supplier Compliance
Supplier Risk
Supplier Assessment
Supplier Performance
Supplier Scorecard
Supplier Incident
Supplier Segmentation
Supplier Event
```

Le code, la documentation, les événements et les tests doivent tendre vers le même vocabulaire.

Exemple :

```text
GOOD

SupplierQualified
QualificationScope
SupplierSuspended
DocumentExpired
RiskAssessment

LESS DESIRABLE

StatusChanged
ObjectUpdated
Record2
SupplierFlag
MiscInfo
```

Le framework doit éviter les abstractions tellement génériques qu'elles effacent le langage du domaine.

---

# 7. Positionnement DDD

PySRMKit adopte une orientation **Domain-Driven Design pragmatique**.

L'objectif n'est pas de reproduire tous les patterns DDD mécaniquement.

L'objectif est d'utiliser les concepts DDD lorsqu'ils clarifient :

- les frontières ;
- les invariants ;
- la cohésion ;
- les responsabilités ;
- les intégrations.

Principes privilégiés :

```text
Ubiquitous Language
Entities
Value Objects
Aggregates
Domain Services
Policies
Domain Events
Repositories as Ports
Application Services
Bounded Context Thinking
Anti-Corruption Layers
```

---

# 8. Bounded Context principal

Le bounded context principal est :

> **Supplier Relationship Management**

Il représente :

```text
Who the supplier is
+
How the supplier relates to the organization
+
Whether the supplier can work with the organization
+
Under which conditions
+
With which trust/risk/performance state
+
How that relationship evolves over time
```

Ce bounded context ne représente pas :

```text
How goods/services are sourced
How purchase orders are issued
How invoices are booked
How payments are executed
How contracts are fully authored
```

---

# 9. Sous-domaines internes envisagés

À l'intérieur du Supplier Domain, plusieurs sous-domaines fonctionnels émergent.

```text
Supplier Domain
│
├── Identity & Master Data
│
├── Organization
│
├── Relationship
│
├── Lifecycle
│
├── Onboarding
│
├── Qualification
│
├── Trust & Compliance
│   ├── Documents
│   ├── Certifications
│   └── Compliance
│
├── Risk
│
├── Assessment
│
├── Performance
│
├── Incident
│
├── Segmentation
│
└── History & Audit
```

Ce découpage est conceptuel.

Il ne signifie pas encore :

- un package Python par sous-domaine ;
- un microservice par sous-domaine ;
- une base par sous-domaine.

Ces décisions seront traitées plus tard.

---

# 10. Core Domain

Le **Core Domain** initial de PySRMKit est constitué des capacités qui donnent au framework son identité propre.

```text
Supplier Identity
Supplier Organization
Supplier Relationship
Supplier Lifecycle
Supplier Onboarding
Supplier Qualification
```

Ces éléments sont prioritaires car ils déterminent :

```text
WHO the supplier is
HOW we relate to it
WHERE it is in its lifecycle
WHETHER it can work with us
```

Les capacités suivantes enrichissent ce core :

```text
Documents
Certifications
Compliance
Risk
Assessments
Performance
Incidents
Segmentation
```

---

# 11. Supplier comme concept métier

Le Supplier ne doit pas être réduit à une projection technique.

```text
Supplier != database row

Supplier != ERP vendor

Supplier != accounting account

Supplier != legal entity only
```

Un Supplier représente un concept métier permettant de gouverner la relation fournisseur.

Il peut agréger ou référencer :

```text
Identity
Organization
Identifiers
Contacts
Locations
Categories
Capabilities
Lifecycle
Relationships
```

Les responsabilités exactes de l'aggregate root seront décidées dans les documents de domain modeling.

---

# 12. Supplier vs Supplier Relationship

Une distinction conceptuelle majeure doit être conservée.

```text
Supplier
    =
Who the external organization is

SupplierRelationship
    =
How our organization works with that supplier
```

Exemple :

```text
ACME France
    │
    ├── Relationship with Subsidiary A
    │      ACTIVE
    │      Qualified for IT
    │
    └── Relationship with Subsidiary B
           SUSPENDED
           Qualified for Consulting only
```

Cette distinction est particulièrement importante pour :

- multi-organisation ;
- multi-pays ;
- qualification ;
- lifecycle ;
- risk ;
- compliance ;
- segmentation.

La décision définitive concernant la frontière d'agrégat sera traitée dans :

```text
04_PYSRMKIT_DOMAIN_OBJECTS.md
05_PYSRMKIT_ENTITIES_AND_VALUE_OBJECTS.md
06_PYSRMKIT_DOMAIN_RELATIONSHIPS_AND_ERD.md
```

---

# 13. Principe d'identité canonique

Le Supplier possède une identité métier indépendante des systèmes intégrés.

```text
SupplierId
    │
    ├── ERP_VENDOR_ID
    ├── IVALUA_SUPPLIER_ID
    ├── SAP_VENDOR_ID
    ├── DUNS
    ├── SIREN
    ├── SIRET
    └── VAT_NUMBER
```

Les identifiants externes sont des **references**, pas l'identité du domaine.

Conséquences :

- un fournisseur peut exister avant sa création dans l'ERP ;
- un changement d'ERP ne change pas l'identité métier ;
- plusieurs systèmes peuvent référencer le même Supplier ;
- les imports externes nécessitent un mapping explicite.

---

# 14. Principe de règles métier explicites

Les règles importantes doivent être exprimées sous une forme testable.

Exemples :

```text
Can supplier be activated?
Can supplier be qualified for this scope?
Can supplier be suspended?
Is this document valid?
Is this certification current?
Can this qualification be renewed?
```

Les règles doivent éviter :

```text
if status == 7
if flag_x
if field_y is not None
```

lorsque ces conditions représentent en réalité un concept métier identifiable.

---

# 15. Principle of Controlled State Transitions

Les changements de state doivent passer par des opérations métier.

Conceptuellement :

```text
supplier.status = ACTIVE
```

est moins souhaitable que :

```text
supplier.activate(...)
```

car l'opération métier peut :

- vérifier les préconditions ;
- appliquer les invariants ;
- conserver la justification ;
- produire un événement ;
- préserver l'historique.

La forme exacte de l'API reste à définir.

---

# 16. Lifecycle comme State Machine métier

Le lifecycle doit être traité comme une machine à états métier.

Elle doit distinguer :

```text
State
Transition
Guard
Reason
Decision
Event
```

Exemple conceptuel :

```text
UNDER_REVIEW
    │
    │ qualification approved
    ▼
QUALIFIED
```

La couche domaine décide si la transition est valide.

La couche workflow peut décider :

```text
who reviews
when
in which sequence
with which SLA
```

---

# 17. Workflow Agnostic

PySRMKit ne doit pas devenir un moteur BPM.

Séparation :

```text
PySRMKit
    defines business possibility

PyWorkflowKit / BPM
    orchestrates human/system process
```

Exemple :

```text
PySRMKit:
    Supplier can be approved if requirements are satisfied.

Workflow:
    Compliance approves first.
    Procurement approves second.
    Finance approves above threshold.
```

Le framework doit donc exposer les règles nécessaires à l'orchestration sans embarquer l'orchestration générique elle-même.

---

# 18. Policy-Driven Extensibility

Toutes les entreprises n'appliquent pas les mêmes règles.

PySRMKit doit distinguer :

```text
Universal Invariant
vs
Organization Policy
```

Exemples de policies :

```text
QualificationPolicy
ActivationPolicy
RiskPolicy
CompliancePolicy
SegmentationPolicy
PerformancePolicy
DocumentRequirementPolicy
```

Une policy permet de personnaliser :

- des seuils ;
- des critères ;
- des pondérations ;
- des exigences ;
- des règles d'éligibilité.

Elle ne doit pas permettre de casser les invariants fondamentaux.

---

# 19. Invariants vs Policies

Cette distinction est centrale.

## Invariant

Règle fondamentale du modèle.

Exemple :

> Une qualification doit avoir un périmètre.

## Policy

Règle configurable d'une organisation.

Exemple :

> Pour la catégorie Cybersecurity, ISO 27001 est obligatoire.

Architecture :

```text
Invariant
    cannot be bypassed
        │
        ▼
Policy
    organization-specific decision
```

---

# 20. Composability First

PySRMKit doit être composé de capacités cohérentes pouvant être adoptées progressivement.

L'objectif est d'éviter :

```text
import pysrmkit_everything
configure 50 services
start database
start broker
```

pour exécuter une règle métier simple.

Un consumer doit pouvoir utiliser :

```text
Supplier
Lifecycle
Qualification
```

sans activer :

```text
Performance
Risk
Documents
```

si cela n'est pas nécessaire.

---

# 21. Modular Monolith Friendly, Microservice Neutral

PySRMKit doit fonctionner naturellement dans un monolithe modulaire.

```text
Application
├── Customer
├── Supplier
├── Procurement
├── Contract
└── Accounting
```

Il doit également pouvoir être placé derrière un service autonome.

```text
Supplier Service
    │
    ▼
PySRMKit
```

Mais PySRMKit ne doit pas supposer :

- qu'il est un microservice ;
- qu'il est déployé séparément ;
- qu'il possède sa propre base ;
- qu'il communique via HTTP.

Principe :

> **Deployment topology is an application concern, not a domain concern.**

---

# 22. Layering Principle

L'architecture cible respecte quatre zones conceptuelles.

```text
┌──────────────────────────────┐
│         Interfaces           │
│ API / CLI / Jobs / Agents    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Application Layer       │
│ Commands / Queries / Cases   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│        Domain Layer          │
│ Entities / VO / Rules / Evts │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Ports / Adapters        │
│ Persistence / External APIs  │
└──────────────────────────────┘
```

Les détails seront précisés dans le `03`.

---

# 23. Dependency Rule

La dépendance doit pointer vers le domaine.

```text
Interfaces
    │
    ▼
Application
    │
    ▼
Domain
```

L'infrastructure implémente des ports définis par les besoins du cœur.

Conceptuellement :

```text
Domain / Application
        │
        │ defines
        ▼
RepositoryPort
        ▲
        │ implements
        │
PostgreSQLAdapter
```

Le domaine ne doit pas dépendre de PostgreSQL.

---

# 24. Pure Domain Principle

Le domaine doit rester aussi proche que possible d'un modèle Python pur.

Il doit pouvoir être exécuté :

```text
without database
without network
without cloud
without HTTP server
without message broker
without workflow engine
without AI model
```

Cette propriété facilite :
- tests unitaires ;
- compréhension ;
- portability ;
- deterministic behavior ;
- réutilisation.

---

# 25. Persistence Agnostic

Le framework ne doit imposer aucun storage backend.

Adapters potentiels :

```text
InMemory
SQLite
PostgreSQL
MySQL
MongoDB
DynamoDB
Snowflake
```

Le modèle de persistence peut varier sans modifier les règles métier.

Conséquence :

> les modèles ORM ne sont pas les entités du domaine.

---

# 26. Repository Principle

Les repositories représentent des ports métier de persistence.

Ils doivent exprimer des intentions liées au domaine.

Exemple conceptuel :

```text
SupplierRepository
    get(...)
    save(...)
    find_by_external_identifier(...)
```

Ils ne doivent pas devenir une abstraction universelle de base de données.

À éviter :

```text
GenericRepository[T]
    arbitrary_query(...)
    raw_sql(...)
    table(...)
```

si ces abstractions dégradent le langage métier.

---

# 27. Integration Agnostic

Les intégrations externes doivent être représentées par des capacités abstraites.

Exemples :

```text
CompanyRegistryProvider
TaxValidationProvider
SanctionsScreeningProvider
BankVerificationProvider
DocumentStorageProvider
RiskDataProvider
ERPProvider
ProcurementProvider
```

Le cœur ne doit pas connaître :

```text
Ivalua REST endpoint
SAP SDK
Azure Blob SDK
AWS S3 SDK
Kafka client
```

---

# 28. Anti-Corruption Layer

Les modèles externes ne doivent pas contaminer directement le Supplier Domain.

Exemple :

```text
Ivalua Supplier JSON
        │
        ▼
Ivalua Adapter / Mapper
        │
        ▼
Canonical Supplier Model
```

Le même principe s'applique à :

- SAP ;
- Coupa ;
- Ariba ;
- registres légaux ;
- fournisseurs KYS ;
- services de risque ;
- DMS.

---

# 29. Domain Events First-Class

Les événements métier doivent être considérés comme des primitives du domaine.

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

Ils expriment :

> **quelque chose de significatif vient de se produire dans le domaine.**

Ils ne sont pas synonymes de :

```text
Kafka Message
RabbitMQ Message
SNS Event
HTTP Webhook
```

Ces derniers sont des mécanismes de transport.

---

# 30. Events vs Integration Events

Une distinction future devra être maintenue.

```text
Domain Event
    internal business fact
        │
        ▼
Application / Outbox
        │
        ▼
Integration Event
    external contract
```

Cette séparation permet :

- de faire évoluer le domaine ;
- de stabiliser les contrats externes ;
- de mapper plusieurs événements métier vers un événement d'intégration ;
- de ne pas exposer directement toute la structure interne.

---

# 31. Auditability by Design

L'audit n'est pas un ajout ultérieur.

Pour les décisions critiques, le modèle doit pouvoir conserver ou produire suffisamment d'information pour répondre à :

```text
WHAT?
WHO?
WHEN?
WHY?
FROM?
TO?
WITH WHICH EVIDENCE?
```

Domaines concernés en priorité :

- lifecycle ;
- onboarding ;
- qualification ;
- compliance ;
- documents ;
- risk ;
- suspension ;
- blocking ;
- reactivation ;
- offboarding.

---

# 32. Temporal Awareness

Le Supplier Domain est temporel.

Exemples :

```text
Qualification valid from t1 to t2
Certification expires at t3
Risk assessed at t4
Performance measured over period P
Supplier suspended at t5
Supplier reactivated at t6
```

Le modèle doit éviter de n'exposer que "l'état courant" lorsque l'historique a une valeur métier.

---

# 33. History without Mandatory Event Sourcing

PySRMKit doit être compatible avec une forte historisation.

Cependant :

> **Event Sourcing ne doit pas être imposé par principe.**

Deux modèles doivent rester possibles conceptuellement :

```text
Current State
+
Audit / History Records
```

ou :

```text
Event Stream
→ Reconstructed State
```

Le choix définitif sera traité dans l'architecture et les stratégies de persistence.

---

# 34. CQRS-Friendly, CQRS-Optional

Le domaine se prête naturellement à la séparation :

```text
Commands
    change state

Queries
    read state
```

Exemples :

```text
ActivateSupplier
SuspendSupplier
QualifySupplier
ReportIncident
```

vs :

```text
GetSupplier
ListQualifiedSuppliers
FindExpiringDocuments
GetSupplierRiskProfile
```

PySRMKit doit être **CQRS-friendly** sans rendre CQRS obligatoire.

---

# 35. Command Principle

Les commandes représentent des intentions métier.

```text
InviteSupplier
StartOnboarding
ApproveQualification
SuspendSupplier
```

Une commande :

- porte une intention ;
- est traitée par l'application layer ;
- déclenche le domaine ;
- ne contient pas la règle métier elle-même.

---

# 36. Query Principle

Les queries peuvent s'appuyer sur :

- repositories ;
- projections ;
- read models ;
- search adapters.

Le domaine ne doit pas être forcé à charger un aggregate complet pour toute lecture.

Ce principe devient important pour :

- dashboards ;
- recherche fournisseur ;
- scorecards ;
- reporting opérationnel ;
- agents ;
- APIs.

---

# 37. Application Layer Principle

L'application layer orchestre les cas d'utilisation.

Il peut :

1. charger un aggregate ;
2. demander une décision au domaine ;
3. persister le nouvel état ;
4. publier les événements ;
5. invoquer des ports externes.

Exemple conceptuel :

```text
ActivateSupplierHandler
    │
    ├── load supplier
    ├── call supplier.activate(...)
    ├── save supplier
    └── dispatch events
```

L'application layer ne doit pas contenir les invariants métier qui appartiennent au domaine.

---

# 38. Domain Service Principle

Un Domain Service est pertinent lorsque la logique :

- est métier ;
- ne relève naturellement d'aucune entité ou value object ;
- implique plusieurs concepts du domaine.

Il ne doit pas devenir :

```text
SupplierService
    with every function in the project
```

Le modèle doit privilégier les comportements là où ils ont du sens.

---

# 39. Value Object Principle

Les concepts sans identité propre doivent être candidats à des Value Objects.

Exemples potentiels :

```text
SupplierId
ExternalIdentifier
Address
CountryCode
Money
RiskScore
QualificationScope
DateRange
EmailAddress
Percentage
```

Un Value Object doit tendre vers :

- validation à la construction ;
- immutabilité ;
- égalité par valeur ;
- sémantique métier.

La liste exacte sera définie dans le document `05`.

---

# 40. Aggregate Boundary Principle

Les aggregates doivent être dimensionnés selon les invariants réellement transactionnels.

Ils ne doivent pas être choisis en fonction :

- des écrans ;
- des tables ;
- des endpoints ;
- du désir de tout charger en une seule fois.

Question structurante :

> Quelles données doivent être cohérentes ensemble lors d'une décision métier ?

Cette question guidera la définition de :

```text
Supplier
SupplierRelationship
Qualification
Assessment
RiskAssessment
```

comme aggregates éventuels.

---

# 41. Avoid the God Aggregate

Le Supplier ne doit pas nécessairement contenir en mémoire :

```text
all documents
all assessments
all risks
all scorecards
all incidents
all history
all relationships
```

pour exécuter chaque opération.

Risques d'un God Aggregate :

- fort couplage ;
- gros objets ;
- concurrency conflicts ;
- faible scalabilité ;
- persistence complexe ;
- évolution difficile.

Le domain model devra donc distinguer :

```text
Supplier Core Aggregate
+
Related Aggregates
+
References
```

lorsque cela sera justifié.

---

# 42. Rich Domain, Not Anemic Domain

PySRMKit doit éviter un modèle où les entités ne seraient que des structures de données.

À éviter :

```python
supplier.status = "ACTIVE"
repository.save(supplier)
```

si aucune règle ne protège cette transition.

Le modèle doit encapsuler le comportement significatif.

Mais "rich domain" ne signifie pas :

- tout mettre dans une seule classe ;
- supprimer l'application layer ;
- bannir les services ;
- rendre les objets artificiellement complexes.

---

# 43. Functional Core, Imperative Shell

Une orientation recommandée est :

```text
Functional / Deterministic Core
        │
        ▼
Imperative Application Shell
```

Le cœur doit tendre à contenir :

- décisions ;
- validations ;
- transitions ;
- calculs ;
- policies.

La périphérie contient :

- I/O ;
- persistence ;
- network ;
- messaging ;
- clock ;
- external providers.

Cela améliore la testabilité.

---

# 44. Time as an Explicit Dependency

Les concepts temporels sont nombreux :

- expiration de document ;
- expiration de certification ;
- période de qualification ;
- date de mesure ;
- review dates.

Les règles importantes ne doivent pas dépendre implicitement d'un appel incontrôlé à :

```python
datetime.now()
```

lorsque cela rend les tests non déterministes.

Le temps doit pouvoir être fourni explicitement lorsque nécessaire.

---

# 45. Determinism Principle

Une règle pure doit produire le même résultat à état et entrées identiques.

Exemple :

```text
evaluate qualification
supplier state = X
scope = Y
policy = Z
time = T
        │
        ▼
same decision
```

Les dépendances non déterministes doivent être explicites.

---

# 46. Error Model Principle

Les erreurs métier doivent être distinguées des erreurs techniques.

Exemples métier :

```text
InvalidLifecycleTransition
QualificationScopeRequired
SupplierAlreadyOffboarded
DocumentExpired
ActivationRequirementsNotMet
```

Exemples techniques :

```text
DatabaseUnavailable
ProviderTimeout
NetworkFailure
SerializationError
```

Cette distinction doit traverser l'architecture.

---

# 47. Validation Principle

Trois niveaux doivent être distingués.

## Structural Validation

Exemple :

```text
email format
non-empty identifier
country code format
```

## Domain Validation

Exemple :

```text
qualification requires scope
expiration must follow issue date
```

## Process / Policy Validation

Exemple :

```text
supplier cannot activate until required compliance checks pass
```

Ces validations ne doivent pas être mélangées sans distinction.

---

# 48. Security Boundary

PySRMKit n'est pas un système IAM.

Il ne doit pas embarquer directement :

- login ;
- OAuth ;
- RBAC engine ;
- token management ;
- sessions.

Cependant, les opérations critiques doivent pouvoir recevoir un contexte permettant l'audit et l'autorisation au niveau application.

Exemple conceptuel :

```text
Actor
Command
Reason
CorrelationId
```

La décision :

> "cet utilisateur a-t-il le droit d'appeler cette commande ?"

appartient principalement à l'application / IAM.

La décision :

> "cette transition métier est-elle valide ?"

appartient au domaine.

---

# 49. Privacy and Sensitive Data Principle

Le Supplier Domain peut référencer des données sensibles :

- informations de contact ;
- données bancaires de référence ;
- documents ;
- données fiscales ;
- résultats de contrôles ;
- risk information.

PySRMKit doit éviter de supposer que toutes ces données peuvent être :

- loggées ;
- publiées dans les events ;
- sérialisées publiquement ;
- stockées dans n'importe quelle projection.

Les contrats d'événements devront minimiser les données sensibles.

---

# 50. Multi-Organization by Design

Le multi-organisation ne doit pas être ajouté après coup.

Un même Supplier peut avoir :

```text
Relationship A
with Organization A

Relationship B
with Organization B
```

et des états différents.

Conséquences :

- qualification peut être scoped ;
- status peut être scoped ;
- risk peut être scoped ;
- compliance peut être scoped ;
- segmentation peut être scoped.

Le modèle exact sera précisé dans les documents de domaine.

---

# 51. Multi-Country by Design

Le modèle ne doit pas considérer comme universels :

```text
SIREN
SIRET
URSSAF attestation
French postal address
French tax rules
```

Ces éléments sont des spécialisations possibles.

Le noyau doit privilégier :

```text
ExternalIdentifier(type, value, jurisdiction)
Address
TaxIdentifier
DocumentType
ComplianceRequirement
```

avec extension par pays lorsque nécessaire.

---

# 52. Localization vs Domain

Langues et formats d'affichage ne doivent pas contaminer le domaine.

Exemple :

```text
Domain:
    ACTIVE

UI FR:
    Actif

UI EN:
    Active
```

Le domaine porte la sémantique.

L'interface porte la présentation.

---

# 53. Serialization Principle

Le framework doit faciliter la sérialisation sans faire d'un format donné sa source de vérité.

Possible representations :

```text
dict
JSON
Message payload
API schema
Database row
```

Le domain model reste distinct de ces representations.

---

# 54. API Stability Principle

PySRMKit a vocation à devenir une bibliothèque réutilisée par d'autres composants.

Les APIs publiques stables doivent donc être :

- intentionnelles ;
- documentées ;
- limitées ;
- versionnées ;
- testées.

Les composants internes doivent rester libres d'évoluer davantage.

Principe :

```text
small stable public surface
+
flexible internal implementation
```

---

# 55. Evolution Principle

La croissance de PySRMKit doit se faire selon :

```text
Need
→ Requirement
→ Domain Concept
→ Business Rule
→ Use Case
→ Public API
```

et non :

```text
Interesting technical pattern
→ add abstraction
```

Le framework ne doit pas accumuler des abstractions sans usage métier clair.

---

# 56. Backward Compatibility

Après stabilisation publique, les changements devront distinguer :

```text
Additive change
Compatible behavior change
Deprecation
Breaking change
```

Les versions initiales alpha/beta pourront évoluer plus rapidement.

La stratégie complète de versioning pourra être documentée séparément.

---

# 57. Open/Closed Architecture

PySRMKit doit être :

> **closed for violation of core invariants, open for extension of organizational rules and integrations.**

Autrement dit :

```text
Core invariants
    stable

Policies
    extensible

Ports
    extensible

Adapters
    replaceable
```

---

# 58. Plugin Principle

Un système de plugins ne doit être ajouté que s'il répond à un besoin réel.

Les premières extensions doivent pouvoir être réalisées par des mécanismes Python simples :

- dependency injection ;
- protocols/interfaces ;
- policies ;
- adapters ;
- registries ciblés.

Éviter un plugin framework complexe prématuré.

---

# 59. Configuration Principle

La configuration ne doit pas devenir un langage métier caché.

À éviter :

```yaml
rule_142:
  flag: true
  code: A7
```

si cela remplace une notion métier explicite.

La configuration est pertinente pour :

- seuils ;
- mappings ;
- policy choices ;
- providers ;
- options d'intégration.

Les invariants fondamentaux doivent rester dans le code du domaine.

---

# 60. Observability Boundary

PySRMKit doit faciliter l'observabilité mais ne doit pas dépendre d'un système spécifique.

Les couches externes pourront instrumenter :

- commands ;
- use cases ;
- events ;
- provider calls ;
- persistence.

Le cœur ne doit pas dépendre directement de :

- OpenTelemetry ;
- Datadog ;
- Prometheus ;
- Sentry.

---

# 61. Logging Principle

Le domaine ne doit pas utiliser le logging comme mécanisme de business state.

Un message de log :

```text
supplier qualified
```

ne remplace pas :

```text
SupplierQualified event
Qualification record
Audit entry
```

Le logging sert à l'observabilité technique.

---

# 62. Testing Philosophy

La pyramide de tests doit privilégier fortement le domaine.

```text
             E2E
            /   \
       Integration
       /         \
  Application Tests
   /             \
Domain Unit Tests
```

Le domaine doit pouvoir être testé :

- rapidement ;
- en mémoire ;
- sans infrastructure ;
- avec des fixtures simples ;
- de manière déterministe.

---

# 63. Contract Tests

Les adapters importants devront pouvoir être qualifiés contre les ports.

Exemple :
```text
SupplierRepositoryContract
        │
        ├── InMemory adapter
        ├── PostgreSQL adapter
        └── Mongo adapter
```

Cette stratégie permet d'assurer que plusieurs implémentations respectent le même contrat.

---

# 64. Reference Implementation Principle

Le framework pourra fournir certaines implémentations simples de référence.

Exemples potentiels :

```text
InMemorySupplierRepository
SimpleQualificationPolicy
SimpleLifecyclePolicy
```

Objectifs :

- faciliter les tests ;
- faciliter l'adoption ;
- fournir un comportement de référence.

Ces implémentations ne doivent pas devenir des dépendances obligatoires.

---

# 65. Agentic Compatibility

PySRMKit doit être utilisable par des agents.

Mais l'agent est un client du domaine.

```text
General Agent
    │
    ▼
Procurement Manager Agent
    │
    ▼
Supplier Agent
    │
    ▼
Application Layer
    │
    ▼
PySRMKit
```

L'agent peut :

- proposer ;
- rechercher ;
- expliquer ;
- déclencher une commande autorisée.

Il ne peut pas :

- muter arbitrairement l'état ;
- ignorer les invariants ;
- contourner la qualification ;
- fabriquer une conformité.

---

# 66. Explainability for Agents

Un système agentique a besoin non seulement d'un résultat, mais souvent d'une raison.

Les décisions métier importantes devraient pouvoir produire ou exposer :

```text
Decision
Reason
Failed Rules
Evidence References
Current State
Required Conditions
```

Exemple :

```text
Supplier cannot be activated.

Reasons:
- TAX_CLEARANCE missing
- CYBER_RISK above allowed threshold
```

Cette capacité profite aussi :

- aux UIs ;
- aux APIs ;
- aux audits ;
- aux workflows.

---

# 67. Separation from AI

PySRMKit ne doit pas dépendre :

- d'un LLM ;
- d'un embedding model ;
- d'un vector database ;
- d'un agent framework.

Un modèle IA peut aider à :

```text
classify documents
summarize assessments
detect anomalies
recommend actions
```

mais la décision métier finale doit repasser par le domaine.

---

# 68. Ecosystem Position

PySRMKit s'inscrit dans un écosystème plus large.

```text
                    ENTERPRISE DOMAIN
                           │
         ┌─────────────────┼──────────────────┐
         │                 │                  │
         ▼                 ▼                  ▼
   CUSTOMER             SUPPLIER            FINANCE
     DOMAIN               DOMAIN             DOMAIN
       │                    │                  │
   PyCRMKit             PySRMKit        PyAccountingKit
                            │
                            ▼
                     PROCUREMENT
                            │
                    PyProcurementKit
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
          PyContractKit              Payments
```

Autour :

```text
PyIAMKit
PyWorkflowKit
PyScheduleKit
PyRuntimeKit
PyTransformKit
PyIngestKit
PyMonitorKit
PyAnalyticsKit
PyAgentsKit
```

---

# 69. Relation avec PyCRMKit

PyCRMKit et PySRMKit sont conceptuellement symétriques.

```text
CUSTOMER SIDE
PyCRMKit
    manages demand-side relationships

SUPPLIER SIDE
PySRMKit
    manages supply-side relationships
```

Ils peuvent partager des idées architecturales.

Ils ne doivent pas nécessairement partager le même modèle métier.

---

# 70. Relation avec PyProcurementKit

Frontière fondamentale :

```text
PySRMKit
    WHO can we buy from?

PyProcurementKit
    WHAT do we buy?
    HOW do we buy it?
```

Exemple :

```text
Supplier
    │
    ▼
Qualification
    │
    ▼
Eligible Supplier
    │
    ▼
Procurement
    │
    ▼
RFQ / PO
```

---

# 71. Relation avec PyContractKit

PySRMKit peut savoir :

```text
Supplier has Contract X
```

mais PyContractKit porte :

- clauses ;
- versions ;
- obligations contractuelles ;
- amendments ;
- contract lifecycle.

PySRMKit ne doit pas reproduire ce domaine.

---

# 72. Relation avec PyAccountingKit

Le Supplier est une entité commerciale.

Le Vendor Account est une représentation comptable.

```text
Supplier
    │
    ▼
Vendor Account
    │
    ▼
Accounts Payable
```

Invariant conceptuel :

```text
Supplier != Vendor Ledger Account
```

---

# 73. Relation avec PyIAMKit

PyIAMKit gère :

```text
identity
authentication
authorization
roles
permissions
```

PySRMKit gère :

```text
supplier business rules
```

Une opération peut nécessiter les deux.

```text
IAM:
    actor is allowed to request suspension

SRM:
    supplier can legally transition to SUSPENDED
```

---

# 74. Relation avec PyWorkflowKit

```text
PySRMKit
    domain state machine

PyWorkflowKit
    orchestration state machine
```

Ces deux state machines ne doivent pas être confondues.

Exemple :

```text
Workflow:
    Legal review pending

Supplier Lifecycle:
    UNDER_REVIEW
```

Le workflow peut évoluer sans modifier la sémantique métier.

---

# 75. Relation avec PyRuntimeKit

PyRuntimeKit peut exécuter :

- commands ;
- jobs ;
- background tasks ;
- handlers.

PySRMKit ne dépend pas de son runtime.

```text
PyRuntimeKit
    executes

PySRMKit
    decides
```

---

# 76. Relation avec PyScheduleKit

PyScheduleKit peut planifier :

```text
document expiry scan
annual supplier review
risk reassessment
scorecard refresh
```

PySRMKit expose la sémantique.

PyScheduleKit expose la temporalité d'exécution.

---

# 77. Relation avec PyAgentsKit

PyAgentsKit peut fournir :

```text
Supplier Agent
Risk Review Agent
Compliance Agent
```

Ces agents utilisent les use cases de PySRMKit.

Ils ne deviennent pas propriétaires du business state.

---

# 78. Architecture Conceptuelle Cible

```text
┌───────────────────────────────────────────────────────────┐
│                       Consumers                           │
│ Portal │ APIs │ ERP │ Procurement │ Agents │ CLI │ Jobs  │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│                    Interface Layer                        │
│ Controllers │ CLI │ Workers │ Agent Tools │ Serializers  │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│                   Application Layer                       │
│ Commands │ Queries │ Handlers │ Use Cases │ UoW          │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│                      Domain Layer                          │
│                                                           │
│ Supplier │ Relationship │ Lifecycle │ Qualification       │
│ Documents │ Compliance │ Risk │ Assessment │ Performance │
│ Policies │ Invariants │ Domain Events                    │
└─────────────────────────────┬─────────────────────────────┘
                              │
                   defines required ports
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│                         Ports                             │
│ Repositories │ Events │ Registries │ Risk │ Documents    │
└─────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│                        Adapters                           │
│ PostgreSQL │ Ivalua │ SAP │ REST │ Kafka │ S3 │ etc.   │
└───────────────────────────────────────────────────────────┘
```

---

# 79. Dependency Direction

La direction conceptuelle est :

```text
Adapters
    ─────► Ports

Interfaces
    ─────► Application

Application
    ─────► Domain
```

Le domaine ne doit pas dépendre des couches extérieures.

Version simplifiée :

```text
OUTSIDE
   │
   ▼
INSIDE
```

et jamais :

```text
DOMAIN
   │
   ▼
FRAMEWORK / VENDOR SDK
```

---

# 80. Architecture Decision Filters

Toute décision future devra être évaluée avec les questions suivantes.

## Domain

- Est-ce un concept métier ou technique ?
- Quel invariant protège-t-il ?
- À quel sous-domaine appartient-il ?

## Coupling

- Cette décision couple-t-elle le domaine à un framework ?
- Peut-elle être remplacée sans changer les règles métier ?

## Extensibility

- S'agit-il d'un invariant ou d'une policy ?
- Comment une organisation peut-elle l'adapter ?

## Testability

- Peut-on tester la règle sans infrastructure ?

## Auditability

- Peut-on expliquer la décision ?

## Composability

- Cette capability peut-elle être utilisée sans activer tout PySRMKit ?

---

# 81. Architecture Principles Catalog

Les principes structurants peuvent être résumés ainsi.

## AP-001 — Domain First

Le métier précède la technologie.

## AP-002 — Ubiquitous Language

Le code doit refléter le vocabulaire SRM.

## AP-003 — Canonical Supplier Identity

L'identité métier ne dépend pas d'un ERP.

## AP-004 — Explicit Business Rules

Les règles critiques sont visibles et testables.

## AP-005 — Controlled State Transitions

Les changements métier passent par des opérations contrôlées.

## AP-006 — Technology Agnostic

Aucun framework technique n'est imposé au cœur.

## AP-007 — Persistence Agnostic

Le domaine est indépendant du stockage.

## AP-008 — Workflow Agnostic

Le domaine ne devient pas un moteur BPM.

## AP-009 — Integration via Ports

Les dépendances externes sont abstraites.

## AP-010 — Domain Events First-Class

Les faits métier significatifs sont représentés explicitement.

## AP-011 — Policies for Variability

Les règles organisationnelles variables passent par des policies.

## AP-012 — Invariants Cannot Be Bypassed

L'extension ne casse pas les règles fondamentales.

## AP-013 — Composability

Les capabilities sont adoptables progressivement.

## AP-014 — Auditability by Design

Les décisions critiques sont traçables.

## AP-015 — Temporal Awareness

Le domaine préserve l'évolution dans le temps.

## AP-016 — Multi-Organization by Design

Les relations peuvent différer selon l'entité interne.

## AP-017 — Multi-Country by Design

Le noyau n'est pas franco-centré.

## AP-018 — Small Stable Public API

La surface publique doit rester maîtrisée.

## AP-019 — Agent as Consumer

Les agents utilisent le domaine, ils ne le remplacent pas.

## AP-020 — No Premature Infrastructure

L'infrastructure ne doit pas dicter le modèle.

---

# 82. Anti-Patterns à éviter

## APAT-001 — ORM-Driven Domain

```text
Database schema
→ ORM
→ business model
```

## APAT-002 — God Supplier

Un Supplier chargé de toute l'histoire et de toutes les capabilities.

## APAT-003 — Generic Everything

```text
Entity
Record
Manager
Service
Repository
Metadata
```

sans langage SRM.

## APAT-004 — Boolean Explosion

```text
is_active
is_blocked
is_suspended
is_qualified
is_offboarded
```

sans machine à états cohérente.

## APAT-005 — Workflow Owns Business Rules

Le BPM décide seul de la validité métier.

## APAT-006 — Agent Owns Business Rules

Le LLM décide arbitrairement si un fournisseur est qualifié.

## APAT-007 — Integration Model Leakage

Le JSON Ivalua devient directement le Supplier Model.

## APAT-008 — Hidden Side Effects

Une méthode métier déclenche réseau, persistence et emails implicitement.

## APAT-009 — Event Bus Coupled Domain

Le domaine importe directement Kafka.

## APAT-010 — Premature Microservices

Chaque concept devient un service avant validation des frontières.

---

# 83. Product Experience for Developers

L'expérience développeur doit tendre vers :

```python
supplier = Supplier.create(...)

supplier.invite(...)
supplier.start_onboarding(...)
supplier.qualify(...)
supplier.activate(...)
```

ou via application layer :

```python
service.activate_supplier(command)
```

sans configuration d'infrastructure obligatoire pour utiliser le domaine.

La forme exacte sera définie ultérieurement.

Objectif DX :

```text
Discoverable
Explicit
Typed
Testable
Predictable
Composable
```

---

# 84. Public API Philosophy

Une API publique PySRMKit doit privilégier :

- noms métier ;
- types explicites ;
- comportements prévisibles ;
- erreurs explicites ;
- petites interfaces.

À éviter :

```python
execute(action="X", payload={...})
```

comme seule primitive universelle si cela efface le langage métier.

---

# 85. Packaging Philosophy

Sans figer l'arborescence finale, le packaging devra probablement distinguer au moins conceptuellement :

```text
domain
application
ports
adapters
```

Les adapters optionnels devront idéalement rester découplés du noyau.

Le `03_PYSRMKIT_SYSTEM_ARCHITECTURE.md` détaillera cette structure.

---

# 86. Dependency Management

Le package cœur doit tendre vers un nombre minimal de dépendances.

Principe :

```text
Core Domain
    minimal dependencies

Adapters
    technology-specific dependencies
```

Cela permet :

- installation légère ;
- moins de conflits ;
- meilleure stabilité ;
- meilleure portability.

---

# 87. Optional Integrations

Les intégrations techniques devraient être activées explicitement.

Exemple conceptuel futur :

```text
pysrmkit
pysrmkit-postgres
pysrmkit-fastapi
```

ou extras :

```text
pysrmkit[postgres]
pysrmkit[fastapi]
```

Aucune décision définitive n'est prise ici.

Le principe est :

> les dépendances lourdes doivent rester optionnelles.

---

# 88. MVP Architecture Scope

Pour le MVP, l'architecture doit principalement permettre :

```text
Supplier Core
Lifecycle
Onboarding
Qualification
Assessments
Policies
Domain Events
Repository Ports
In-memory testing
```

Le MVP ne nécessite pas initialement :

- Kafka ;
- PostgreSQL officiel ;
- Web framework ;
- distributed transactions ;
- event sourcing ;
- complex plugin engine ;
- AI integration.

---

# 89. Phase Architecture Evolution

## Phase 1 — Supplier Core

```text
Identity
Organization
Contacts
Locations
Categories
Capabilities
Lifecycle
History
Events
```

Focus architectural :

- core domain ;
- value objects ;
- state transitions ;
- repository contracts.

## Phase 2 — Onboarding & Qualification

```text
Onboarding
Qualification
Assessments
Policies
```

Focus architectural :

- use cases ;
- policies ;
- decision model ;
- scoped qualification.

## Phase 3 — Trust & Control

```text
Documents
Certifications
Compliance
Risk
```

Focus architectural :

- provider ports ;
- time-based rules ;
- evidence ;
- external verification.

## Phase 4 — Relationship Intelligence

```text
Performance
Scorecards
Incidents
Segmentation
Relationships
```

Focus architectural :

- temporal metrics ;
- projections ;
- aggregation ;
- advanced read models.

---

# 90. Decision Matrix — Core vs External

| Concern | PySRMKit Core | Application | Adapter / External |
|---|---:|---:|---:|
| Supplier identity | Yes | — | — |
| Lifecycle invariant | Yes | — | — |
| Qualification rule | Yes | Coordinates | — |
| Workflow approval order | No | Possible | BPM |
| Database persistence | No | Coordinates | Yes |
| HTTP API | No | Possible | Interface |
| Document validity | Yes | Coordinates | — |
| File storage | No | Coordinates | DMS/S3 |
| Compliance meaning | Yes | Coordinates | — |
| Sanctions lookup | No | Coordinates | Provider |
| Risk rule | Yes | Coordinates | — |
| External risk feed | No | Coordinates | Provider |
| Domain event | Yes | Dispatches | Broker adapter |
| Authentication | No | Uses actor | IAM |
| Authorization | No | Yes | IAM |
| Agent reasoning | No | Agent invokes | PyAgentsKit |
| Business invariant | Yes | Cannot bypass | Cannot bypass |

---

# 91. Decision Matrix — Invariant vs Policy vs Integration

| Example | Invariant | Policy | Integration |
|---|---:|---:|---:|
| Qualification must have scope | Yes | No | No |
| ISO 27001 required for Cyber category | No | Yes | No |
| Check ISO certificate in external service | No | No | Yes |
| Offboarded history must remain | Yes | No | No |
| Risk > 80 blocks activation | No | Yes | No |
| Retrieve external risk score | No | No | Yes |
| Document expiry date after issue date | Yes | No | No |

---

# 92. Open Architecture Questions

Les questions suivantes restent volontairement ouvertes.

## OAQ-001 — Aggregate Root

`Supplier` doit-il être l'unique root principal ou plusieurs roots doivent-ils coexister ?

## OAQ-002 — SupplierRelationship

`SupplierRelationship` doit-il être un aggregate root de premier niveau ?

## OAQ-003 — Lifecycle Scope

Le lifecycle est-il :

- Supplier-scoped ;
- Relationship-scoped ;
- les deux selon le niveau ?

## OAQ-004 — Qualification Aggregate

La Qualification doit-elle être :

- entité interne ;
- aggregate autonome ;
- projection d'assessment ?

## OAQ-005 — Compliance Model

Faut-il distinguer explicitement :

```text
ComplianceRequirement
ComplianceCheck
ComplianceFinding
ComplianceDecision
```

## OAQ-006 — Risk Model

Faut-il distinguer :

```text
RiskDefinition
RiskObservation
RiskAssessment
RiskDecision
RiskMitigation
```

## OAQ-007 — History Model

Simple audit log, temporal records ou event sourcing optionnel ?

## OAQ-008 — Policy Composition

Comment plusieurs policies se combinent-elles ?

## OAQ-009 — Sync/Async

Les ports du cœur application doivent-ils être :

- synchrones ;
- asynchrones ;
- séparés ?

## OAQ-010 — Package Boundaries

Quels sous-domaines méritent un package indépendant ?

Ces décisions devront être documentées dans les prochaines étapes.

---

# 93. Architecture Principles Acceptance Criteria

L'architecture pourra être considérée conforme aux principes de ce document si :

1. le cœur peut être importé sans ORM ;
2. les tests du domaine s'exécutent sans base ;
3. les transitions lifecycle sont contrôlées ;
4. les identifiers externes ne remplacent pas `SupplierId` ;
5. les adapters externes implémentent des ports ;
6. le domaine ne connaît aucun SDK fournisseur ;
7. les policies peuvent être remplacées ;
8. les invariants ne peuvent pas être contournés par une policy ;
9. les événements métier existent sans broker ;
10. le framework est utilisable sans serveur Web ;
11. le framework est utilisable depuis un agent sans dépendre d'un LLM ;
12. un même fournisseur peut être représenté dans un contexte multi-organisation ;
13. les concepts ne sont pas limités au contexte français ;
14. les décisions métier critiques peuvent être expliquées ;15. les capabilities principales peuvent être testées indépendamment.

---

# 94. Architecture Fitness Functions candidates

Des tests automatisés pourront plus tard protéger les principes.

Exemples :

```text
domain package must not import sqlalchemy
domain package must not import fastapi
domain package must not import boto3
domain package must not import kafka clients
domain tests must run without network
```

Des règles statiques pourront également empêcher certaines dépendances interdites.

---

# 95. Guiding Heuristics

Lorsqu'une décision n'est pas évidente :

## Heuristic 1

> Put business meaning in the domain.

## Heuristic 2

> Put I/O at the edges.

## Heuristic 3

> Prefer explicit types over magic values.

## Heuristic 4

> Prefer policies over customer-specific branching.

## Heuristic 5

> Prefer ports over vendor SDK leakage.

## Heuristic 6

> Prefer small aggregates over one omniscient aggregate.

## Heuristic 7

> Prefer domain events over hidden side effects.

## Heuristic 8

> Prefer explainable decisions over opaque automation.

## Heuristic 9

> Prefer composition over mandatory full-stack adoption.

## Heuristic 10

> Add abstractions only when the domain requires them.

---

# 96. North Star Architecture

La cible conceptuelle peut être résumée ainsi :

```text
                    ┌────────────────────┐
                    │      Consumers     │
                    │ UI API ERP Agents  │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ Application Layer  │
                    │ Commands / Queries │
                    └─────────┬──────────┘
                              │
                              ▼
        ┌────────────────────────────────────────┐
        │              PySRMKit                  │
        │                                        │
        │ Supplier Identity                      │
        │ Supplier Relationship                  │
        │ Lifecycle                              │
        │ Onboarding                             │
        │ Qualification                          │
        │ Compliance / Risk                      │
        │ Assessment / Performance               │
        │ Policies / Invariants                  │
        │ Domain Events                          │
        └───────────────┬────────────────────────┘
                        │
                     Ports
                        │
        ┌───────────────┼─────────────────────┐
        ▼               ▼                     ▼
   Persistence      External Data          Events
   Adapters          Adapters              Adapters
```

---

# 97. Product North Star

Le produit doit progressivement permettre à une application de répondre de manière fiable à des questions comme :

```text
Who is this supplier?

What legal entities and locations belong to it?

How does our organization relate to it?

Where is it in its lifecycle?

For what scope is it qualified?

Why is it not qualified?

Which documents are missing or expired?

Which certifications are valid?

What compliance controls have been performed?

What risks are currently known?

How has its risk evolved?

How does it perform?

Which incidents occurred?

Why was it suspended?

Can it be reactivated?

What happened during the entire relationship?
```

avec un modèle métier cohérent et indépendant de la technologie.

---

# 98. Product Principles Summary

PySRMKit doit être :

```text
DOMAIN-FIRST
    business meaning before technology

RICH
    supplier as a full business concept

EXPLICIT
    visible rules and transitions

COMPOSABLE
    adopt only needed capabilities

EXTENSIBLE
    organization-specific policies

AGNOSTIC
    no mandatory infrastructure stack

AUDITABLE
    explain decisions and history

TEMPORAL
    preserve evolution through time

INTEGRATION-FRIENDLY
    ports and domain events

MULTI-ORGANIZATION
    relation-aware

MULTI-COUNTRY
    jurisdiction-neutral core

AGENT-READY
    usable by agents without delegating invariants to them
```

---

# 99. Transition vers le System Architecture

Ce document fixe les **principes**.

Le document suivant devra définir la **structure du système** qui concrétise ces principes.

Le prochain document est :

> **`03_PYSRMKIT_SYSTEM_ARCHITECTURE.md`**

Il devra notamment détailler :

- les couches ;
- les modules ;
- les dépendances autorisées ;
- les flux Commands / Queries ;
- le traitement des domain events ;
- les repositories ;
- les ports ;
- les adapters ;
- les boundaries internes ;
- les projections ;
- l'intégration ;
- la persistence ;
- l'architecture de test ;
- les extension points ;
- une première proposition de package topology.

---

# 100. Conclusion

PySRMKit ne doit pas être conçu comme une collection de modèles Python représentant des tables fournisseur.

Il doit être conçu comme un **Supplier Domain Engine**.

Sa valeur vient de la combinaison suivante :

```text
Canonical Supplier Model
+
Explicit Business Rules
+
Controlled Lifecycle
+
Scoped Qualification
+
Trust / Compliance / Risk
+
Temporal History
+
Policies
+
Domain Events
+
Ports
```

Le principe le plus important reste :

> **The Supplier Domain owns business truth.**

Les bases de données stockent cette vérité.

Les APIs l'exposent.

Les workflows l'orchestrent.

Les systèmes externes l'enrichissent.

Les agents l'utilisent.

Mais aucun de ces éléments ne doit remplacer les invariants et la sémantique du domaine.

C'est cette séparation qui permettra à PySRMKit de rester :

- durable ;
- réutilisable ;
- testable ;
- extensible ;
- composable ;
- indépendant des technologies ;
- compatible avec des architectures classiques comme agentiques.

PySRMKit doit donc devenir non pas une application SRM supplémentaire, mais une **primitive métier réutilisable du Supplier Domain** dans l'écosystème Py*Kit.