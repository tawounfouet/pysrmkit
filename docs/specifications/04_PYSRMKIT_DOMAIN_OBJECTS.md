# PySRMKit — Domain Objects

**Document :** `04_PYSRMKIT_DOMAIN_OBJECTS.md`  
**Projet :** PySRMKit  
**Domaine :** Supplier Relationship Management  
**Type :** Domain Modeling — Inventaire et responsabilités des objets métier  
**Statut :** Draft de modélisation conceptuelle  
**Version du document :** 0.1.0  
**Documents de référence :**
- `00_PYSRMKIT_EXPRESSION_DU_BESOIN.md`
- `01_PYSRMKIT_REQUIREMENTS_ANALYSIS.md`
- `02_PYSRMKIT_PRODUCT_VISION_AND_ARCHITECTURE_PRINCIPLES.md`
- `03_PYSRMKIT_SYSTEM_ARCHITECTURE.md`
- `PYSRMKIT_SOFTWARE_DESIGN_LEARNING_CONVENTION.md`

---

# 1. Objet du document

Ce document identifie les **objets du domaine PySRMKit** et décrit leur rôle métier, leurs responsabilités, leurs relations conceptuelles et leur classification DDD candidate.

Il répond principalement aux questions suivantes :

> Quels objets composent réellement le Supplier Domain ?

> Quels objets représentent une identité durable ?

> Quels objets représentent une valeur ?

> Quels objets peuvent devenir Aggregate Roots ?

> Quelles règles appartiennent à des Policies ?

> Quelles opérations peuvent nécessiter des Domain Services ?

> Quels concepts représentent des faits passés sous forme de Domain Events ?

> Quelles frontières doivent empêcher `Supplier` de devenir un God Aggregate ?

Le document reste **conceptuel**.

Il ne fige pas encore :

- les attributs Python définitifs ;
- les signatures publiques ;
- les constructeurs ;
- les types exacts d'identifiants ;
- la persistence ;
- les relations ORM ;
- le package layout final ;
- la frontière transactionnelle définitive de chaque aggregate.

Ces décisions seront affinées dans :

```text
05_PYSRMKIT_ENTITIES_AND_VALUE_OBJECTS.md
06_PYSRMKIT_DOMAIN_RELATIONSHIPS_AND_ERD.md
07_PYSRMKIT_DOMAIN_INVARIANTS_AND_BUSINESS_RULES.md
08_PYSRMKIT_COMMANDS_QUERIES_AND_USE_CASES.md
```

---

# 2. Position dans la chaîne de conception

```text
Business Need
    │
    ▼
Requirements
    │
    ▼
Architecture Principles
    │
    ▼
System Architecture
    │
    ▼
DOMAIN OBJECTS        ← ce document
    │
    ▼
Entities / Value Objects
    │
    ▼
Relationships / ERD
    │
    ▼
Invariants
    │
    ▼
Use Cases
    │
    ▼
Implementation
```

Le `04` constitue donc le passage entre :

```text
architecture
```

et :

```text
domain model concret
```

---

# 3. Convention pédagogique appliquée

Pour chaque objet important, ce document tente de distinguer :

```text
BUSINESS PROBLEM
        │
        ▼
DOMAIN CONCEPT
        │
        ▼
DDD ROLE CANDIDATE
        │
        ▼
RESPONSIBILITY
        │
        ▼
INVARIANTS / BEHAVIOR
        │
        ▼
RELATIONSHIPS
        │
        ▼
DESIGN CONCEPTS
```

La classification n'est pas forcée.

La règle reste :

> **Problem before Pattern.**

---

# 4. Classification Status

Afin de ne pas présenter comme définitives des décisions encore ouvertes, chaque objet peut être associé à l'un des statuts suivants.

## CONFIRMED CONCEPT

Le concept métier est clairement nécessaire.

Exemple :

```text
Supplier
Qualification
SupplierDocument
```

## CANDIDATE DDD ROLE

Le concept est confirmé, mais sa classification précise reste à valider.

Exemple :

```text
SupplierRelationship
    confirmed concept
    aggregate-root candidate
```

## PROPOSED SUPPORTING OBJECT

L'objet est proposé pour rendre un concept existant explicite.

Exemple :

```text
QualificationDecision
```

## DEFERRED

La conception détaillée doit attendre une analyse dédiée.

Exemple :

```text
RiskDefinition vs RiskObservation vs RiskAssessment
```

---

# 5. Ubiquitous Language — noyau

Les objets doivent rester alignés avec le vocabulaire déjà adopté.

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

Les nouveaux objets proposés dans ce document doivent servir à **préciser** ce vocabulaire, pas à le remplacer.

---

# 6. Domain Object Families

Le Supplier Domain peut être lu comme plusieurs familles d'objets.

```text
SUPPLIER DOMAIN
│
├── Identity & Master Data
│
├── Organization & Relationships
│
├── Lifecycle
│
├── Onboarding
│
├── Qualification & Capabilities
│
├── Documents & Certifications
│
├── Compliance
│
├── Risk
│
├── Assessments
│
├── Performance & Scorecards
│
├── Incidents
│
├── Segmentation
│
├── History & Audit
│
├── Policies
│
├── Domain Services
│
└── Domain Events
```

---

# 7. First Domain Map

```text
                              Supplier
                                 │
               ┌─────────────────┼─────────────────┐
               │                 │                 │
               ▼                 ▼                 ▼
         Identity          Organization       Relationships
               │                 │                 │
               │                 │                 ▼
               │                 │         SupplierRelationship
               │                 │                 │
               │                 │        ┌────────┼────────┐
               │                 │        │        │        │
               │                 │        ▼        ▼        ▼
               │                 │    Lifecycle Qualification Segmentation
               │                 │
               ├─────────────────┼──────────────────────────────┐
               │                 │                              │
               ▼                 ▼                              ▼
          Documents        Certifications                  Assessments
               │                 │                              │
               └──────────┬──────┘                              │
                          ▼                                     │
                     Compliance                                 │
                          │                                     │
                          ▼                                     ▼
                         Risk                              Performance
                          │                                     │
                          └──────────────┬──────────────────────┘
                                         ▼
                                      Incidents
```

Cette carte est **conceptuelle**, pas un diagramme de classes final.

---

# 8. Core Domain Objects

Le Core Domain initial reste centré sur :

```text
Supplier
SupplierIdentity
SupplierOrganization
SupplierRelationship
SupplierLifecycle
SupplierOnboarding
SupplierQualification
```

Ces objets répondent aux quatre questions centrales :

```text
WHO is the supplier?
HOW is it organized?
HOW do we relate to it?
CAN it work with us?
```

---

# 9. Supplier

**Status :** CONFIRMED CONCEPT  
**DDD role candidate :** Entity + Aggregate Root candidate  
**Priority :** Core

## 9.1 Business meaning

`Supplier` représente l'organisation externe reconnue par PySRMKit comme fournisseur ou fournisseur potentiel.

Il ne doit pas être confondu avec :

```text
ERP Vendor Record
Accounting Vendor Account
Contract
Purchase Order Supplier Line
External Registry Company Record
```

## 9.2 Core responsibility

Le Supplier porte l'identité canonique du fournisseur.

Il constitue le point de référence métier pour :

- son identité ;
- ses identifiants ;
- ses informations principales ;
- son organisation ;
- ses catégories ;
- ses capacités ;
- certains liens vers les autres parties du domaine.

## 9.3 Candidate conceptual shape

```text
Supplier
├── SupplierId
├── SupplierIdentity
├── SupplierType
├── ExternalIdentifiers
├── Contacts / references
├── Locations / references
├── Categories
├── Capabilities
└── Relationships / references
```

Cette structure ne signifie pas que toutes les collections doivent être chargées dans un seul Aggregate.

## 9.4 Key invariant candidate

```text
Supplier identity
must remain independent
from external system identifiers.
```

## 9.5 Design concepts applied

```text
[DDD: Entity]
[DDD: Aggregate Root candidate]
[PRINCIPLE: Encapsulation]
[PRINCIPLE: Information Hiding]
[PRINCIPLE: Domain First]
```

---

# 10. SupplierId

**Status :** CONFIRMED NEED  
**DDD role candidate :** Value Object

`SupplierId` représente l'identité interne stable de l'objet `Supplier`.

Il doit être distinct de :

```text
ERP_VENDOR_ID
IVALUA_SUPPLIER_ID
SAP_VENDOR_ID
DUNS
SIREN
SIRET
VAT_NUMBER
```

## Why

Un fournisseur doit pouvoir :

- exister avant son enregistrement dans l'ERP ;
- changer de système externe ;
- posséder plusieurs identifiants externes ;
- conserver la même identité métier.

## Design concepts

```text
[DDD: Value Object]
[PRINCIPLE: Canonical Identity]
[PRINCIPLE: Information Hiding]
```

---

# 11. SupplierIdentity

**Status :** CONFIRMED CONCEPT  
**DDD role candidate :** Composite Value Object / Domain component  
**Decision :** à confirmer dans le `05`

## Business meaning

Regroupe les informations permettant de décrire qui est le fournisseur.

Exemples :

```text
legal_name
trading_name
supplier_type
legal identifiers
```

La frontière exacte entre :

```text
Supplier
SupplierIdentity
LegalEntity
SupplierOrganization
```

reste volontairement ouverte.

## Design pressure

Éviter un `Supplier` rempli de chaînes primitives sans sémantique.

---

# 12. ExternalIdentifier

**Status :** CONFIRMED NEED  
**DDD role candidate :** Value Object

Exemples :

```text
ExternalIdentifier(
    type="SIREN",
    value="...",
    jurisdiction="FR"
)
```

ou :

```text
ExternalIdentifier(
    type="IVALUA_SUPPLIER_ID",
    value="..."
)
```

## Responsibility

Exprimer explicitement :

- le type ;
- la valeur ;
- éventuellement le système source ;
- éventuellement la juridiction.

## Invariant candidate

Un identifiant externe ne doit pas remplacer `SupplierId`.

---

# 13. SupplierType

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Enum / Value Object

Permet de distinguer éventuellement des catégories structurelles de fournisseur.

La taxonomie exacte n'est pas encore définie.

Le modèle doit éviter de créer trop tôt une enum fermée si les organisations ont besoin d'extension.

---

# 14. SupplierOrganization

**Status :** CONFIRMED CONCEPT  
**DDD role candidate :** Entity / organizational model  
**Aggregate role :** deferred

## Business meaning

Représente la structure organisationnelle du fournisseur.

Elle doit permettre de décrire :

```text
Parent company
Subsidiary
Establishment
Branch
Group
Related organization
```

## Example

```text
ACME GROUP
│
├── ACME France
├── ACME Germany
└── ACME UK
```

## Key modeling question

Faut-il représenter :

```text
Supplier
```

comme organisation entière

ou :

```text
Supplier
+ SupplierOrganization nodes
```

ou plusieurs Suppliers liés ?

Cette décision doit rester ouverte jusqu'au `06`.

---

# 15. OrganizationRelationship

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Entity or Value Object depending identity/history needs

Permettrait de représenter :

```text
PARENT_OF
SUBSIDIARY_OF
BRANCH_OF
RELATED_TO
```

entre organisations fournisseur.

Ce concept ne sera retenu que si la simple parenté hiérarchique devient insuffisante.

## YAGNI guard

Ne pas introduire un graphe générique d'organisations si le MVP n'en a pas besoin.

---

# 16. SupplierContact

**Status :** CONFIRMED CONCEPT  
**DDD role candidate :** Entity candidate

## Business meaning

Personne de contact associée au fournisseur.

Rôles possibles :

```text
Sales
Management
Accounting
Support
Compliance
Legal
Account Manager
```

## Why Entity candidate

Un contact peut :

- changer de rôle ;
- changer de coordonnées ;
- devenir inactif ;
- conserver son identité à travers ces changements.

La décision finale sera prise dans le `05`.

---

# 17. ContactRole

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object / extensible reference

Exemples :

```text
SALES
ACCOUNTING
LEGAL
COMPLIANCE
SUPPORT
```

Le modèle doit permettre plusieurs rôles lorsque nécessaire.

---

# 18. EmailAddress

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object

Rôle :

- validation structurelle ;
- éviter les chaînes non qualifiées ;
- porter éventuellement une normalisation.

Aucune logique de communication n'appartient à ce Value Object.

---

# 19. SupplierLocation

**Status :** CONFIRMED CONCEPT  
**DDD role candidate :** Entity candidate

## Business meaning

Représente un site ou établissement fournisseur.

Exemples :

```text
Headquarters
Factory
Agency
Warehouse
Office
Logistics Center
```

## Why Entity candidate

Une implantation peut avoir :

- une identité ;
- une adresse changeante ;
- un rôle opérationnel ;
- un statut ;
- une histoire.

L'`Address` elle-même reste un Value Object candidat.

---

# 20. Address

**Status :** CONFIRMED NEED  
**DDD role candidate :** Value Object

Le modèle d'adresse doit rester :

- multi-pays ;
- extensible ;
- indépendant du format français.

## Important distinction

```text
SupplierLocation
    entity

Address
    value
```

Changer l'adresse d'une usine ne crée pas nécessairement une nouvelle usine.

---

# 21. CountryCode

**Status :** CONFIRMED NEED  
**DDD role candidate :** Value Object

Doit permettre d'exprimer un pays sans embarquer les règles réglementaires nationales directement dans le code du Supplier.

---

# 22. SupplierCategory

**Status :** CONFIRMED CONCEPT  
**DDD role candidate :** Reference Value Object / Reference Entity candidate

Exemples :

```text
IT
Consulting
Construction
Maintenance
Energy
Facilities
Transport
Software
Telecommunications
```

## Business meaning

Classification du fournisseur.

## Key distinction

```text
Category
    classification

Capability
    what the supplier can actually provide
```

---

# 23. CategoryCode

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object

Permettrait de ne pas manipuler directement des chaînes libres.

Exemple :

```text
CategoryCode("IT_SERVICES")
```

La taxonomie elle-même peut être externe ou configurable.

---

# 24. SupplierCapability

**Status :** CONFIRMED CONCEPT  
**DDD role candidate :** Entity or Value Object — unresolved

Exemples :

```text
Cloud Consulting
Python Development
Data Engineering
Managed Services
```

## Modeling question

Une capability simple pourrait être un Value Object.

Mais si elle porte :

- verification status ;
- dates ;
- source ;
- evidence ;
- scope ;

elle peut nécessiter une identité propre.

Décision reportée au `05`.

---

# 25. CapabilityStatus

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Enum / Value Object

Exemples possibles :

```text
DECLARED
VERIFIED
REJECTED
EXPIRED
```

Cette taxonomie n'est pas encore une exigence ferme.

---

# 26. SupplierRelationship

**Status :** CONFIRMED CONCEPT  
**DDD role candidate :** Entity + Aggregate Root candidate  
**Priority :** Core

## Business meaning

Représente :

> **How our organization works with the supplier.**

et non :

> **Who the supplier is.**

## Example

```text
ACME France
    │
    ├── Relationship with Internal Entity A
    │      ACTIVE
    │      IT qualified
    │
    └── Relationship with Internal Entity B
           SUSPENDED
           Consulting qualified
```

## Why this object matters

Il permet d'éviter de considérer comme globales des propriétés qui peuvent être locales à une relation :

- lifecycle ;
- qualification ;
- compliance ;
- risk ;
- segmentation ;
- status.

## Aggregate root candidate

Très forte candidature à un Aggregate séparé de `Supplier`.

Décision finale à prendre après analyse des invariants.

---

# 27. SupplierRelationshipId

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object

Identifie une relation fournisseur particulière indépendamment de l'identité du Supplier.

---

# 28. InternalOrganizationId

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object

Référence l'entité interne de l'entreprise concernée par la relation.

PySRMKit ne doit pas devenir propriétaire de tout le modèle organisationnel interne de l'entreprise.

---

# 29. Supplier Lifecycle

**Status :** CONFIRMED CONCEPT  
**DDD role candidate :** Domain behavior + State Machine  
**Not automatically :** GoF State Pattern

## Reference states

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

Le `REJECTED` apparaît également dans le parcours de qualification/review et devra être précisément positionné.

## Responsibility

Le lifecycle contrôle :

- les états autorisés ;
- les transitions ;
- les guards ;
- les raisons ;
- les événements associés.

---

# 30. SupplierLifecycleStage

**Status :** CONFIRMED NEED  
**DDD role candidate :** Enum / Value Object

Représente un état du lifecycle.

Le choix entre :

```text
enum
```

et objets State dédiés

sera guidé par la complexité réelle.

## Initial recommendation

```text
Enum + explicit transition rules
```

pour respecter KISS/YAGNI.

---

# 31. LifecycleTransition

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object / Domain result

Peut représenter :

```text
source
target
reason
occurred_at
```

Il ne doit être introduit que si une transition mérite d'être manipulée comme concept de première classe.

---

# 32. LifecycleTransitionReason

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object

Particulièrement utile pour :

```textSUSPENDED
BLOCKED
REACTIVATED
OFFBOARDED
```

où la justification est métier.

---

# 33. LifecycleTransitionDecision

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Domain result Value Object

Peut permettre d'expliquer :

```text
allowed
reasons
failed_rules
```

et faciliter :

- tests ;
- audit ;
- agents ;
- UI.

---

# 34. SupplierOnboarding

**Status :** CONFIRMED CONCEPT  
**DDD role candidate :** Entity / Aggregate candidate  
**Boundary :** unresolved

## Business meaning

Représente l'état métier du processus d'intégration du fournisseur.

## Important boundary

PySRMKit représente :

```text
business onboarding state
```

mais pas :

```text
generic BPM orchestration
```

---

# 35. OnboardingStage

**Status :** CONFIRMED NEED  
**DDD role candidate :** Enum / Value Object

Étapes conceptuelles :

```text
Invitation
Identity Collection
Company Information
Legal Information
Tax Information
Bank Information Reference
Document Collection
Compliance Checks
Qualification
Approval
Activation
```

La liste peut être configurable.

---

# 36. OnboardingRequirement

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Entity or Value Object

Représente une exigence nécessaire à l'onboarding.

Exemples :

```text
required company data
required tax information
required document
required compliance check
required qualification
```

Cet objet pourrait être important pour calculer la complétude sans introduire un moteur de workflow.

---

# 37. OnboardingProgress

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object / Projection

Peut exprimer :

```text
completed requirements
missing requirements
completion ratio
current business stage
```

À déterminer s'il appartient au domaine ou à une projection de lecture.

---

# 38. SupplierQualification

**Status :** CONFIRMED CONCEPT  
**DDD role candidate :** Entity + Aggregate candidate  
**Priority :** Core

## Business meaning

Représente l'autorisation métier d'un fournisseur à fournir quelque chose dans un contexte donné.

## Key rule

```text
ACTIVE supplier
≠
QUALIFIED for everything
```

## Scope dimensions

Une qualification peut dépendre de :

```text
category
country
organization
business unit
service type
financial threshold
risk level
```

---

# 39. QualificationId

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object

Nécessaire si les qualifications deviennent des Entities historisées individuellement.

---

# 40. QualificationScope

**Status :** CONFIRMED NEED  
**DDD role candidate :** Value Object

Le `QualificationScope` est l'un des Value Objects les plus importants du modèle.

Il exprime :

> **For what exactly is this supplier qualified?**

Structure conceptuelle possible :

```text
QualificationScope
├── organization
├── category
├── country
├── business_unit
├── service_type
└── optional limits
```

Toutes les dimensions ne doivent pas être obligatoires.

---

# 41. QualificationStatus

**Status :** CONFIRMED NEED  
**DDD role candidate :** Enum / Value Object

États possibles à raffiner :

```text
PENDING
QUALIFIED
NOT_QUALIFIED
REVOKED
EXPIRED
```

Le vocabulaire définitif sera aligné avec le lifecycle de qualification.

---

# 42. QualificationDecision

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object / Domain result

Peut représenter :

```text
approved
status
reasons
failed_requirements
evidence_refs
decided_at
```

Cette structure est particulièrement utile pour l'explicabilité.

---

# 43. QualificationPolicy

**Status :** CONFIRMED ARCHITECTURAL CONCEPT  
**DDD role :** Domain Policy  
**Design Pattern :** Strategy

## Responsibility

Évaluer les critères variables d'une qualification.

## Example

```text
QualificationPolicy
    │
    ├── DefaultQualificationPolicy
    ├── CybersecurityQualificationPolicy
    ├── ConstructionQualificationPolicy
    └── OrganizationSpecificQualificationPolicy
```

## Important

Le nom reste métier :

```text
QualificationPolicy
```

et non :

```text
QualificationStrategyPattern
```

---

# 44. SupplierDocument

**Status :** CONFIRMED CONCEPT  
**DDD role candidate :** Entity candidate

## Business meaning

Référence un document nécessaire à la relation fournisseur.

## Source structure

```text
SupplierDocument
├── type
├── reference
├── issue_date
├── expiration_date
├── verification_status
├── issuer
└── storage_reference
```

## Important boundary

Le domaine gère :

```text
document metadata
validity
verification
business meaning
```

mais pas nécessairement :

```text
file bytes
blob storage
DMS
```

---

# 45. SupplierDocumentId

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object

Nécessaire si le document possède une identité durable et des révisions.

---

# 46. DocumentType

**Status :** CONFIRMED NEED  
**DDD role candidate :** Value Object / extensible reference

Exemples :

```text
REGISTRATION_EXTRACT
TAX_CLEARANCE
SOCIAL_CLEARANCE
INSURANCE_CERTIFICATE
BANK_REFERENCE
ESG_POLICY
```

Les types doivent être extensibles et multi-pays.

---

# 47. DocumentReference

**Status :** CONFIRMED NEED  
**DDD role candidate :** Value Object

Référence logique ou externe du document.

Il ne doit pas supposer :

```text
S3
Azure Blob
local filesystem
```

---

# 48. DocumentVerificationStatus

**Status :** CONFIRMED NEED  
**DDD role candidate :** Enum / Value Object

Exemples à raffiner :

```text
PENDING
VERIFIED
REJECTED
```

L'expiration est idéalement une propriété temporelle distincte de la vérification.

---

# 49. SupplierCertification

**Status :** CONFIRMED CONCEPT  
**DDD role candidate :** Entity candidate

## Business meaning

Certification détenue par le fournisseur.

Exemples :

```text
ISO 9001
ISO 27001
ISO 14001
SOC 2
EcoVadis
Professional License
```

## Candidate properties

```text
issuer
issue_date
expiration_date
scope
status
evidence_reference
```

---

# 50. CertificationType

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object / reference type

Permet de distinguer la certification elle-même de sa taxonomie.

---

# 51. CertificationStatus

**Status :** CONFIRMED NEED  
**DDD role candidate :** Enum / Value Object

Exemples :

```text
ACTIVE
EXPIRED
REVOKED
UNVERIFIED
```

La règle :

```text
REVOKED
must never be interpreted as ACTIVE
```

fait partie des invariants candidats.

---

# 52. CertificationScope

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object

Permet de préciser qu'une certification peut ne couvrir :

- qu'une entité ;
- qu'un site ;
- qu'une activité ;
- qu'un produit/service.

---

# 53. Compliance Domain

**Status :** CONFIRMED CAPABILITY  
**Object model :** DEFERRED / requires decomposition

Le document de requirements confirme les besoins suivants :

```text
legal compliance
tax compliance
sanctions
KYS
social obligations
ESG
cybersecurity
data protection
professional insurance
```

Mais le modèle objet exact doit encore être clarifié.

---

# 54. ComplianceRequirement

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Entity or Value Object

Représente ce qui est exigé.

Exemple :

```text
"Supplier must have valid social clearance"
```

Il peut être contextualisé par :

```text
country
organization
category
risk level
```

---

# 55. ComplianceCheck

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Entity candidate

Représente une vérification effectivement exécutée.

Conceptuellement :

```text
ComplianceCheck
├── requirement
├── performed_at
├── source
├── result
├── evidence
└── next_review_at
```

---

# 56. ComplianceResult

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object / Domain result

Peut distinguer :

```text
PASS
FAIL
REVIEW_REQUIRED
UNKNOWN
```

La taxonomie est à confirmer.

---

# 57. ComplianceFinding

**Status :** DEFERRED CANDIDATE

Peut devenir utile pour représenter plusieurs constats issus d'un même check.

Ne pas l'introduire tant que le besoin n'est pas démontré.

---

# 58. ComplianceDecision

**Status :** DEFERRED CANDIDATE

Pourrait représenter la décision métier dérivée de plusieurs checks.

Important :

```text
External provider result
≠
Compliance decision
```

---

# 59. CompliancePolicy

**Status :** CONFIRMED ARCHITECTURAL CONCEPT  
**DDD role :** Domain Policy  
**Pattern :** Strategy candidate

Rôle :

- interpréter des exigences variables ;
- évaluer des résultats ;
- appliquer des règles organisationnelles.

---

# 60. Risk Domain

**Status :** CONFIRMED CAPABILITY  
**Object model :** DEFERRED / requires decomposition

Risques confirmés :

```text
Financial
Operational
Cyber
Compliance
ESG
Geopolitical
Supply Chain
Concentration
Reputational
```

Le requirements document impose une dimension temporelle :

```text
Risk(t1) != Risk(t2)
```

---

# 61. RiskType

**Status :** CONFIRMED NEED  
**DDD role candidate :** Value Object / reference

Représente la nature du risque.

Le modèle doit permettre extension.

---

# 62. RiskAssessment

**Status :** CONFIRMED CANDIDATE  
**DDD role candidate :** Entity + Aggregate candidate

Représente une évaluation datée d'un risque.

Candidate structure :

```text
RiskAssessment
├── supplier / relationship
├── risk_type
├── assessed_at
├── score / level
├── source
├── rationale
└── mitigations
```

---

# 63. RiskScore

**Status :** CONFIRMED NEED  
**DDD role candidate :** Value Object

Peut représenter un score normalisé.

La plage exacte ne doit pas être supposée universelle trop tôt.

---

# 64. RiskLevel

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Enum / Value Object

Exemple :

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Une organisation peut nécessiter une autre taxonomie.

---

# 65. RiskObservation

**Status :** DEFERRED CANDIDATE

Peut représenter une donnée brute observée avant interprétation.

Exemple :

```text
external credit score
sanctions hit
geopolitical exposure
```

L'objet n'est à retenir que si la distinction :

```text
observation
vs
assessment
```

apporte une valeur réelle.

---

# 66. RiskDecision

**Status :** DEFERRED CANDIDATE

Peut représenter la décision métier :

```text
acceptable
review_required
block_activation
```

dérivée d'une ou plusieurs observations/assessments.

---

# 67. RiskMitigation

**Status :** PROPOSED SUPPORTING OBJECT

Peut représenter une action ou condition destinée à réduire un risque.

La responsabilité exacte vis-à-vis de Workflow/Task Management doit être surveillée.

---

# 68. RiskPolicy

**Status :** CONFIRMED ARCHITECTURAL CONCEPT  
**DDD role :** Domain Policy

Rôle :

```text
external/internal risk evidence
        │
        ▼
RiskPolicy
        │
        ▼
Domain risk interpretation
```

---

# 69. SupplierAssessment

**Status :** CONFIRMED CONCEPT  
**DDD role candidate :** Entity + Aggregate Root candidate

Types confirmés :

```text
Questionnaire
Audit
Business Evaluation
Compliance Review
Annual Review
Risk Review
Self-Assessment
```

Structure conceptuelle source :

```text
Assessment
├── assessment_type
├── supplier
├── questions
├── answers
├── scores
├── reviewers
├── evidence
└── decision
```

---

# 70. AssessmentId

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object

---

# 71. AssessmentType

**Status :** CONFIRMED NEED  
**DDD role candidate :** Value Object / extensible reference

La taxonomie doit rester extensible.

---

# 72. AssessmentQuestion

**Status :** CONFIRMED NEED  
**DDD role candidate :** Entity or Value Object — unresolved

Question de modélisation :

Une question réutilisable avec identité/version :

```text
Entity
```

Une question figée à l'intérieur d'une Assessment Definition :

```text
Value Object
```

Décision à différer.

---

# 73. AssessmentAnswer

**Status :** CONFIRMED NEED  
**DDD role candidate :** Value Object / child entity candidate

La classification dépendra de :

- la version ;
- l'audit ;
- la correction ;
- l'identité propre.

---

# 74. AssessmentScore

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object

Peut exprimer :

```text
raw score
normalized score
dimension
weight
```

---

# 75. AssessmentDecision

**Status :** CONFIRMED NEED  
**DDD role candidate :** Value Object / Domain result

Exemples :

```text
APPROVED
REJECTED
REVIEW_REQUIRED
```

Peut alimenter qualification, compliance ou risk selon le type d'assessment.

---

# 76. EvidenceReference

**Status :** PROPOSED CROSS-CUTTING VALUE OBJECT

De nombreux objets peuvent avoir besoin de preuves :

```text
Qualification
ComplianceCheck
Assessment
RiskAssessment
Certification
```

`EvidenceReference` pourrait permettre de référencer :

```text
document
external record
URL
external system record
```

sans embarquer le stockage physique.

---

# 77. SupplierPerformance

**Status :** CONFIRMED CAPABILITY  
**DDD role :** conceptual domain area

La source demande une série d'indicateurs mesurables.

Exemples :

```text
Delivery Performance
Quality
Service Level
Cost
Responsiveness
Innovation
Compliance
Sustainability
Incident Rate
```

---

# 78. PerformanceMetric

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** reference definition / Value Object

Représente ce qui est mesuré.

Exemple :

```text
DELIVERY_ON_TIME_RATE
QUALITY_SCORE
INCIDENT_RATE
```

---

# 79. PerformanceMeasurement

**Status :** CONFIRMED NEED  
**DDD role candidate :** Entity or immutable record

Représente une mesure datée ou associée à une période.

Candidate structure :

```text
PerformanceMeasurement
├── metric
├── value
├── period
├── scope
├── source
└── recorded_at
```

---

# 80. PerformancePeriod

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object

Exemples :

```text
2026-Q1
2026-01
2026-01-01 → 2026-03-31
```

---

# 81. PerformanceScore

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object

Peut encapsuler :

- plage autorisée ;
- unité ;
- normalisation.

---

# 82. SupplierScorecard

**Status :** CONFIRMED CONCEPT  
**DDD role candidate :** Aggregate / Projection candidate

Exemple :

```text
Quality       91/100
Delivery      86/100
Cost          78/100
Compliance   100/100
ESG           83/100
Overall       87/100
```

## Modeling question

Une scorecard est-elle :

```text
persisted domain aggregate
```
ou :

```text
derived projection
```

La réponse dépendra des besoins d'historisation et de décision.

---

# 83. ScorecardDimension

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object

Exemples :

```text
QUALITY
DELIVERY
COST
COMPLIANCE
ESG
```

---

# 84. ScorecardPolicy

**Status :** CONFIRMED ARCHITECTURAL CONCEPT

Encapsule :

- pondérations ;
- agrégations ;
- règles de scoring.

## Design concepts

```text
[DDD: Domain Policy]
[PATTERN: Strategy]
[PRINCIPLE: Open/Closed]
```

---

# 85. SupplierIncident

**Status :** CONFIRMED CONCEPT  
**DDD role candidate :** Entity + Aggregate candidate

Types confirmés :

```text
Delay
Non-conforming delivery
Quality issue
Contractual breach
Security incident
Fraud
Service interruption
Regulatory non-compliance
```

## Business effects

Un incident peut influencer :

```text
Performance
Risk
Qualification
Lifecycle status
```

Ces effets ne doivent pas être cachés dans des side effects implicites.

---

# 86. IncidentId

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object

---

# 87. IncidentType

**Status :** CONFIRMED NEED  
**DDD role candidate :** Value Object / extensible reference

---

# 88. IncidentSeverity

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object / Enum

La taxonomie exacte reste configurable.

---

# 89. IncidentStatus

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Enum

Si PySRMKit suit le lifecycle d'un incident, il faudra distinguer ce lifecycle du Supplier Lifecycle.

---

# 90. IncidentImpact

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Value Object

Peut représenter l'impact sans modifier automatiquement d'autres aggregates.

---

# 91. Cross-Aggregate Incident Effects

Exemple :

```text
SupplierIncidentReported
        │
        ├──► Risk reassessment
        ├──► Performance update
        ├──► Qualification review
        └──► Suspension consideration
```

Ces effets doivent idéalement être orchestrés explicitement par :

```text
Application Layer
+
Domain Events
+
Policies
```

plutôt que par appels bidirectionnels cachés.

---

# 92. Supplier Segmentation

**Status :** CONFIRMED CAPABILITY

Segments de référence :

```text
Strategic
Critical
Preferred
Approved
Standard
Transactional
Restricted
```

---

# 93. SupplierSegment

**Status :** CONFIRMED NEED  
**DDD role candidate :** Value Object / reference

Représente le segment attribué.

---

# 94. SegmentationDecision

**Status :** PROPOSED SUPPORTING OBJECT  
**DDD role candidate :** Domain result Value Object

Peut expliquer :

```text
segment
reasons
inputs
decided_at
```

---

# 95. SegmentationPolicy

**Status :** CONFIRMED ARCHITECTURAL CONCEPT  
**DDD role :** Domain Policy  
**Pattern :** Strategy

Inputs possibles :

```text
purchase volume
criticality
dependency
risk
performance
substitutability
```

Note :

les données d'achat peuvent provenir de PyProcurementKit plutôt que du cœur PySRMKit.

---

# 96. Domain History

**Status :** CONFIRMED REQUIREMENT  
**Model :** partially deferred

Le domaine doit permettre de reconstruire :

```text
Supplier Created
Onboarding Started
Documents Submitted
Compliance Approved
Supplier Qualified
Supplier Activated
Performance Review
Risk Increased
Supplier Suspended
Supplier Reactivated
Supplier Offboarded
```

---

# 97. DomainEvent

**Status :** CONFIRMED CONCEPT  
**DDD role :** Domain Event

Exemples :

```text
SupplierCreated
SupplierRegistered
SupplierInvited
SupplierOnboardingStarted
SupplierInformationUpdated
SupplierDocumentSubmitted
SupplierDocumentExpired
SupplierQualificationRequested
SupplierQualified
SupplierQualificationRejected
SupplierActivated
SupplierSuspended
SupplierBlocked
SupplierReactivated
SupplierRiskDetected
SupplierRiskChanged
SupplierAssessmentCompleted
SupplierPerformanceRecorded
SupplierIncidentReported
SupplierOffboarded
```

## Important

```text
DomainEvent
≠
Observer Pattern
≠
Kafka Message
```

---

# 98. EventId

**Status :** PROPOSED SUPPORTING VALUE OBJECT

Peut identifier de manière unique un événement métier pour :

- déduplication ;
- audit ;
- correlation ;
- integration mapping.

---

# 99. OccurredAt

**Status :** PROPOSED SUPPORTING VALUE OBJECT / primitive wrapper

Une date d'événement doit idéalement être explicitement fournie plutôt que dépendre implicitement du système global.

---

# 100. CorrelationId

**Status :** APPLICATION/INTEGRATION SUPPORT OBJECT

Utile pour relier :

- command ;
- events ;
- external calls.

Il ne constitue pas nécessairement un concept du Supplier Domain lui-même.

---

# 101. AuditRecord

**Status :** PROPOSED SUPPORTING OBJECT  
**Layer ownership :** unresolved between domain/application/audit subsystem

Doit permettre de répondre :

```text
WHAT?
WHO?
WHEN?
WHY?
FROM?
TO?
WITH WHICH EVIDENCE?
```

Important :

Un `AuditRecord` n'est pas automatiquement un Domain Event.

---

# 102. ActorReference

**Status :** PROPOSED SUPPORTING OBJECT

Permet de référencer l'acteur à l'origine d'une action sans intégrer IAM dans le domaine.

Exemples :

```text
USER
SYSTEM
AGENT
EXTERNAL_SYSTEM
```

La permission elle-même appartient à l'IAM/Application Layer.

---

# 103. Domain Policies — inventory

Policies déjà justifiées par les specs :

```text
QualificationPolicy
ActivationPolicy
RiskPolicy
CompliancePolicy
SegmentationPolicy
PerformancePolicy
DocumentRequirementPolicy
```

Possible future policy :

```text
ScorecardPolicy
```

---

# 104. ActivationPolicy

**Status :** CONFIRMED ARCHITECTURAL CONCEPT  
**DDD role :** Domain Policy

Rôle :

Déterminer si les préconditions variables d'activation sont satisfaites.

Exemple :

```text
required qualification
required documents
required compliance
risk threshold
```

## Important

La policy complète les invariants.

Elle ne peut pas rendre valide une transition structurellement interdite.

---

# 105. DocumentRequirementPolicy

**Status :** CONFIRMED ARCHITECTURAL CONCEPT

Rôle :

Déterminer quels documents sont requis selon :

```text
country
category
organization
supplier type
risk
```

---

# 106. PerformancePolicy

**Status :** CONFIRMED ARCHITECTURAL CONCEPT

Peut encapsuler :

- règles de scoring ;
- seuils ;
- agrégation.

Selon la conception finale, elle pourra être séparée en plusieurs policies plus cohésives.

---

# 107. Domain Services — candidates

Aucun `DomainService` ne doit être créé par défaut.

Candidats possibles uniquement si la logique le justifie :

```text
SupplierEligibilityService
QualificationEvaluationService
RiskAggregationService
```

Mais avant tout Domain Service, la question doit être :

> Ce comportement peut-il naturellement appartenir à une Entity, un Value Object ou une Policy ?

---

# 108. SupplierEligibilityService

**Status :** DEFERRED CANDIDATE

Peut devenir pertinent si l'éligibilité dépend simultanément de plusieurs objets :

```text
SupplierRelationship
Qualification
Compliance
Risk
Lifecycle
```

## Risk

Peut facilement devenir un "God Service".

À n'introduire qu'avec un use case précis.

---

# 109. Domain Factories — candidates

Le besoin de factories reste limité.

Candidats potentiels :

```text
SupplierFactory
AssessmentFactory
```

uniquement si la création devient complexe.

La priorité reste :

```text
constructor
or
named constructor
```

tant qu'ils suffisent.

---

# 110. SupplierFactory

**Status :** DEFERRED CANDIDATE

Une Factory ne sera justifiée que si créer un Supplier nécessite réellement :

- plusieurs dépendances ;
- plusieurs policies ;
- composition complexe ;
- création coordonnée de plusieurs objets.

Sinon :

```text
Supplier.create(...)
```

reste préférable.

---

# 111. Domain Repositories — candidates

Repositories candidats :

```text
SupplierRepository
SupplierRelationshipRepository
QualificationRepository
AssessmentRepository
RiskAssessmentRepository
IncidentRepository
```

La création d'un Repository dépend de l'existence d'un Aggregate Root autonome.

Il ne faut donc pas créer un repository pour chaque classe.

---

# 112. SupplierRepository

**Status :** CONFIRMED PORT CANDIDATE  
**Pattern :** Repository

Rôle :

```text
load/save Supplier Aggregate
```

Il peut également fournir des recherches liées à l'identité canonique.

Exemple :

```text
find_by_external_identifier
```

---

# 113. Repository Boundary Rule

```text
Repository
per aggregate root
```

est une heuristique plus pertinente que :

```text
Repository
per table/class
```

Cette règle sera validée après définition des aggregates.

---

# 114. Domain Errors — object family

Les erreurs métier font partie du vocabulaire du domaine.

Candidats confirmés ou déjà évoqués :

```text
InvalidLifecycleTransition
QualificationScopeRequired
SupplierAlreadyOffboarded
ActivationRequirementsNotMet
ExpiredDocumentCannotBeAccepted
InvalidCertificationPeriod
```

Ils sont distincts des erreurs techniques.

---

# 115. InvalidLifecycleTransition

**Status :** CONFIRMED NEED

Exprime qu'une transition demandée viole la state machine métier.

Il ne s'agit pas d'une erreur HTTP ou de persistence.

---

# 116. QualificationScopeRequired

**Status :** CONFIRMED NEED

Protège l'invariant :

```text
Qualification must have a scope.
```

---

# 117. ActivationRequirementsNotMet

**Status :** CONFIRMED NEED

Peut transporter une explication structurée des règles non satisfaites.

---

# 118. Domain Decision Objects

Une famille transversale d'objets peut apparaître :

```text
QualificationDecision
ActivationDecision
ComplianceDecision
RiskDecision
SegmentationDecision
```

## Why

Les décisions complexes ont souvent besoin de transporter :

```text
allowed / status
reasons
failed rules
evidence
```

Ces objets facilitent :

- explicabilité ;
- agents ;
- API ;
- audit ;
- tests.

---

# 119. Decision Objects vs Exceptions

Les deux concepts ont des usages différents.

## Decision

Pour un résultat métier attendu :

```text
not qualified because requirement X failed
```

## Exception

Pour une opération invalide :

```text
cannot activate OFFBOARDED supplier
```

Cette distinction devra être affinée dans le `07`.

---

# 120. Generic Value Objects

Plusieurs Value Objects transversaux sont candidats.

```text
SupplierId
SupplierRelationshipId
QualificationId
AssessmentId
IncidentId
ExternalIdentifier
CountryCode
Address
EmailAddress
QualificationScope
DateRange
Percentage
RiskScore
DocumentReference
EvidenceReference
```

Le `05` devra confirmer :

- lesquels existent réellement ;
- lesquels sont immuables ;
- leurs invariants ;
- leur API.

---

# 121. DateRange

**Status :** PROPOSED SUPPORTING VALUE OBJECT

Peut être utilisé pour :

```text
qualification validity
certification validity
assessment period
performance period
```

Invariant :

```text
end >= start
```

lorsque `end` existe.

---

# 122. Percentage

**Status :** PROPOSED SUPPORTING VALUE OBJECT

Peut éviter des conventions incohérentes :

```text
0.87
87
87.0
```

pour les scores en pourcentage.

À introduire seulement si plusieurs domaines en ont réellement besoin.

---

# 123. Money

**Status :** DEFERRED SUPPORTING VALUE OBJECT

Le requirements mentionne des seuils financiers.

Mais PySRMKit n'est pas un domaine comptable.

`Money` ne doit être introduit que si une règle Supplier utilise réellement :

```text
amount + currency
```

Sinon cette responsabilité peut rester dans PyProcurementKit/PyAccountingKit.

---

# 124. Reference Objects

Certains concepts peuvent être des références plutôt que des Entities riches.

Exemples :

```text
Category
DocumentType
CertificationType
AssessmentType
RiskType
IncidentType
```

Le choix dépendra du besoin de :

- versioning ;
- metadata ;
- lifecycle ;
- administration.

---

# 125. Domain Object Ownership Map

Première proposition :

| Object | Domain Area | Candidate DDD Role | Aggregate Root? | Status |
|---|---|---|---:|---|
| Supplier | Supplier Core | Entity | Yes | Strong candidate |
| SupplierIdentity | Supplier Core | VO/component | No | Candidate |
| ExternalIdentifier | Supplier Core | Value Object | No | Strong candidate |
| SupplierOrganization | Organization | Entity | Maybe | Open |
| SupplierContact | Supplier Core | Entity | No/Maybe | Open |
| SupplierLocation | Supplier Core | Entity | No/Maybe | Open |
| Address | Supplier Core | Value Object | No | Strong candidate |
| SupplierCategory | Classification | Reference/VO | No | Open |
| SupplierCapability | Capability | Entity/VO | Maybe | Open |
| SupplierRelationship | Relationship | Entity | Yes | Strong candidate |
| SupplierLifecycleStage | Lifecycle | Value Object/Enum | No | Strong candidate |
| SupplierOnboarding | Onboarding | Entity | Maybe | Open |
| SupplierQualification | Qualification | Entity | Yes/Maybe | Strong candidate |
| QualificationScope | Qualification | Value Object | No | Strong candidate |
| SupplierDocument | Documents | Entity | Maybe | Candidate |
| SupplierCertification | Certification | Entity | Maybe | Candidate |
| ComplianceCheck | Compliance | Entity | Maybe | Proposed |
| RiskAssessment | Risk | Entity | Yes/Maybe | Strong candidate |
| SupplierAssessment | Assessment | Entity | Yes/Maybe | Strong candidate |
| PerformanceMeasurement | Performance | Entity/record | Maybe | Candidate |
| SupplierScorecard | Performance | Aggregate/Projection | Maybe | Open |
| SupplierIncident | Incident | Entity | Yes/Maybe | Strong candidate |
| SupplierSegment | Segmentation | Value Object | No | Strong candidate |
| DomainEvent | History | Domain Event | No | Confirmed |

---

# 126. Aggregate Candidates

Le modèle actuel suggère plusieurs Aggregate Roots potentiels.

```text
Supplier
SupplierRelationship
Qualification
Assessment
RiskAssessment
Incident
```

Possiblement :

```text
Onboarding
Document
Scorecard
```

selon les invariants réels.

---

# 127. Supplier Core Aggregate — candidate boundary

Une frontière initiale raisonnable pourrait être :

```text
Supplier
│
├── SupplierId
├── SupplierIdentity
├── ExternalIdentifiers
├── lightweight categories/capabilities references
└── selected contact/location references
```

Mais :

```text
all assessments
all risks
all incidents
all scorecards
all history
```

ne devraient probablement pas appartenir au même Aggregate.

---

# 128. Why Avoid a God Supplier Aggregate?

Sinon chaque opération pourrait nécessiter :

```text
Supplier
+ 50 documents
+ 20 assessments
+ 15 risks
+ 1000 measurements
+ 200 incidents
+ full history
```

Conséquences :

- persistence lourde ;
- couplage fort ;
- conflits de concurrence ;
- faible modularité ;
- transactions surdimensionnées.

Le domain model doit préférer :

```text
small coherent aggregates
+
references
+
application orchestration
+
domain events
```

---

# 129. SupplierRelationship Aggregate — candidate boundary

Proposition conceptuelle :

```text
SupplierRelationship
├── relationship_id
├── supplier_id
├── internal_organization_id
├── lifecycle
├── segment
└── selected relationship-level state
```

Puis références vers :

```text
Qualifications
Compliance
Risk
Assessments
```

si ces objets deviennent des aggregates séparés.

---

# 130. Qualification Aggregate — candidate boundary

```text
SupplierQualification
├── qualification_id
├── supplier / relationship reference
├── scope
├── status
├── validity
├── decision
└── evidence references
```

Raisons pour un aggregate autonome :

- lifecycle propre ;
- historique ;
- scope obligatoire ;
- réévaluation ;
- expiration ;
- révocation.

---

# 131. Assessment Aggregate — candidate boundary

```text
SupplierAssessment
├── assessment_id
├── type
├── subject
├── questions
├── answers
├── scores
├── evidence
└── decision
```

Il possède potentiellement une cohérence transactionnelle propre.

---

# 132. RiskAssessment Aggregate — candidate boundary

```text
RiskAssessment
├── id
├── subject
├── risk_type
├── assessed_at
├── score├── level
├── evidence
└── mitigation references
```

L'historique temporel plaide pour des records/aggregates distincts plutôt que pour écraser une valeur courante.

---

# 133. Incident Aggregate — candidate boundary

```text
SupplierIncident
├── incident_id
├── type
├── severity
├── occurred_at
├── impact
├── evidence
└── status
```

Les conséquences sur les autres domaines doivent passer par des événements/policies.

---

# 134. Cross-Aggregate References

Les Aggregates doivent se référencer principalement par identifiant.

Exemple :

```text
Qualification
    supplier_id
    relationship_id
```

plutôt que charger automatiquement :

```text
full Supplier
full SupplierRelationship
```

dans chaque objet.

---

# 135. Cross-Aggregate Consistency

La cohérence entre plusieurs aggregates est généralement :

```text
application-coordinated
or
eventually consistent
```

sauf invariant métier nécessitant réellement une transaction unique.

Cette décision sera étudiée use case par use case.

---

# 136. Object Relationships — initial view

```text
Supplier
    1 ─── * ExternalIdentifier

Supplier
    1 ─── * SupplierContact

Supplier
    1 ─── * SupplierLocation

Supplier
    * ─── * SupplierCategory

Supplier
    * ─── * SupplierCapability

Supplier
    1 ─── * SupplierRelationship

SupplierRelationship
    1 ─── * SupplierQualification

SupplierRelationship
    1 ─── * ComplianceCheck

SupplierRelationship
    1 ─── * RiskAssessment

Supplier
    1 ─── * SupplierAssessment

Supplier
    1 ─── * SupplierDocument

Supplier
    1 ─── * SupplierCertification

Supplier
    1 ─── * SupplierIncident

Supplier
    1 ─── * PerformanceMeasurement
```

Cette cardinalité est **indicative**.

Elle sera validée dans le `06`.

---

# 137. Subject / Scope Problem

Plusieurs objets peuvent être attachés à des scopes différents.

Exemple document :

```text
Supplier-level
Legal-entity-level
Location-level
Relationship-level
Qualification-level
```

Même difficulté pour :

```text
Certification
Compliance
Risk
Assessment
```

Le `06` devra déterminer si un concept de :

```text
SubjectRef
Scope
```

est utile ou trop générique.

---

# 138. Avoid Generic Subject Too Early

Il serait tentant de créer immédiatement :

```text
DomainSubject
SubjectRef
ScopedObject[T]
```

Mais cela pourrait rendre le modèle abstrait et difficile à comprendre.

Règle :

> Préférer d'abord des relations métier explicites.

Généraliser uniquement après répétition réelle.

---

# 139. Object Lifecycle Matrix

| Object | Own lifecycle? | Temporal history important? | Candidate state machine? |
|---|---:|---:|---:|
| Supplier | Yes | Yes | Yes |
| SupplierRelationship | Yes | Yes | Likely |
| Qualification | Yes | Yes | Likely |
| Onboarding | Yes | Yes | Yes |
| Document | Yes/derived | Yes | Maybe |
| Certification | Yes/derived | Yes | Maybe |
| ComplianceCheck | Usually finite | Yes | Maybe |
| RiskAssessment | Record-oriented | Yes | No/Maybe |
| Assessment | Yes | Yes | Likely |
| Incident | Possibly | Yes | Maybe |
| Scorecard | Version/period | Yes | Usually no |

---

# 140. State vs Status vs Lifecycle

Le modèle doit éviter d'utiliser ces termes indistinctement.

## Lifecycle

Suite structurée d'états et transitions.

## Status

Valeur décrivant la situation courante d'un objet.

## Decision

Résultat d'une règle métier.

Exemple :

```text
QualificationStatus = PENDING

QualificationDecision = REJECTED
because missing ISO 27001
```

La taxonomie exacte sera précisée objet par objet.

---

# 141. Temporal Objects

Objets fortement temporels :

```text
Qualification
Document
Certification
RiskAssessment
Assessment
PerformanceMeasurement
Incident
Relationship
```

Le temps doit être modélisé explicitement lorsqu'il change la signification métier.

---

# 142. Validity Period

**Status :** PROPOSED VALUE OBJECT

Peut être un alias métier de `DateRange` pour les objets portant une validité :

```text
Qualification
Certification
Document
```

À décider si un seul `DateRange` suffit.

---

# 143. Time and Clock

Une règle telle que :

```text
document.is_expired(at)
```

est plus déterministe que :

```text
document.is_expired()
```

si la seconde lit implicitement l'horloge système.

Le modèle objet doit permettre de tester explicitement le temps.

---

# 144. Domain Object vs Application DTO

Important :

```text
Supplier
≠
CreateSupplierRequest
```

```text
Qualification
≠
QualificationResponseDTO
```

```text
RiskAssessment
≠
RiskProviderPayload
```

Les DTOs servent les frontières applicatives.

Les Domain Objects portent la sémantique métier.

---

# 145. Domain Object vs Persistence Model

Important :

```text
Supplier
≠
SupplierORM
```

Un ORM model peut refléter la persistence.

Il ne doit pas déterminer le Domain Model.

---

# 146. Domain Object vs Integration Model

Important :

```text
External Ivalua Supplier
≠
PySRMKit Supplier
```

La traduction appartient à l'Adapter / Anti-Corruption Layer.

---

# 147. Rich Domain Object

Un objet métier riche encapsule un comportement significatif.

Exemple conceptuel :

```python
supplier.activate(...)
```

plutôt que :

```python
supplier.status = ACTIVE
```

Mais :

> Rich Domain Model ne signifie pas tout mettre dans `Supplier`.

---

# 148. Tell, Don't Ask — candidate principle

Lorsqu'une Entity possède suffisamment d'information pour protéger son invariant, l'application doit préférer lui demander d'agir.

Exemple conceptuel :

```python
supplier.suspend(reason)
```

plutôt que :

```python
if supplier.status == ACTIVE:
    supplier.status = SUSPENDED
```

Le principe sera approfondi dans le `07`.

---

# 149. Encapsulation

Les collections internes ne doivent pas nécessairement être exposées comme listes mutables.

Exemple conceptuel :

```text
supplier.add_identifier(...)
```

plutôt que :

```text
supplier.identifiers.append(...)
```

si l'ajout doit contrôler des invariants.

---

# 150. Information Hiding

Les consommateurs n'ont pas besoin de connaître :

- comment la transition est validée ;
- comment les identifiers sont normalisés ;
- comment les events sont accumulés.

Ils doivent connaître le contrat métier.

---

# 151. Primitive Obsession Risk

Le modèle doit surveiller l'abus de :

```text
str
int
float
dict
```

pour représenter des concepts riches.

Exemples candidats à encapsulation :

```text
SupplierId
ExternalIdentifier
CountryCode
QualificationScope
RiskScore
DocumentReference
DateRange
```

Mais :

> créer un Value Object pour chaque champ serait également excessif.

---

# 152. Anemic Domain Risk

À l'inverse, éviter :

```text
Supplier
    only data

SupplierService
    all behavior
```

Les comportements doivent être placés au niveau le plus cohérent.

---

# 153. God Service Risk

Éviter :

```text
SupplierDomainService
```

contenant :

- qualification ;
- lifecycle ;
- risk ;
- documents ;
- performance ;
- compliance.

Le nom générique cache généralement plusieurs responsabilités.

---

# 154. Generic Metadata

Le `00` prévoit des `metadata`.

Ce mécanisme doit rester contrôlé.

Risque :

```text
metadata
becomes
unmodeled domain
```

Les informations métier importantes doivent devenir des objets explicites plutôt que rester durablement dans un dictionnaire libre.

---

# 155. Metadata Rule

Utiliser `metadata` pour :

- extension temporaire ;
- informations non critiques ;
- données vendor-specific non structurantes.

Ne pas l'utiliser pour :

- lifecycle ;
- qualification ;
- compliance ;
- risk ;
- identifiers principaux.

---

# 156. Domain Events by Object

## Supplier

```text
SupplierCreated
SupplierRegistered
SupplierInformationUpdated
```

## Lifecycle

```text
SupplierInvited
SupplierOnboardingStarted
SupplierActivated
SupplierSuspended
SupplierBlocked
SupplierReactivated
SupplierOffboarded
```

## Document

```text
SupplierDocumentSubmitted
SupplierDocumentExpired
```

## Qualification

```text
SupplierQualificationRequested
SupplierQualified
SupplierQualificationRejected
```

## Risk

```text
SupplierRiskDetected
SupplierRiskChanged
```

## Assessment

```text
SupplierAssessmentCompleted
```

## Performance

```text
SupplierPerformanceRecorded
```

## Incident

```text
SupplierIncidentReported
```

---

# 157. Missing Event Candidates

Le modèle détaillé pourra éventuellement nécessiter :

```text
SupplierQualificationRevoked
SupplierCertificationExpired
SupplierCertificationRevoked
SupplierComplianceFailed
SupplierRelationshipCreated
SupplierSegmentChanged
```

Ces événements sont **candidats**, pas encore confirmés par le document source.

Ils devront être ajoutés seulement si les use cases le justifient.

---

# 158. Policy Mapping

| Domain Area | Policy candidate | Variation represented |
|---|---|---|
| Qualification | QualificationPolicy | qualification criteria |
| Activation | ActivationPolicy | activation prerequisites |
| Compliance | CompliancePolicy | organization/jurisdiction rules |
| Risk | RiskPolicy | risk interpretation |
| Segmentation | SegmentationPolicy | segmentation algorithm |
| Performance | PerformancePolicy | scoring/thresholds |
| Documents | DocumentRequirementPolicy | required documents |
| Scorecard | ScorecardPolicy | aggregation/weights |

---

# 159. Strategy Pattern Mapping

Ces policies sont des **Strategy candidates** lorsque :

```text
multiple interchangeable algorithms
+
stable caller
+
same business intent
```

Elles ne doivent pas être nommées `Strategy` dans le domaine.

---

# 160. Factory Pattern Mapping

Factory n'est pas encore requise partout.

Candidats :

```text
Supplier.create(...)
Assessment.create(...)
```

avant de créer :

```text
SupplierFactory
AssessmentFactory
```

---

# 161. Repository Pattern Mapping

Repositories correspondent aux Aggregate Roots retenus.

Pas aux Value Objects.

Pas automatiquement à chaque Entity.

---

# 162. Adapter Pattern Boundary

Aucun des objets suivants ne doit connaître :

```text
Ivalua DTO
SAP object
REST response
database row
Kafka envelope
```

La traduction appartient aux adapters.

---

# 163. Domain Object Dependency Direction

Un Domain Object peut dépendre de :

```text
other domain types
domain policies
domain errors
domain events
```

Il ne doit pas dépendre de :

```text
application handlers
repositories implementations
adapters
HTTP
ORM
cloud
```

---

# 164. Python Representation — illustrative only

Exemple conceptuel minimal :

```python
@dataclass(frozen=True)
class SupplierId:
    value: UUID


@dataclass(frozen=True)
class ExternalIdentifier:
    kind: str
    value: str
    jurisdiction: str | None = None
```

Il s'agit d'une illustration de la forme.

Le choix final :

```text
UUID
str
dataclass
attrs
Pydantic
```

n'est pas encore figé.

---

# 165. Entity Example — illustrative only

```python
class Supplier:
    def activate(
        self,
        *,
        decision: ActivationDecision,
        occurred_at: datetime,
    ) -> None:
        ...
```

Cette signature n'est pas normative.

Elle illustre :

```text
behavior
instead of
public field mutation
```

---

# 166. Policy Example — illustrative only

```python
class QualificationPolicy(Protocol):
    def evaluate(
        self,
        supplier: Supplier,
        scope: QualificationScope,
    ) -> QualificationDecision:
        ...
```

Concepts :

```text
Domain Policy
Strategy
DIP
OCP
Protocol
```

---

# 167. Event Example — illustrative only

```python
@dataclass(frozen=True)
class SupplierQualified:
    supplier_id: SupplierId
    qualification_id: QualificationId
    scope: QualificationScope
    occurred_at: datetime
```

Le contrat définitif viendra plus tard.

---

# 168. Domain Modeling Heuristic — identity

Question :

> Si toutes les propriétés de cet objet changent, reste-t-il le même objet ?

Si oui :

```text
Entity candidate
```

Exemple :

```text
SupplierContact
```

peut rester la même personne après changement d'email.

---

# 169. Domain Modeling Heuristic — value

Question :

> Deux occurrences ayant exactement les mêmes valeurs sont-elles interchangeables ?

Si oui :

```text
Value Object candidate
```

Exemple :

```text
CountryCode("FR")
```

---

# 170. Domain Modeling Heuristic — aggregate

Question :

> Quels objets doivent être immédiatement cohérents ensemble pour protéger un invariant ?

Réponse :

```text
Aggregate boundary candidate
```

---

# 171. Domain Modeling Heuristic — service

Question :

> Cette règle est-elle métier mais n'appartient-elle naturellement à aucun objet ?

Alors seulement :

```text
Domain Service candidate
```

---

# 172. Domain Modeling Heuristic — policy

Question :

> La règle exprime-t-elle une décision métier qui varie selon l'organisation ou le contexte ?

Alors :

```text
Domain Policy candidate
```

---

# 173. Domain Modeling Heuristic — event

Question :

> Quel fait métier significatif vient réellement de se produire ?

Alors :

```text
Domain Event candidate
```

---

# 174. Domain Modeling Heuristic — repository

Question :

> Devons-nous charger/persister cet Aggregate indépendamment ?

Alors :

```text
Repository candidate
```

---

# 175. Domain Object Test Categories

Chaque catégorie d'objet suggère des tests différents.

## Value Object

```text
construction validation
equality
immutability
normalization
```

## Entity

```text
identity
behavior
state transitions
```

## Aggregate

```text
invariants
transactional consistency
event recording
```

## Policy

```text
decision matrix
replaceability
edge cases
```

## Domain Event

```text
correct emission
correct payload
no emission on failed operation
```

---

# 176. Supplier Tests — candidates

```text
supplier_id remains stable
external identifiers can change without changing supplier identity
duplicate identifiers are handled according to policy
invalid direct lifecycle transition is rejected
```

---

# 177. Relationship Tests — candidates

```text
same supplier can have multiple internal relationships
relationship status can differ by organization
qualification can differ by relationship
offboarding one relationship does not necessarily delete supplier identity
```

---

# 178. Qualification Tests — candidates

```text
qualification requires scope
active supplier is not globally qualified
qualification can expire
qualification can be revoked
policy implementations can vary
```

---

# 179. Document Tests — candidates

```text
expiration date cannot precede issue date
expired document is not valid
verification status is distinct from expiration
storage reference is technology-agnostic
```

---

# 180. Certification Tests — candidates

```text
revoked certification is not active
expiration is time-awarescope is preserved
```

---

# 181. Risk Tests — candidates

```text
risk assessment is timestamped
new assessment does not erase history
risk policy interprets evidence deterministically
```

---

# 182. Assessment Tests — candidates

```text
assessment can retain evidence
decision is linked to assessment execution
completed assessment becomes immutable or versioned according to final design
```

---

# 183. Incident Tests — candidates

```text
incident retains occurred_at
incident event is emitted once accepted
incident does not silently mutate unrelated aggregates
```

---

# 184. Architecture Tests for Domain Objects

Examples :

```text
domain objects do not import SQLAlchemy
domain objects do not import FastAPI
domain objects do not import Ivalua SDK
domain objects do not import message broker clients
```

---

# 185. Domain Object Documentation Convention

Chaque objet majeur devra progressivement être documenté avec :

```text
Business Meaning
Responsibility
Identity
State
Behavior
Invariants
Relationships
Events
DDD Role
Design Concepts Applied
Testing Implications
Open Questions
```

---

# 186. Docstring Convention — Entity

Exemple :

```python
class Supplier:
    """
    Canonical supplier entity.

    Domain role:
        Aggregate Root candidate for supplier master identity.

    Responsibilities:
        - preserve canonical supplier identity;
        - manage supplier-level information;
        - protect supplier-level invariants.

    Design:
        - DDD Entity
        - Encapsulation
        - Information Hiding
    """
```

Le texte définitif devra rester court.

---

# 187. Docstring Convention — Value Object

```python
@dataclass(frozen=True)
class QualificationScope:
    """
    Defines the business scope of a supplier qualification.

    Domain role:
        Value Object.

    Invariant:
        A qualification cannot exist without a valid scope.
    """
```

---

# 188. Docstring Convention — Policy

```python
class QualificationPolicy(Protocol):
    """
    Evaluate supplier qualification rules.

    Domain role:
        Domain Policy.

    Design:
        - Strategy Pattern
        - Open/Closed Principle
        - Dependency Inversion Principle
    """
```

---

# 189. Comments Convention

Le code ne doit pas contenir :

```python
# Strategy pattern
```

sans expliquer le besoin.

Préférer :

```python
# Qualification criteria vary by organization; keep them outside the
# aggregate so the core lifecycle remains stable.
```

---

# 190. Learning Map — Supplier

```text
Supplier
    │
    ├── DDD
    │      Entity
    │      Aggregate Root candidate
    │
    ├── Principles
    │      Encapsulation
    │      Information Hiding
    │      SRP
    │
    └── Python
           class
           typed Value Objects
```

---

# 191. Learning Map — QualificationPolicy

```text
Problem
    variable qualification rules
        │
        ▼
Principles
    OCP + DIP
        │
        ▼
Pattern
    Strategy
        │
        ▼
DDD
    Domain Policy
        │
        ▼
Python
    Protocol
```

---

# 192. Learning Map — SupplierRepository

```text
Problem
    persistence must vary
        │
        ▼
Principle
    DIP
        │
        ▼
DDD
    Repository
        │
        ▼
Architecture
    Port
        │
        ▼
Python
    Protocol
        │
        ▼
Implementations
    InMemory / PostgreSQL / ...
```

---

# 193. Learning Map — ExternalIdentifier

```text
Problem
    external IDs differ by system
        │
        ▼
Domain concept
    ExternalIdentifier
        │
        ▼
DDD
    Value Object
        │
        ▼
Principles
    Information Hiding
    Canonical Identity
```

---

# 194. Learning Map — Ivalua Integration

```text
External Model
    │
    ▼
Problem
    model leakage
    │
    ▼
DDD
    Anti-Corruption Layer
    │
    ▼
Pattern
    Adapter
    │
    ▼
Domain
    Supplier
```

Cet adapter n'est pas lui-même un Domain Object, mais il protège les Domain Objects.

---

# 195. Core vs Supporting Objects

## Core

```text
Supplier
SupplierRelationship
SupplierLifecycle
SupplierOnboarding
SupplierQualification
```

## Important supporting

```text
SupplierDocument
SupplierCertification
ComplianceCheck
RiskAssessment
SupplierAssessment
PerformanceMeasurement
SupplierIncident
SupplierSegment
```

## Foundational Value Objects

```text
SupplierId
ExternalIdentifier
Address
CountryCode
QualificationScope
DateRange
DocumentReference
RiskScore
```

---

# 196. Objects Outside PySRMKit Core

Les objets suivants ne doivent pas devenir des Domain Objects PySRMKit.

```text
PurchaseOrder
PurchaseRequisition
RFQ
RFP
Invoice
Payment
VendorLedgerAccount
GeneralLedgerEntry
Full Contract Aggregate
WorkflowTask
UserAccount
OAuthToken
Blob
KafkaMessage
HTTPResponse
```

---

# 197. Why Exclude PurchaseOrder?

Parce que :

```text
Supplier Relationship
≠
Purchasing Process
```

`PurchaseOrder` appartient à PyProcurementKit.

---

# 198. Why Exclude VendorLedgerAccount?

Parce que :

```text
Supplier
≠
Vendor Ledger Account
```

Le compte fournisseur appartient à PyAccountingKit.

---

# 199. Why Exclude Contract Aggregate?

PySRMKit peut référencer un contrat.

Mais le lifecycle contractuel complet appartient à PyContractKit.

---

# 200. Why Exclude WorkflowTask?

PySRMKit définit la validité métier.

PyWorkflowKit peut définir :

```text
who approves
when
in which order
with which SLA
```

---

# 201. Why Exclude Physical File?

PySRMKit connaît :

```text
DocumentReference
EvidenceReference
```

pas nécessairement :

```text
file bytes
S3 object
Azure blob
```

---

# 202. Multi-Organization Impact on Objects

Le multi-organisation pousse plusieurs concepts vers `SupplierRelationship`.

Probables relationship-scoped objects :

```text
Lifecycle
Qualification
Segmentation
Compliance
Risk
```

Mais certains concepts peuvent aussi exister globalement.

Cette dualité devra être explicitement résolue.

---

# 203. Multi-Country Impact on Objects

Les objets suivants doivent rester jurisdiction-aware :

```text
ExternalIdentifier
Address
DocumentType
ComplianceRequirement
Certification
Tax-related references
```

Le domaine ne doit pas supposer que :

```text
SIREN
SIRET
URSSAF
```

sont universels.

---

# 204. Object Scope Matrix

| Object | Global Supplier | Legal Entity | Relationship | Location | Qualification Scope |
|---|---:|---:|---:|---:|---:|
| ExternalIdentifier | Yes | Possible | Rare | Rare | No |
| Contact | Yes | Yes | Possible | Possible | No |
| Document | Yes | Yes | Yes | Possible | Possible |
| Certification | Yes | Yes | Yes | Possible | Possible |
| Compliance | Possible | Yes | Yes | Possible | Possible |
| Risk | Possible | Yes | Yes | Possible | Possible |
| Qualification | No/rare | Possible | Yes | No | Yes |
| Performance | Possible | Possible | Yes | Possible | Possible |
| Incident | Possible | Possible | Yes | Possible | Possible |

Cette matrice est exploratoire.

---

# 205. Key Modeling Tension — Supplier vs Relationship

La question la plus structurante du modèle reste :

> Qu'est-ce qui appartient au Supplier global et qu'est-ce qui appartient à la relation entre le Supplier et une organisation interne ?

Une première règle de raisonnement :

```text
Intrinsic to external supplier
    → Supplier

Specific to how "we" work with supplier
    → SupplierRelationship
```

---

# 206. Examples — Supplier-scoped

Probablement :

```text
legal name
trading name
external legal identifiers
group structure
global sites
global contacts
```

---

# 207. Examples — Relationship-scoped

Probablement :

```text
our lifecycle with supplier
our qualification
our segmentation
our suspension
our relationship-specific compliance
our relationship-specific risk appetite decision
```

---

# 208. Key Modeling Tension — Evidence vs Decision

Plusieurs capabilities doivent distinguer :

```text
evidence
```

de :

```text
business decision
```

Exemples :

```text
External risk score
≠
Risk decision

Sanctions API response
≠
Compliance decision

Certificate file
≠
Certification validity decision
```

Cette séparation est essentielle pour les Domain Objects.

---

# 209. EvidenceReference as shared concept

Si plusieurs objets ont besoin de référencer des preuves, `EvidenceReference` peut devenir un Value Object transverse.

Mais il ne doit pas devenir un conteneur générique opaque.

---

# 210. Key Modeling Tension — Definition vs Instance

Plusieurs domaines possèdent :

```text
definition
vs
execution/instance
```

Exemples :

```text
AssessmentDefinition
vs
SupplierAssessment

ComplianceRequirement
vs
ComplianceCheck

PerformanceMetric
vs
PerformanceMeasurement
```

Cette distinction sera importante pour éviter les mélanges.

---

# 211. Assessment Definition — candidate

**Status :** DEFERRED CANDIDATE

Peut devenir nécessaire pour versionner :

- questionnaires ;
- questions ;
- scoring rules.

Mais le MVP peut commencer sans moteur générique de questionnaire.

---

# 212. Performance Metric Definition — candidate

Même distinction :

```text
metric definition
vs
measurement
```

Le premier décrit ce qui doit être mesuré.

Le second contient une valeur observée.

---

# 213. Compliance Requirement — definition object

Même logique :

```text
Requirement
    rule/expectation

Check
    actual verification
```

---

# 214. Domain Object Stability Levels

Tous les objets n'ont pas la même stabilité.

## Stable early

```text
Supplier
SupplierId
ExternalIdentifier
QualificationScope
DomainEvent concept
```

## Likely stable after modeling

```text
SupplierRelationship
Qualification
Assessment
RiskAssessment
Incident
```

## More experimental

```text
ComplianceFinding
RiskObservation
SupplierScorecard aggregate form
Generic Scope/Subject abstractions
```

---

# 215. MVP Domain Objects

Pour le MVP, priorité à :

```text
Supplier
SupplierId
SupplierIdentity
ExternalIdentifier
SupplierContact
SupplierLocation
Address
SupplierCategory
SupplierCapability
SupplierRelationship
SupplierLifecycleStage
SupplierOnboarding
SupplierQualification
QualificationScope
QualificationDecision
SupplierAssessment
DomainEvent
QualificationPolicy
ActivationPolicy
SupplierRepository
```

Cette liste reste à ajuster après le `05`.

---

# 216. Phase 2 Domain Objects

Trust & Control :

```text
SupplierDocument
DocumentType
DocumentReference
SupplierCertification
CertificationType
ComplianceRequirement
ComplianceCheck
RiskAssessment
RiskScore
EvidenceReference
```

---

# 217. Phase 3 Domain Objects

Relationship Intelligence :

```text
PerformanceMetric
PerformanceMeasurement
SupplierScorecard
SupplierIncident
SupplierSegment
SegmentationDecision
```

---

# 218. Domain Object Traceability — requirements

Exemples :

```text
FR-001 Create Supplier
    → Supplier

FR-003 Manage Identifiers
    → ExternalIdentifier

FR-004 Supplier Organizations
    → SupplierOrganization

FR-005 Contacts
    → SupplierContact

FR-006 Locations
    → SupplierLocation + Address

FR-009 Lifecycle
    → SupplierLifecycleStage + transition behavior

FR-010/011 Onboarding
    → SupplierOnboarding

FR-012/013/014 Qualification
    → SupplierQualification + QualificationScope

FR-015/016 Documents
    → SupplierDocument

FR-017 Certifications
    → SupplierCertification

FR-018 Compliance
    → ComplianceRequirement / ComplianceCheck

FR-019/020 Risk
    → RiskAssessment

FR-021/022 Assessment
    → SupplierAssessment

FR-023 Performance
    → PerformanceMeasurement

FR-024 Scorecard
    → SupplierScorecard

FR-025 Incident
    → SupplierIncident

FR-026 Segmentation
    → SupplierSegment + SegmentationPolicy
```

---

# 219. Domain Object Traceability — invariants

```text
INV-001
Supplier + SupplierId + ExternalIdentifier

INV-002
SupplierLifecycleStage + transition rules

INV-003
SupplierRelationship + SupplierQualification

INV-004
QualificationScope

INV-005
ComplianceCheck

INV-006
RiskAssessment.assessed_at

INV-007
PerformanceMeasurement.period/recorded_at

INV-008
SupplierDocument + validity

INV-009
SupplierCertification + status

INV-010
LifecycleTransitionReason

INV-011
History / Domain Events

INV-012
SupplierRelationship history

INV-013
Domain Events only after accepted transition
```

---

# 220. Domain Object Traceability — architecture

```text
Supplier
    Domain Entity

QualificationPolicy
    Domain Policy / Strategy

SupplierRepository
    Repository Port

DomainEvent
    Domain concept

IvaluaSupplierAdapter
    Adapter / ACL
    NOT a domain object

ActivateSupplierCommand
    Application object
    NOT a domain object

SupplierResponseDTO
    Interface/Application DTO
    NOT a domain object
```

---

# 221. What `04` Deliberately Does Not Decide

Ce document ne décide pas définitivement :

```text
Supplier aggregate exact boundary
SupplierRelationship aggregate exact boundary
whether Contact is child entity or separate aggregate
whether Location is child entity or separate aggregate
whether Capability is Entity or Value Object
whether Document is aggregate root
whether Scorecard is projection or aggregate
whether RiskObservation exists
whether ComplianceFinding exists
whether SupplierFactory exists
whether UnitOfWork exists
```

---

# 222. Decisions Deferred to `05`

`05_PYSRMKIT_ENTITIES_AND_VALUE_OBJECTS.md` devra trancher principalement :

- Entity vs Value Object ;
- identité ;
- immutabilité ;
- value equality ;
- primitive wrappers ;
- enum vs extensible type ;
- child entity vs aggregate.

---

# 223. Decisions Deferred to `06`

`06_PYSRMKIT_DOMAIN_RELATIONSHIPS_AND_ERD.md` devra trancher principalement :

- cardinalités ;
- ownership ;
- aggregate boundaries ;
- supplier vs relationship scope ;
- organization graph ;
- document/certification scope ;
- cross-aggregate references.

---

# 224. Decisions Deferred to `07`

`07_PYSRMKIT_DOMAIN_INVARIANTS_AND_BUSINESS_RULES.md` devra trancher :

- transition guards ;
- qualification invariants ;
- document validity ;
- certification validity ;
- risk rules ;
- suspension/blocking rules ;
- decision vs exception model.

---

# 225. Decisions Deferred to `08`

`08_PYSRMKIT_COMMANDS_QUERIES_AND_USE_CASES.md` devra préciser :

- creation flows ;
- handlers ;
- commands ;
- queries ;
- orchestration ;
- transaction boundaries ;
- event dispatch.

---

# 226. Design Concepts Applied — this document

## DDD

```text
Entity
Value Object
Aggregate
Aggregate Root
Domain Policy
Domain Service
Domain Event
Repository
Anti-Corruption Layer
```

## Principles

```text
Domain First
Encapsulation
Information Hiding
SRP
OCP
DIP
KISS
YAGNI
High Cohesion
Low Coupling
Tell, Don't Ask — candidate
```

## Patterns

```text
Strategy
Repository
Adapter
Factory — conditional
State — explicitly not assumed
```

## Python

```text
Protocol
dataclass candidate
Enum candidate
typed IDs
typed errors
composition
```
---

# 227. Pattern Evidence — Strategy

Present when:

```text
QualificationPolicy
RiskPolicy
CompliancePolicy
SegmentationPolicy
```

possess genuinely interchangeable behaviors.

Not because the classes merely share an interface.

---

# 228. Pattern Evidence — Repository

Present when:

```text
Aggregate persistence
```

is abstracted behind a domain-oriented collection interface.

Not merely because a class exposes CRUD methods.

---

# 229. Pattern Evidence — Adapter

Present at external boundaries when one model/interface is translated to another.

Not inside the Domain Model itself.

---

# 230. Pattern Evidence — Factory

Not confirmed yet.

Requires actual construction pressure.

---

# 231. Pattern Evidence — State

Not confirmed yet.

Lifecycle state machine exists.

GoF State Pattern does not yet.

---

# 232. Learning Checklist for Each Future Object

For every important object, ask:

```text
[ ] What business reality does it represent?
[ ] Does it have identity?
[ ] Is it defined by value?
[ ] Which invariant does it own?
[ ] Which behavior naturally belongs to it?
[ ] Is it part of an aggregate?
[ ] Is it an aggregate root?
[ ] Is this rule instead a policy?
[ ] Is a service really needed?
[ ] Which events can it emit?
[ ] What should remain outside it?
[ ] Which test proves its role?
[ ] Which pattern, if any, actually emerges?
```

---

# 233. Domain Model North Star

Le modèle cible doit permettre de lire le métier dans le code.

Exemple souhaité :

```text
Supplier
SupplierRelationship
QualificationScope
QualificationPolicy
RiskAssessment
SupplierDocument
SupplierIncident
```

et non :

```text
Record
Manager
Helper
GenericEntity
DataObject
Processor
```

---

# 234. Domain Model Summary

La première carte d'objets de PySRMKit peut être résumée ainsi :

```text
                         SUPPLIER DOMAIN
                               │
                               ▼
                            Supplier
                               │
           ┌───────────────────┼────────────────────┐
           │                   │                    │
           ▼                   ▼                    ▼
       Identity          Organization         Relationship
                                                    │
                                 ┌──────────────────┼──────────────────┐
                                 ▼                  ▼                  ▼
                             Lifecycle          Onboarding        Qualification
                                                                      │
                                                                      ▼
                                                               QualificationScope

             ┌────────────────────── TRUST & CONTROL ───────────────────────┐
             │                                                               │
             ▼                    ▼                    ▼                      ▼
         Documents          Certifications        Compliance                Risk
                                                      │                      │
                                                      ▼                      ▼
                                               ComplianceCheck       RiskAssessment

             ┌──────────────── RELATIONSHIP INTELLIGENCE ─────────────────┐
             │                                                             │
             ▼                    ▼                    ▼                    ▼
        Assessments          Performance          Incidents           Segmentation
                                 │
                                 ▼
                              Scorecard

                               │
                               ▼
                         Domain Events
                         History / Audit
```

---

# 235. Key Architectural Consequence

La conclusion principale de ce document est :

> **`Supplier` est central, mais il n'est pas le domaine entier.**

Le Domain Model doit éviter :

```text
Supplier
    owns everything
```

et tendre vers :

```text
Supplier Core Aggregate
+
SupplierRelationship
+
coherent related aggregates
+
Value Objects
+
Policies
+
Domain Events
```

---

# 236. Pedagogical Consequence

Ce modèle devient également un support direct de pratique DDD.

```text
Supplier
    → Entity / Aggregate question

QualificationScope
    → Value Object

QualificationPolicy
    → Domain Policy + Strategy

SupplierRepository
    → Repository + DIP

IvaluaSupplierAdapter
    → Adapter + ACL

SupplierActivated
    → Domain Event

Lifecycle
    → State Machine
      not automatically State Pattern
```

Les concepts ne sont donc pas ajoutés pour être étudiés.

Ils sont étudiés parce qu'ils apparaissent naturellement dans le modèle.

---

# 237. Next Step

Le prochain document est :

> **`05_PYSRMKIT_ENTITIES_AND_VALUE_OBJECTS.md`**

Il devra reprendre chaque objet candidat et décider plus précisément :

```text
ENTITY?
VALUE OBJECT?
REFERENCE OBJECT?
CHILD ENTITY?
AGGREGATE ROOT?
DOMAIN RESULT?
ENUM?
```

avec, pour chacun :

- identité ;
- equality semantics ;
- immutabilité ;
- lifecycle ;
- invariants ;
- Python representation candidate ;
- tests ;
- justification DDD.

---

# 238. Conclusion

PySRMKit possède désormais une première carte explicite de ses Domain Objects.

Le modèle s'organise autour d'un noyau :

```text
Supplier
+
SupplierRelationship
+
Lifecycle
+
Onboarding
+
Qualification
```

enrichi par :

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

et soutenu par :

```text
Value Objects
Policies
Domain Services
Domain Events
Repositories
Domain Errors
```

Le point le plus important est de ne pas confondre :

```text
Domain object inventory
```

avec :

```text
final class hierarchy
```

Ce document expose les concepts et les pressions de conception.

Les prochains documents devront progressivement transformer cette carte en un modèle précis.

La règle demeure :

> **Identifier le concept avant de choisir la classe.**

> **Identifier l'invariant avant de choisir l'Aggregate.**

> **Identifier la variation avant de choisir Strategy.**

> **Identifier la frontière avant de choisir Repository.**

> **Identifier le problème avant de choisir le pattern.**