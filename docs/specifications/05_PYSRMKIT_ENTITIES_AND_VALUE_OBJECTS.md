# PySRMKit — Entities and Value Objects

**Document :** `05_PYSRMKIT_ENTITIES_AND_VALUE_OBJECTS.md`  
**Projet :** PySRMKit  
**Domaine :** Supplier Relationship Management  
**Type :** Domain Modeling — Entities, Value Objects et identité métier  
**Statut :** Draft de modélisation détaillée  
**Version du document :** 0.1.0  
**Documents de référence :**
- `00_PYSRMKIT_EXPRESSION_DU_BESOIN.md`
- `01_PYSRMKIT_REQUIREMENTS_ANALYSIS.md`
- `02_PYSRMKIT_PRODUCT_VISION_AND_ARCHITECTURE_PRINCIPLES.md`
- `03_PYSRMKIT_SYSTEM_ARCHITECTURE.md`
- `04_PYSRMKIT_DOMAIN_OBJECTS.md`
- `PYSRMKIT_SOFTWARE_DESIGN_LEARNING_CONVENTION.md`

---

# 1. Objet du document

Ce document précise la classification DDD des principaux objets de PySRMKit.

Il vise à répondre aux questions suivantes :

> Quels concepts sont des **Entities** ?

> Quels concepts sont des **Value Objects** ?

> Quels objets possèdent une identité durable ?

> Quels objets doivent être immuables ?

> Quels objets sont comparés par identité et lesquels par valeur ?

> Quels objets sont enfants d’un Aggregate ?

> Quels objets peuvent devenir Aggregate Roots ?

> Quels concepts doivent rester des références simples ?

> Quels concepts ne doivent surtout pas être modélisés comme de simples primitives ?

Le document ne définit pas encore :

- toutes les relations et cardinalités finales ;
- les schémas de base de données ;
- les classes Python définitives ;
- les repositories finaux ;
- les signatures finales des commandes ;
- les stratégies de sérialisation ;
- les mappings ORM.

Ces éléments seront approfondis dans :

```text
06_PYSRMKIT_DOMAIN_RELATIONSHIPS_AND_ERD.md
07_PYSRMKIT_DOMAIN_INVARIANTS_AND_BUSINESS_RULES.md
08_PYSRMKIT_COMMANDS_QUERIES_AND_USE_CASES.md
```

---

# 2. Principe de classification

La distinction Entity / Value Object ne dépend pas principalement de la forme technique de l’objet.

Elle dépend de sa **sémantique métier**.

---

# 3. Entity — définition retenue

Une **Entity** possède une identité propre qui persiste à travers le temps.

Même si plusieurs attributs changent, l’objet reste conceptuellement le même.

Question de référence :

> **Si toutes les propriétés changent, est-ce toujours le même objet métier ?**

Si oui :

```text
Entity candidate
```

Exemple :

```text
SupplierContact
```

peut changer :

- d’email ;
- de téléphone ;
- de rôle ;

tout en restant la même personne de contact.

---

# 4. Value Object — définition retenue

Un **Value Object** est défini par ses valeurs.

Deux instances possédant les mêmes valeurs sont conceptuellement interchangeables.

Question de référence :

> **Deux occurrences ayant les mêmes valeurs représentent-elles la même valeur métier ?**

Si oui :

```text
Value Object candidate
```

Exemple :

```text
CountryCode("FR")
```

Deux occurrences de ce code représentent la même valeur.

---

# 5. Aggregate Root — rappel

Une **Aggregate Root** est une Entity qui protège un ensemble d’invariants transactionnels.

Elle définit la frontière à l’intérieur de laquelle les changements doivent rester immédiatement cohérents.

Question de référence :

> **Quels objets doivent être modifiés de façon cohérente dans une même décision métier ?**

Un Aggregate Root n’est pas :

```text
the biggest object
```

ni :

```text
the object with most fields
```

---

# 6. Child Entity — rappel

Une Entity peut posséder une identité sans être Aggregate Root.

Elle peut vivre à l’intérieur d’un Aggregate.

Exemple possible :

```text
Supplier
    └── SupplierContact
```

si la gestion du contact n’a aucun lifecycle indépendant du Supplier.

Cette décision dépendra des invariants réels.

---

# 7. Reference Object — rappel

Certains objets décrivent une taxonomie ou une référence stable.

Exemples :

```text
Category
DocumentType
AssessmentType
RiskType
```

Ils peuvent être :

- Value Objects ;
- reference entities ;
- configuration data ;

selon le besoin de :

- versioning ;
- metadata ;
- lifecycle ;
- administration.

---

# 8. Domain Result — rappel

Certains objets représentent le résultat d’une décision métier.

Exemples :

```text
QualificationDecision
ActivationDecision
RiskDecision
SegmentationDecision
```

Ils ne sont généralement ni Entities ni Aggregate Roots.

Ils sont souvent :

```text
immutable Value Objects
```

ou :

```text
immutable result objects
```

---

# 9. Classification globale — première décision

| Objet | Classification candidate | Identité propre ? | Immuable ? | Aggregate Root ? | Statut |
|---|---|---:|---:|---:|---|
| Supplier | Entity | Oui | Non | Oui | Strong |
| SupplierId | Value Object | Non | Oui | Non | Strong |
| SupplierIdentity | Value Object / component | Non | Oui | Non | Strong |
| ExternalIdentifier | Value Object | Non | Oui | Non | Strong |
| SupplierContact | Entity | Oui | Non | Non/Maybe | Strong |
| SupplierLocation | Entity | Oui | Non | Non/Maybe | Strong |
| Address | Value Object | Non | Oui | Non | Strong |
| CountryCode | Value Object | Non | Oui | Non | Strong |
| SupplierCategory | Reference Object / VO | Non/Maybe | Oui | Non | Open |
| SupplierCapability | Entity or VO | Maybe | Maybe | No/Maybe | Open |
| SupplierRelationship | Entity | Oui | Non | Oui | Strong |
| SupplierRelationshipId | Value Object | Non | Oui | Non | Strong |
| SupplierLifecycleStage | Value Object / Enum | Non | Oui | Non | Strong |
| SupplierOnboarding | Entity | Oui | Non | Maybe | Open |
| SupplierQualification | Entity | Oui | Non | Yes/Maybe | Strong |
| QualificationId | Value Object | Non | Oui | Non | Strong |
| QualificationScope | Value Object | Non | Oui | Non | Strong |
| QualificationDecision | Domain Result / VO | Non | Oui | Non | Strong |
| SupplierDocument | Entity | Oui | Non | Maybe | Strong |
| DocumentReference | Value Object | Non | Oui | Non | Strong |
| SupplierCertification | Entity | Oui | Non | Maybe | Strong |
| ComplianceRequirement | Reference/VO | Non/Maybe | Oui | Non | Open |
| ComplianceCheck | Entity | Oui | Non | Maybe | Strong |
| ComplianceResult | Domain Result / VO | Non | Oui | Non | Strong |
| RiskAssessment | Entity | Oui | Non | Yes/Maybe | Strong |
| RiskScore | Value Object | Non | Oui | Non | Strong |
| RiskLevel | Value Object / Enum | Non | Oui | Non | Strong |
| SupplierAssessment | Entity | Oui | Non | Yes/Maybe | Strong |
| AssessmentAnswer | Value Object / Child Entity | Maybe | Maybe | Non | Open |
| AssessmentScore | Value Object | Non | Oui | Non | Strong |
| AssessmentDecision | Domain Result / VO | Non | Oui | Non | Strong |
| PerformanceMeasurement | Entity / immutable record | Maybe | Often yes | Maybe | Open |
| SupplierScorecard | Projection or Entity | Maybe | Maybe | Maybe | Open |
| SupplierIncident | Entity | Oui | Non | Yes/Maybe | Strong |
| IncidentSeverity | Value Object / Enum | Non | Oui | Non | Strong |
| SupplierSegment | Value Object / reference | Non | Oui | Non | Strong |
| SegmentationDecision | Domain Result / VO | Non | Oui | Non | Strong |
| EvidenceReference | Value Object | Non | Oui | Non | Strong |
| DateRange | Value Object | Non | Oui | Non | Strong |

---

# 10. Supplier — Entity / Aggregate Root

**Classification :** Entity  
**Aggregate Root :** Oui — candidat principal  
**Status :** STRONG DECISION

## Identity

```text
SupplierId
```

## Why Entity

Le Supplier garde son identité même si changent :

- sa raison sociale ;
- son adresse ;
- ses contacts ;
- ses catégories ;
- ses identifiants externes.

## Why Aggregate Root

Le Supplier protège les invariants de son identité canonique.

Exemple :

```text
duplicate external identifier handling
canonical identity consistency
supplier-level master data integrity
```

## Equality

L’égalité métier du Supplier doit être basée sur :

```text
SupplierId
```

et non sur :

```text
legal_name
SIREN
ERP_VENDOR_ID
```

---

# 11. SupplierId — Value Object

**Classification :** Value Object  
**Status :** STRONG DECISION

## Responsibility

Représenter l’identité interne stable du Supplier.

## Properties

```text
immutable
validated
hashable
serializable
```

## Equality

Par valeur.

```text
SupplierId("A") == SupplierId("A")
```

## Python candidate

```python
@dataclass(frozen=True, slots=True)
class SupplierId:
    value: UUID
```

Le type interne exact n’est pas encore figé.

---

# 12. SupplierIdentity — Value Object / Composite Value Object

**Classification :** Value Object candidate  
**Status :** STRONG CANDIDATE

Le `SupplierIdentity` regroupe les valeurs fondamentales décrivant l’identité légale/commerciale.

Exemple conceptuel :

```text
SupplierIdentity
├── legal_name
├── trading_name
├── supplier_type
└── primary_legal_reference
```

## Why Value Object

Le composant ne nécessite pas nécessairement une identité indépendante.

Sa valeur est portée par son contenu.

## Important

`SupplierIdentity` ne remplace pas l’identité de l’Entity `Supplier`.

```text
SupplierId
    = identity of entity

SupplierIdentity
    = business descriptive value
```

---

# 13. ExternalIdentifier — Value Object

**Classification :** Value Object  
**Status :** STRONG DECISION

Structure candidate :

```text
ExternalIdentifier
├── type
├── value
├── source_system?
└── jurisdiction?
```

Exemples :

```text
SIREN
SIRET
DUNS
VAT_NUMBER
IVALUA_SUPPLIER_ID
SAP_VENDOR_ID
```

## Invariants candidates

```text
type must exist
value must not be blank
jurisdiction format valid when present
```

## Design concepts

```text
[DDD: Value Object]
[PRINCIPLE: Canonical Identity]
[PRINCIPLE: Information Hiding]
```

---

# 14. SupplierContact — Entity

**Classification :** Entity  
**Aggregate Root :** probablement non  
**Status :** STRONG CANDIDATE

## Identity candidate

```text
SupplierContactId
```

## Why Entity

Un contact peut :

- changer d’email ;
- changer de téléphone ;
- changer de rôle ;
- devenir inactif ;

sans devenir une nouvelle personne.

## Aggregate membership

Première hypothèse :

```text
Supplier
    owns
SupplierContact
```

Mais la décision définitive dépendra des use cases :

- contacts partagés entre plusieurs Supplier entities ?
- historique indépendant ?
- accès direct par identifiant ?

---

# 15. SupplierContactId — Value Object

**Classification :** Value Object  
**Status :** PROPOSED

Identifie un SupplierContact.

À introduire uniquement si `SupplierContact` est confirmé comme Entity.

---

# 16. ContactRole — Value Object / reference

**Classification :** Value Object candidate

Exemples :

```text
SALES
ACCOUNTING
LEGAL
COMPLIANCE
SUPPORT
```

## Open question

Taxonomie fermée :

```text
Enum
```

ou extensible :

```text
Reference Value Object
```

Le contexte multi-organisation plaide pour l’extensibilité.

---

# 17. EmailAddress — Value Object

**Classification :** Value Object  
**Status :** STRONG CANDIDATE

## Responsibility

Encapsuler :

- validation ;
- normalisation éventuelle ;
- égalité par valeur.

## Important

`EmailAddress` ne gère pas :

- envoi ;
- SMTP ;
- notification.

---

# 18. PhoneNumber — Value Object candidate

**Classification :** Value Object  
**Status :** PROPOSED

À introduire uniquement si :

- normalisation ;
- validation ;
- internationalisation ;

justifient autre chose qu’une chaîne.

---

# 19. SupplierLocation — Entity

**Classification :** Entity  
**Status :** STRONG CANDIDATE

## Identity candidate

```text
SupplierLocationId
```

## Why Entity

Une implantation :

- peut déménager ;
- changer d’adresse ;
- changer de fonction ;
- rester le même site métier.

Exemple :

```text
Factory A
```

reste Factory A après changement de rue.

---

# 20. SupplierLocationId — Value Object

**Classification :** Value Object  
**Status :** PROPOSED

Introduit si `SupplierLocation` reste Entity.

---

# 21. Address — Value Object

**Classification :** Value Object  
**Status :** STRONG DECISION

## Why

L’adresse est définie par sa valeur.

Structure candidate :

```text
Address
├── line1
├── line2?
├── postal_code?
├── city
├── region?
├── country_code
```

## Multi-country

Aucun champ ne doit supposer le modèle postal français comme universel.

---

# 22. CountryCode — Value Object

**Classification :** Value Object  
**Status :** STRONG DECISION

Structure probable :

```text
ISO 3166 alpha-2
```

mais la dépendance à une librairie externe n’est pas obligatoire.

---

# 23. SupplierCategory — Reference Object / Value Object

**Classification :** OPEN  
**Status :** DECISION DEFERRED

Deux options.

## Option A — Value Object

```text
CategoryCode("IT_SERVICES")
```

suffit si la catégorie est simplement une référence stable.

## Option B — Reference Entity

Nécessaire si la catégorie possède :

- label ;
- version ;
- hierarchy ;
- metadata ;
- lifecycle ;
- administration.

## Default recommendation

Commencer par :

```text
CategoryCode
```

ou un Value Object léger.

Éviter une Entity riche trop tôt.

---

# 24. CategoryCode — Value Object

**Classification :** Value Object  
**Status :** STRONG CANDIDATE

Exemple :

```text
CategoryCode("IT_SERVICES")
```

---

# 25. SupplierCapability — Entity or Value Object

**Classification :** OPEN

## Option A — Value Object

Si une capability signifie simplement :

```text
"Supplier can provide DATA_ENGINEERING"
```

alors :

```text
CapabilityCode
```

peut suffire.

## Option B — Entity

Si elle porte :

```text
status
verification
source
evidence
validity
history
```

alors elle possède potentiellement une identité propre.

## Default recommendation

Commencer par une Value Object/reference representation.

Élever en Entity lorsque le besoin de lifecycle indépendant apparaît.

---

# 26. CapabilityCode — Value Object

**Classification :** Value Object candidate

Exemple :

```text
CapabilityCode("DATA_ENGINEERING")
```

---

# 27. SupplierRelationship — Entity / Aggregate Root

**Classification :** Entity  
**Aggregate Root :** Oui — strong candidate  
**Status :** STRONG DECISION

## Business identity

Une relation fournisseur est distincte du Supplier lui-même.

Elle exprime :

```text
Supplier X
works with
Internal Organization Y
under
Relationship Z
```

## Identity

```text
SupplierRelationshipId
```

## Why Entity

La relation possède son propre lifecycle.

Elle peut :

- devenir active ;
- être suspendue ;
- être offboardée ;

tout en restant la même relation.

## Why Aggregate Root

Elle semble posséder ses propres invariants transactionnels.

Exemples :

```text
relationship lifecycle
organization-specific qualification
organization-specific segmentation
```

---

# 28. SupplierRelationshipId — Value Object

**Classification :** Value Object  
**Status :** STRONG DECISION

---

# 29. InternalOrganizationId — Value Object

**Classification :** Value Object  
**Status :** STRONG CANDIDATE

Référence l’entité interne.

PySRMKit ne doit pas devenir propriétaire de tout le modèle d’organisation interne.

---

# 30. SupplierLifecycleStage — Enum / Value Object

**Classification :** Value Object  
**Implementation candidate :** Enum  
**Status :** STRONG DECISION

États :

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

## Important

L’Enum représente l’état.

Elle ne représente pas toute la State Machine.

---

# 31. LifecycleTransition — Value Object candidate

**Classification :** Value Object / Domain Result  
**Status :** PROPOSED

Structure :

```text
LifecycleTransition
├── from_stage
├── to_stage
├── reason
└── occurred_at
```

## Why Value Object

Une transition est décrite par ses valeurs.

Elle n’a pas nécessairement besoin d’une identité durable.

---

# 32. LifecycleTransitionReason — Value Object

**Classification :** Value Object  
**Status :** STRONG CANDIDATE

Particulièrement utile pour :

```text
SUSPENDED
BLOCKED
OFFBOARDED
REACTIVATED
```

---

# 33. SupplierOnboarding — Entity

**Classification :** Entity candidate  
**Aggregate Root :** OPEN  
**Status :** STRONG CANDIDATE

## Identity candidate

```text
OnboardingId
```

## Why Entity

Un onboarding possède :

- début ;
- progression ;
- décisions ;
- history ;
- end state.

Il peut évoluer dans le temps tout en restant le même onboarding.

## Open question

Un Supplier peut-il avoir plusieurs onboardings successifs ?

Si oui :

```text
Onboarding
```

devient encore plus clairement une Entity autonome.

---

# 34. OnboardingId — Value Object

**Classification :** Value Object  
**Status :** PROPOSED

---

# 35. OnboardingStage — Value Object / Enum

**Classification :** Value Object  
**Status :** STRONG CANDIDATE

Étapes candidates :

```text
INVITATION
IDENTITY_COLLECTION
COMPANY_INFORMATION
LEGAL_INFORMATION
TAX_INFORMATION
BANK_REFERENCE
DOCUMENT_COLLECTION
COMPLIANCE_CHECKS
QUALIFICATION
APPROVAL
ACTIVATION
```

---

# 36. OnboardingRequirement — Entity or Value Object

**Classification :** OPEN

## Value Object if

Une requirement est figée dans une définition.

## Entity if

Elle possède :

- identité ;
- statut ;
- evidence ;
- history ;
- assignment.

Le MVP peut commencer par une représentation simple.

---

# 37. OnboardingProgress — Domain Result / Projection

**Classification :** Domain Result / Projection  
**Status :** STRONG CANDIDATE

Peut être calculé :

```text
completed
missing
percentage
current_stage
```

## Recommendation
Ne pas en faire une Entity tant que le besoin d’identité indépendante n’existe pas.

---

# 38. SupplierQualification — Entity

**Classification :** Entity  
**Aggregate Root :** STRONG CANDIDATE  
**Status :** STRONG DECISION

## Identity

```text
QualificationId
```

## Why Entity

Une qualification possède :

- scope ;
- status ;
- validity ;
- decision ;
- history ;
- possible renewal/revocation.

Elle reste la même qualification lorsque son statut évolue.

---

# 39. QualificationId — Value Object

**Classification :** Value Object  
**Status :** STRONG DECISION

---

# 40. QualificationScope — Value Object

**Classification :** Value Object  
**Status :** STRONG DECISION

## Business meaning

Décrit le périmètre précis dans lequel la qualification s’applique.

Candidate shape :

```text
QualificationScope
├── organization_id?
├── category_code?
├── country_code?
├── business_unit?
├── service_type?
└── financial_limit?
```

## Core invariant

```text
Qualification
must have
a meaningful scope.
```

---

# 41. QualificationStatus — Enum / Value Object

**Classification :** Value Object  
**Implementation candidate :** Enum  
**Status :** STRONG DECISION

États candidats :

```text
PENDING
QUALIFIED
NOT_QUALIFIED
REVOKED
EXPIRED
```

---

# 42. QualificationDecision — Domain Result / Value Object

**Classification :** Value Object  
**Status :** STRONG DECISION

Candidate structure :

```text
QualificationDecision
├── approved
├── resulting_status
├── reasons
├── failed_requirements
├── evidence_refs
└── decided_at
```

## Why Value Object

La décision est définie par son contenu.

Elle n’a pas besoin d’une identité autonome.

---

# 43. SupplierDocument — Entity

**Classification :** Entity  
**Aggregate Root :** OPEN  
**Status :** STRONG DECISION

## Identity

```text
SupplierDocumentId
```

## Why Entity

Le document métier peut :

- être remplacé ;
- être re-vérifié ;
- expirer ;
- changer de status ;

tout en restant une référence documentaire identifiable dans le domaine.

---

# 44. SupplierDocumentId — Value Object

**Classification :** Value Object  
**Status :** STRONG CANDIDATE

---

# 45. DocumentType — Reference Value Object

**Classification :** Value Object / Reference Object  
**Status :** STRONG DECISION

Le type doit rester extensible.

Exemples :

```text
REGISTRATION_EXTRACT
TAX_CLEARANCE
SOCIAL_CLEARANCE
INSURANCE_CERTIFICATE
BANK_REFERENCE
ESG_POLICY
```

---

# 46. DocumentReference — Value Object

**Classification :** Value Object  
**Status :** STRONG DECISION

Représente une référence logique vers le document.

Important :

```text
DocumentReference
≠
S3Object
≠
AzureBlob
```

---

# 47. DocumentVerificationStatus — Enum / Value Object

**Classification :** Value Object

États possibles :

```text
PENDING
VERIFIED
REJECTED
```

L’expiration doit rester une notion distincte.

---

# 48. SupplierCertification — Entity

**Classification :** Entity  
**Aggregate Root :** OPEN  
**Status :** STRONG DECISION

## Identity candidate

```text
SupplierCertificationId
```

## Why Entity

Une certification :

- possède un issuer ;
- a une période de validité ;
- peut être renouvelée ;
- peut être révoquée ;
- possède souvent des evidence refs.

---

# 49. SupplierCertificationId — Value Object

**Classification :** Value Object  
**Status :** PROPOSED

---

# 50. CertificationType — Reference Value Object

**Classification :** Value Object / Reference Object

Exemples :

```text
ISO_9001
ISO_27001
ISO_14001
SOC_2
ECOVADIS
```

---

# 51. CertificationStatus — Enum / Value Object

**Classification :** Value Object

États candidats :

```text
ACTIVE
EXPIRED
REVOKED
UNVERIFIED
```

---

# 52. CertificationScope — Value Object

**Classification :** Value Object  
**Status :** STRONG CANDIDATE

Permet de préciser :

- entité ;
- site ;
- activité ;
- produit/service ;

couvert par la certification.

---

# 53. ComplianceRequirement — Reference Object / Value Object

**Classification :** OPEN

## Option A — Value Object

Si le requirement est défini par :

```text
code
scope
jurisdiction
```

## Option B — Reference Entity

Si l’exigence possède :

- version ;
- lifecycle ;
- administration ;
- documentation ;
- metadata.

## Recommendation

Commencer simple :

```text
ComplianceRequirementCode
```

et n’introduire une Entity riche qu’en cas de besoin.

---

# 54. ComplianceRequirementCode — Value Object

**Classification :** Value Object  
**Status :** STRONG CANDIDATE

---

# 55. ComplianceCheck — Entity

**Classification :** Entity  
**Aggregate Root :** OPEN  
**Status :** STRONG DECISION

## Identity candidate

```text
ComplianceCheckId
```

## Why Entity

Une vérification réelle a :

- une occurrence ;
- une date ;
- une source ;
- un résultat ;
- une evidence ;
- potentiellement une review.

Deux checks identiques en valeur à deux dates différentes ne sont pas le même événement métier.

---

# 56. ComplianceCheckId — Value Object

**Classification :** Value Object  
**Status :** PROPOSED

---

# 57. ComplianceResult — Domain Result / Value Object

**Classification :** Value Object  
**Status :** STRONG CANDIDATE

États candidats :

```text
PASS
FAIL
REVIEW_REQUIRED
UNKNOWN
```

---

# 58. ComplianceFinding — Entity or Value Object

**Classification :** DEFERRED

Dépend du besoin d’identifier, de suivre et de résoudre chaque finding individuellement.

Sans lifecycle propre :

```text
Value Object
```

Avec lifecycle propre :

```text
Entity
```

---

# 59. RiskAssessment — Entity

**Classification :** Entity  
**Aggregate Root :** STRONG CANDIDATE  
**Status :** STRONG DECISION

## Identity

```text
RiskAssessmentId
```

## Why Entity

Chaque évaluation de risque constitue une observation métier datée distincte.

Deux évaluations ayant le même score mais à deux dates différentes sont deux objets différents.

---

# 60. RiskAssessmentId — Value Object

**Classification :** Value Object  
**Status :** STRONG CANDIDATE

---

# 61. RiskType — Reference Value Object

**Classification :** Value Object / Reference Object

Exemples :

```text
FINANCIAL
OPERATIONAL
CYBER
COMPLIANCE
ESG
GEOPOLITICAL
SUPPLY_CHAIN
CONCENTRATION
REPUTATIONAL
```

---

# 62. RiskScore — Value Object

**Classification :** Value Object  
**Status :** STRONG DECISION

## Responsibility

Encapsuler :

- valeur ;
- range ;
- éventuelle normalisation.

## Open question

Échelle universelle ou dépendante d’un modèle ?

Ne pas figer trop tôt :

```text
0-100
```

comme seule représentation.

---

# 63. RiskLevel — Value Object / Enum

**Classification :** Value Object

Exemple :

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Le mapping score → level peut appartenir à une `RiskPolicy`.

---

# 64. RiskObservation — Value Object or Entity

**Classification :** DEFERRED

## Value Object if

Il représente un snapshot externe sans identité métier propre.

## Entity if

Il doit être historisé et suivi indépendamment.

La nécessité réelle n’est pas encore démontrée.

---

# 65. RiskDecision — Domain Result / Value Object

**Classification :** Value Object candidate

Structure possible :

```text
acceptable
level
reasons
required_actions
```

---

# 66. RiskMitigation — Entity candidate

**Classification :** DEFERRED

Si une mitigation possède :

- owner ;
- due date ;
- status ;
- lifecycle ;

elle devient potentiellement une Entity.

Mais cette responsabilité peut aussi appartenir à Workflow / Task Management.

---

# 67. SupplierAssessment — Entity

**Classification :** Entity  
**Aggregate Root :** STRONG CANDIDATE  
**Status :** STRONG DECISION

## Identity

```text
AssessmentId
```

## Why Entity

Une assessment constitue une exécution spécifique.

Elle possède :

- subject ;
- type ;
- questions ;
- answers ;
- evidence ;
- scoring ;
- decision ;
- history.

---

# 68. AssessmentId — Value Object

**Classification :** Value Object

---

# 69. AssessmentType — Reference Value Object

**Classification :** Value Object / Reference Object

Exemples :

```text
QUESTIONNAIRE
AUDIT
BUSINESS_REVIEW
COMPLIANCE_REVIEW
ANNUAL_REVIEW
RISK_REVIEW
SELF_ASSESSMENT
```

---

# 70. AssessmentQuestion — Value Object by default

**Classification :** Value Object candidate  
**Status :** DEFAULT DECISION

## Recommendation

Dans une assessment execution :

```text
AssessmentQuestion
```

peut être un Value Object snapshot.

Si un moteur de questionnaire versionné est ajouté plus tard :

```text
QuestionDefinition
```

peut devenir une Entity séparée.

---

# 71. AssessmentAnswer — Value Object by default

**Classification :** Value Object  
**Status :** DEFAULT DECISION

Une réponse est définie par :

- question ;
- value ;
- evidence éventuelle.

Elle n’a pas forcément besoin d’une identité indépendante.

---

# 72. AssessmentScore — Value Object

**Classification :** Value Object  
**Status :** STRONG DECISION

Peut encapsuler :

```text
value
scale
dimension
weight
```

---

# 73. AssessmentDecision — Domain Result / Value Object

**Classification :** Value Object

Exemples :

```text
APPROVED
REJECTED
REVIEW_REQUIRED
```

---

# 74. EvidenceReference — Value Object

**Classification :** Value Object  
**Status :** STRONG DECISION

Candidate shape :

```text
EvidenceReference
├── type
├── reference
├── source?
└── metadata?
```

## Important

Ne doit pas devenir un container opaque de données métier.

---

# 75. PerformanceMetric — Reference Value Object

**Classification :** Value Object / Reference Object

Exemples :

```text
DELIVERY_ON_TIME_RATE
QUALITY_SCORE
INCIDENT_RATE
```

---

# 76. PerformanceMeasurement — Entity or immutable record

**Classification :** OPEN

## Entity argument

Chaque mesure a :

- date ;
- source ;
- subject ;
- period.

Deux mesures identiques peuvent être deux observations distinctes.

## Immutable-record argument

Si la mesure est append-only et jamais modifiée, un record immuable peut suffire.

## Recommendation

Traiter comme **immutable domain record with identity only if operationally needed**.

---

# 77. PerformancePeriod — Value Object

**Classification :** Value Object

Exemples :

```text
2026-Q1
2026-01-01 → 2026-03-31
```

---

# 78. PerformanceScore — Value Object

**Classification :** Value Object

Encapsule :

- value ;
- scale ;
- optional unit.

---

# 79. SupplierScorecard — Projection by default

**Classification :** Projection / Domain Read Model candidate  
**Status :** DEFAULT DECISION

## Why

Une scorecard ressemble souvent à :

```text
derived aggregation
```

à partir de multiples measurements.

## Promote to Entity only if

La scorecard possède :

- validation ;
- publication ;
- approval ;
- lifecycle ;
- historical identity.

Le MVP doit éviter une Aggregate Scorecard si une projection suffit.

---

# 80. ScorecardDimension — Value Object

**Classification :** Value Object

Exemples :

```text
QUALITY
DELIVERY
COST
COMPLIANCE
ESG
```

---

# 81. SupplierIncident — Entity

**Classification :** Entity  
**Aggregate Root :** STRONG CANDIDATE  
**Status :** STRONG DECISION

## Identity

```text
IncidentId
```

## Why Entity

Un incident :

- s’est produit à une date ;
- possède une identité ;
- peut évoluer ;
- peut être investigué ;
- peut être résolu ;
- conserve son histoire.

---

# 82. IncidentId — Value Object

**Classification :** Value Object

---

# 83. IncidentType — Reference Value Object

**Classification :** Value Object / Reference Object

Exemples :

```text
DELAY
QUALITY_ISSUE
SECURITY_INCIDENT
FRAUD
SERVICE_INTERRUPTION
REGULATORY_NON_COMPLIANCE
```

---

# 84. IncidentSeverity — Value Object / Enum

**Classification :** Value Object

Exemple :

```text
LOW
MEDIUM
HIGH
CRITICAL
```

---

# 85. IncidentStatus — Enum / Value Object

**Classification :** Value Object

Possible states :

```text
OPEN
UNDER_REVIEW
RESOLVED
CLOSED
```

Ce lifecycle reste distinct du Supplier lifecycle.

---

# 86. IncidentImpact — Value Object

**Classification :** Value Object candidate

Peut représenter :

- business severity ;
- operational consequence ;
- affected scope.

---

# 87. SupplierSegment — Value Object / Reference

**Classification :** Value Object  
**Status :** STRONG DECISION

Segments :

```text
STRATEGIC
CRITICAL
PREFERRED
APPROVED
STANDARD
TRANSACTIONAL
RESTRICTED
```

Le segment est une classification, pas une Entity.

---

# 88. SegmentationDecision — Domain Result / Value Object

**Classification :** Value Object

Structure possible :

```text
segment
reasons
inputs
decided_at
```

---

# 89. DateRange — Value Object

**Classification :** Value Object  
**Status :** STRONG DECISION

Candidate shape :

```text
start
end?
```

## Invariant

```text
end >= start
```

---

# 90. Percentage — Value Object candidate

**Classification :** Value Object

À utiliser si plusieurs capacités manipulent réellement des pourcentages.

But :

```text
avoid ambiguity
0.82 vs 82
```

---

# 91. Money — Deferred Value Object

**Classification :** Value Object candidate  
**Status :** DEFERRED

Le besoin existe uniquement si PySRMKit manipule de vrais seuils financiers.

Sinon :

```text
Money
```

reste du ressort des domaines Procurement / Accounting.

---

# 92. CurrencyCode — Value Object candidate

À introduire uniquement si `Money` est réellement nécessaire.

---

# 93. Domain Events — immutable domain records

Les Domain Events sont naturellement candidats à des objets immuables.

Exemple :

```python
@dataclass(frozen=True, slots=True)
class SupplierActivated:
    supplier_id: SupplierId
    occurred_at: datetime
```

## Classification

```text
Domain Event
```

et non Entity.

Ils représentent un fait passé.

---

# 94. EventId — Value Object

**Classification :** Value Object candidate

Peut être utile pour :
- idempotency ;
- tracing ;
- deduplication.

---

# 95. ActorReference — Value Object candidate

Peut représenter :

```text
actor_type
actor_id
```

sans dépendre du système IAM concret.

---

# 96. CorrelationId — Application Value Object

**Classification :** Value Object  
**Layer :** plutôt Application/Integration

Ne constitue pas un concept intrinsèque du Supplier Domain.

---

# 97. Aggregate Root Candidates — revised

À ce stade, les candidats les plus solides sont :

```text
Supplier
SupplierRelationship
SupplierQualification
SupplierAssessment
RiskAssessment
SupplierIncident
```

Possibles mais non confirmés :

```text
SupplierOnboarding
SupplierDocument
SupplierCertification
ComplianceCheck
```

---

# 98. Why Supplier Is an Aggregate Root

Il protège :

```text
canonical identity
master-level information
supplier-level invariants
```

Il ne doit pas protéger tous les invariants du domaine.

---

# 99. Why SupplierRelationship Is a Strong Aggregate Root

Il protège probablement :

```text
relationship identity
internal organization scope
relationship lifecycle
relationship-level status
```

C’est le meilleur candidat pour séparer :

```text
supplier global truth
```

de :

```text
our organization-specific relationship
```

---

# 100. Why Qualification May Be a Separate Aggregate

Une qualification possède :

- identity ;
- own lifecycle ;
- scope ;
- validity ;
- decision ;
- revocation ;
- history.

Cela crée une forte pression vers un Aggregate autonome.

---

# 101. Why Assessment May Be a Separate Aggregate

Une assessment possède :

- execution ;
- questions ;
- answers ;
- scoring ;
- evidence ;
- final decision.

Sa cohérence transactionnelle peut être indépendante du Supplier.

---

# 102. Why RiskAssessment May Be a Separate Aggregate

Le risque est temporel.

Chaque assessment doit préserver l’histoire.

Écraser une propriété :

```text
supplier.risk = HIGH
```

serait insuffisant pour le modèle cible.

---

# 103. Why Incident May Be a Separate Aggregate

Un incident possède son propre lifecycle et ses propres actions.

Il ne doit pas forcer le chargement de l’Aggregate Supplier pour chaque mise à jour d’investigation.

---

# 104. Aggregate Boundary Heuristic

Règle de conception :

```text
If an object has:
- own identity
- own lifecycle
- own concurrency
- own transactional invariants
- independent loading needs

then
Aggregate Root candidate
```

---

# 105. Child Entity Heuristic

Un objet reste Child Entity si :

```text
it has identity
but
cannot meaningfully exist or change independently
from its aggregate root.
```

---

# 106. Value Object Heuristic

Un objet est Value Object si :

```text
identity is irrelevant
and
meaning is fully determined by value.
```

---

# 107. Entity Equality

Pour une Entity :

```text
same identity
→ same entity
```

même si les attributs diffèrent.

Exemple :

```text
SupplierId("123")
```

identifie toujours le même Supplier.

---

# 108. Value Object Equality

Pour un Value Object :

```text
same values
→ equivalent object
```

Exemple :

```text
CountryCode("FR") == CountryCode("FR")
```

---

# 109. Entity Mutability

Une Entity n’a pas besoin d’être techniquement mutable partout.

Mais elle possède un état qui peut évoluer.

Les mutations doivent idéalement passer par :

```text
business methods
```

et non par changement arbitraire de champs.

---

# 110. Value Object Immutability

Par défaut :

```text
Value Objects should be immutable.
```

Bénéfices :

- sécurité ;
- equality claire ;
- testabilité ;
- absence d’aliasing mutable ;
- usage comme clés/hash.

---

# 111. Copy-on-change

Pour modifier un Value Object :

```text
create a new value
```

plutôt que le muter.

Exemple :

```text
old_address
→ new_address
```

---

# 112. Validation at Construction

Un Value Object doit idéalement être valide dès sa création.

Exemple :

```text
CountryCode("")
```

ne doit pas créer un objet invalide.

---

# 113. Primitive Obsession — Rule

On introduit un Value Object lorsque la primitive cache une vraie sémantique.

Bon candidat :

```text
QualificationScope
```

Mauvais candidat possible :

```text
SupplierDescriptionText
```

si aucun invariant ou comportement ne justifie ce type.

---

# 114. Value Object Cost

Chaque Value Object ajoute :

- type ;
- API ;
- imports ;
- serialization ;
- mapping.

Donc :

> **Créer un Value Object uniquement s’il porte une vraie sémantique ou protège un invariant.**

---

# 115. Enum vs Value Object

Une `Enum` convient lorsque :

- ensemble stable ;
- fermé ;
- comportement simple.

Un Value Object extensible convient lorsque :

- taxonomy configurable ;
- custom codes ;
- metadata ;
- jurisdiction-specific values.

---

# 116. Example — LifecycleStage

Bon candidat Enum car :

```text
core lifecycle
```

est relativement stable.

---

# 117. Example — DocumentType

Meilleur candidat Reference Value Object qu’Enum stricte si :

```text
organizations
or countries
need custom document types.
```

---

# 118. Example — RiskType

Même prudence.

Le noyau fournit une taxonomie par défaut.

Mais l’architecture doit permettre extension.

---

# 119. Identity Objects

Liste initiale des IDs typés :

```text
SupplierId
SupplierRelationshipId
SupplierContactId
SupplierLocationId
OnboardingId
QualificationId
SupplierDocumentId
SupplierCertificationId
ComplianceCheckId
RiskAssessmentId
AssessmentId
IncidentId
```

Ils ne seront introduits que pour les Entities réellement retenues.

---

# 120. Typed IDs — rationale

Pourquoi ne pas utiliser `str` partout ?

Parce que :

```text
SupplierId
≠
QualificationId
```

même si techniquement les deux contiennent un UUID.

Le type réduit les erreurs de confusion.

---

# 121. Typed IDs — YAGNI guard

Cependant, si l’API devient trop lourde :

```text
do not wrap everything blindly.
```

La valeur d’un ID typé est forte pour les Aggregate Roots.

Elle est moins certaine pour chaque enfant interne.

---

# 122. Domain Result Objects

Domain Results candidats :

```text
QualificationDecision
ActivationDecision
ComplianceResult
RiskDecision
SegmentationDecision
OnboardingProgress
```

Propriétés recommandées :

```text
immutable
explicit
explainable
serializable
```

---

# 123. Why Domain Results Matter

Une simple valeur :

```text
True
```

est souvent insuffisante.

Exemple :

```text
False
```

ne dit pas :

```text
why
which requirement failed
which evidence was missing
```

Les agents, interfaces et audits bénéficient d’un objet explicable.

---

# 124. Exceptions vs Domain Results

## Use Domain Result when

Le refus est un résultat métier attendu.

Exemple :

```text
supplier not qualified because evidence missing
```

## Use Exception when

L’opération elle-même est invalide.

Exemple :

```text
cannot transition OFFBOARDED → ACTIVE
```

---

# 125. Reference Objects

Reference Objects candidats :

```text
CategoryCode
CapabilityCode
DocumentType
CertificationType
ComplianceRequirementCode
RiskType
AssessmentType
PerformanceMetric
IncidentType
SupplierSegment
```

Leur rôle principal :

```text
stable domain vocabulary
```

---

# 126. Reference Entity Escalation

Un Reference Object devient potentiellement Entity si l’on a besoin de :

- ID propre ;
- history ;
- activation/deactivation ;
- hierarchy ;
- versioning ;
- localization ;
- administration.

---

# 127. Supplier vs Legal Entity

Le document `04` laisse ouverte la question :

```text
Supplier
vs
Legal Entity
```

À ce stade :

- `Supplier` reste l’Entity centrale ;
- une `LegalEntity` séparée n’est pas encore confirmée ;
- `SupplierOrganization` peut porter la structure groupe/filiales.

Cette question doit être traitée dans le `06`.

---

# 128. SupplierIdentity vs LegalEntity

Ne pas créer deux objets recouvrant exactement la même sémantique.

Le `06` devra décider si :

```text
SupplierIdentity
```

contient simplement des données légales

ou si :

```text
LegalEntity
```

devient une Entity autonome.

---

# 129. SupplierContact ownership

Hypothèse par défaut :

```text
Supplier Aggregate
    owns SupplierContact
```

Mais si les contacts deviennent :

- partagés ;
- independently queried ;
- independently permissioned ;
- independently audited ;

leur frontière peut évoluer.

---

# 130. SupplierLocation ownership

Même logique.

Hypothèse initiale :

```text
Supplier
    owns SupplierLocation
```

jusqu’à preuve qu’un lifecycle autonome justifie un Aggregate séparé.

---

# 131. Document ownership

Question difficile.

Un document peut être lié à :

```text
Supplier
Legal Entity
Location
Relationship
Qualification
ComplianceCheck
```

Le `06` devra éviter un modèle arbitraire.

---

# 132. Certification ownership

Même problème.

Une certification peut s’appliquer à :

- groupe ;
- entité ;
- site ;
- activité.

Cela rend `CertificationScope` important.

---

# 133. Qualification ownership

Hypothèse privilégiée :

```text
SupplierRelationship
    1 ─── * SupplierQualification
```

plutôt que :

```text
Supplier
    global qualifications
```

car la qualification est souvent spécifique à :

- organisation ;
- catégorie ;
- pays ;
- business unit.

---

# 134. Risk ownership

Le risque peut avoir plusieurs perspectives.

```text
intrinsic supplier risk
```

vs

```text
our relationship risk
```

Le `06` devra déterminer si `RiskAssessment.subject` peut être :

```text
Supplier
or
SupplierRelationship
```

sans introduire un abstraction générique prématurée.

---

# 135. Compliance ownership

Même dualité :

```text
supplier-level compliance evidence
```

vs

```text
relationship-specific compliance decision
```

---

# 136. Assessment ownership

Une assessment peut concerner :

```text
Supplier
SupplierRelationship
Qualification
Risk
Compliance
```

Le modèle doit rester explicite.

---

# 137. Avoid Generic SubjectRef Too Early

Il serait possible de créer :

```text
SubjectRef(type, id)
```

pour tous ces cas.

Mais cela cacherait la sémantique.

Décision actuelle :

> **Ne pas introduire `SubjectRef` générique avant que la répétition réelle le justifie.**

---

# 138. Aggregate References by ID

Les Aggregate Roots doivent se référencer principalement par ID.

Exemple :

```text
SupplierQualification
    supplier_id
    relationship_id
```

plutôt que :

```text
full Supplier object
full Relationship object
```

---

# 139. Why references by ID?

Pour éviter :

- agrégats géants ;
- chargements implicites ;
- cycles ;
- transactions involontaires ;
- forte contention.

---

# 140. Python Representation Guidelines

## Entities

Candidate style :

```python
class Supplier:
    ...
```

ou :

```python
@dataclass
class Supplier:
    ...
```

selon le niveau de contrôle requis.

## Value Objects

Candidate style :

```python
@dataclass(frozen=True, slots=True)
class SupplierId:
    ...
```

## Domain Results

Candidate style :

```python
@dataclass(frozen=True, slots=True)
class QualificationDecision:
    ...
```

---

# 141. Dataclass Is Not DDD

Important :

```text
@dataclass
≠
Value Object
```

Une dataclass peut représenter :

- Entity ;
- DTO ;
- Command ;
- Event ;
- Value Object.

La classification est sémantique.

---

# 142. Frozen Is Not Value Object

Même distinction :

```text
frozen=True
```

rend un objet immuable.

Cela ne le transforme pas automatiquement en Value Object DDD.

---

# 143. Enum Is Not State Pattern

`SupplierLifecycleStage(Enum)` :

```text
does not mean
GoF State Pattern
```

Il représente seulement une valeur d’état.

---

# 144. Protocol Is Not Interface Segregation

Créer un `Protocol` ne suffit pas à dire que l’ISP est respecté.

Le contrat doit réellement être :

- petit ;
- cohésif ;
- adapté au consumer.

---

# 145. Entity Behavior

Une Entity doit idéalement exposer des comportements métier.

Exemples :

```text
Supplier.add_external_identifier(...)
SupplierRelationship.suspend(...)
SupplierQualification.revoke(...)
SupplierIncident.resolve(...)
```

La forme exacte viendra dans les documents d’invariants/use cases.

---

# 146. Avoid Public Field Mutation

Préférer :

```text
qualification.revoke(reason)
```

à :

```text
qualification.status = REVOKED
```

si la transition porte des règles.

---

# 147. Value Object Behavior

Un Value Object peut avoir du comportement.

Exemples :

```text
DateRange.contains(date)
RiskScore.is_above(threshold)
Address.normalized()
QualificationScope.matches(...)
```

Un Value Object n’est pas un simple sac de données.

---

# 148. Value Object Validation

Exemple :

```python
@dataclass(frozen=True)
class DateRange:
    start: date
    end: date | None

    def __post_init__(self) -> None:
        if self.end is not None and self.end < self.start:
            raise InvalidDateRange(...)
```

Illustration seulement.

---

# 149. SupplierId Example

```python
@dataclass(frozen=True, slots=True)
class SupplierId:
    value: UUID
```

Concepts :

```text
[DDD: Value Object]
[PRINCIPLE: Explicit Types]
[PRINCIPLE: Information Hiding]
```

---

# 150. QualificationScope Example

```python
@dataclass(frozen=True, slots=True)
class QualificationScope:
    organization_id: InternalOrganizationId | None = None
    category_code: CategoryCode | None = None
    country_code: CountryCode | None = None
```

Une validation devra empêcher un scope vide si le métier l’interdit.
---

# 151. ExternalIdentifier Example

```python
@dataclass(frozen=True, slots=True)
class ExternalIdentifier:
    kind: ExternalIdentifierType
    value: str
    jurisdiction: CountryCode | None = None
```

---

# 152. Address Example

```python
@dataclass(frozen=True, slots=True)
class Address:
    line1: str
    city: str
    country: CountryCode
    postal_code: str | None = None
    region: str | None = None
    line2: str | None = None
```

---

# 153. QualificationDecision Example

```python
@dataclass(frozen=True, slots=True)
class QualificationDecision:
    approved: bool
    reasons: tuple[str, ...]
```

La version finale pourra utiliser des objets de reason plus structurés.

---

# 154. DecisionReason — Value Object candidate

Pour éviter :

```text
free-text reasons only
```

un objet peut représenter :

```text
code
message
evidence_refs
```

Mais cela peut attendre le besoin réel.

---

# 155. Rich Error vs DecisionReason

Une erreur de transition :

```text
InvalidLifecycleTransition
```

et une reason de décision :

```text
MISSING_TAX_CLEARANCE
```

ne sont pas le même concept.

---

# 156. Domain Events as Immutable Objects

Domain Events candidats :

```text
SupplierCreated
SupplierInvited
SupplierQualified
SupplierActivated
SupplierSuspended
SupplierOffboarded
```

Ils devraient être immuables.

---

# 157. Event Equality

Les events sont généralement distingués par :

```text
EventId
```

ou par occurrence.

Deux événements avec le même payload ne sont pas forcément le même événement.

Donc :

```text
Domain Event
```

n’est pas un Value Object classique même s’il est immuable.

---

# 158. Entity Identity Generation

L’ID peut être généré :

- dans le domaine ;
- dans l’application ;
- via une factory ;
- via un injected ID generator.

Décision différée.

Le domain model ne doit pas dépendre d’un service réseau pour générer ses IDs.

---

# 159. Identity Generator — Port candidate

Un `IdGenerator` générique n’est pas nécessaire tant que :

```text
UUID generation
```

suffit localement.

KISS/YAGNI s’applique.

---

# 160. Equality Semantics Summary

| Object family | Equality |
|---|---|
| Entity | identity-based |
| Value Object | value-based |
| Domain Result | value-based |
| Reference Value Object | value/code-based |
| Domain Event | occurrence/event-id based |
| Projection | representation-specific |

---

# 161. Mutability Summary

| Object family | Default mutability |
|---|---|
| Entity | controlled state evolution |
| Aggregate Root | controlled state evolution |
| Value Object | immutable |
| Domain Result | immutable |
| Domain Event | immutable |
| Reference Object | usually immutable |
| Projection | usually immutable snapshot |

---

# 162. Lifecycle Summary

| Object | Own lifecycle |
|---|---|
| Supplier | Yes |
| SupplierRelationship | Yes |
| SupplierQualification | Yes |
| SupplierOnboarding | Yes |
| SupplierDocument | Yes/derived |
| SupplierCertification | Yes/derived |
| ComplianceCheck | Limited |
| RiskAssessment | Snapshot/history |
| SupplierAssessment | Yes |
| PerformanceMeasurement | Usually append-only |
| SupplierIncident | Yes |
| SupplierScorecard | Usually derived |

---

# 163. Value Objects Core Set

Première proposition du **core set** :

```text
SupplierId
SupplierRelationshipId
ExternalIdentifier
Address
CountryCode
CategoryCode
CapabilityCode
SupplierLifecycleStage
QualificationId
QualificationScope
QualificationStatus
DateRange
DocumentReference
EvidenceReference
RiskScore
RiskLevel
AssessmentScore
SupplierSegment
```

---

# 164. Value Objects Optional Set

```text
EmailAddress
PhoneNumber
Percentage
Money
CurrencyCode
CertificationScope
IncidentImpact
DecisionReason
```

À ajouter uniquement lorsque leur sémantique justifie le coût.

---

# 165. Entities Core Set

Première proposition :

```text
Supplier
SupplierContact
SupplierLocation
SupplierRelationship
SupplierOnboarding
SupplierQualification
SupplierDocument
SupplierCertification
ComplianceCheck
RiskAssessment
SupplierAssessment
SupplierIncident
```

---

# 166. Entities to Reconsider

```text
SupplierContact
SupplierLocation
SupplierDocument
SupplierCertification
ComplianceCheck
```

peuvent rester child entities plutôt qu’Aggregate Roots.

---

# 167. Projection / Record Set

```text
OnboardingProgress
SupplierScorecard
PerformanceMeasurement [possibly]
SupplierRiskSummary
SupplierQualificationView
```

Ces objets ne doivent pas être artificiellement promus en Entities.

---

# 168. Reference Object Set

```text
CategoryCode
CapabilityCode
DocumentType
CertificationType
ComplianceRequirementCode
RiskType
AssessmentType
PerformanceMetric
IncidentType
SupplierSegment
```

---

# 169. Domain Result Set

```text
QualificationDecision
ActivationDecision
ComplianceResult
RiskDecision
AssessmentDecision
SegmentationDecision
```

---

# 170. Entity / Value Object — decision table

| Question | Entity | Value Object |
|---|---:|---:|
| Identity matters? | Yes | No |
| Same values = same object? | No | Yes |
| Lifecycle independent? | Often | No |
| Mutability? | Controlled | Usually immutable |
| Equality by ID? | Yes | No |
| Can be freely replaced? | No | Yes |
| Good candidate for hashability? | Rarely | Yes |

---

# 171. Classification Exercise — Supplier

```text
Identity matters?
YES

Can all attributes change and object remain same?
YES

→ ENTITY
```

---

# 172. Classification Exercise — Address

```text
Identity matters?
NO

Same values mean same address value?
YES

→ VALUE OBJECT
```

---

# 173. Classification Exercise — QualificationScope

```text
Identity matters?
NO

Defined entirely by organization/category/country/etc.?
YES

→ VALUE OBJECT
```

---

# 174. Classification Exercise — RiskAssessment

```text
Identity matters?
YES

Same score at two dates = same assessment?
NO

→ ENTITY
```

---

# 175. Classification Exercise — SupplierScorecard

```text
Identity matters?
NOT NECESSARILY

Can it be recalculated from measurements?
YES

→ PROJECTION by default
```

---

# 176. Classification Exercise — SupplierSegment

```text
Identity matters?
NO

Defined by code/value?
YES

→ VALUE OBJECT / reference
```

---

# 177. Design Concepts Applied — Entities

```text
[DDD: Entity]
[PRINCIPLE: Encapsulation]
[PRINCIPLE: Information Hiding]
[PRINCIPLE: Tell, Don't Ask]
```

---

# 178. Design Concepts Applied — Value Objects

```text
[DDD: Value Object]
[PRINCIPLE: Immutability]
[PRINCIPLE: Explicit Types]
[PRINCIPLE: Primitive Obsession avoidance]
```

---

# 179. Design Concepts Applied — Aggregate Roots

```text
[DDD: Aggregate]
[DDD: Aggregate Root]
[PRINCIPLE: Transactional Consistency]
[PRINCIPLE: Information Hiding]
```

---

# 180. Design Concepts Applied — Domain Results

```text
[DDD: Value Object-like result]
[PRINCIPLE: Explicitness]
[PRINCIPLE: Explainability]
```

---

# 181. Design Concepts Applied — Reference Objects

```text
[DDD: Reference Data]
[PRINCIPLE: KISS]
[PRINCIPLE: Extensibility]
```

---

# 182. Learning Note — Entity vs mutable object

Une Entity n’est pas simplement :

```text
an object with setters
```

Une Entity est un objet dont l’identité métier compte.

---

# 183. Learning Note — Value Object vs dataclass

Un Value Object n’est pas simplement :

```text
@dataclass(frozen=True)
```

Il est défini par sa valeur et sa sémantique métier.

---

# 184. Learning Note — Aggregate Root vs top-level class

Une Aggregate Root n’est pas forcément :

```text
the top-level class in a module
```

Elle protège une frontière de cohérence.

---

# 185. Learning Note — Reference Object vs Entity

Un type de document n’a pas besoin d’une Entity riche si un code suffit.

Ne pas sur-modéliser les taxonomies.

---

# 186. Learning Note — Domain Result vs Exception

Un refus normal :

```text
NOT_QUALIFIED
```

n’est pas forcément une exception.

Une transition impossible :

```text
OFFBOARDED → ACTIVE
```

peut l’être.

---

# 187. Testing — Entity identity

Exemple :

```text
same SupplierId
→ same logical Supplier
```

même après modification de son nom.

---

# 188. Testing — Value Object equality

Exemple :

```text
CountryCode("FR")
==
CountryCode("FR")
```

---

# 189. Testing — Value Object validation

Exemples :

```text
empty SupplierId rejected
invalid DateRange rejected
empty QualificationScope rejected
```

selon les invariants finaux.

---

# 190. Testing — immutability

Les Value Objects critiques doivent être testés comme immuables si cette propriété est contractuelle.

---

# 191. Testing — Entity behavior

Tester :

```text
behavior
not internal fields
```

Exemple :

```text
supplier_relationship.suspend(...)
```

et vérifier :

- nouvel état ;
- event ;
- reason.

---

# 192. Testing — Aggregate boundary

Un test peut vérifier qu’un invariant est protégé uniquement via l’Aggregate Root.

---

# 193. Testing — no primitive leakage

Les tests de type peuvent éventuellement garantir que :

```text
SupplierId
```

n’est pas interchangeable avec :

```text
QualificationId
```

---

# 194. Architecture Test — no ORM in entities

```text
pysrmkit.domain
MUST NOT import
sqlalchemy
```

---

# 195. Architecture Test — no API DTO in domain

```text
domain
MUST NOT depend on
interface models
```

---

# 196. Serialization Impact

Entities et Value Objects ne doivent pas être conçus uniquement pour JSON.

La sérialisation passe par des mappers si nécessaire.

---

# 197. Persistence Impact

L’Entity n’est pas obligée d’exposer :

```text
database id
created_at
updated_at
version
```

si ces champs sont uniquement techniques.

Ils doivent être distingués de la sémantique métier.

---

# 198. Business timestamp vs technical timestamp

Exemples métier :

```text
qualified_at
occurred_at
expires_at
```

Exemples techniques :

```text
row_created_at
row_updated_at
```

Ne pas les confondre.

---

# 199. Technical version vs business version

```text
optimistic_lock_version
```

n’est pas nécessairement une propriété métier.

---

# 200. Auditing Impact

Les Entities importantes devront pouvoir fournir suffisamment de données pour reconstruire :

```text
who
what
when
why
```

sans intégrer le système IAM.

---

# 201. Multi-organization Impact

Les Value Objects suivants deviennent particulièrement importants :

```text
InternalOrganizationId
QualificationScope
SupplierRelationshipId
```

Ils empêchent les règles relationnelles d’être traitées comme globales.

---

# 202. Multi-country Impact

Les Value Objects suivants doivent être jurisdiction-aware ou extensibles :

```text
ExternalIdentifier
Address
CountryCode
DocumentType
ComplianceRequirementCode
```

---

# 203. Domain Event Identity

Un événement possède souvent :

```text
EventId
OccurredAt
AggregateId
```

mais il n’est pas une Entity métier au sens classique.

---

# 204. Domain Event Immutability

Un événement représente le passé.

Il ne doit pas être modifié après création.

---

# 205. Domain Error Objects

Les erreurs métier peuvent transporter des Value Objects.

Exemple conceptuel :

```text
InvalidLifecycleTransition(
    from_stage,
    to_stage
)
```

---

# 206. No Generic Entity Base Required

PySRMKit n’a pas besoin immédiatement de :

```python
class Entity[T]:
    id: T
```

Une base générique ne doit être introduite que si elle apporte un réel bénéfice.

---

# 207. No Generic ValueObject Base Required

Même règle.

Une marker base class :

```text
ValueObject
```

peut être utile pédagogiquement ou techniquement.

Mais elle n’est pas nécessaire pour que les objets soient des Value Objects.

---

# 208. No Universal Aggregate Base Required

Éviter :

```python
class AggregateRoot(Generic[T]):
    ...
```

si cela ne sert qu’à étiqueter.

Un aggregate peut être reconnu par son rôle, ses invariants et ses events.

---

# 209. Event Recording Mechanism

Une Aggregate Root peut éventuellement accumuler :

```text
pending domain events
```

Mais le mécanisme exact sera défini ultérieurement.

---

# 210. Example — Aggregate event recording

Illustration :

```python
class SupplierRelationship:
    def activate(...):
        ...
        self._events.append(
            SupplierActivated(...)
        )
```

Non normative.

---

# 211. Encapsulation of Collections

Si `Supplier` possède des identifiers :

Préférer :

```text
supplier.add_external_identifier(identifier)
```

à :

```text
supplier.external_identifiers.append(identifier)
```

lorsqu’un invariant doit être protégé.

---

# 212. Duplicate Identifier Invariant

Question à traiter dans `07` :

```text
Can a Supplier have two identical external identifiers?
```

Le Value Object permet de poser cette question explicitement.

---

# 213. Equality and Normalization

La normalisation doit être claire.

Exemple :

```text
VAT number spaces
email case
country code case
```

Ne pas appliquer des transformations implicites non documentées.

---

# 214. Stringly-Typed Domain Risk

À éviter :

```python
qualification.status = "qualified"
document.type = "tax"
risk.level = "high"
```

Préférer des types métier lorsque le vocabulaire est stable.

---

# 215. Over-Typing Risk

À éviter également :

```text
LegalName
TradingName
SupplierDescription
SupplierNotes
SupplierAlias
```

comme classes séparées sans invariant réel.

---

# 216. Recommended Strong Types

Valeur pédagogique et métier forte :

```text
SupplierId
SupplierRelationshipId
ExternalIdentifier
CountryCode
QualificationScope
QualificationStatus
DocumentReference
RiskScore
DateRange
EvidenceReference
```

---

# 217. Recommended Plain Primitives Initially

Peuvent rester primitifs au début :

```text
legal_name: str
trading_name: str | None
description: str | None
```

tant qu’aucun invariant complexe ne les justifie.

---

# 218. Domain Type Escalation Rule

Une primitive doit être promue en Value Object lorsque :

1. plusieurs règles la concernent ;
2. elle possède un vocabulaire propre ;
3. elle est souvent confondue ;
4. elle nécessite validation/normalisation ;
5. elle porte du comportement.

---

# 219. Example — CountryCode escalation

`str` devient `CountryCode` parce que :

- format ;
- sémantique ;
- réutilisation ;
- validation ;
- multi-country.

---

# 220. Example — LegalName stays primitive initially

`legal_name` peut rester `str` si :

- pas de comportement ;
- pas de validation complexe ;
- pas de confusion fréquente.

---

# 221. Entity Ownership Matrix

| Entity | Owner candidate | Independent repository? ||---|---|---:|
| Supplier | self | Yes |
| SupplierContact | Supplier | Usually no |
| SupplierLocation | Supplier | Usually no |
| SupplierRelationship | self | Yes |
| SupplierOnboarding | Relationship or self | Maybe |
| SupplierQualification | self | Likely |
| SupplierDocument | Supplier/subject | Maybe |
| SupplierCertification | Supplier/subject | Maybe |
| ComplianceCheck | Relationship/subject | Maybe |
| RiskAssessment | self | Likely |
| SupplierAssessment | self | Likely |
| SupplierIncident | self | Likely |

---

# 222. Value Object Ownership Matrix

| Value Object | Used by |
|---|---|
| SupplierId | Supplier, references |
| ExternalIdentifier | Supplier |
| Address | SupplierLocation |
| CountryCode | many |
| QualificationScope | Qualification |
| DateRange | Qualification, Certification, Performance |
| EvidenceReference | Qualification, Compliance, Risk, Assessment |
| RiskScore | RiskAssessment |
| SupplierSegment | Relationship |
| DocumentReference | Document |
| AssessmentScore | Assessment |

---

# 223. Core Aggregate Candidate — Supplier

Candidate boundary:

```text
Supplier
│
├── SupplierId
├── SupplierIdentity
├── ExternalIdentifier*
├── SupplierContact*
├── SupplierLocation*
├── CategoryCode*
└── CapabilityCode*
```

Le `*` signifie collection potentielle.

---

# 224. Core Aggregate Candidate — SupplierRelationship

```text
SupplierRelationship
│
├── SupplierRelationshipId
├── SupplierId
├── InternalOrganizationId
├── SupplierLifecycleStage
├── SupplierSegment?
└── relationship-level state
```

---

# 225. Aggregate Candidate — SupplierQualification

```text
SupplierQualification
│
├── QualificationId
├── SupplierId
├── SupplierRelationshipId?
├── QualificationScope
├── QualificationStatus
├── DateRange?
├── QualificationDecision?
└── EvidenceReference*
```

---

# 226. Aggregate Candidate — SupplierAssessment

```text
SupplierAssessment
│
├── AssessmentId
├── AssessmentType
├── Questions
├── Answers
├── AssessmentScore*
├── EvidenceReference*
└── AssessmentDecision
```

---

# 227. Aggregate Candidate — RiskAssessment

```text
RiskAssessment
│
├── RiskAssessmentId
├── RiskType
├── RiskScore
├── RiskLevel
├── assessed_at
├── EvidenceReference*
└── rationale
```

---

# 228. Aggregate Candidate — SupplierIncident

```text
SupplierIncident
│
├── IncidentId
├── IncidentType
├── IncidentSeverity
├── IncidentStatus
├── occurred_at
├── IncidentImpact?
└── EvidenceReference*
```

---

# 229. Aggregate Boundary Validation Questions

Pour chaque aggregate candidat :

```text
1. What invariant does it protect?
2. What changes atomically?
3. What can change independently?
4. What must be loaded together?
5. What can be eventually consistent?
6. Does it need its own repository?
7. Does it have its own lifecycle?
```

---

# 230. Domain Modeling Anti-Patterns

Éviter :

```text
Everything is an Entity
Everything is a Value Object
Everything has a Repository
Everything has an ID
Everything is immutable
Everything is generic
```

Le choix dépend de la sémantique.

---

# 231. Anti-Pattern — Entity per table

Une table SQL future ne définit pas automatiquement une Entity.

---

# 232. Anti-Pattern — Value Object per column

Une colonne ne justifie pas automatiquement une classe.

---

# 233. Anti-Pattern — Aggregate per module

Le package layout ne définit pas la frontière transactionnelle.

---

# 234. Anti-Pattern — Repository per Entity

Le repository correspond plutôt à un Aggregate Root.

---

# 235. Anti-Pattern — IDs everywhere

Les IDs typés sont utiles, mais peuvent devenir du bruit s’ils sont créés sans usage.

---

# 236. Anti-Pattern — Immutable everything

Les Value Objects sont idéalement immuables.

Les Entities, elles, évoluent.

L’objectif est :

```text
controlled mutation
```

pas :

```text
no mutation ever.
```

---

# 237. Test Strategy by Classification

## Entity

Tester :

- identity ;
- lifecycle ;
- behavior ;
- invariant.

## Value Object

Tester :

- construction ;
- validation ;
- equality ;
- immutability.

## Aggregate Root

Tester :

- invariant boundary ;
- domain events ;
- coordinated state changes.

## Domain Result

Tester :

- exact reasons ;
- stable representation ;
- explainability.

---

# 238. Example test — SupplierId

```python
def test_supplier_id_equality_is_value_based():
    ...
```

---

# 239. Example test — ExternalIdentifier

```python
def test_external_identifier_keeps_type_and_jurisdiction():
    ...
```

---

# 240. Example test — QualificationScope

```python
def test_qualification_scope_cannot_be_empty():
    ...
```

si cet invariant est confirmé.

---

# 241. Example test — SupplierRelationship

```python
def test_relationship_identity_survives_lifecycle_changes():
    ...
```

---

# 242. Example test — QualificationDecision

```python
def test_rejected_decision_contains_failed_requirements():
    ...
```

---

# 243. Example test — RiskAssessment

```python
def test_two_risk_assessments_at_different_times_are_distinct():
    ...
```

---

# 244. Example test — Address

```python
def test_equal_addresses_are_value_equal():
    ...
```

---

# 245. Documentation Convention

Chaque Entity importante devra documenter :

```text
Identity
Lifecycle
Responsibilities
Owned objects
Invariants
Events
```

---

# 246. Value Object Documentation Convention

Chaque Value Object important devra documenter :

```text
Meaning
Allowed values
Validation
Equality
Immutability
Serialization considerations
```

---

# 247. Example docstring — SupplierId

```python
@dataclass(frozen=True, slots=True)
class SupplierId:
    """
    Canonical identifier of a Supplier entity.

    DDD role:
        Value Object.

    Design:
        Equality by value.
        Independent from ERP/vendor identifiers.
    """
```

---

# 248. Example docstring — Supplier

```python
class Supplier:
    """
    Canonical supplier entity.

    DDD role:
        Entity and Aggregate Root candidate.

    Identity:
        SupplierId.

    Responsibilities:
        Preserve supplier master identity and supplier-level invariants.
    """
```

---

# 249. Example docstring — QualificationScope

```python
@dataclass(frozen=True, slots=True)
class QualificationScope:
    """
    Defines the business perimeter of a supplier qualification.

    DDD role:
        Value Object.

    Invariant:
        A qualification must target a meaningful scope.
    """
```

---

# 250. Example docstring — SupplierQualification

```python
class SupplierQualification:
    """
    Represents a supplier qualification within a defined business scope.

    DDD role:
        Entity and Aggregate Root candidate.

    Identity:
        QualificationId.
    """
```

---

# 251. Naming Convention

Préférer :

```text
SupplierId
QualificationScope
RiskAssessment
SupplierRelationship
```

à :

```text
IdWrapper
ScopeData
RiskRecordModel
RelationEntity
```

Le nom doit exprimer le domaine.

---

# 252. Entity Suffix Rule

Ne pas ajouter :

```text
Entity
```

dans le nom uniquement pour signaler DDD.

Préférer :

```text
Supplier
```

à :

```text
SupplierEntity
```

---

# 253. ValueObject Suffix Rule

Même principe.

Préférer :

```text
Address
```

à :

```text
AddressValueObject
```

---

# 254. AggregateRoot Suffix Rule

Préférer :

```text
SupplierRelationship
```

à :

```text
SupplierRelationshipAggregateRoot
```

La classification appartient à la documentation.

---

# 255. Repository Naming

Ici le suffixe est naturel car il exprime une responsabilité technique/domain interface :

```text
SupplierRepository
```

---

# 256. Policy Naming

Le suffixe `Policy` est naturel car il exprime une notion métier :

```text
QualificationPolicy
RiskPolicy
```

---

# 257. Decision Naming

Le suffixe `Decision` est pertinent :

```text
QualificationDecision
ActivationDecision
```

car il exprime la nature du résultat.

---

# 258. Status Naming

Utiliser `Status` uniquement lorsqu’il s’agit réellement d’une valeur d’état.

---

# 259. Stage Naming

Utiliser `Stage` pour une étape d’un lifecycle.

Exemple :

```text
SupplierLifecycleStage
```

---

# 260. Type Naming

Les taxonomies peuvent utiliser :

```text
DocumentType
RiskType
IncidentType
```

si le terme "type" correspond réellement au métier.

---

# 261. Code Review Questions — Entities

```text
Does identity matter?
Could this be a Value Object instead?
What invariant does it own?
Why is it mutable?
Should it be a child entity?
Does it need a repository?
```

---

# 262. Code Review Questions — Value Objects

```text
Is identity irrelevant?
Can it be immutable?
What invariant does it protect?
Does the wrapper add real semantics?
Could a primitive be enough?
```

---

# 263. Code Review Questions — Aggregate Roots

```text
What must remain consistent atomically?
Why does this object own the boundary?
Are we loading too much?
Could another aggregate evolve independently?
```

---

# 264. Code Review Questions — Reference Objects

```text
Is the taxonomy closed or extensible?
Does it need identity?
Does it need versioning?
Could a code Value Object suffice?
```

---

# 265. Code Review Questions — Domain Results

```text
Is failure expected?
Should this be an exception?
Do callers need reasons?
Do agents/UI need explainability?
```

---

# 266. Learning Map — SupplierId

```text
Problem
    external IDs are unstable
        │
        ▼
Domain need
    canonical identity
        │
        ▼
DDD
    Value Object
        │
        ▼
Python
    immutable typed ID
```

---

# 267. Learning Map — Supplier

```text
Problem
    supplier identity persists over time
        │
        ▼
DDD
    Entity
        │
        ▼
Aggregate question
    which invariants belong here?
        │
        ▼
Python
    behavior-rich class
```

---

# 268. Learning Map — QualificationScope

```text
Problem
    qualification is never global by default
        │
        ▼
Domain concept
    scope
        │
        ▼
DDD
    Value Object
        │
        ▼
Invariant
    meaningful scope required
```

---

# 269. Learning Map — RiskAssessment

```text
Problem
    risk changes over time
        │
        ▼
Domain concept
    assessment occurrence
        │
        ▼
DDD
    Entity
        │
        ▼
Identity
    RiskAssessmentId
```

---

# 270. Learning Map — Scorecard

```text
Problem
    aggregated supplier performance view
        │
        ▼
Question
    source of truth or derived view?
        │
        ▼
Decision
    Projection by default
        │
        ▼
YAGNI
    do not create Aggregate unless lifecycle appears
```

---

# 271. Learning Map — SupplierCapability

```text
Problem
    represent what supplier can provide
        │
        ▼
Question
    simple classification or verified lifecycle?
        │
        ├── simple
        │      → Value Object / reference
        │
        └── rich lifecycle
               → Entity
```

---

# 272. Classification Decisions — summary

## Strong Entity decisions

```text
Supplier
SupplierRelationship
SupplierQualification
SupplierDocument
SupplierCertification
ComplianceCheck
RiskAssessment
SupplierAssessment
SupplierIncident
```

## Strong Entity candidates

```text
SupplierContact
SupplierLocation
SupplierOnboarding
```

## Strong Value Objects

```text
SupplierId
SupplierRelationshipId
ExternalIdentifier
Address
CountryCode
QualificationId
QualificationScope
QualificationStatus
DateRange
DocumentReference
EvidenceReference
RiskScore
RiskLevel
AssessmentScore
SupplierSegment
```

## Default projections/results

```text
SupplierScorecard
OnboardingProgress
QualificationDecision
ComplianceResult
RiskDecision
AssessmentDecision
SegmentationDecision
```

---

# 273. Decisions intentionally left open

```text
SupplierCapability
SupplierCategory richness
ComplianceRequirement richness
ComplianceFinding
RiskObservation
RiskMitigation
PerformanceMeasurement identity
SupplierScorecard lifecycle
SupplierDocument aggregate boundary
SupplierCertification aggregate boundary
SupplierOnboarding aggregate boundary
```

---

# 274. Why keep decisions open?

Parce que le modèle doit être guidé par :

```text
real invariants
real lifecycle
real use cases
```

et non par :

```text
desire to classify everything immediately.
```

---

# 275. Relationship with `06`

Le prochain document devra prendre ces classifications et établir :

```text
ownership
cardinality
aggregate references
supplier vs relationship scope
cross-aggregate boundaries
```

---

# 276. Relationship with `07`

Le `07` devra préciser :

```text
which object protects which invariant
```

et pourra modifier certaines frontières d’aggregate.

---

# 277. Relationship with implementation

Aucune classe de ce document ne doit être implémentée mécaniquement avant validation des invariants les plus importants.

---

# 278. Minimal implementation order candidate

```text
1. SupplierId
2. ExternalIdentifier
3. CountryCode
4. Address
5. Supplier
6. SupplierRelationshipId
7. SupplierRelationship
8. SupplierLifecycleStage
9. QualificationId
10. QualificationScope
11. SupplierQualification
12. QualificationDecision
13. Domain Events
```

Puis les autres capabilities.

---

# 279. Why this order?

Il suit :

```text
canonical identity
→ relationship context
→ lifecycle
→ qualification
```

qui constituent le cœur du produit.

---

# 280. Entity / Value Object North Star

Le modèle doit permettre au code de dire clairement :

```text
this object IS something
```

pour une Entity

et :

```text
this object DESCRIBES something
```

pour un Value Object.

---

# 281. Final Architecture Mapping

```text
Entity
    owns identity and behavior

Value Object
    owns semantic value and validation

Aggregate Root
    protects consistency boundary

Domain Result
    explains a business decision

Reference Object
    names stable domain vocabulary

Domain Event
    records a business fact
```

---

# 282. Pedagogical North Star

L’objectif n’est pas de mémoriser :

```text
"Entity = object with ID"
```

mais d’apprendre à poser :

```text
Does identity matter here?
```

L’objectif n’est pas de mémoriser :

```text
"Value Object = immutable object"
```

mais :

```text
Is this concept completely defined by its value?
```

L’objectif n’est pas de mémoriser :

```text
"Aggregate Root = root object"
```

mais :

```text
Which invariants must remain consistent together?
```
---

# 283. Final Checklist

Avant de valider un nouvel objet :

```text
[ ] Business meaning is clear
[ ] Naming is domain-oriented
[ ] Identity semantics are explicit
[ ] Equality semantics are explicit
[ ] Mutability is intentional
[ ] Aggregate ownership is known or deferred
[ ] Invariants are known or referenced
[ ] Domain vs DTO distinction is preserved
[ ] Domain vs ORM distinction is preserved
[ ] Technology leakage is absent
[ ] Pattern labels are justified
[ ] KISS/YAGNI were considered
```

---

# 284. Conclusion

PySRMKit dispose désormais d’une classification DDD plus précise de ses objets.

Le modèle s’organise autour de quelques règles fortes :

> **Une Entity est définie par son identité.**

> **Un Value Object est défini par sa valeur.**

> **Une Aggregate Root protège une frontière de cohérence.**

> **Un Domain Result explique une décision.**

> **Un Reference Object stabilise un vocabulaire.**

> **Un Domain Event représente un fait passé.**

Les décisions les plus importantes de ce document sont :

```text
Supplier
    = Entity + Aggregate Root candidate

SupplierRelationship
    = Entity + Aggregate Root candidate

SupplierQualification
    = Entity + strong Aggregate Root candidate

SupplierAssessment
    = Entity + strong Aggregate Root candidate

RiskAssessment
    = Entity + strong Aggregate Root candidate

SupplierIncident
    = Entity + strong Aggregate Root candidate

SupplierId
ExternalIdentifier
Address
CountryCode
QualificationScope
DateRange
RiskScore
EvidenceReference
    = Value Objects
```

Le document conserve volontairement certaines ambiguïtés lorsque les invariants et use cases ne permettent pas encore de trancher proprement.

Le prochain document devra résoudre la question structurelle suivante :

> **Comment tous ces objets sont-ils reliés, qui possède quoi, et où se trouvent réellement les frontières d’Aggregate ?**

Cette question sera traitée dans :

> **`06_PYSRMKIT_DOMAIN_RELATIONSHIPS_AND_ERD.md`**