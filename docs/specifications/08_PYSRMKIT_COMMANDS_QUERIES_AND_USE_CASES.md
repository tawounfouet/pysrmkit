# PySRMKit — Commands, Queries and Use Cases

**Document :** `08_PYSRMKIT_COMMANDS_QUERIES_AND_USE_CASES.md`  
**Projet :** PySRMKit  
**Domaine :** Supplier Relationship Management  
**Type :** Application Modeling — Commands, Queries, Handlers et Use Cases  
**Statut :** Draft de conception applicative  
**Version du document :** 0.1.0  
**Documents de référence :**
- `00_PYSRMKIT_EXPRESSION_DU_BESOIN.md`
- `01_PYSRMKIT_REQUIREMENTS_ANALYSIS.md`
- `02_PYSRMKIT_PRODUCT_VISION_AND_ARCHITECTURE_PRINCIPLES.md`
- `03_PYSRMKIT_SYSTEM_ARCHITECTURE.md`
- `04_PYSRMKIT_DOMAIN_OBJECTS.md`
- `05_PYSRMKIT_ENTITIES_AND_VALUE_OBJECTS.md`
- `06_PYSRMKIT_DOMAIN_RELATIONSHIPS_AND_ERD.md`
- `PYSRMKIT_SOFTWARE_DESIGN_LEARNING_CONVENTION.md`

> **Note de séquencement :** le document `07_PYSRMKIT_DOMAIN_INVARIANTS_AND_BUSINESS_RULES.md` doit préciser les invariants, guards et policies auxquels les use cases définis ici délèguent les décisions métier. Le présent document reste donc volontairement compatible avec cette couche de règles sans la réimplémenter.

---

# 1. Objet du document

Ce document décrit la **couche applicative** de PySRMKit.

Il transforme les capacités métier et les objets du domaine en :

```text
Commands
Queries
Handlers
Use Cases
Application Results
Application Errors
Transaction Boundaries
Event Dispatch Flows
```

Il répond notamment aux questions suivantes :

> Comment une application demande-t-elle à PySRMKit de modifier le domaine ?

> Comment une application lit-elle le Supplier Domain ?

> Quelle différence existe entre une Command et une Query ?

> Quelle responsabilité appartient au Handler ?

> Quelle responsabilité reste dans le Domain Model ?

> Où les repositories interviennent-ils ?

> Où les Domain Policies interviennent-elles ?

> Où commence et où finit une transaction applicative ?

> Comment les Domain Events sont-ils collectés et publiés ?

> Comment un agent, une API, une CLI ou un job utilisent-ils exactement les mêmes use cases ?

---

# 2. Position dans la chaîne de conception

```text
Business Need
    │
    ▼
Requirements
    │
    ▼
Architecture
    │
    ▼
Domain Objects
    │
    ▼
Entities / Value Objects
    │
    ▼
Relationships / Aggregates
    │
    ▼
Invariants / Business Rules
    │
    ▼
COMMANDS / QUERIES / USE CASES   ← ce document
    │
    ▼
Ports / Adapters
    │
    ▼
Implementation
```

---

# 3. Intention architecturale

La couche applicative a une mission simple :

> **orchestrer un cas d'usage sans devenir propriétaire de la vérité métier.**

Elle doit pouvoir :

```text
receive intent
load state
collect external facts
invoke domain behavior
persist state
commit
dispatch events
return result
```

Elle ne doit pas :

```text
reimplement domain invariants
mutate entity fields arbitrarily
embed vendor-specific integration logic
own HTTP semantics
own database semantics
```

---

# 4. Architecture de référence

```text
┌──────────────────────────────────────────────────────┐
│                 Primary Adapters                     │
│ API │ CLI │ Agent Tools │ Workers │ Python Facade   │
└──────────────────────────┬───────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────┐
│                 Application Layer                    │
│ Commands │ Queries │ Handlers │ Use Cases           │
│ Transaction Coordination │ Event Dispatch           │
└──────────────────────────┬───────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────┐
│                    Domain Layer                      │
│ Aggregates │ Value Objects │ Policies │ Events       │
│ Invariants │ Domain Errors                          │
└──────────────────────────┬───────────────────────────┘
                           │
                      Output Ports
                           │
                           ▼
┌──────────────────────────────────────────────────────┐
│                 Secondary Adapters                   │
│ Persistence │ Registries │ Risk │ Documents │ Events │
└──────────────────────────────────────────────────────┘
```

---

# 5. Design Concepts Applied

## DDD

```text
Aggregate
Repository
Domain Policy
Domain Event
Domain Service
Application Service
```

## Principles

```text
Single Responsibility Principle
Dependency Inversion Principle
Separation of Concerns
Information Hiding
Explicit Dependencies
Command-Query Separation
KISS
YAGNI
```

## Architectural Patterns

```text
Application Layer
CQRS-friendly
Ports and Adapters
Hexagonal Architecture
Event-Driven friendly
Unit of Work candidate
```

## Python Mechanisms

```text
dataclass(frozen=True)
Protocol
typed commands
typed queries
typed result objects
dependency injection
composition
```

---

# 6. Command — définition retenue

Une **Command** représente une intention explicite de modifier l'état métier.

Exemples :

```text
RegisterSupplier
CreateSupplierRelationship
InviteSupplierRelationship
StartSupplierOnboarding
RequestSupplierQualification
ApproveSupplierQualification
SuspendSupplierRelationship
ReportSupplierIncident
```

Une Command dit :

> **Do this.**

Elle ne décrit pas :

> **How to do it.**

---

# 7. Query — définition retenue

Une **Query** représente une demande de lecture.

Exemples :

```text
GetSupplier
FindSupplierByExternalIdentifier
GetSupplierRelationship
ListQualifiedSuppliers
ListExpiringSupplierDocuments
GetSupplierRiskProfile
GetSupplier360
```

Une Query dit :

> **Tell me this.**

Elle ne modifie pas l'état métier.

---

# 8. Command-Query Separation

Règle structurante :

```text
Command
    may change state
    returns limited business/application result

Query
    reads state
    must not change business state
```

Cette règle est utile même sans implémenter un système CQRS complet.

---

# 9. CQRS-Friendly, Not Full CQRS

PySRMKit adopte :

```text
Command / Query conceptual separation
```

mais n'impose pas :

```text
two databases
two deployed services
event sourcing
message bus
eventual consistency for all reads
```

Le principe est :

> **Use CQRS where it clarifies intent; do not turn it into mandatory distributed architecture.**

---

# 10. CQRS Command ≠ GoF Command Pattern

Important :

```text
Application Command
≠
GoF Command Pattern
```

Une classe :

```text
ActivateSupplierRelationship
```

est d'abord un message applicatif représentant une intention.

Elle n'implique pas automatiquement :

- undo ;
- command object queueing ;
- command invoker ;
- receiver abstraction ;

au sens du GoF Command Pattern.

---

# 11. Query ≠ Repository Method

Une Query applicative :

```text
ListQualifiedSuppliers
```

n'est pas nécessairement une méthode :

```text
SupplierRepository.list_qualified_suppliers()
```

Le Query side peut utiliser :

- read models ;
- projections ;
- search indexes ;
- dedicated query ports.

Les repositories servent principalement les Aggregates du Command side.

---

# 12. Handler — définition retenue

Un Handler traduit une intention applicative en orchestration.

Flux type :

```text
Command
    │
    ▼
Handler
    │
    ├── validate application context
    ├── load aggregates
    ├── gather external facts
    ├── invoke domain behavior/policy
    ├── persist aggregates
    ├── commit
    ├── dispatch events
    └── return result
```

---

# 13. Handler Is Not Domain Service

Important :

```text
Application Handler
≠
Domain Service
```

## Handler

Orchestre :

```text
load
call
save
publish
```

## Domain Service

Porte une logique métier qui n'appartient naturellement à aucune Entity/Value Object.

---

# 14. Application Service ≠ Domain Service

Même distinction.

Un Application Service coordonne un use case.

Un Domain Service exprime une règle du métier.

Exemple :

```text
ActivateSupplierRelationshipHandler
    Application Service / Handler

SupplierEligibilityService
    possible Domain Service
```

si ce dernier est réellement justifié.

---

# 15. Commands should be immutable

Recommandation :

```python
@dataclass(frozen=True, slots=True)
class RegisterSupplier:
    legal_name: str
```

Pourquoi :

- intention stable ;
- simple à tester ;
- simple à logger/redacter ;
- simple à transporter ;
- évite mutation entre réception et traitement.

---

# 16. Commands should use application-friendly inputs

Une Command ne doit pas toujours exiger que l'appelant construise lui-même tous les Domain Value Objects.

Deux approches sont possibles.

## Strict domain input

```python
RegisterSupplier(
    identity=SupplierIdentity(...),
)
```

## Application input

```python
RegisterSupplier(
    legal_name="ACME",
    country_code="FR",
)
```

Le Handler construit alors les Value Objects.

Le choix doit équilibrer :

```text
ergonomics
vs
type safety
```

---

# 17. Command naming convention

Préférer un verbe métier explicite :

```text
RegisterSupplier
AddSupplierContact
CreateSupplierRelationship
InviteSupplierRelationship
RequestSupplierQualification
SuspendSupplierRelationship
```

Éviter :

```text
UpdateSupplier
ProcessSupplier
ExecuteSupplierAction
ChangeStatus
```

lorsqu'une intention métier plus précise existe.

---

# 18. Query naming convention

Préférer :

```text
GetSupplier
FindSupplierByExternalIdentifier
ListSupplierRelationships
GetRelationshipQualificationSummary
```

à :

```text
QuerySupplierData
GetData
FetchEverything
```

---

# 19. Application Result

Un Handler peut retourner un résultat applicatif.

Exemples :

```text
RegisterSupplierResult
ActivateSupplierRelationshipResult
SubmitSupplierDocumentResult
```

Le résultat peut transporter :

- IDs créés ;
- business decision ;
- state final ;
- warnings ;
- version éventuelle.

---

# 20. Command Result ≠ Domain Decision

Exemple :

```text
QualificationDecision
```

est un résultat métier produit par le domaine/policy.

```text
ApproveSupplierQualificationResult
```

peut être un résultat applicatif contenant :

```text
qualification_id
status
decision
```

Les deux niveaux ne doivent pas être confondus.

---

# 21. Actor Context

Certains use cases nécessitent un contexte d'acteur.

Exemple :

```text
actor_id
actor_type
reason
correlation_id
```

Ce contexte peut vivre dans :

- Command envelope ;
- ExecutionContext ;
- ApplicationContext.

Il ne doit pas transformer le Domain Model en IAM system.

---

# 22. ApplicationContext — candidate

Objet candidat :

```text
ApplicationContext
├── actor
├── correlation_id
├── causation_id?
├── locale?
└── request metadata?
```

À utiliser avec parcimonie.

Éviter un context object universel rempli de données cachées.

---

# 23. Explicit Dependencies

Les Handlers doivent recevoir explicitement leurs dépendances.

Exemple :

```python
class RegisterSupplierHandler:
    def __init__(
        self,
        repository: SupplierRepository,
        uow: UnitOfWork,
    ) -> None:
        ...
```

Éviter :

```text
global service locator
singleton container access
hidden database session
```

---

# 24. Core Application Ports

Ports candidats :

```text
SupplierRepository
SupplierRelationshipRepository
SupplierQualificationRepository
SupplierAssessmentRepository
RiskAssessmentRepository
SupplierIncidentRepository

UnitOfWork
Clock
EventPublisher

CompanyRegistryProvider
TaxValidationProvider
SanctionsScreeningProvider
RiskDataProvider
DocumentStorageProvider
```

---

# 25. Command-side Repository rule

Le Repository sert à :

```text
load Aggregate
save Aggregate
```

Il ne doit pas devenir l'API de toutes les lectures possibles.

---

# 26. Query-side Ports

Des ports dédiés peuvent exister :

```text
SupplierQueryService
SupplierRelationshipReadModel
SupplierSearchPort
```

ou des query handlers utilisant directement des adapters dédiés.

Le choix dépendra de l'implémentation.

---

# 27. Unit of Work — candidate

Le `UnitOfWork` devient pertinent si un use case doit coordonner :

- une transaction ;
- plusieurs repository writes ;
- commit/rollback ;
- event collection.

Conceptuellement :

```python
class UnitOfWork(Protocol):
    def commit(self) -> None:
        ...
```

La forme finale peut être plus riche.

---

# 28. Unit of Work is not mandatory ceremony

Ne pas créer un framework UoW complexe tant qu'un besoin transactionnel réel n'existe pas.

Pour un adapter InMemory :

```text
simple implementation
```

suffit.

---

# 29. Transaction Boundary

Une transaction applicative correspond généralement à :

```text
one business command
```

Exemple :

```text
ActivateSupplierRelationship
```

peut constituer une transaction.

Le Domain Layer ne gère pas la transaction technique.

---

# 30. Event dispatch boundary

Principe recommandé :

```text
domain operation
→ save
→ commit
→ dispatch external/integration effects
```

afin d'éviter de publier un événement externe pour une transaction finalement rollbackée.

---

# 31. Domain Events collection

Une Aggregate Root peut accumuler des Domain Events.

Le Handler ou UoW peut ensuite les collecter.

Exemple conceptuel :

```text
relationship.activate(...)
    records SupplierActivated

repository.save(...)
uow.commit()
dispatcher.dispatch(events)
```

---

# 32. Internal Event Handling

Certains Domain Events peuvent être traités in-process.

Exemple :

```text
SupplierQualified
    → evaluate activation readiness
```

Cette coordination appartient à l'Application Layer.

---

# 33. Integration Event Mapping

Un Domain Event peut être transformé en contrat externe.

```text
SupplierActivated
    │
    ▼
SupplierLifecycleActivatedV1
```

Le mapping ne doit pas vivre dans l'Aggregate.

---

# 34. Idempotency

Certaines Commands doivent supporter un rejeu sûr.

Exemples :

```text
RegisterSupplier
ActivateSupplierRelationship
SubmitSupplierDocument
ReportSupplierIncident
```

Selon les use cases, l'idempotency peut être :

- sémantique dans le domaine ;
- gérée par application idempotency key ;
- gérée par adapter.

---

# 35. Idempotency Key

Objet applicatif candidat :

```text
IdempotencyKey
```

À introduire uniquement pour les interfaces nécessitant réellement le rejeu.

---

# 36. Application Error Categories

Trois catégories principales :

```text
Domain Error
Application Error
Infrastructure Error
```

---

# 37. Domain Error

Exemples :

```text
InvalidLifecycleTransition
QualificationScopeRequired
ActivationRequirementsNotMet
SupplierAlreadyOffboarded
```

Produit par les règles métier.

---

# 38. Application Error

Exemples :

```text
SupplierNotFound
SupplierRelationshipNotFound
QualificationNotFound
DuplicateSupplierDetected
ApplicationConflict
```

Ils concernent le traitement du use case.

---

# 39. Infrastructure Error

Exemples :

```text
RepositoryUnavailable
ExternalProviderTimeout
DocumentStorageUnavailable
```

Ils doivent être traduits/propagés de façon contrôlée.

---

# 40. Error Translation

Le Handler peut traduire certaines erreurs techniques vers une erreur applicative stable.

Puis le Primary Adapter traduit en :

```text
HTTP response
CLI exit code
Agent tool result
```

Le Domain ne connaît pas ces protocoles.

---

# 41. Use Case Families

Les use cases sont regroupés par capability.

```text
Supplier Master
Supplier Organization
Supplier Contacts
Supplier Locations
Supplier Categories & Capabilities
Supplier Relationships & Lifecycle
Onboarding
Qualification
Documents
Certifications
Compliance
Risk
Assessments
Performance
Incidents
Segmentation
History & Audit
```

---

# 42. Supplier Master — Command Catalog

Commands candidates :

```text
RegisterSupplier
UpdateSupplierIdentity
AddSupplierExternalIdentifier
RemoveSupplierExternalIdentifier
AddSupplierCategory
RemoveSupplierCategory
AddSupplierCapability
RemoveSupplierCapability
ArchiveSupplier
```

---

# 43. RegisterSupplier

## Intent

Créer l'identité canonique d'un fournisseur.

## Inputs

Candidate :

```text
legal_name
trading_name?
supplier_type?
initial_external_identifiers?
country?
```

## Loads

```text
none
```

sauf duplicate detection éventuelle.
## Domain

```text
Supplier.create(...)
```

ou constructeur contrôlé.

## Persists

```text
Supplier
```

## Events

```text
SupplierCreated
or
SupplierRegistered
```

selon vocabulaire final.

## Result

```text
SupplierId
```

---

# 44. RegisterSupplier — duplicate detection

La détection de doublons peut nécessiter :

```text
find_by_external_identifier
```

avant création.

Important :

```text
duplicate detection
```

peut être une règle applicative/repository-assisted

et non un invariant purement interne à l'Aggregate.

---

# 45. RegisterSupplier — flow

```text
RegisterSupplier
    │
    ▼
RegisterSupplierHandler
    │
    ├── normalize/build inputs
    ├── check known identifiers
    ├── create Supplier
    ├── save
    ├── commit
    └── dispatch SupplierCreated
```

---

# 46. UpdateSupplierIdentity

## Intent

Modifier des informations master autorisées.

## Loads

```text
Supplier
```

## Domain behavior

Candidate :

```text
supplier.update_identity(...)
```

## Important

Éviter une Command générique :

```text
PatchSupplier(fields=dict)
```

pour les règles critiques.

---

# 47. AddSupplierExternalIdentifier

## Intent

Ajouter une référence externe au Supplier.

## Domain

```text
supplier.add_external_identifier(identifier)
```

L'Aggregate protège :

- duplicate local identifier ;
- validity.

---

# 48. RemoveSupplierExternalIdentifier

Doit vérifier :

- identifier exists ;
- removal does not violate required identity rule ;
- history/audit.

La suppression métier peut devenir :

```text
deactivate identifier
```

plutôt qu'effacement physique.

---

# 49. Supplier Master — Query Catalog

```text
GetSupplier
FindSupplierByExternalIdentifier
SearchSuppliers
ListSuppliers
GetSupplierMasterProfile
```

---

# 50. GetSupplier

Retourne une représentation du Supplier.

Ne doit pas forcément exposer directement l'Aggregate Python.

Pour une interface externe :

```text
SupplierView
```

est préférable.

---

# 51. FindSupplierByExternalIdentifier

Query très importante pour intégrations :

```text
ERP Vendor ID
Ivalua Supplier ID
SIREN
DUNS
```

Retour :

```text
SupplierSummary
or
SupplierId
```

---

# 52. SearchSuppliers

Peut utiliser un index/read model.

Critères potentiels :

```text
name
identifier
country
category
capability
relationship status
```

Ce n'est pas nécessairement une méthode `SupplierRepository`.

---

# 53. Supplier Contacts — Commands

```text
AddSupplierContact
UpdateSupplierContact
DeactivateSupplierContact
RemoveSupplierContact
AssignSupplierContactRole
```

---

# 54. AddSupplierContact

## Loads

```text
Supplier
```

## Domain behavior

```text
supplier.add_contact(...)
```

si Contact reste child Entity.

## Persists

```text
Supplier
```

---

# 55. Supplier Contacts — Queries

```text
ListSupplierContacts
GetSupplierContact
FindSupplierContactByEmail
```

Une Query dédiée peut utiliser une projection sans exposer le Supplier Aggregate complet.

---

# 56. Supplier Locations — Commands

```text
AddSupplierLocation
UpdateSupplierLocationAddress
DeactivateSupplierLocation
RemoveSupplierLocation
```

---

# 57. UpdateSupplierLocationAddress

Le Handler :

```text
loads Supplier
builds new Address VO
asks Supplier/Location to replace address
persists Supplier
```

---

# 58. Supplier Locations — Queries

```text
ListSupplierLocations
GetSupplierLocation
FindSuppliersByCountry
```

---

# 59. Supplier Organization — Commands

Selon la décision finale du modèle organisationnel :

```text
LinkSupplierParent
LinkSupplierSubsidiary
RemoveSupplierOrganizationLink
```

si les legal entities sont modélisées comme Suppliers distincts.

---

# 60. Supplier Organization — Queries

```text
GetSupplierOrganizationTree
ListSupplierAffiliates
GetSupplierParent
```

Le tree est probablement un read model/projection.

---

# 61. Supplier Relationship — Command Catalog

```text
CreateSupplierRelationship
InviteSupplierRelationship
StartSupplierOnboarding
MoveSupplierRelationshipToReview
ActivateSupplierRelationship
SuspendSupplierRelationship
BlockSupplierRelationship
ReactivateSupplierRelationship
DeactivateSupplierRelationship
OffboardSupplierRelationship
ChangeSupplierSegment
```

---

# 62. CreateSupplierRelationship

## Intent

Créer une relation entre :

```text
Supplier
+
InternalOrganization
```

## Inputs

```text
SupplierId
InternalOrganizationId
relationship_type?
initial_stage?
```

## Loads

```text
Supplier existence
existing relationship check
```

## Creates

```text
SupplierRelationship
```

## Events

Candidate :

```text
SupplierRelationshipCreated
```

---

# 63. Relationship uniqueness check

Le Handler peut vérifier via Repository :

```text
relationship already exists?
```

L'Aggregate nouveau ne peut pas connaître toutes les autres Relationships existantes.

C'est donc un exemple de règle :

```text
application + repository
```

---

# 64. InviteSupplierRelationship

## Loads

```text
SupplierRelationship
```

## Domain

```text
relationship.invite(...)
```

## Guard

Transition valide depuis état autorisé.

## Event

```text
SupplierInvited
```

---

# 65. StartSupplierOnboarding

## Loads

```text
SupplierRelationship
```

et éventuellement onboarding courant.

## Domain

- transition lifecycle ;
- create `SupplierOnboarding` si modèle séparé.

## Event

```text
SupplierOnboardingStarted
```

---

# 66. ActivateSupplierRelationship

Use case central.

Inputs :

```text
relationship_id
reason?
actor context
```

Needs current facts:

```text
qualification status
compliance status
risk status
required document status
```

---

# 67. Activation orchestration

```text
ActivateSupplierRelationship
        │
        ▼
Handler
        │
        ├── load Relationship
        ├── query qualification facts
        ├── query compliance facts
        ├── query risk facts
        ├── query document readiness
        ├── build ActivationContext
        ├── ActivationPolicy.evaluate(...)
        ├── relationship.activate(decision)
        ├── save
        ├── commit
        └── publish events
```

---

# 68. ActivationContext

Candidate immutable object:

```text
ActivationContext
├── valid_qualifications
├── compliance_summary
├── risk_summary
├── document_requirements
└── evaluation_time
```

Il représente les faits requis par une décision.

---

# 69. ActivationPolicy

La policy produit :

```text
ActivationDecision
```

Le Handler ne code pas :

```python
if qualified and compliant and risk < 80:
    ...
```

si cette logique appartient au métier configurable.

---

# 70. SuspendSupplierRelationship

## Inputs

```text
relationship_id
reason
effective_at?
```

## Domain

```text
relationship.suspend(...)
```

## Event

```text
SupplierSuspended
```

## Important

La suspension d'une Relationship ne suspend pas toutes les Relationships du Supplier.

---

# 71. BlockSupplierRelationship

Différencier sémantiquement :

```text
SUSPENDED
```

et :

```text
BLOCKED
```

Le `07` doit définir leurs règles.

Le Handler n'invente pas cette différence.

---

# 72. ReactivateSupplierRelationship

Peut nécessiter de reconstruire un `ActivationContext`.

Une réactivation ne signifie pas :

```text
status = ACTIVE
```

sans revalidation.

---

# 73. OffboardSupplierRelationship

## Domain effects

```text
relationship lifecycle → OFFBOARDED
```

## Not domain effects

Ne doit pas :

```text
delete Supplier
delete all evidence
delete history
```

---

# 74. Relationship — Query Catalog

```text
GetSupplierRelationship
ListSupplierRelationships
ListRelationshipsByOrganization
GetRelationshipLifecycle
GetRelationshipReadiness
GetRelationship360
```

---

# 75. GetRelationshipReadiness

Projection/read model utile :

```text
lifecycle stage
qualification readiness
document readiness
compliance readiness
risk readiness
activation readiness
```

Très utile pour :

- UI ;
- agents ;
- workflows.

---

# 76. Onboarding — Command Catalog

```text
CreateSupplierOnboarding
StartSupplierOnboarding
RecordOnboardingRequirement
SatisfyOnboardingRequirement
RejectOnboardingRequirement
CompleteSupplierOnboarding
CancelSupplierOnboarding
```

La granularité finale dépendra du modèle `OnboardingRequirement`.

---

# 77. Onboarding is not Workflow

Les Commands d'onboarding représentent des **faits métier**.

Éviter :

```text
AssignOnboardingTaskToJohn
SendReminderToReviewer
EscalateAfter24Hours
```

qui appartiennent plutôt au workflow.

---

# 78. CompleteSupplierOnboarding

Peut nécessiter :

```text
all mandatory requirements satisfied
```

Le Handler charge les faits nécessaires.

Le domaine/onboarding protège sa règle de complétude.

---

# 79. Onboarding — Queries

```text
GetSupplierOnboarding
GetOnboardingProgress
ListMissingOnboardingRequirements
ListCurrentOnboardings
```

---

# 80. Qualification — Command Catalog

```text
RequestSupplierQualification
ApproveSupplierQualification
RejectSupplierQualification
RevokeSupplierQualification
ExpireSupplierQualification
RenewSupplierQualification
```

---

# 81. RequestSupplierQualification

## Inputs

```text
relationship_id
qualification_scope
```

## Loads

```text
SupplierRelationship
current qualification for scope?
```

## Creates

```text
SupplierQualification
```

## Event

```text
SupplierQualificationRequested
```

---

# 82. Qualification uniqueness

Le Handler peut vérifier :

```text
existing current qualification for same relationship + scope
```

avant création.

Cette règle traverse plusieurs aggregate instances et peut nécessiter Repository lookup.

---

# 83. ApproveSupplierQualification

Deux formes possibles.

## Command expresses decision already made

```text
ApproveSupplierQualification
```

si l'approbation humaine est externe.

## Command requests evaluation

```text
EvaluateSupplierQualification
```

si PySRMKit doit calculer la décision.

Les deux use cases ne doivent pas être mélangés.

---

# 84. EvaluateSupplierQualification

Candidate use case :

```text
load qualification
load supplier/relationship facts
collect required evidence
QualificationPolicy.evaluate(...)
qualification.apply_decision(...)
save
publish
```

---

# 85. QualificationPolicy flow

```text
Qualification Context
        │
        ▼
QualificationPolicy
        │
        ▼
QualificationDecision
        │
        ▼
SupplierQualification
        │
        ▼
State transition
```

---

# 86. RejectSupplierQualification

Doit conserver :

```text
reason
decision
evidence
decided_at
```

selon modèle final.

---

# 87. RevokeSupplierQualification

Distinct de :

```text
Reject
Expire
```

Le domaine doit refléter cette différence.

---

# 88. ExpireSupplierQualification

Peut être déclenché :

- par job planifié ;
- lors d'une query/command ;
- par temporal rule.

PyScheduleKit peut planifier la détection.

PySRMKit porte la règle d'expiration.

---

# 89. RenewSupplierQualification

Deux stratégies :

```text
mutate same Qualification
```

ou :

```text
create new Qualification instance
```

Le `07` doit définir l'invariant historique.

---

# 90. Qualification — Query Catalog

```text
GetSupplierQualification
ListSupplierQualifications
ListQualifiedScopes
ListExpiringQualifications
ListExpiredQualifications
IsSupplierQualified
GetQualificationDecisionExplanation
```

---

# 91. IsSupplierQualified

Cette Query doit exiger un scope.

Éviter :

```text
is supplier qualified?
```

sans contexte.

---

# 92. Qualification Summary Read Model

```text
QualificationSummary
├── scope
├── status
├── valid_from
├── valid_until
├── decision_reasons
└── current
```

---

# 93. Documents — Command Catalog

```text
RegisterSupplierDocument
VerifySupplierDocument
RejectSupplierDocument
SupersedeSupplierDocument
ExpireSupplierDocument
RemoveSupplierDocumentReference
```

---

# 94. RegisterSupplierDocument

## Inputs

```text
supplier/relationship context
document_type
document_reference
issue_date?
expiration_date?
issuer?
```

## Important

Le Handler ne stocke pas nécessairement le fichier.

Un Primary Adapter peut :

1. stocker le fichier via `DocumentStoragePort` ;
2. obtenir `DocumentReference` ;
3. exécuter `RegisterSupplierDocument`.

---

# 95. Upload vs Register

Distinction utile :

```text
UploadDocument
    infrastructure/application concern

RegisterSupplierDocument
    supplier-domain concern
```

---

# 96. VerifySupplierDocument

Peut s'appuyer sur :

- human review ;
- external provider ;
- automated validation.

Mais le résultat final devient :

```text
business verification status
```

dans PySRMKit.

---

# 97. SupersedeSupplierDocument

Doit préserver :

```text
old document history
```

et lier éventuellement :
```text
new document
```

comme replacement.

---

# 98. Documents — Query Catalog

```text
GetSupplierDocument
ListSupplierDocuments
ListRequiredDocuments
ListMissingRequiredDocuments
ListExpiringSupplierDocuments
ListExpiredSupplierDocuments
GetDocumentVerificationStatus
```

---

# 99. ListRequiredDocuments

Cette Query peut utiliser :

```text
DocumentRequirementPolicy
```

avec :

- country ;
- category ;
- supplier type ;
- relationship ;
- risk.

---

# 100. Certifications — Command Catalog

```text
RegisterSupplierCertification
VerifySupplierCertification
RevokeSupplierCertification
ExpireSupplierCertification
RenewSupplierCertification
```

---

# 101. RegisterSupplierCertification

Chaque issuance peut créer une nouvelle Entity si l'historique doit être préservé.

---

# 102. Certifications — Queries

```text
GetSupplierCertification
ListSupplierCertifications
ListValidSupplierCertifications
ListExpiringSupplierCertifications
ListExpiredSupplierCertifications
```

---

# 103. Compliance — Command Catalog

```text
RecordComplianceCheck
EvaluateSupplierCompliance
ApproveSupplierCompliance
RejectSupplierCompliance
ScheduleComplianceReview
```

Les noms finaux dépendent du modèle `ComplianceCheck` vs `ComplianceDecision`.

---

# 104. RecordComplianceCheck

## Intent

Enregistrer une vérification réelle.

Inputs :

```text
relationship_id
requirement_code
performed_at
source
result
evidence_refs
```

---

# 105. EvaluateSupplierCompliance

Peut agréger plusieurs checks/evidences.

```text
current requirements
+
evidence
+
checks
        │
        ▼
CompliancePolicy
        │
        ▼
ComplianceDecision
```

---

# 106. External compliance providers

Un Handler peut appeler :

```text
SanctionsScreeningProvider
TaxValidationProvider
CompanyRegistryProvider
```

Puis transformer leurs réponses en :

```text
evidence/check data
```

avant de laisser le domaine décider.

---

# 107. Provider data ≠ Compliance decision

Règle importante :

```text
external provider says X
```

n'est pas automatiquement :

```text
domain is compliant
```

---

# 108. Compliance — Query Catalog

```text
GetRelationshipComplianceStatus
ListComplianceChecks
ListFailedComplianceRequirements
ListPendingComplianceRequirements
GetComplianceDecisionExplanation
```

---

# 109. Risk — Command Catalog

```text
RecordRiskAssessment
ReassessSupplierRisk
AddRiskMitigation
CloseRiskMitigation
```

Les mitigations restent conditionnelles au modèle final.

---

# 110. RecordRiskAssessment

Inputs :

```text
supplier/relationship
risk_type
score
level?
source
assessed_at
evidence_refs
```

Creates :

```text
RiskAssessment
```

---

# 111. ReassessSupplierRisk

Peut appeler :

```text
RiskDataProvider
```

puis :

```text
RiskPolicy
```

et créer une nouvelle `RiskAssessment`.

Ne doit pas écraser l'histoire.

---

# 112. Risk evaluation flow

```text
External/Internal Risk Evidence
        │
        ▼
Application Handler
        │
        ▼
RiskPolicy
        │
        ▼
RiskDecision
        │
        ▼
RiskAssessment / Relationship follow-up
```

---

# 113. Risk — Query Catalog

```text
GetSupplierRiskProfile
GetRelationshipRiskProfile
ListRiskAssessments
GetCurrentRiskLevel
ListHighRiskSuppliers
ListSuppliersRequiringRiskReview
```

---

# 114. Current risk

`GetCurrentRiskLevel` est typiquement une Query/projection basée sur le dernier `RiskAssessment` valide.

Le Domain Model conserve l'historique.

---

# 115. Assessments — Command Catalog

```text
CreateSupplierAssessment
RecordAssessmentAnswer
AttachAssessmentEvidence
ScoreSupplierAssessment
CompleteSupplierAssessment
CancelSupplierAssessment
```

---

# 116. CreateSupplierAssessment

Inputs :

```text
supplier/relationship context
assessment_type
question snapshot/template reference
period?
```

Creates :

```text
SupplierAssessment
```

---

# 117. RecordAssessmentAnswer

Si `AssessmentAnswer` reste child Value Object/Entity :

```text
load Assessment
assessment.record_answer(...)
save Assessment
```

---

# 118. ScoreSupplierAssessment

Peut utiliser :

- deterministic scoring rule ;
- policy ;
- external analyzer.

Le résultat métier reste explicite :

```text
AssessmentScore
```

---

# 119. CompleteSupplierAssessment

Doit vérifier :

```text
mandatory questions answered
required evidence present
score coherent
decision valid
```

selon invariants.

---

# 120. Assessments — Query Catalog

```text
GetSupplierAssessment
ListSupplierAssessments
ListOpenAssessments
GetAssessmentProgress
GetAssessmentResult
```

---

# 121. Performance — Command Catalog

```text
RecordSupplierPerformance
RecordPerformanceMeasurement
RecalculateSupplierScorecard
PublishSupplierScorecard
```

Les deux dernières ne sont nécessaires que si Scorecard devient persisted/published artifact.

---

# 122. RecordPerformanceMeasurement

Inputs :

```text
supplier/relationship
metric
value
period
source
recorded_at
```

Creates append-only measurement candidate.

---

# 123. RecalculateSupplierScorecard

Si Scorecard reste projection :

```text
Query
```

est peut-être plus appropriée que Command.

Si Scorecard est persistée/versionnée :

```text
Command
```

peut être justifiée.

---

# 124. Performance — Query Catalog

```text
GetSupplierPerformance
GetSupplierScorecard
ListPerformanceMeasurements
GetPerformanceTrend
CompareSupplierPerformance
```

---

# 125. Incidents — Command Catalog

```text
ReportSupplierIncident
UpdateSupplierIncident
EscalateSupplierIncident
ResolveSupplierIncident
CloseSupplierIncident
```

La taxonomie finale dépendra du lifecycle Incident.

---

# 126. ReportSupplierIncident

Inputs :

```text
supplier_id
relationship_id?
incident_type
severity
occurred_at
description
evidence_refs
```

Creates :

```text
SupplierIncident
```

Emits :

```text
SupplierIncidentReported
```

---

# 127. Incident side effects

Le Handler `ReportSupplierIncident` ne doit pas directement :

```text
change qualification
change risk level
suspend relationship
```

Ces effets passent par :

- Domain Event handlers ;
- explicit subsequent commands ;
- policies.

---

# 128. Incident reaction flow

```text
ReportSupplierIncident
        │
        ▼
SupplierIncidentReported
        │
        ├──► ReassessSupplierRisk
        ├──► ReevaluateQualification
        └──► ConsiderRelationshipSuspension
```

---

# 129. ResolveSupplierIncident

Met à jour uniquement l'Aggregate Incident.

Des réactions externes peuvent suivre par event.

---

# 130. Incidents — Query Catalog

```text
GetSupplierIncident
ListSupplierIncidents
ListOpenSupplierIncidents
GetIncidentHistory
GetSupplierIncidentRate
```

---

# 131. Segmentation — Command Catalog

Deux modèles.

## Explicit assignment

```text
AssignSupplierSegment
```

## Policy-based calculation

```text
EvaluateSupplierSegmentation
```

Les deux peuvent coexister selon règles métier.

---

# 132. EvaluateSupplierSegmentation

Flow :

```text
collect inputs
    purchase context
    risk
    performance
    dependency
        │
        ▼
SegmentationPolicy
        │
        ▼
SegmentationDecision
        │
        ▼
SupplierRelationship.change_segment(...)
```

---

# 133. Segmentation — Queries

```text
GetSupplierSegment
ListSuppliersBySegment
ExplainSupplierSegmentation
```

---

# 134. History & Audit — Query Catalog

```text
GetSupplierHistory
GetSupplierRelationshipHistory
GetQualificationHistory
GetRiskHistory
GetIncidentHistory
GetAuditTrail
```

---

# 135. History is Query-oriented

L'historique est principalement lu via :

- domain events ;
- audit records ;
- temporal persistence.

Éviter un `History` Aggregate géant.

---

# 136. Domain Event Query

Un système peut exposer :

```text
ListDomainEventsForAggregate
```

mais cette API relève souvent de l'audit/infrastructure, pas du core public.

---

# 137. Use Case Catalog — Supplier Master

| Use Case | Type | Main Aggregate |
|---|---|---|
| RegisterSupplier | Command | Supplier |
| UpdateSupplierIdentity | Command | Supplier |
| AddExternalIdentifier | Command | Supplier |
| AddSupplierContact | Command | Supplier |
| AddSupplierLocation | Command | Supplier |
| AddSupplierCategory | Command | Supplier |
| AddSupplierCapability | Command | Supplier |
| GetSupplier | Query | Read model |
| SearchSuppliers | Query | Read model |
| FindSupplierByExternalIdentifier | Query | Read model/repository lookup |

---

# 138. Use Case Catalog — Relationship

| Use Case | Type | Main Aggregate |
|---|---|---|
| CreateSupplierRelationship | Command | SupplierRelationship |
| InviteSupplierRelationship | Command | SupplierRelationship |
| StartSupplierOnboarding | Command | Relationship/Onboarding |
| ActivateSupplierRelationship | Command | SupplierRelationship |
| SuspendSupplierRelationship | Command | SupplierRelationship |
| BlockSupplierRelationship | Command | SupplierRelationship |
| ReactivateSupplierRelationship | Command | SupplierRelationship |
| OffboardSupplierRelationship | Command | SupplierRelationship |
| GetSupplierRelationship | Query | Read model |
| GetRelationshipReadiness | Query | Projection |

---

# 139. Use Case Catalog — Qualification

| Use Case | Type | Main Aggregate |
|---|---|---|
| RequestSupplierQualification | Command | SupplierQualification |
| EvaluateSupplierQualification | Command | SupplierQualification |
| ApproveSupplierQualification | Command | SupplierQualification |
| RejectSupplierQualification | Command | SupplierQualification |
| RevokeSupplierQualification | Command | SupplierQualification |
| RenewSupplierQualification | Command | SupplierQualification |
| GetSupplierQualification | Query | Read model |
| IsSupplierQualified | Query | Projection/domain read |
| ListExpiringQualifications | Query | Projection |

---

# 140. Use Case Catalog — Documents / Certifications

| Use Case | Type |
|---|---|
| RegisterSupplierDocument | Command |
| VerifySupplierDocument | Command |
| RejectSupplierDocument | Command |
| SupersedeSupplierDocument | Command |
| RegisterSupplierCertification | Command |
| VerifySupplierCertification | Command |
| RevokeSupplierCertification | Command |
| ListRequiredDocuments | Query |
| ListExpiringDocuments | Query |
| ListValidCertifications | Query |

---

# 141. Use Case Catalog — Compliance / Risk

| Use Case | Type |
|---|---|
| RecordComplianceCheck | Command |
| EvaluateSupplierCompliance | Command |
| RecordRiskAssessment | Command |
| ReassessSupplierRisk | Command |
| GetRelationshipComplianceStatus | Query |
| GetSupplierRiskProfile | Query |
| ListHighRiskSuppliers | Query |

---

# 142. Use Case Catalog — Assessment / Performance / Incident

| Use Case | Type |
|---|---|
| CreateSupplierAssessment | Command |
| RecordAssessmentAnswer | Command |
| CompleteSupplierAssessment | Command |
| RecordPerformanceMeasurement | Command |
| ReportSupplierIncident | Command |
| ResolveSupplierIncident | Command |
| GetAssessmentResult | Query |
| GetSupplierScorecard | Query |
| ListOpenIncidents | Query |

---

# 143. Traceability to Functional Requirements

```text
FR-001 Create Supplier
    → RegisterSupplier

FR-002 Enrich supplier identity
    → UpdateSupplierIdentity

FR-003 Manage identifiers
    → Add/RemoveSupplierExternalIdentifier

FR-004 Supplier organization
    → LinkSupplierParent / organization queries

FR-005 Contacts
    → Add/Update/DeactivateSupplierContact

FR-006 Locations
    → Add/UpdateSupplierLocation

FR-007 Categories
    → Add/RemoveSupplierCategory

FR-008 Capabilities
    → Add/RemoveSupplierCapability

FR-009 Lifecycle
    → relationship lifecycle commands

FR-010/011 Onboarding
    → Start/Complete onboarding + progress queries

FR-012/013/014 Qualification
    → qualification commands

FR-015/016 Documents
    → document commands/queries

FR-017 Certifications
    → certification commands/queries

FR-018 Compliance
    → Record/EvaluateCompliance

FR-019/020 Risk
    → Record/ReassessRisk

FR-021/022 Assessment
    → Create/CompleteAssessment

FR-023 Performance
    → RecordPerformanceMeasurement

FR-024 Scorecard
    → Get/RecalculateScorecard

FR-025 Incident
    → Report/ResolveIncident

FR-026 Segmentation
    → Evaluate/AssignSegment

FR-027/028/029/030
    → Suspend/Block/Reactivate/OffboardRelationship

FR-031 History
    → history/audit queries

FR-032 Domain Events
    → command-side event dispatch
```

---

# 144. Use Case Template

Chaque use case important pourra être documenté selon :

```text
Name
Intent
Command/Query
Actor
Inputs
Preconditions
Aggregate(s)
Repositories
Policies
External Ports
Transaction Boundary
Domain Behavior
Events
Result
Errors
Idempotency
Audit
Tests
```

---

# 145. Detailed Use Case — Register Supplier

## Intent

Créer un Supplier canonique.

## Actor

```text
Supplier Manager
System
Integration
Agent via authorized application tool
```

## Command

```text
RegisterSupplier
```

## Preconditions

Candidate :

```text
required identity data valid
no forbidden duplicate known identifier
```

## Aggregate

```text
Supplier
```

## Repository

```text
SupplierRepository
```

## Domain behavior

```text
Supplier.create(...)
```

## Events

```text
SupplierCreated
```

## Result

```text
SupplierId
```

## Errors

```text
InvalidSupplierIdentity
DuplicateExternalIdentifier
```

---

# 146. Detailed Use Case — Create Supplier Relationship

## Intent

Créer une relation entre Supplier et organisation interne.

## Command

```text
CreateSupplierRelationship
```

## Preconditions

```text
Supplier exists
InternalOrganization reference valid
relationship uniqueness rule satisfied
```

## Aggregate

```text
SupplierRelationship
```

## Repository

```text
SupplierRepository
SupplierRelationshipRepository
```

## Event

```text
SupplierRelationshipCreated
```

---

# 147. Detailed Use Case — Activate Supplier Relationship

## Intent

Autoriser la relation fournisseur à devenir opérationnelle.

## Command

```text
ActivateSupplierRelationship
```

## Preconditions

```text
relationship in activatable lifecycle stage
```

## Facts required

```text
qualification readiness
compliance readiness
risk readiness
document readiness
```

## Policy

```text
ActivationPolicy
```

## Domain

```text
SupplierRelationship.activate(decision)
```

## Event

```text
SupplierActivated
```

## Errors

```text
RelationshipNotFound
InvalidLifecycleTransition
ActivationRequirementsNotMet
```

---

# 148. Detailed Use Case — Request Qualification

## Intent

Créer une qualification pour un scope.

## Command

```text
RequestSupplierQualification
```

## Aggregate

```text
SupplierQualification
```

## Preconditions

```text
relationship exists
scope valid
no conflicting current qualification
```

## Event

```text
SupplierQualificationRequested
```

---

# 149. Detailed Use Case — Evaluate Qualification
## Intent

Calculer une décision selon une policy.

## Command

```text
EvaluateSupplierQualification
```

## Dependencies

```text
SupplierQualificationRepository
QualificationPolicy
Evidence/read ports
Clock
```

## Result

```text
QualificationDecision
```

## Domain transition

```text
apply decision
```

## Event

```text
SupplierQualified
or
SupplierQualificationRejected
```

---

# 150. Detailed Use Case — Record Risk Assessment

## Intent

Ajouter une évaluation temporelle de risque.

## Command

```text
RecordRiskAssessment
```

## Aggregate

```text
RiskAssessment
```

## Domain rule

```text
assessment timestamp required
risk values valid
```

## Event

```text
SupplierRiskDetected
or
SupplierRiskChanged
```

selon design final.

---

# 151. Detailed Use Case — Report Incident

## Intent

Enregistrer un incident fournisseur.

## Command

```text
ReportSupplierIncident
```

## Aggregate

```text
SupplierIncident
```

## Event

```text
SupplierIncidentReported
```

## Subsequent reactions

```text
risk reassessment
qualification review
suspension consideration
```

via application/event handling.

---

# 152. Query Models

Les Queries peuvent retourner des objets spécialisés :

```text
SupplierView
SupplierSummary
SupplierRelationshipView
QualificationSummary
RiskProfileView
ComplianceSummary
SupplierScorecardView
Supplier360View
```

Ces objets sont :

```text
read models
```

et non Entities.

---

# 153. SupplierView

Candidate :

```text
supplier_id
legal_name
trading_name
identifiers
categories
capabilities
contacts
locations
```

---

# 154. SupplierRelationshipView

Candidate :

```text
relationship_id
supplier_id
organization_id
lifecycle_stage
segment
activation_readiness
```

---

# 155. QualificationSummary

Candidate :

```text
qualification_id
scope
status
validity
decision_summary
```

---

# 156. RiskProfileView

Candidate :

```text
current risk levels
latest assessments
trend
review_due
```

---

# 157. Supplier360View

Projection composite :

```text
Supplier identity
Relationships
Qualifications
Compliance
Risk
Documents
Certifications
Performance
Incidents
```

## Important

```text
Supplier360View
≠
Supplier Aggregate
```

---

# 158. Query Optimization

Query side peut utiliser :

- denormalized projections ;
- indexes ;
- caches ;
- search engines ;
- SQL joins ;
- Snowflake analytical views.

Ces optimisations ne déterminent pas le Command-side Domain Model.

---

# 159. Query consistency

Certaines Queries peuvent être :

```text
eventually consistent
```

Exemple :

```text
Supplier360View
```

Mais une Command critique doit revalider les faits nécessaires si un invariant fort en dépend.

---

# 160. Authorization Boundary

Avant un Handler :

```text
Can actor invoke this use case?
```

Application/IAM concern.

Dans le Domain :

```text
Is the requested business transition valid?
```

Domain concern.

---

# 161. Example authorization flow

```text
API
 │
 ├── authenticate
 ├── authorize actor for "supplier:activate"
 │
 ▼
ActivateSupplierRelationshipHandler
 │
 ▼
Domain checks activation rules
```

---

# 162. Agent Tool Boundary

Un Agent Tool doit appeler un use case.

Bon :

```text
activate_supplier_relationship_tool
    → ActivateSupplierRelationship
```

Mauvais :

```text
agent
    → repository.save()
```

---

# 163. Agent Query Tools

Queries particulièrement adaptées :

```text
GetSupplier360
GetRelationshipReadiness
ListMissingDocuments
ExplainQualificationDecision
GetSupplierRiskProfile
```

---

# 164. Explainability

Les Queries peuvent exposer les raisons des décisions.

Exemple :

```text
ExplainSupplierActivationReadiness
```

Retour :

```text
allowed
failed_rules
missing_documents
qualification_issues
risk_issues
```

---

# 165. Commands should not be CRUD mirrors

Éviter :

```text
CreateQualification
UpdateQualification
DeleteQualification
```

si le métier possède des intentions plus précises :

```text
Request
Approve
Reject
Revoke
Renew
```

---

# 166. Business verbs over CRUD verbs

Principe :

```text
business verb
>
generic persistence verb
```

Cela rend le modèle plus expressif et pédagogique.

---

# 167. Generic Update anti-pattern

Une Command :

```text
UpdateSupplier(payload: dict)
```

risque de contourner :

- invariants ;
- audit ;
- intent ;
- authorization fine-grained.

Utiliser des Commands spécifiques pour les modifications significatives.

---

# 168. Fine-grained vs excessive Commands

Attention inverse :

Ne pas créer :

```text
ChangeSupplierLegalName
ChangeSupplierTradingName
ChangeSupplierDescription
```

si :

```text
UpdateSupplierIdentity
```

est un use case cohésif suffisant.

KISS s'applique.

---

# 169. Command granularity heuristic

Une Command mérite un nom propre si :

- l'intention métier est distincte ;
- les règles sont distinctes ;
- l'autorisation est distincte ;
- l'audit doit distinguer l'action ;
- les events sont distincts.

---

# 170. Query granularity heuristic

Une Query mérite un nom propre si :

- le consumer exprime une vraie question métier ;
- la projection est stable ;
- le coût/forme de lecture diffère.

---

# 171. Handler granularity

Par défaut :

```text
one handler
per command/query
```

est simple et explicite.

Mais un même Application Service peut regrouper plusieurs use cases si cela reste cohésif.

---

# 172. Avoid God Application Service

Éviter :

```text
SupplierService
    register
    qualify
    assess
    risk
    incident
    performance
    documents
    ...
```

Cela détruit les frontières de capability.

---

# 173. Capability-oriented handlers

Préférer :

```text
supplier/master/
relationship/
qualification/
risk/
assessment/
incident/
```

selon package topology final.

---

# 174. Suggested Application Package — layer-first

```text
application/
├── commands/
│   ├── supplier/
│   ├── relationship/
│   ├── onboarding/
│   ├── qualification/
│   ├── compliance/
│   ├── risk/
│   ├── assessment/
│   ├── performance/
│   └── incident/
├── queries/
├── handlers/
├── dto/
└── results/
```

---

# 175. Suggested Application Package — vertical slices

Alternative :

```text
supplier/
├── domain/
└── application/
    ├── register_supplier.py
    ├── update_identity.py
    └── get_supplier.py

qualification/
├── domain/
└── application/
    ├── request.py
    ├── evaluate.py
    └── query.py
```

Le choix reste ouvert.

---

# 176. Vertical Slice advantage

Regroupe :

```text
command
handler
result
tests
```

près du use case.

Peut améliorer la navigation.

---

# 177. Layer-first advantage

Rend la séparation architecturale très visible.

Utile pédagogiquement.

Le choix final devra privilégier la cohésion réelle.

---

# 178. Python Command Example

```python
@dataclass(frozen=True, slots=True)
class CreateSupplierRelationship:
    supplier_id: SupplierId
    organization_id: InternalOrganizationId
```

---

# 179. Python Handler Example

```python
class CreateSupplierRelationshipHandler:
    def __init__(
        self,
        supplier_repository: SupplierRepository,
        relationship_repository: SupplierRelationshipRepository,
        uow: UnitOfWork,
    ) -> None:
        self._supplier_repository = supplier_repository
        self._relationship_repository = relationship_repository
        self._uow = uow

    def handle(
        self,
        command: CreateSupplierRelationship,
    ) -> SupplierRelationshipId:
        ...
```

Illustratif, non normatif.

---

# 180. Handler orchestration example

Pseudo-code :

```text
supplier = suppliers.get(command.supplier_id)

if supplier is None:
    raise SupplierNotFound

if relationships.exists(...):
    raise RelationshipAlreadyExists

relationship = SupplierRelationship.create(...)

relationships.save(relationship)
uow.commit()

dispatch(relationship.pull_events())

return relationship.id
```

---

# 181. What is business logic here?

Dans l'exemple :

```text
SupplierRelationship.create(...)
```

porte les invariants locaux.

La vérification :

```text
relationship already exists across repository
```

est une règle traversant les instances et doit être coordonnée applicativement.

---

# 182. Query Handler Example

```python
class GetSupplierRelationshipHandler:
    def __init__(
        self,
        reader: SupplierRelationshipReader,
    ) -> None:
        self._reader = reader

    def handle(
        self,
        query: GetSupplierRelationship,
    ) -> SupplierRelationshipView:
        ...
```

Aucun Aggregate complet n'est forcément nécessaire.

---

# 183. Command Bus — optional

Un Command Bus peut permettre :

```text
dispatch(command)
```

Mais il ne doit pas être introduit uniquement pour ressembler à une architecture CQRS.

Direct handler invocation est acceptable :

```python
handler.handle(command)
```

---

# 184. Query Bus — optional

Même règle.

```text
query_bus.ask(query)
```

peut être utile à grande échelle.

Mais ajoute :

- indirection ;
- registry ;
- debugging complexity.

YAGNI s'applique.

---

# 185. Mediator pattern — not assumed

Utiliser un mediator library ne signifie pas que l'architecture est meilleure.

Le besoin doit précéder l'outil.

---

# 186. Application pipeline behaviors — optional

Future needs possibles :

```text
validation
authorization
logging
tracing
idempotency
transaction handling
```

peuvent être ajoutés autour des handlers.

Mais éviter une pipeline framework complexe au MVP.

---

# 187. Input validation layers

Trois niveaux :

## Transport validation

```text
JSON shape
required HTTP field
```

## Application validation

```text
referenced supplier exists
command context coherent
```

## Domain validation

```text
qualification scope valid
transition allowed
```

---

# 188. Structural validation

Les Value Objects peuvent valider :

```text
CountryCode
DateRange
RiskScore
```

au moment de construction.

---

# 189. Application preconditions

Exemples :

```text
Supplier exists
Relationship exists
No duplicate active qualification
```

---

# 190. Domain preconditions

Exemples :

```text
Relationship stage allows activation
Qualification can be revoked
Document validity period coherent
```

---

# 191. Postconditions

Un Handler peut vérifier implicitement via le domaine :

```text
after successful ActivateSupplierRelationship
stage == ACTIVE
SupplierActivated event recorded
```

Les postconditions métier appartiennent au Domain behavior.

---

# 192. Retry semantics

Un Handler peut être rejoué après failure.

Il faut distinguer :

```text
retry technical failure
```

de :

```text
repeat business intent
```

L'idempotency doit être conçue par use case.

---

# 193. Timeout and cancellation

Concernent surtout les appels externes :

```text
RiskDataProvider
SanctionsScreeningProvider
DocumentStorage
```

Le Domain Model ne porte pas les timeouts.

---

# 194. External call ordering

Pour une Command nécessitant un provider externe :

```text
external call before transaction?
inside transaction?
after transaction?
```

doit être choisi consciemment.

Éviter de tenir une transaction DB ouverte pendant un appel réseau long si possible.

---

# 195. Example — sanctions check

Approche :

```text
1. call provider
2. map evidence
3. open transaction
4. record compliance check
5. commit
```

selon besoin de cohérence.

---

# 196. Application Saga — future candidate

Des workflows multi-command longs pourraient nécessiter une Saga/Process Manager.

Exemple :

```text
complete onboarding
→ qualification
→ compliance
→ activation
```

Mais :

> **Do not introduce Saga infrastructure until long-running cross-aggregate coordination is real.**

---

# 197. Process Manager vs Domain Service

Un Process Manager :

```text
coordinates events and commands over time
```

Un Domain Service :

```text
executes domain logic
```

Ne pas les confondre.

---

# 198. Onboarding Process Manager — candidate

Future candidate if onboarding becomes long-running:

```text
SupplierOnboardingProcess
```

peut réagir aux events :

```text
DocumentVerified
ComplianceApproved
QualificationApproved
```

et déclencher la suite.

Pas nécessaire au MVP initial.

---

# 199. Scheduled Use Cases

Jobs planifiés peuvent invoquer :

```text
ExpireQualifications
ExpireDocuments
ExpireCertifications
ScheduleRiskReviews
```

Mais PyScheduleKit gère :

```text
when
```

PySRMKit gère :

```text
what the business action means
```

---

# 200. Batch Commands

Pour des traitements bulk :

```text
ExpireQualifications
```

peut être un Application Job qui :

1. Query candidates ;
2. envoie une Command par Aggregate.

Éviter une mutation SQL directe contournant le domaine si des invariants/events sont requis.

---

# 201. Bulk operations

Une bulk API peut exister :

```text
BulkRegisterSuppliers
```

mais doit définir :
- atomicity ;
- partial failure ;
- event semantics ;
- idempotency.

Le MVP peut rester single-aggregate command first.

---

# 202. Application Facade

Une façade Python ergonomique peut exposer :

```python
srm.register_supplier(...)
srm.create_relationship(...)
srm.request_qualification(...)
```

Elle délègue aux handlers.

Elle ne contient pas la logique métier.

---

# 203. Facade pattern — candidate

Si utilisée, la façade peut correspondre au :

```text
Facade Pattern
```

car elle simplifie l'accès à un sous-système complexe.

Mais ne pas créer une façade uniquement pour cocher le pattern.

---

# 204. Python-native consumer

PySRMKit doit rester utilisable sans API HTTP.

Exemple :

```python
result = register_supplier_handler.handle(
    RegisterSupplier(...)
)
```

---

# 205. CLI consumer

```text
CLI args
    │
    ▼
Command object
    │
    ▼
Handler
```

---

# 206. API consumer

```text
HTTP Request
    │
    ▼
Request DTO
    │
    ▼
Command
    │
    ▼
Handler
    │
    ▼
Application Result
    │
    ▼
Response DTO
```

---

# 207. Agent consumer

```text
Tool invocation
    │
    ▼
Command / Query
    │
    ▼
Handler
    │
    ▼
Result
```

L'agent ne connaît pas les repositories.

---

# 208. Worker consumer

```text
Message
    │
    ▼
Integration mapper
    │
    ▼
Command
    │
    ▼
Handler
```

---

# 209. Command serialization

Les Commands peuvent être sérialisables.

Mais leur schema Python interne ne doit pas devenir automatiquement un contrat public stable.

---

# 210. Public integration command

Si un message externe est accepté :

```text
IntegrationCommand DTO
```

peut être mappé vers :

```text
Application Command
```

pour protéger l'API interne.

---

# 211. Application result serialization

Même séparation :

```text
Application Result
≠
HTTP Response Model
```

---

# 212. Query pagination

Queries de liste doivent prévoir :

```text
limit
cursor/page
sort
filters
```

mais les abstractions exactes peuvent rester dans le query layer.

---

# 213. Pagination Value Objects

`PageRequest` / `Cursor` sont des objets applicatifs, pas du Supplier Domain.

---

# 214. Sorting

Même distinction :

```text
SortSpec
```

peut appartenir au Query Layer.

---

# 215. Filtering

Éviter de construire un generic dynamic query language dans le core.

Expose business filters needed by real use cases.

---

# 216. Search Query Example

```text
SearchSuppliers(
    name="ACME",
    country="FR",
    category="IT_SERVICES",
)
```

peut être mappée vers un search adapter.

---

# 217. Read Models are disposable representations

Un read model peut évoluer sans changer les Entities.

C'est l'un des bénéfices de la séparation Query/Command.

---

# 218. Consistency choice per Query

Exemple :

```text
GetRelationshipReadiness
```

peut nécessiter un calcul plus frais que :

```text
SupplierDashboardList
```

La cohérence n'a pas besoin d'être uniforme.

---

# 219. Caching Queries

Le cache peut entourer :

```text
GetSupplier360
GetSupplierScorecard
```

sans toucher au Domain Model.

---

# 220. Cache invalidation

Peut être déclenchée par Domain/Integration Events.

Mais ne doit pas devenir un invariant métier.

---

# 221. Command Audit

Chaque Command critique devrait permettre de tracer :

```text
command type
actor
aggregate id
reason
timestamp
correlation id
result
```

selon politique d'audit.

---

# 222. Audit ≠ Event

Un audit entry et un Domain Event peuvent se recouper mais répondent à des besoins différents.

---

# 223. Sensitive command data

Éviter de logger aveuglément :

```text
bank details
personal contact data
compliance evidence
```

Les Commands peuvent nécessiter redaction.

---

# 224. Query privacy

Même règle pour les read models.

Un `Supplier360View` complet ne doit pas être exposé à tout caller.

Authorization reste une responsabilité applicative.

---

# 225. Optimistic concurrency

Une Command peut échouer si l'Aggregate a changé depuis chargement.

Application error candidate :

```text
ConcurrentModification
```

Infrastructure peut détecter via version.

---

# 226. Retry after concurrency conflict

Selon use case :

```text
reload + retry
```

peut être acceptable

ou exiger intervention humaine.

Ne pas retry aveuglément une décision métier.

---

# 227. Application clock

Les Handlers nécessitant le temps doivent recevoir :

```text
Clock
```

ou passer explicitement `now` au domaine.

Éviter :

```text
datetime.now()
```

dispersé dans les règles.

---

# 228. Example — expiration job

```text
Clock.now()
    │
    ▼
ListExpiringQualifications
    │
    ▼
ExpireSupplierQualification
```

---

# 229. Command validation using Value Objects

Le Handler transforme :

```text
country_code: str
```

en :

```text
CountryCode
```

et laisse le Value Object valider sa structure.

---

# 230. Domain decision using Policy

Le Handler ne reproduit pas la policy.

```text
facts
    │
    ▼
Policy
    │
    ▼
Decision
```

---

# 231. Application decision using orchestration

Le Handler décide parfois :

```text
which repository to call
which provider to call
which aggregate to load
```

Ce sont des décisions applicatives, pas métier.

---

# 232. Business rule placement test

Question :

> If we call the same domain behavior from CLI, API and Agent, should this rule remain identical?

Si oui :

```text
probably domain rule
```

---

# 233. Application rule placement test

Question :

> Does this rule mainly coordinate external systems or aggregate loading?

Si oui :

```text
probably application rule
```

---

# 234. Adapter rule placement test

Question :

> Is this rule about HTTP, SQL, SAP, Ivalua or Kafka representation?

Si oui :

```text
adapter rule
```

---

# 235. Use Case Test Strategy

Chaque Command Handler doit être testé avec :

```text
fake/in-memory repositories
fake clock
fake providers
fake event publisher
```

sans infrastructure réelle.

---

# 236. RegisterSupplier handler tests

```text
creates supplier
saves supplier
commits
returns SupplierId
emits SupplierCreated
rejects duplicate identifier
```

---

# 237. ActivateRelationship handler tests

```text
loads required facts
delegates to ActivationPolicy
activates when allowed
refuses when denied
persists only successful transition
emits SupplierActivated
```

---

# 238. Qualification handler tests

```text
requires valid scope
does not globally qualify supplier
applies policy
records decision
emits correct event
```

---

# 239. Incident handler tests

```text
creates incident
commits incident
publishes IncidentReported
does not mutate risk directly
```

---

# 240. Query handler tests

Tester :

```text
filter semantics
projection mapping
pagination
not-found behavior
```

pas les invariants métier des Aggregates.

---

# 241. Contract tests for query ports

Si plusieurs adapters implémentent :

```text
SupplierReader
```

une suite de contract tests peut être utile.

---

# 242. End-to-end application scenario

```text
RegisterSupplier
    │
    ▼
CreateSupplierRelationship
    │
    ▼
InviteSupplierRelationship
    │
    ▼
StartSupplierOnboarding
    │
    ▼
RegisterSupplierDocument
    │
    ▼
RecordComplianceCheck
    │
    ▼
RequestSupplierQualification
    │
    ▼
EvaluateSupplierQualification
    │
    ▼
ActivateSupplierRelationship
```

---

# 243. Scenario — incident after activation

```text
ACTIVE Relationship
    │
    ▼
ReportSupplierIncident
    │
    ▼
IncidentReported
    │
    ├── ReassessSupplierRisk
    │
    └── ConsiderSuspension
```

---

# 244. Scenario — document expiration

```text
Document expires
    │
    ▼
ExpireSupplierDocument
    │
    ▼
DocumentExpired
    │
    ▼
ReevaluateCompliance
    │
    ▼
Maybe review qualification/relationship
```

---

# 245. Scenario — multi-organization

```text
Supplier S
    │
    ├── Relationship R1 / Org A
    │      ACTIVE
    │
    └── Relationship R2 / Org B
           SUSPENDED
```

Commands always target:

```text
relationship_id
```

for lifecycle operations.

---

# 246. Command targeting rule

Lifecycle Commands should not target only:

```text
SupplierId
```

when state is relationship-scoped.

Use:

```text
SupplierRelationshipId
```

---

# 247. Qualification targeting rule

Qualification Commands target:

```text
QualificationId
```

after creation

or:

```text
RelationshipId + QualificationScope
```

for request/query.

---

# 248. Risk targeting rule

Risk Commands must specify whether risk is:

```text
Supplier-level
or
Relationship-level
```

explicitly.

Avoid hidden scope.

---

# 249. Application DTO boundaries

Potential DTOs :

```text
SupplierView
SupplierSummary
RelationshipView
QualificationSummary
RiskProfileView
ComplianceSummary
DocumentView
IncidentView
```

---

# 250. DTO naming rule

Use `View`, `Summary`, `DTO` or semantic names consistently.

Do not name a DTO simply:

```text
Supplier
```

if it is not the Domain Entity.

---

# 251. Mapping rule

Mapping occurs at boundaries.

```text
Command input
→ Value Objects
→ Domain

Domain/Projection
→ Application View
→ Adapter response
```

---

# 252. Mapper classes — optional

Do not create mapper classes for every trivial transformation.

Simple functions are acceptable.

KISS.

---

# 253. Application Events vs Domain Events

Possible distinction :

```text
Domain Event
    SupplierActivated

Application Event
    SupplierActivationWorkflowCompleted
```

Ne pas multiplier les event types sans besoin.

---

# 254. Event Handler naming

Examples :

```text
OnSupplierQualifiedEvaluateActivation
OnSupplierIncidentReportedReassessRisk
OnDocumentExpiredReevaluateCompliance
```

ou noms plus orientés action :

```text
EvaluateActivationAfterQualification
```

La convention finale doit rester lisible.

---

# 255. Event Handler side effects

Un Event Handler peut :

- envoyer une Command ;
- mettre à jour une projection ;
- déclencher une integration event ;
- notifier un système externe.

Il ne doit pas modifier directement des aggregates sans use case explicite.

---

# 256. Notifications

Email/Slack notifications sont des side effects applicatifs.

Ils ne doivent pas être inclus dans :

```text
Supplier.activate()
```

---

# 257. Workflow integration

Un use case peut émettre un event consommé par PyWorkflowKit.

Exemple :

```text
SupplierQualificationRequested
```

→ start approval workflow.

---

# 258. Procurement integration

`SupplierQualified` peut alimenter :

```text
eligible supplier projection
```

dans PyProcurementKit.

---

# 259. Accounting integration

`SupplierActivated` peut déclencher :

```text
CreateVendorAccount
```

dans PyAccountingKit.

Ce n'est pas un effet interne de l'Aggregate.

---

# 260. Contract integration

Une relationship peut Query :

```text
active contracts
```

via Contract port si une policy l'exige.

Mais le Handler ne manipule pas le full Contract Aggregate.

---

# 261. Application orchestration with external domains

Exemple suspension :

```text
SuspendSupplierRelationship
    │
    ├── maybe check critical active contracts
    ├── evaluate policy
    ├── suspend relationship
    └── emit event
```

Le besoin exact doit être confirmé par le métier.

---

# 262. Long-running process boundary

Si une opération exige des heures/jours :

```text
onboarding approval
external compliance review
```

elle ne doit pas rester une transaction ouverte.

Utiliser :

```text
state + events + later commands
```

---

# 263. Command lifecycle

Une Command elle-même ne devient pas Entity.

Elle est un message.

Elle peut être persistée par infrastructure pour retry/audit sans changer sa nature.

---

# 264. Query lifecycle

Une Query est éphémère.

Elle n'a pas d'identité métier durable.

---

# 265. Handler lifecycle

Handler peut être stateless.

Ses dependencies sont injectées.

---

# 266. Service lifetime

Singleton/scoped/transient est une décision du composition root/framework adapter.

Pas du Domain Model.

---

# 267. No Singleton pattern in core

Aucun besoin identifié pour GoF Singleton.

Un container peut gérer un lifetime singleton sans utiliser le pattern dans le domaine.

---

# 268. Strategy usage in application flows

Policies injectées :

```text
QualificationPolicy
ActivationPolicy
RiskPolicy
CompliancePolicy
SegmentationPolicy
```

représentent les principales Strategy applications.

---

# 269. Adapter usage in application flows

Providers injectés :

```text
RiskDataProvider
SanctionsScreeningProvider
CompanyRegistryProvider
```

sont des ports implémentés par Adapters.

---

# 270. Repository usage

Repositories sont utilisés seulement lorsque l'Aggregate correspondant doit être chargé/persisté.

---

# 271. Factory usage

Un Handler peut appeler :

```text
Supplier.create(...)
```

plutôt qu'une Factory tant que construction simple.
---

# 272. Facade usage

Une façade Python est une UX de consumer.

Elle ne remplace pas les handlers.

---

# 273. Mediator usage

Non requis au MVP.

---

# 274. Specification pattern — candidate

Peut devenir pertinent pour des critères réutilisables :

```text
EligibleForActivation
DocumentRequirementSatisfied
```

Mais si une Policy simple suffit :

```text
do not introduce Specification framework.
```

---

# 275. Chain of Responsibility — candidate

Pour des validations configurables en chaîne, on pourrait imaginer :

```text
QualificationRule*
```

Mais ne pas imposer GoF Chain of Responsibility tant qu'une simple collection de rules suffit.

---

# 276. Rule collection ≠ Chain of Responsibility automatically

Si toutes les règles sont évaluées indépendamment :

```text
for rule in rules:
    results.append(rule.evaluate(...))
```

cela n'est pas nécessairement le GoF pattern.

---

# 277. State pattern — not assumed

Handlers utilisent la state machine métier.

Ils ne dépendent pas nécessairement d'objets State GoF.

---

# 278. Observer pattern — not assumed

Event dispatch peut ressembler à Observer.

Mais Domain Events + Dispatcher ne doivent pas être appelés Observer par défaut.

---

# 279. Command pattern — not assumed

Déjà rappelé :

```text
CQRS/Application Command
≠
GoF Command
```

---

# 280. Application Layer Learning Map

```text
User Intent
    │
    ▼
Command
    │
    ▼
Handler
    │
    ├── Repository Port
    ├── External Port
    ├── Domain Policy
    ▼
Aggregate
    │
    ▼
Domain Event
    │
    ▼
Commit / Dispatch
```

---

# 281. Learning Map — Command

```text
Problem
    express state-changing intent
        │
        ▼
Architecture
    Command
        │
        ▼
Python
    immutable dataclass
        │
        ▼
Handler
    orchestration
```

---

# 282. Learning Map — Query

```text
Problem
    read without forcing aggregate shape
        │
        ▼
Architecture
    Query / Read Model
        │
        ▼
CQRS
    command-query separation
        │
        ▼
Optimization
    projection/index/cache
```

---

# 283. Learning Map — Handler

```text
Problem
    coordinate use case
        │
        ▼
Application Service
        │
        ├── load
        ├── delegate
        ├── save
        └── publish
        │
        ▼
SRP + SoC
```

---

# 284. Learning Map — Activation

```text
Problem
    activation depends on several domain facts
        │
        ▼
Application
    gather facts
        │
        ▼
Domain Policy
    ActivationPolicy
        │
        ▼
Domain Result
    ActivationDecision
        │
        ▼
Aggregate
    relationship.activate(...)
```

---

# 285. Learning Map — Repository

```text
Handler needs Aggregate
        │
        ▼
Repository Port
        │
        ▼
DIP
        │
        ▼
Adapter
    InMemory/PostgreSQL
```

---

# 286. Learning Map — Domain Event

```text
Aggregate changes state
        │
        ▼
records Domain Event
        │
        ▼
Application commits
        │
        ▼
Event handlers / Integration
```

---

# 287. Application Anti-Pattern — Business logic in Handler

Mauvais :

```python
if qualification.status == "QUALIFIED" and risk < 80:
    relationship.status = "ACTIVE"
```

Meilleur :

```text
ActivationPolicy
+
relationship.activate(decision)
```

---

# 288. Application Anti-Pattern — Generic CRUD service

Mauvais :

```text
SupplierService.update(entity, fields)
```

si cela contourne l'intention métier.

---

# 289. Application Anti-Pattern — Repository as Query God Object

Mauvais :

```text
SupplierRepository.search_by_every_possible_filter(...)
```

si les queries analytiques devraient utiliser un read model.

---

# 290. Application Anti-Pattern — External SDK in Handler

Mauvais :

```text
handler imports IvaluaClient directly
```

Préférer :

```text
port
+
adapter
```

---

# 291. Application Anti-Pattern — Hidden transaction

Le Handler doit savoir où se situe sa transaction.

Éviter un repository qui commit automatiquement de façon imprévisible.

---

# 292. Application Anti-Pattern — Publish before commit

Éviter :

```text
publish SupplierActivated
then DB commit fails
```

---

# 293. Application Anti-Pattern — Giant command payload

Éviter :

```text
UpdateEverythingSupplier
```

avec tout le Supplier Domain dans un payload.

---

# 294. Application Anti-Pattern — Command with domain object graph

Éviter que l'interface construise :

```text
Supplier
+ Relationship
+ Qualification objects
```

pour lancer une action.

Une Command doit transporter l'intention et les inputs nécessaires.

---

# 295. Application Anti-Pattern — Query changes state

Une Query ne doit pas :

```text
mark document expired
update last_seen
recalculate and persist score
```

sans rendre l'effet explicite.

---

# 296. Lazy state updates

Si l'expiration est dérivée du temps :

```text
document.is_expired(at)
```

peut être calculé sans Command.

Si le système doit persister un status `EXPIRED`, utiliser un use case explicite/job.

---

# 297. Application Anti-Pattern — Side effects in Entity

Éviter :

```text
relationship.activate()
    sends email
    calls ERP
    publishes Kafka
```

---

# 298. Application Anti-Pattern — Handler becomes workflow engine

Si le Handler contient des dizaines d'étapes long-running et retries :

```text
consider process manager/workflow
```

---

# 299. Application Anti-Pattern — Pattern ceremony

Ne pas introduire :

```text
CommandBus
QueryBus
Mediator
Pipeline
Saga
Specification
```

uniquement parce qu'ils existent dans les architectures d'entreprise.

---

# 300. MVP Command Set

Pour un premier MVP :

```text
RegisterSupplier
UpdateSupplierIdentity
AddSupplierExternalIdentifier
AddSupplierContact
AddSupplierLocation

CreateSupplierRelationship
InviteSupplierRelationship
StartSupplierOnboarding

RequestSupplierQualification
EvaluateSupplierQualification

ActivateSupplierRelationship
SuspendSupplierRelationship
ReactivateSupplierRelationship
OffboardSupplierRelationship

CreateSupplierAssessment
CompleteSupplierAssessment
```

---

# 301. MVP Query Set

```text
GetSupplier
FindSupplierByExternalIdentifier
ListSupplierRelationships
GetSupplierRelationship
GetOnboardingProgress
GetSupplierQualification
IsSupplierQualified
GetRelationshipReadiness
GetSupplierHistory
```

---

# 302. MVP Ports

```text
SupplierRepository
SupplierRelationshipRepository
SupplierQualificationRepository
SupplierAssessmentRepository
Clock
UnitOfWork candidate
EventPublisher / in-process dispatcher
```

---

# 303. Phase 2 Commands — Trust & Control

```text
RegisterSupplierDocument
VerifySupplierDocument
RegisterSupplierCertification
RecordComplianceCheck
EvaluateSupplierCompliance
RecordRiskAssessment
ReassessSupplierRisk
```

---

# 304. Phase 3 Commands — Relationship Intelligence

```text
RecordPerformanceMeasurement
ReportSupplierIncident
ResolveSupplierIncident
EvaluateSupplierSegmentation
```

---

# 305. Phase 3 Queries

```text
GetSupplierScorecard
GetPerformanceTrend
GetSupplierRiskProfile
ListOpenIncidents
ListSuppliersBySegment
GetSupplier360
```

---

# 306. Application Acceptance Criteria

L'Application Layer est correctement conçue si :

1. chaque Command représente une intention métier claire ;
2. chaque Query est sans effet métier ;
3. les Handlers restent minces ;
4. les invariants restent dans le domaine ;
5. les Policies sont invoquées explicitement ;
6. les Aggregates sont chargés via ports ;
7. les Adapters concrets ne fuient pas dans le Handler core ;
8. la transaction est explicite ;
9. les Domain Events sont publiés après succès ;
10. les read models ne dictent pas les Aggregate boundaries ;
11. agents/API/CLI peuvent partager les mêmes use cases ;
12. les use cases sont testables avec fakes/in-memory implementations.

---

# 307. Command Quality Checklist

```text
[ ] Name expresses business intent
[ ] Immutable if possible
[ ] Contains only required inputs
[ ] Does not contain infrastructure objects
[ ] Targets explicit aggregate/scope
[ ] Authorization context is separate/clear
[ ] Idempotency considered
[ ] Audit relevance considered
```

---

# 308. Query Quality Checklist

```text
[ ] Name expresses a real question
[ ] No business mutation
[ ] Returns purpose-built read model
[ ] Pagination considered for collections
[ ] Consistency requirement explicit
[ ] Authorization/privacy considered
[ ] Does not force Aggregate loading unnecessarily
```

---

# 309. Handler Quality Checklist

```text
[ ] Loads only required state
[ ] Delegates business decisions
[ ] Uses ports, not concrete adapters
[ ] Transaction boundary is clear
[ ] Does not encode HTTP/SQL/vendor semantics
[ ] Persists only required aggregates
[ ] Dispatches events correctly
[ ] Returns explicit result
[ ] Is easy to unit test
```

---

# 310. Use Case Quality Checklist

```text
[ ] Actor identified
[ ] Intent clear
[ ] Preconditions known
[ ] Domain owner identified
[ ] Cross-aggregate facts explicit
[ ] Policy identified if variation exists
[ ] Result defined
[ ] Errors defined
[ ] Events defined
[ ] Audit/idempotency considered
```

---

# 311. Design Concepts Applied — Command Handler

```text
[ARCH: Application Layer]
[PRINCIPLE: SRP]
[PRINCIPLE: Separation of Concerns]
[PRINCIPLE: Dependency Inversion]
[DDD: Aggregate orchestration]
```

---

# 312. Design Concepts Applied — Query Handler

```text
[ARCH: CQRS-friendly]
[PRINCIPLE: Command-Query Separation]
[PRINCIPLE: Information Hiding]
[ARCH: Read Model]
```

---

# 313. Design Concepts Applied — Policy interaction

```text
[DDD: Domain Policy]
[PATTERN: Strategy]
[PRINCIPLE: OCP]
[PRINCIPLE: DIP]
```

---

# 314. Design Concepts Applied — Event reaction

```text
[DDD: Domain Event]
[ARCH: Event-Driven]
[PRINCIPLE: Low Coupling]
```

---

# 315. Design Concepts Applied — Repository interaction

```text
[DDD: Repository]
[ARCH: Port]
[PRINCIPLE: DIP]
[PATTERN: Repository]
```

---

# 316. Design Concepts Applied — External Provider

```text
[ARCH: Port and Adapter]
[PATTERN: Adapter]
[DDD: Anti-Corruption Layer]
[PRINCIPLE: Information Hiding]
```

---

# 317. Important terminology summary

```text
Command
    application intent to change state

Query
    application intent to read

Handler
    application orchestration

Application Service
    use-case coordination

Domain Service
    domain logic without natural entity owner

Domain Policy
    replaceable business decision logic

Repository
    aggregate persistence abstraction

Read Model
    query-optimized representation

Domain Event
    significant business fact

Integration Event
    external messaging contract
```

---

# 318. Concepts not to confuse

```text
CQRS Command
≠
GoF Command Pattern
```

```text
Query
≠
Repository method
```

```text
Application Service
≠
Domain Service
```

```text
Domain Event
≠
Integration Event
```

```text
Unit of Work
≠
Aggregate
```

```text
Read Model
≠
Domain Entity
```

```text
Application DTO
≠
Value Object
```

---

# 319. Application Layer North Star

```text
INTENT
    │
    ▼
COMMAND / QUERY
    │
    ▼
HANDLER
    │
    ├── Ports
    ├── Repositories
    ├── Policies
    ▼
DOMAIN
    │
    ▼
RESULT / EVENT
```

---

# 320. Full Command Flow North Star

```text
Primary Adapter
      │
      ▼
Command
      │
      ▼
Handler
      │
      ├── Authorize
      ├── Load Aggregate(s)
      ├── Gather external/domain facts
      ├── Invoke Policy
      ├── Invoke Aggregate behavior
      ├── Save
      ├── Commit
      └── Dispatch Events
      │
      ▼
Application Result
```

---

# 321. Full Query Flow North Star

```text
Primary Adapter
      │
      ▼
Query
      │
      ▼
Query Handler
      │
      ▼
Read Port / Projection / Search Adapter
      │
      ▼
Read Model
      │
      ▼
Primary Adapter Response
```

---

# 322. Pedagogical interpretation

Ce document fait apparaître une nouvelle descente d'abstraction :

```text
Business intention
        │
        ▼
Use Case
        │
        ▼
Command / Query
        │
        ▼
Handler
        │
        ▼
Domain Object / Policy
        │
        ▼
Port
        │
        ▼
Adapter
        │
        ▼
Runtime
```

---

# 323. Why this matters for learning

Le même concept sera rencontré de manière répétée.

Exemple `Dependency Inversion` :

```text
Handler
    depends on
SupplierRepository Protocol

not
PostgreSQLSupplierRepository
```

Exemple `Strategy` :

```text
Handler
    depends on
QualificationPolicy

not
CybersecurityQualificationPolicy directly
```

Exemple `Adapter` :

```text
Handler
    depends on
RiskDataProvider

not
VendorXYZ SDK
```

---

# 324. From definitions to intuition

À force de manipuler les use cases :

```text
"variation métier"
    → Policy / Strategy

"besoin de persistence"
    → Repository Port

"modèle externe incompatible"
    → Adapter

"lecture composite"
    → Query / Projection

"changement significatif"
    → Domain Event

"orchestration de cas d'usage"
    → Handler
```

ces associations doivent devenir progressivement intuitives.

---

# 325. Open Questions

Les questions suivantes restent ouvertes.

## OQ-001 — Unit of Work

Obligatoire dans le core application ou seulement dans certains adapters ?

## OQ-002 — Command Bus

Direct handlers ou bus optionnel ?

## OQ-003 — Query Ports

Dedicated Readers ou adapters directement injectés ?

## OQ-004 — Sync / Async

Handlers synchrones, async, ou deux API séparées ?

## OQ-005 — Domain Event Dispatcher

Dans UnitOfWork, application service ou infrastructure ?

## OQ-006 — Onboarding Process Manager

À quel moment devient-il nécessaire ?

## OQ-007 — Qualification approval model

Evaluation automatique vs décision humaine déjà approuvée.

## OQ-008 — Read Model ownership

PySRMKit fournit-il certaines projections de référence ou uniquement les contrats ?

## OQ-009 — Application Facade

Faut-il une façade `PySRMKit` ergonomique ?

## OQ-010 — Idempotency

Quels use cases ont besoin d'un support first-class ?

---

# 326. Decisions Deferred to Later Specifications

Les documents suivants devront approfondir :

```text
Ports and Repository Contracts
Persistence Architecture
Domain Events and Integration Events
Testing Strategy
Security / Authorization Integration
Observability
Idempotency
Concurrency
```

---

# 327. Suggested Next Documents

Après ce `08`, la suite logique peut être organisée autour de :

```text
09_PYSRMKIT_DOMAIN_EVENTS_AND_EVENT_MODEL.md
10_PYSRMKIT_PORTS_AND_REPOSITORY_CONTRACTS.md
11_PYSRMKIT_APPLICATION_SERVICES_AND_HANDLER_MODEL.md
12_PYSRMKIT_PERSISTENCE_AND_UNIT_OF_WORK_MODEL.md
13_PYSRMKIT_ADAPTERS_AND_EXTERNAL_INTEGRATION_MODEL.md
14_PYSRMKIT_TESTING_STRATEGY.md
```

L'ordre pourra être adapté selon la roadmap d'implémentation.

---

# 328. Final Summary

La couche applicative de PySRMKit repose sur une séparation simple :

```text
Commands
    express state-changing intent

Queries
    express information needs

Handlers
    orchestrate use cases
Domain
    decides what is valid

Repositories / Ports
    connect to external capabilities

Events
    communicate significant outcomes
```

Le Handler n'est pas le lieu de la règle métier.

Le Repository n'est pas un moteur de recherche universel.

La Query n'est pas une Entity.

La Command n'est pas automatiquement le GoF Command Pattern.

Le Domain Event n'est pas automatiquement un message Kafka.

---

# 329. Final Rules

> **Commands express intention.**

> **Queries express questions.**

> **Handlers orchestrate.**

> **Aggregates protect invariants.**

> **Policies decide variable business rules.**

> **Repositories load and persist Aggregate Roots.**

> **Read Models serve consumers.**

> **Events communicate facts.**

> **Adapters handle technology.**

---

# 330. Conclusion

PySRMKit dispose désormais d'un modèle applicatif cohérent avec son architecture Domain-First.

Les capabilities métier peuvent être exposées sans coupler le domaine :

- à HTTP ;
- à un ORM ;
- à un ERP ;
- à un workflow ;
- à un agent ;
- à un broker.

La structure cible devient :

```text
Primary Adapter
    │
    ▼
Command / Query
    │
    ▼
Handler
    │
    ▼
Domain
    │
    ▼
Port
    │
    ▼
Adapter
```

Cette organisation permet à la même vérité métier d'être utilisée par :

```text
Python
CLI
API
Jobs
Agents
ERP integrations
Procurement systems
```

sans duplication des règles.

Enfin, elle poursuit l'objectif pédagogique de PySRMKit :

```text
Problem
→ Intent
→ Use Case
→ Command/Query
→ Handler
→ Domain
→ Pattern
→ Python
→ Test
→ Repetition
→ Intuition
```

Le principe final reste :

> **The Application Layer coordinates the business.  
> The Domain Layer decides the business.**