# PySRMKit — Domain Relationships and ERD

**Document :** `06_PYSRMKIT_DOMAIN_RELATIONSHIPS_AND_ERD.md`  
**Projet :** PySRMKit  
**Domaine :** Supplier Relationship Management  
**Type :** Domain Modeling — Relations, ownership, cardinalités et ERD logique  
**Statut :** Draft de modélisation relationnelle  
**Version du document :** 0.1.0  
**Documents de référence :**
- `00_PYSRMKIT_EXPRESSION_DU_BESOIN.md`
- `01_PYSRMKIT_REQUIREMENTS_ANALYSIS.md`
- `02_PYSRMKIT_PRODUCT_VISION_AND_ARCHITECTURE_PRINCIPLES.md`
- `03_PYSRMKIT_SYSTEM_ARCHITECTURE.md`
- `04_PYSRMKIT_DOMAIN_OBJECTS.md`
- `05_PYSRMKIT_ENTITIES_AND_VALUE_OBJECTS.md`
- `PYSRMKIT_SOFTWARE_DESIGN_LEARNING_CONVENTION.md`

---

# 1. Objet du document

Ce document décrit les **relations entre les objets du domaine PySRMKit**.

Il précise notamment :

- qui possède quoi ;
- quelles relations sont internes à un Aggregate ;
- quelles relations doivent être représentées par des identifiants ;
- quelles cardinalités sont attendues ;
- quelles relations sont globales au Supplier ;
- quelles relations sont propres à une SupplierRelationship ;
- quelles dépendances sont synchrones ;
- quelles dépendances peuvent devenir éventuellement cohérentes ;
- quelles relations sont réellement métier ;
- quelles relations doivent rester hors du domaine.

Il introduit également une première représentation :

> **ERD logique du Supplier Domain**

Cette ERD n'est pas un schéma SQL.

Elle représente les **relations métier**.

---

# 2. Position dans la chaîne documentaire

```text
00 — Expression du besoin
        │
        ▼
01 — Requirements
        │
        ▼
02 — Vision & Architecture Principles
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
06 — DOMAIN RELATIONSHIPS & ERD   ← ce document
        │
        ▼
07 — Invariants & Business Rules
        │
        ▼
08 — Commands, Queries & Use Cases
```

Le `06` consolide donc :

```text
objects
+
ownership
+
cardinality
+
aggregate boundaries
```

avant de formaliser les invariants.

---

# 3. Convention pédagogique appliquée

Pour chaque relation importante, le document cherche à distinguer :

```text
BUSINESS RELATIONSHIP
        │
        ▼
OWNERSHIP
        │
        ▼
CARDINALITY
        │
        ▼
AGGREGATE BOUNDARY
        │
        ▼
REFERENCE STYLE
        │
        ▼
CONSISTENCY MODEL
        │
        ▼
TESTING IMPLICATION
```

---

# 4. Première règle — relation métier ≠ relation SQL

Une relation DDD n'est pas automatiquement :

```text
FOREIGN KEY
```

et une foreign key n'est pas automatiquement :

```text
business relationship
```

Exemple :

```text
SupplierQualification
    references
SupplierRelationshipId
```

est d'abord une relation métier.

La manière dont elle sera persistée :

```text
SQL FK
document reference
event projection
embedded document
```

reste une décision technique.

---

# 5. Deuxième règle — ownership ≠ navigation bidirectionnelle

Le fait que :

```text
Supplier
owns
SupplierContact
```

ne signifie pas nécessairement que :

```text
SupplierContact
```

doit contenir un objet complet `Supplier`.

Le modèle doit éviter les graphes d'objets bidirectionnels inutiles.

---

# 6. Troisième règle — Aggregate Reference by ID

Entre deux Aggregate Roots, la référence privilégiée est :

```text
typed identifier
```

Exemple :

```text
SupplierQualification
    supplier_id: SupplierId
    relationship_id: SupplierRelationshipId
```

plutôt que :

```text
supplier: Supplier
relationship: SupplierRelationship
```

si cela oblige à charger plusieurs aggregates ensemble.

---

# 7. Quatrième règle — ownership follows invariants

On ne décide pas qu'un objet appartient à un Aggregate parce qu'il est "visuellement lié".

La question est :

> **Quels objets doivent rester immédiatement cohérents pour protéger une règle métier ?**

---

# 8. Cinquième règle — global vs relational scope

Le Supplier Domain possède une distinction fondamentale :

```text
WHAT THE SUPPLIER IS
```

vs

```text
HOW OUR ORGANIZATION WORKS WITH THE SUPPLIER
```

Cette distinction guide le placement des relations.

---

# 9. Supplier Global Scope

Relèvent prioritairement du Supplier global :

```text
canonical identity
legal/commercial name
external identifiers
global organizational structure
global locations
global contacts
global capabilities
```

---

# 10. Supplier Relationship Scope

Relèvent prioritairement de `SupplierRelationship` :

```text
relationship lifecycle
organization-specific activation
organization-specific qualification
organization-specific segmentation
organization-specific compliance decision
organization-specific risk decision
```

---

# 11. Core Relationship Model

Le cœur du modèle peut être résumé ainsi :

```text
InternalOrganization
        │
        │ 1
        │
        │ *
        ▼
SupplierRelationship
        ▲
        │ *
        │
        │ 1
      Supplier
```

Une `SupplierRelationship` relie :

```text
one Supplier
```

à :

```text
one Internal Organization
```

dans un contexte relationnel précis.

---

# 12. Why SupplierRelationship Is Central

Sans `SupplierRelationship`, le modèle serait tenté d'attacher directement au Supplier :

- lifecycle ;
- qualification ;
- segmentation ;
- suspension ;
- compliance ;
- risk.

Or ces propriétés peuvent différer selon l'entité interne.

Exemple :

```text
Supplier ACME
│
├── Relationship with France BU
│      ACTIVE
│      IT_SERVICES = QUALIFIED
│
└── Relationship with Germany BU
       SUSPENDED
       IT_SERVICES = NOT_QUALIFIED
```

Le Supplier est le même.

La relation est différente.

---

# 13. First ERD — high level

```text
┌──────────────────────┐
│      Supplier        │
│  Aggregate Root      │
└──────────┬───────────┘
           │ 1
           │
           │ *
           ▼
┌────────────────────────────┐
│   SupplierRelationship     │
│      Aggregate Root        │
└───────┬─────────┬──────────┘
        │         │
        │         │
        ▼         ▼
Qualification   Lifecycle
        │
        ├─────────────┐
        ▼             ▼
Compliance          Risk
        │             │
        └──────┬──────┘
               ▼
          Assessments

Supplier also relates to:
Contacts
Locations
Documents
Certifications
Capabilities
Incidents
Performance
```

---

# 14. Logical ERD — expanded

```text
Supplier
│
├── 1..* ExternalIdentifier
│
├── 0..* SupplierContact
│
├── 0..* SupplierLocation
│
├── 0..* CategoryCode
│
├── 0..* CapabilityCode
│
├── 0..* SupplierDocument
│
├── 0..* SupplierCertification
│
├── 0..* SupplierAssessment
│
├── 0..* SupplierIncident
│
├── 0..* PerformanceMeasurement
│
└── 0..* SupplierRelationship
          │
          ├── 1 InternalOrganizationId
          │
          ├── 1 SupplierLifecycleStage
          │
          ├── 0..1 SupplierSegment
          │
          ├── 0..* SupplierQualification
          │
          ├── 0..* ComplianceCheck
          │
          ├── 0..* RiskAssessment
          │
          └── 0..* Relationship-specific Assessments
```

Cette représentation est une première cible logique.

---

# 15. Supplier Aggregate — proposed internal ownership

Proposition :

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

Ces objets sont fortement liés à l'identité canonique du Supplier.

---

# 16. Supplier Aggregate — excluded objects

Le Supplier Aggregate ne devrait pas contenir directement :

```text
SupplierQualification*
RiskAssessment*
SupplierAssessment*
SupplierIncident*
PerformanceMeasurement*
full history*
```

si ces objets possèdent un lifecycle ou une cohérence indépendante.

---

# 17. Supplier → ExternalIdentifier

## Cardinality

```text
Supplier
1
│
└── 1..* ExternalIdentifier
```

Un Supplier peut posséder plusieurs identifiants externes.

## Ownership

```text
Supplier owns ExternalIdentifier values
```

## DDD classification

```text
Supplier
    Entity / Aggregate Root

ExternalIdentifier
    Value Object
```

## Consistency

Immediate consistency inside Supplier Aggregate.

---

# 18. ExternalIdentifier uniqueness

Question d'invariant :

```text
Can the same Supplier contain duplicate external identifiers?
```

Réponse probable :

```text
No
```

mais la règle précise sera définie dans le `07`.

Autre question :

```text
Can two Suppliers share the same external identifier?
```

Probablement non pour certaines combinaisons :

```text
(type, value, source, jurisdiction)
```

mais cela peut nécessiter une contrainte repository/application.

---

# 19. Supplier → SupplierContact

## Cardinality

```text
Supplier
1
│
└── 0..* SupplierContact
```

## Ownership

Hypothèse actuelle :

```text
Supplier owns SupplierContact
```

## Why

Le contact est principalement une composante de la représentation fournisseur.

---

# 20. Contact direct access

Si l'application doit :

- rechercher tous les contacts par email ;
- gérer des permissions indépendantes ;
- partager un contact entre plusieurs Suppliers ;

la frontière devra être revue.

Pour le MVP :

```text
Child Entity
```

est suffisant.

---

# 21. Supplier → SupplierLocation

## Cardinality

```text
Supplier
1
│
└── 0..* SupplierLocation
```

## Ownership

Hypothèse :

```text
Supplier owns SupplierLocation
```

## Value relationship

```text
SupplierLocation
    owns
Address
```

---

# 22. SupplierLocation → Address

```text
SupplierLocation
1
│
└── 1 Address
```

`Address` est un Value Object.

Changer l'adresse :

```text
creates a new Address value
```

mais ne crée pas nécessairement une nouvelle Location.

---

# 23. Supplier → CategoryCode

## Cardinality

```text
Supplier
*
│
└── * CategoryCode
```

Conceptuellement :

```text
Supplier
has many categories
```

Une catégorie peut être utilisée par plusieurs Suppliers.

## Ownership

Le Supplier ne possède pas la définition globale de la catégorie.

Il possède seulement :

```text
references to CategoryCode
```

---

# 24. Category taxonomy

La taxonomie globale peut appartenir :

- à PySRMKit reference data ;
- à une application ;
- à PyProcurementKit ;
- à un catalogue externe.

PySRMKit doit éviter de devenir propriétaire d'un catalogue achats complet.

---

# 25. Supplier → CapabilityCode

Relation analogue :

```text
Supplier
0..*
│
└── CapabilityCode*
```

Le Supplier déclare ou possède certaines capacités.

La capability peut évoluer plus tard vers une Entity si elle porte :

- evidence ;
- verification ;
- lifecycle.

---

# 26. Supplier → SupplierRelationship

## Cardinality

```text
Supplier
1
│
└── 0..* SupplierRelationship
```

## Reference style

Le Supplier n'a pas nécessairement besoin de charger tous les objets Relationship.

La relation peut être naviguée via :

```text
SupplierRelationshipRepository
```

ou Query models.

---

# 27. SupplierRelationship → Supplier

Chaque Relationship référence exactement un Supplier.

```text
SupplierRelationship
*
│
└── 1 SupplierId
```

La relation stocke :

```text
SupplierId
```

pas nécessairement l'objet `Supplier`.

---

# 28. SupplierRelationship → InternalOrganization

Chaque Relationship concerne une entité interne.

```text
SupplierRelationship
*
│
└── 1 InternalOrganizationId
```

PySRMKit référence l'organisation interne sans en posséder le modèle complet.

---

# 29. Relationship uniqueness

Invariant candidat :

```text
A Supplier should not have two active relationships
with the same InternalOrganization
for the same relationship type/context
unless explicitly allowed.
```

Le scope exact sera défini dans `07`.

---

# 30. SupplierRelationship → Lifecycle

La relation possède un lifecycle.

```text
SupplierRelationship
1
│
└── 1 SupplierLifecycleStage
```

Le lifecycle est une valeur d'état et un comportement de transition.

---

# 31. Global Supplier lifecycle vs Relationship lifecycle

Deux options existaient :

```text
A. lifecycle on Supplier
B. lifecycle on SupplierRelationship
```

Décision privilégiée :

> **Le lifecycle opérationnel doit principalement être relationship-scoped.**

Raison :

Un Supplier peut être :

```text
ACTIVE
```

avec une entité interne

et :

```text
SUSPENDED
```

avec une autre.

---

# 32. Supplier-level lifecycle

Un Supplier global peut néanmoins avoir un état master minimal, par exemple :

```text
KNOWN
MERGED
ARCHIVED
```

si le besoin apparaît.

Mais cela doit rester distinct du Supplier Relationship Lifecycle.

Ne pas dupliquer :

```text
ACTIVE / SUSPENDED
```

à deux niveaux sans sémantique claire.

---

# 33. Relationship lifecycle — reference model

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

---

# 34. SupplierRelationship → SupplierSegment

## Cardinality

```text
SupplierRelationship
1
│
└── 0..1 SupplierSegment
```

La segmentation est par défaut relationnelle.

Raison :

Un Supplier peut être :

```text
STRATEGIC
```

pour une organisation

et :

```text
TRANSACTIONAL
```

pour une autre.

---

# 35. Relationship → Qualification

## Cardinality

```text
SupplierRelationship
1
│
└── 0..* SupplierQualification
```

## Ownership

La Relationship ne devrait pas nécessairement **own** les Qualifications dans le même aggregate.

Référence recommandée :

```text
SupplierQualification
    relationship_id
```

si Qualification devient Aggregate Root.

---

# 36. Why Qualification Separate?

Une Qualification possède :

- identity ;
- scope ;
- lifecycle ;
- validity ;
- decisions ;
- evidence ;
- revocation ;
- renewal.

Elle peut donc évoluer indépendamment de la Relationship.

---

# 37. SupplierQualification references

Proposition :

```text
SupplierQualification
├── QualificationId
├── SupplierId
├── SupplierRelationshipId
├── QualificationScope
├── QualificationStatus
├── validity
└── evidence references
```

Le `SupplierId` peut être redondant techniquement mais utile comme référence explicite.

Décision de persistence différée.

---

# 38. Qualification → Scope

```text
SupplierQualification
1
│
└── 1 QualificationScope
```

Le Scope est un Value Object.

---

# 39. QualificationScope → Organization

Le scope peut référencer :

```text
InternalOrganizationId
```

Mais si la Qualification appartient déjà à une Relationship, cette dimension peut être implicite.

Important :

> éviter de répéter la même information dans plusieurs niveaux sans raison.

---

# 40. QualificationScope → Category

```text
QualificationScope
0..1
│
└── CategoryCode```

ou plusieurs catégories selon la stratégie retenue.

Recommendation initiale :

```text
one qualification per meaningful scope
```

plutôt qu'une Qualification couvrant arbitrairement plusieurs catégories hétérogènes.

---

# 41. QualificationScope → Country

Le scope peut contenir :

```text
CountryCode
```

si la qualification varie par juridiction.

---

# 42. QualificationScope → Business Unit

Peut contenir une référence métier spécifique.

À éviter si :

```text
InternalOrganizationId
```

suffit déjà.

---

# 43. Qualification → Decision

Une Qualification peut avoir une décision courante :

```text
QualificationDecision
```

mais cette Decision est un Value Object / result.

Elle ne nécessite pas une relation séparée par ID.

---

# 44. Qualification history

Historique possible :

```text
QualificationRequested
QualificationApproved
QualificationRejected
QualificationRevoked
QualificationExpired
```

L'historique peut être reconstruit via :

- Domain Events ;
- audit records ;
- snapshots/versioning.

Pas besoin d'une relation objet complète dès le MVP.

---

# 45. Relationship → ComplianceCheck

## Cardinality

```text
SupplierRelationship
1
│
└── 0..* ComplianceCheck
```

Par défaut, les decisions de conformité sont relationnelles.

---

# 46. Supplier → Compliance evidence

Certaines evidences peuvent être supplier-level.

Exemple :

```text
tax certificate
ISO certification
company registration
```

Ainsi :

```text
SupplierDocument / SupplierCertification
```

peuvent être globales

tandis que :

```text
ComplianceCheck
```

interprète ces evidences dans un contexte de Relationship.

---

# 47. Evidence vs Decision architecture

```text
SupplierDocument
SupplierCertification
External Registry Result
         │
         ▼
     EVIDENCE
         │
         ▼
ComplianceCheck / Policy
         │
         ▼
Compliance Result
         │
         ▼
Relationship decision
```

Cette distinction évite de confondre :

```text
document exists
```

avec :

```text
supplier is compliant for this relationship.
```

---

# 48. ComplianceCheck references

Proposition :

```text
ComplianceCheck
├── ComplianceCheckId
├── SupplierId
├── SupplierRelationshipId
├── ComplianceRequirementCode
├── performed_at
├── ComplianceResult
└── EvidenceReference*
```

---

# 49. Relationship → RiskAssessment

## Cardinality

```text
SupplierRelationship
1
│
└── 0..* RiskAssessment
```

Une Relationship peut posséder plusieurs RiskAssessments dans le temps.

---

# 50. Global Supplier Risk

Certains risques peuvent être intrinsèques au Supplier :

```text
financial health
sanctions exposure
reputational issue
```

Alors que d'autres dépendent de notre contexte :

```text
concentration risk
dependency risk
criticality
```

---

# 51. Risk subject model

Pour éviter un `SubjectRef` générique prématuré, le MVP peut distinguer explicitement :

```text
SupplierRiskAssessment
```

et :

```text
RelationshipRiskAssessment
```

ou utiliser des champs explicites :

```text
supplier_id
relationship_id?
```

Le choix final sera affiné dans `07/08`.

---

# 52. RiskAssessment cardinality

```text
SupplierRelationship
1
│
└── 0..* RiskAssessment
```

et potentiellement :

```text
Supplier
1
│
└── 0..* RiskAssessment
```

selon le scope.

La multiplicité est temporelle.

---

# 53. RiskAssessment → RiskType

```text
RiskAssessment
1
│
└── 1 RiskType
```

---

# 54. RiskAssessment → Evidence

```text
RiskAssessment
1
│
└── 0..* EvidenceReference
```

---

# 55. Risk history

Ne pas écraser :

```text
current_risk_score
```

sans conserver le passé.

Le modèle naturel est :

```text
RiskAssessment(t1)
RiskAssessment(t2)
RiskAssessment(t3)
```

avec éventuellement une projection :

```text
CurrentRiskProfile
```

---

# 56. Supplier → SupplierDocument

## Cardinality

```text
Supplier
1
│
└── 0..* SupplierDocument
```

Mais cette relation est insuffisante pour tous les cas.

Un document peut être scope à :

```text
Supplier
Legal Entity
Location
Relationship
Qualification
```

---

# 57. Document ownership — recommended model

Le `SupplierDocument` reste une Entity indépendante ou child entity selon l'implémentation.

Sa relation doit porter explicitement son contexte.

Option initiale simple :

```text
SupplierDocument
├── supplier_id
├── relationship_id?
├── location_id?
├── document_type
└── ...
```

Cette approche reste explicite.

---

# 58. Avoid Generic DocumentSubject Too Early

Ne pas introduire immédiatement :

```text
DocumentSubject(type, id)
```

ou :

```text
PolymorphicOwner
```

sans besoin réel.

Préférer des références explicitement nommées.

---

# 59. SupplierDocument → DocumentReference

```text
SupplierDocument
1
│
└── 1 DocumentReference
```

Le `DocumentReference` pointe vers le stockage externe.

---

# 60. SupplierDocument → EvidenceReference

Un document peut lui-même servir d'evidence.

On peut convertir ou référencer :

```text
SupplierDocumentId
```

depuis `EvidenceReference`.

La forme définitive reste à définir.

---

# 61. Supplier → SupplierCertification

## Cardinality

```text
Supplier
1
│
└── 0..* SupplierCertification
```

La certification peut être globalement détenue par le Supplier ou scope à une entité/site.

---

# 62. Certification scope

```text
SupplierCertification
1
│
└── 1 CertificationScope
```

ou scope optionnel si global.

Le `CertificationScope` peut référencer :

```text
SupplierOrganization
SupplierLocation
CapabilityCode
CategoryCode
```

selon besoin.

---

# 63. Supplier → SupplierAssessment

## Cardinality

```text
Supplier
1
│
└── 0..* SupplierAssessment
```

Mais une Assessment peut aussi être Relationship-specific.

---

# 64. Assessment subject

Première recommandation :

```text
SupplierAssessment
├── supplier_id
├── relationship_id?
├── assessment_type
└── ...
```

Ainsi :

- supplier-level review ;
- relationship-level review ;

restent explicitement possibles.

---

# 65. Assessment → Questions

```text
SupplierAssessment
1
│
└── 1..* AssessmentQuestion
```

Les questions sont par défaut des Value Objects snapshot à l'intérieur de l'Assessment Aggregate.

---

# 66. Assessment → Answers

```text
AssessmentQuestion
1
│
└── 0..1 AssessmentAnswer
```

ou plusieurs réponses selon le type de question.

Le modèle final dépendra du moteur d'assessment.

---

# 67. Assessment → Score

```text
SupplierAssessment
1
│
└── 0..* AssessmentScore
```

Scores par dimension possibles.

---

# 68. Assessment → Decision

```text
SupplierAssessment
1
│
└── 0..1 AssessmentDecision
```

La décision peut n'exister qu'à la clôture.

---

# 69. Supplier → PerformanceMeasurement

## Cardinality

```text
Supplier
1
│
└── 0..* PerformanceMeasurement
```

Mais les performances peuvent être relationship-scoped.

Recommendation :

```text
supplier_id
relationship_id?
```

---

# 70. PerformanceMeasurement → Metric

```text
PerformanceMeasurement
1
│
└── 1 PerformanceMetric
```

---

# 71. PerformanceMeasurement → Period

```text
PerformanceMeasurement
1
│
└── 1 PerformancePeriod
```

ou timestamp unique selon métrique.

---

# 72. SupplierScorecard

Par défaut :

```text
SupplierScorecard
```

est une projection.

Elle agrège :

```text
PerformanceMeasurement*
AssessmentScore*
Incident data*
Compliance information*
```

selon policy.

---

# 73. Scorecard is not an owner

Une Scorecard dérivée ne doit pas devenir propriétaire des measurements.

Direction :

```text
Measurements
    ↓
Scorecard projection
```

et non l'inverse.

---

# 74. Supplier → SupplierIncident

## Cardinality

```text
Supplier
1
│
└── 0..* SupplierIncident
```

L'incident peut également appartenir à une Relationship.

---

# 75. Incident scope

Recommendation :

```text
SupplierIncident
├── supplier_id
├── relationship_id?
├── location_id?
└── ...
```

si nécessaire.

---

# 76. Incident effects

Un incident ne doit pas contenir directement :

```text
RiskAssessment object
Qualification object
SupplierRelationship object
```

Il émet plutôt :

```text
SupplierIncidentReported
```

puis l'application orchestre les effets.

---

# 77. Incident → Risk relationship

Conceptuellement :

```text
Incident
    may trigger
Risk Reassessment
```

mais pas :

```text
Incident owns RiskAssessment
```

---

# 78. Incident → Qualification relationship

Conceptuellement :

```text
Incident
    may trigger
Qualification Review
```

mais ne modifie pas directement la qualification.

---

# 79. Relationship → Onboarding

## Cardinality

```text
SupplierRelationship
1
│
└── 0..* SupplierOnboarding
```

si plusieurs cycles d'onboarding sont possibles.

Alternative :

```text
0..1 current onboarding
```

avec historique externe.

---

# 80. Recommended onboarding model

Pour préserver l'historique :

```text
SupplierRelationship
    1
    │
    └── 0..* SupplierOnboarding
```

où un seul onboarding peut être courant.

---

# 81. SupplierOnboarding ownership

Strong candidate :

```text
SupplierOnboarding
    separate Entity / possibly Aggregate Root
```

si plusieurs onboardings successifs sont autorisés.

Sinon une child entity peut suffire.

Décision finale après invariants.

---

# 82. Onboarding → Requirement

```text
SupplierOnboarding
1
│
└── 0..* OnboardingRequirement
```

si les requirements sont snapshot de l'onboarding.

---

# 83. Onboarding vs Workflow

Important :

```text
OnboardingRequirement
```

ne doit pas devenir :

```text
WorkflowTask
```

PySRMKit modélise :

```text
what is required
```

pas :

```text
who must perform which task at 14:00.
```

---

# 84. Organization Structure

Le Supplier peut être lié à plusieurs `SupplierOrganization` nodes.

Conceptuellement :

```text
Supplier
1
│
└── 1..* SupplierOrganization
```

si l'on sépare clairement Supplier de ses entités légales.

---

# 85. SupplierOrganization model options

Deux options principales.

## Option A — embedded organizational structure

```text
Supplier
    owns
SupplierOrganization nodes
```

## Option B — multiple linked Supplier entities

Chaque legal entity est elle-même un Supplier.

Le groupe est modélisé par relationships.

---

# 86. Recommended direction

Pour conserver une identité claire :

> **Treat legal entities that can independently enter supplier relationships as Supplier entities.**

Puis représenter :

```text
SupplierOrganizationRelationship
```

entre elles.

Cela évite un Supplier global trop abstrait.

---

# 87. Group structure example

```text
ACME GROUP
   │
   ├── ACME FRANCE
   │      SupplierId = S1
   │
   ├── ACME GERMANY
   │      SupplierId = S2
   │
   └── ACME UK
          SupplierId = S3
```

avec :

```text
OrganizationRelationship
    PARENT_OF
```

---

# 88. SupplierOrganization role reconsidered

Conséquence :

`SupplierOrganization` pourrait devenir principalement :

```text
organization graph / relationship model
```

plutôt qu'une entité contenant toutes les filiales à l'intérieur d'un Supplier.

Cette décision est plus scalable pour multi-country / legal entities.

---

# 89. Legal Entity principle

Si une entité possède :

- identifiant légal propre ;
- contrats propres ;
- taxes propres ;
- relations fournisseur propres ;

elle mérite probablement son propre :

```text
SupplierId
```

---

# 90. OrganizationRelationship

Proposition :

```text
SupplierOrganizationRelationship
├── parent_supplier_id
├── child_supplier_id
├── relationship_type
└── validity?
```

DDD role :

```text
Entity or immutable relationship record
```

selon history.

---

# 91. Supplier relationship types

Différents types de relation avec l'organisation interne peuvent exister :

```text
DIRECT_SUPPLIER
SUBCONTRACTOR
PARTNER_SUPPLIER
TEMPORARY_VENDOR
```

Ne pas figer tant que le métier ne le requiert pas.

---

# 92. Supplier-to-Supplier relationships

Possible future need :

```text
parent
subsidiary
affiliate
subcontractor
distributor
```

À garder hors MVP si non nécessaire.

---

# 93. Internal organization is external context

PySRMKit ne doit pas modéliser :

```text
full corporate hierarchy
HR org chart
cost centers
IAM groups
```

Il utilise simplement :

```text
InternalOrganizationId
```

ou une projection externe.

---

# 94. Cross-Bounded-Context Reference

Lorsqu'un objet PySRMKit référence un autre bounded context :

```text
ContractId
VendorAccountId
ProcurementCategoryId
```

il doit utiliser un identifiant/reference, pas embarquer l'Aggregate externe.

---

# 95. Supplier → Contracts

Conceptuellement :

```text
Supplier
1
│└── 0..* ContractReference
```

Mais :

```text
Contract Aggregate
```

appartient à PyContractKit.

---

# 96. ContractReference

Peut être un Value Object :

```text
ContractReference
├── contract_id
├── external_system?
└── status_snapshot?
```

À introduire uniquement si PySRMKit a besoin de matérialiser ce lien.

---

# 97. Supplier → Vendor Account

Conceptuellement :

```text
Supplier
    may map to
VendorAccount
```

mais cette relation appartient à l'intégration avec PyAccountingKit.

PySRMKit ne possède pas le VendorAccount.

---

# 98. Supplier → Procurement

PyProcurementKit consomme :

```text
SupplierId
Qualification
Capability
```

mais les POs et sourcing events restent externes.

---

# 99. Domain Boundaries Diagram

```text
                    ┌─────────────────┐
                    │    PyCRMKit     │
                    └─────────────────┘

┌──────────────────────────────────────────────────────────┐
│                      PySRMKit                            │
│                                                          │
│ Supplier → Relationship → Qualification / Risk / ...    │
└───────────────┬───────────────────────┬──────────────────┘
                │                       │
                ▼                       ▼
       PyProcurementKit          PyContractKit
                │                       │
                ▼                       ▼
         Purchase Process         Contract Domain
                │
                └──────────┬────────────┘
                           ▼
                    PyAccountingKit
```

---

# 100. Aggregate Boundary Map

Première proposition consolidée :

```text
AGGREGATE 1
Supplier
├── SupplierIdentity
├── ExternalIdentifier*
├── SupplierContact*
├── SupplierLocation*
├── CategoryCode*
└── CapabilityCode*

AGGREGATE 2
SupplierRelationship
├── SupplierId
├── InternalOrganizationId
├── SupplierLifecycleStage
└── SupplierSegment?

AGGREGATE 3
SupplierQualification
├── SupplierId
├── SupplierRelationshipId
├── QualificationScope
├── QualificationStatus
└── QualificationDecision?

AGGREGATE 4
SupplierAssessment
├── AssessmentQuestion*
├── AssessmentAnswer*
├── AssessmentScore*
└── AssessmentDecision?

AGGREGATE 5
RiskAssessment
├── RiskType
├── RiskScore
├── RiskLevel
└── EvidenceReference*

AGGREGATE 6
SupplierIncident
├── IncidentType
├── IncidentSeverity
├── IncidentStatus
└── EvidenceReference*
```

---

# 101. Conditional Aggregate Roots

À confirmer :

```text
SupplierOnboarding
SupplierDocument
SupplierCertification
ComplianceCheck
```

Ces objets peuvent devenir Aggregate Roots si leur lifecycle, concurrence ou accès indépendant le justifie.

---

# 102. Aggregate Root → Repository map

Si confirmés :

```text
Supplier
    → SupplierRepository

SupplierRelationship
    → SupplierRelationshipRepository

SupplierQualification
    → SupplierQualificationRepository

SupplierAssessment
    → SupplierAssessmentRepository

RiskAssessment
    → RiskAssessmentRepository

SupplierIncident
    → SupplierIncidentRepository
```

Pas de Repository pour :

```text
Address
CountryCode
QualificationScope
RiskScore
```

---

# 103. Consistency model

## Within Aggregate

```text
strong / immediate consistency
```

## Across Aggregates

Prefer:

```text
application coordination
or
eventual consistency
```

selon le use case.

---

# 104. Example — Supplier activation

L'activation peut dépendre de plusieurs aggregates :

```text
SupplierRelationship
Qualification
Compliance
Risk
```

Il serait dangereux d'en faire un mega-aggregate uniquement pour obtenir une transaction unique.

---

# 105. Activation orchestration

Architecture possible :

```text
Application Handler
    │
    ├── load Relationship
    ├── query qualifying state
    ├── query compliance state
    ├── query risk state
    ├── build ActivationContext
    ├── ActivationPolicy.evaluate()
    └── Relationship.activate(decision)
```

---

# 106. ActivationContext

**Status :** PROPOSED APPLICATION/DOMAIN INPUT VALUE OBJECT

Peut rassembler les faits nécessaires à la policy :

```text
qualification summary
compliance summary
risk summary
required documents status
```

sans charger tous les aggregates dans `SupplierRelationship`.

---

# 107. Why ActivationContext Matters

Il évite :

```text
SupplierRelationship
    depending directly on
QualificationRepository
RiskRepository
ComplianceProvider
```

Le Domain Object reste pur.

---

# 108. Cross-Aggregate invariant strategy

Si une règle dépend de plusieurs aggregates :

```text
Application gathers facts
        │
        ▼
Domain Policy evaluates
        │
        ▼
Aggregate applies local state transition
```

---

# 109. Example — incident triggers suspension review

```text
SupplierIncident
    │
    └── emits SupplierIncidentReported
                │
                ▼
         Application handler
                │
                ├── reassess risk
                └── consider suspension
```

Aucun Aggregate ne modifie directement l'autre.

---

# 110. Relationship cardinality notation

Convention :

```text
1
0..1
0..*
1..*
```

Les cardinalités sont conceptuelles, pas SQL-specific.

---

# 111. Master cardinality table

| From | Relation | To | Cardinality |
|---|---|---|---|
| Supplier | has | ExternalIdentifier | 1 → 1..* |
| Supplier | has | SupplierContact | 1 → 0..* |
| Supplier | has | SupplierLocation | 1 → 0..* |
| Supplier | classified by | CategoryCode | * ↔ * conceptually |
| Supplier | has | CapabilityCode | * ↔ * conceptually |
| Supplier | participates in | SupplierRelationship | 1 → 0..* |
| SupplierRelationship | references | Supplier | * → 1 |
| SupplierRelationship | references | InternalOrganization | * → 1 |
| SupplierRelationship | has current | LifecycleStage | 1 → 1 |
| SupplierRelationship | has | SupplierQualification | 1 → 0..* |
| SupplierRelationship | has | ComplianceCheck | 1 → 0..* |
| SupplierRelationship | has | RiskAssessment | 1 → 0..* |
| SupplierRelationship | has | SupplierSegment | 1 → 0..1 |
| Supplier | has | SupplierDocument | 1 → 0..* |
| Supplier | has | SupplierCertification | 1 → 0..* |
| Supplier | has | SupplierAssessment | 1 → 0..* |
| Supplier | has | SupplierIncident | 1 → 0..* |
| Supplier | has | PerformanceMeasurement | 1 → 0..* |

---

# 112. Contextual relationships

Certaines relations peuvent être supplier-level ou relationship-level.

| Object | Supplier-level | Relationship-level |
|---|---:|---:|
| Document | Yes | Yes |
| Certification | Yes | Yes |
| Assessment | Yes | Yes |
| RiskAssessment | Yes | Yes |
| PerformanceMeasurement | Yes | Yes |
| Incident | Yes | Yes |
| ComplianceCheck | Rare/possible | Yes |

---

# 113. Avoid polymorphic ownership prematurely

Il serait facile d'ajouter :

```text
owner_type
owner_id
```

partout.

Mais ce modèle :

- cache la sémantique ;
- complique les invariants ;
- fragilise le typing.

Préférer des références explicitement nommées.

---

# 114. Relation object vs foreign key

Si une relation a :

- son propre lifecycle ;
- des attributs ;
- une identité ;
- une histoire ;

elle mérite un objet de domaine.

Exemple :

```text
SupplierRelationship
```

et non simplement :

```text
supplier.internal_organization_id
```

---

# 115. SupplierRelationship is not a join table

C'est un point clé.

`SupplierRelationship` n'est pas simplement :

```text
supplier_id + organization_id
```

Il porte :

- lifecycle ;
- segmentation ;
- relation status ;
- relationship-level decisions.

Il s'agit donc d'une **Entity métier**.

---

# 116. Qualification is not a join table

De même :

```text
SupplierQualification
```

n'est pas simplement :

```text
supplier_id + category_id
```

Elle possède :

- status ;
- validity ;
- decision ;
- evidence ;
- history.

---

# 117. Relationship graph complexity

Le modèle peut devenir un graphe.

Risques :

- navigation infinie ;
- cycles ;
- gros chargements ;
- ORM cascades.

Solution :

```text
Aggregate boundaries
+
typed IDs
+
queries/projections
```

---

# 118. Navigation Principle

Dans le domain code, navigation privilégiée :

```text
inside aggregate
    object references allowed

across aggregates
    IDs preferred
```

---

# 119. Collection ownership

Une collection interne doit être protégée si elle porte des invariants.

Exemple :

```text
Supplier.external_identifiers
```

ne devrait pas être librement mutable.

---

# 120. Relationship creation

Créer une `SupplierRelationship` nécessite au minimum :

```text
SupplierId
InternalOrganizationId
```

et potentiellement :

```text
RelationshipId
initial lifecycle stage
relationship type
```

---

# 121. Relationship start

La relation peut commencer à :

```text
DISCOVERED
```

ou :

```text
PROSPECTIVE
```

selon use case.

Cette décision appartient aux invariants/use cases.

---

# 122. Qualification uniqueness

Possible invariant :

```text
Only one current qualification
for a given relationship + qualification scope
```

mais plusieurs historical qualifications peuvent exister.

---

# 123. Qualification renewal

Deux modèles possibles :

## Update same Qualification entity

```text
same QualificationId
new validity/status
```

## Create new Qualification

```text
new QualificationId
previous qualification referenced
```

Décision à prendre dans `07`.

---

# 124. Risk history cardinality

```text
Relationship
1
│
└── many RiskAssessment
```

Il n'existe pas seulement :

```text
one risk
```

mais une série temporelle.

---

# 125. Performance history cardinality

Même logique :

```text
Relationship
1
│
└── many PerformanceMeasurement
```

par metric/période.

---

# 126. Incident cardinality

```text
Supplier/Relationship
1
│
└── many Incidents
```

Chaque incident reste individuel.

---

# 127. Assessment cardinality

```text
Supplier/Relationship
1
│
└── many Assessments
```

Exemple :

```text
annual review 2026
annual review 2027
```

---

# 128. Certification renewal

Une certification peut être modélisée comme :

```text
same certification entity
with renewed validity
```

ou :

```text
new certification instance per issuance
```

La seconde approche préserve mieux l'historique.

Recommendation :

```text
new SupplierCertification instance per issued certificate
```

avec relation logique vers le même `CertificationType`.

---

# 129. Document versioning

Même question :

```text
new document version
```

devrait probablement créer :

```text
new SupplierDocument instance
```

ou une révision explicite.

Ne pas écraser les preuves historiques.

---

# 130. Immutable evidence principle

Les evidence utilisées dans une décision historique doivent rester référencables.

Si un document est remplacé :

```text
old evidence reference
must remain resolvable
```

si l'audit l'exige.

---

# 131. ERD — Aggregate View

```text
┌───────────────────────┐
│      Supplier AR      │
└───────────┬───────────┘
            │ SupplierId
            ▼
┌─────────────────────────────┐
│ SupplierRelationship AR     │
└───────┬──────────┬──────────┘
        │          │
        │          ├───────────────┐
        │          │               │
        ▼          ▼               ▼
Qualification AR  RiskAssessment AR  ComplianceCheck?
        │
        │
        ▼
Assessment AR? / evidence

Supplier AR also referenced by:
Document?
Certification?
Assessment AR
Incident AR
Performance records
```

---

# 132. ERD — Value Object View

```text
Supplier
├── SupplierId
├── SupplierIdentity
├── ExternalIdentifier*
├── CategoryCode*
└── CapabilityCode*

SupplierRelationship
├── SupplierRelationshipId
├── InternalOrganizationId
├── SupplierLifecycleStage
└── SupplierSegment?

SupplierQualification
├── QualificationId
├── QualificationScope
├── QualificationStatus
├── DateRange?
└── QualificationDecision?

RiskAssessment
├── RiskAssessmentId
├── RiskType
├── RiskScore
├── RiskLevel
└── EvidenceReference*
```

---

# 133. Logical ERD — Mermaid-compatible draft

```text
SUPPLIER ||--o{ SUPPLIER_RELATIONSHIP : has
SUPPLIER ||--o{ SUPPLIER_CONTACT : has
SUPPLIER ||--o{ SUPPLIER_LOCATION : has
SUPPLIER ||--o{ SUPPLIER_DOCUMENT : has
SUPPLIER ||--o{ SUPPLIER_CERTIFICATION : has
SUPPLIER ||--o{ SUPPLIER_ASSESSMENT : has
SUPPLIER ||--o{ SUPPLIER_INCIDENT : has

SUPPLIER_RELATIONSHIP ||--o{ SUPPLIER_QUALIFICATION : has
SUPPLIER_RELATIONSHIP ||--o{ COMPLIANCE_CHECK : has
SUPPLIER_RELATIONSHIP ||--o{ RISK_ASSESSMENT : has
SUPPLIER_RELATIONSHIP ||--o{ SUPPLIER_ONBOARDING : has

SUPPLIER_ASSESSMENT ||--o{ ASSESSMENT_QUESTION : contains
ASSESSMENT_QUESTION ||--o| ASSESSMENT_ANSWER : receives
```

Cette représentation devra être transformée en Mermaid/PlantUML formel si nécessaire.

---

# 134. Physical ERD is deferred

Le document ne définit pas encore :

```text
table names
primary keys
foreign keys
indexes
join tables
cascade rules
```

Ces décisions appartiennent à la persistence.

---

# 135. Domain ERD vs Persistence ERD

```text
DOMAIN ERD
    business meaning

PERSISTENCE ERD
    storage model
```

Ils peuvent se ressembler.

Ils ne doivent pas être identiques par obligation.

---

# 136. Relationship consistency table

| Relation | Consistency |
|---|---|
| Supplier → ExternalIdentifier | Immediate |
| Supplier → Contact | Immediate |
| Supplier → Location | Immediate |
| Relationship → Lifecycle | Immediate |
| Qualification → Scope | Immediate |
| Assessment → Answers | Immediate |
| Supplier → Relationship | Cross-aggregate |
| Relationship → Qualification | Cross-aggregate |
| Relationship → RiskAssessment | Cross-aggregate |
| Incident → Risk effect | Eventual/application coordinated |
| Incident → Qualification review | Eventual/application coordinated |

---

# 137. Domain Events for relationships

Relations cross-aggregate peuvent être coordonnées via :

```text
SupplierRelationshipCreated
SupplierQualified
SupplierRiskChanged
SupplierIncidentReported
SupplierSuspended
SupplierOffboarded
```

---

# 138. Example — qualification approved

```text
SupplierQualification
        │
        ├── status = QUALIFIED
        └── emits SupplierQualified
                 │
                 ▼
          Application Layer
                 │
                 ├── update projection
                 └── evaluate relationship activation
```

---

# 139. Example — risk increased

```text
RiskAssessment
      │
      └── RiskChanged event
              │
              ▼
      Application / Policy
              │
              └── consider suspension
```

---

# 140. Example — document expired

```text
SupplierDocument
      │
      └── DocumentExpired
              │
              ▼
       Compliance reevaluation
              │
              ▼
       Relationship decision
```

---

# 141. Eventual Consistency

Cross-aggregate consistency may be delayed.

Exemple :

```text
Document expires at t1
Compliance projection updates at t1 + delta
```

Pour certaines règles critiques, l'application peut faire une vérification synchrone lors de la décision.

---

# 142. Command-side truth vs projection

Une activation ne doit pas faire confiance uniquement à une projection éventuellement obsolète si l'invariant exige une décision forte.

Possible strategy :

```text
load current decision inputs
→ evaluate policy
→ transition relationship
```

---

# 143. Read Model relationships

Les Queries peuvent exposer une vue dénormalisée :

```text
Supplier360View
├── supplier identity
├── relationships
├── qualification summary
├── risk summary
├── compliance summary
└── performance summary
```

sans transformer cette vue en Aggregate.

---

# 144. Supplier360View

**Classification :** Projection / Read Model

Très utile pour :

- UI ;
- agents ;
- API ;
- reporting.

Mais ce n'est pas :

```text
Supplier Aggregate
```

---

# 145. Avoid aggregate inflation from UI needs

Un dashboard montrant tout le fournisseur ne justifie pas un Aggregate contenant tout le fournisseur.

UI composition ≠ transaction boundary.

---

# 146. Search relationships

Recherche par :

```text
name
external identifier
country
category
status
qualification
risk
```

peut utiliser des projections/indexes.
Pas besoin de méthodes repository complexes sur le Domain Aggregate.

---

# 147. Supplier merge

Future use case possible :

```text
duplicate suppliers detected
→ merge
```

Ce use case peut impacter :

- relationships ;
- documents ;
- identifiers ;
- history.

Il devra être traité explicitement plus tard.

---

# 148. Supplier split

Inversement, une mauvaise modélisation d'organisation peut nécessiter de séparer un Supplier en plusieurs legal entities.

Ce besoin renforce l'intérêt de IDs canoniques et relations explicites.

---

# 149. Relationship termination vs Supplier deletion

Important :

```text
Offboard SupplierRelationship
≠
Delete Supplier
```

L'identité Supplier peut rester dans le référentiel.

---

# 150. Hard delete policy

Par défaut :

```text
business entities with history
should not be hard-deleted casually
```

Le `07` précisera les règles d'archivage/offboarding.

---

# 151. Supplier archival

Un Supplier sans aucune relation active peut éventuellement être :

```text
ARCHIVED
```

au niveau master.

Mais cela est distinct de :

```text
OFFBOARDED relationship.
```

---

# 152. Aggregate ownership summary

## Supplier owns

```text
SupplierIdentity
ExternalIdentifier*
SupplierContact*
SupplierLocation*
Category/Capability references
```

## SupplierRelationship owns

```text
Relationship identity
InternalOrganizationId
Relationship lifecycle
Relationship segment
```

## SupplierQualification owns

```text
QualificationScope
QualificationStatus
Validity
Decision snapshot
Evidence references
```

## SupplierAssessment owns

```text
Questions
Answers
Scores
Decision
Evidence references
```

## RiskAssessment owns

```text
RiskType
RiskScore
RiskLevel
Evidence references
```

## SupplierIncident owns

```text
IncidentType
IncidentSeverity
IncidentStatus
Impact
Evidence references
```

---

# 153. Non-ownership summary

SupplierRelationship does **not** own:

```text
full Supplier
full Qualification aggregate collection in memory
full RiskAssessment history
full Compliance history
```

Supplier does **not** own:

```text
all relationship operations
all qualifications
all incidents
all history
```

---

# 154. Aggregate reference summary

```text
SupplierRelationship
    → SupplierId

SupplierQualification
    → SupplierId
    → SupplierRelationshipId

RiskAssessment
    → SupplierId
    → SupplierRelationshipId?

SupplierAssessment
    → SupplierId
    → SupplierRelationshipId?

SupplierIncident
    → SupplierId
    → SupplierRelationshipId?
```

---

# 155. Reference duplication

Including both:

```text
supplier_id
relationship_id
```

can be useful but may be redundant.

Rule:

> duplicate identifiers only if they improve invariants/querying without creating ambiguity.

Physical model decision deferred.

---

# 156. Relationship-level source of truth

If a Qualification references a Relationship, the Supplier can be derived from that Relationship.

Thus:

```text
supplier_id
```

may not be necessary in the domain object.

This choice will be revisited in implementation.

---

# 157. Aggregate Root identity graph

```text
SupplierId
   │
   ▼
SupplierRelationshipId
   │
   ├──► QualificationId
   ├──► RiskAssessmentId
   ├──► AssessmentId
   └──► IncidentId
```

Conceptually, not necessarily hierarchical IDs.

---

# 158. Business invariant locality

Un invariant doit idéalement être protégé par l'Aggregate qui possède toutes les données nécessaires.

Exemple :

```text
Qualification scope cannot be empty
```

→ `SupplierQualification`

Exemple :

```text
Relationship cannot transition OFFBOARDED → ACTIVE
```

→ `SupplierRelationship`

---

# 159. Cross-aggregate business rule

Exemple :

```text
Relationship can activate only if qualification is valid.
```

Aucun Aggregate seul ne possède toutes les données.

Solution :

```text
Application + ActivationPolicy + current facts
```

---

# 160. Why not make everything one aggregate?

Parce que cela créerait :

- fort couplage ;
- forte contention ;
- gros chargements ;
- persistence difficile ;
- logique difficile à tester ;
- faible composabilité.

---

# 161. Why not make every object separate?

L'inverse serait aussi mauvais.

Trop de petits aggregates entraîneraient :

- orchestration excessive ;
- trop de repositories ;
- eventual consistency inutile ;
- difficulté à protéger les invariants locaux.

---

# 162. Aggregate sizing rule

Chercher :

```text
smallest aggregate
that can protect
the required invariant.
```

---

# 163. Relationship between Documents and Compliance

```text
SupplierDocument
    is evidence

ComplianceCheck
    interprets evidence
```

Cette relation doit être par référence :

```text
EvidenceReference
```

plutôt que composition forte.

---

# 164. Relationship between Certifications and Qualification

Une certification peut être un input de :

```text
QualificationPolicy
```

Mais Qualification ne possède pas la Certification.

---

# 165. Relationship between Risk and Qualification

Le Risk peut influencer :

```text
qualification decision
```

mais doit rester un domaine séparé.

---

# 166. Relationship between Performance and Segmentation

Performance peut influencer :

```text
SegmentationPolicy
```

sans que Segment possède les metrics.

---

# 167. Relationship between Incidents and Performance

Incident Rate peut être dérivé des Incidents.

Direction :

```text
Incidents
    → metric/projection
```

pas :

```text
Performance owns Incident
```

---

# 168. Relationship between Assessment and Qualification

Une Assessment peut produire evidence/decision utilisée pour une Qualification.

Mais :

```text
Assessment
≠
Qualification
```

---

# 169. Relationship between Assessment and Risk

Même distinction.

Une Assessment de risque peut produire des inputs pour `RiskAssessment`.

---

# 170. Relationship between Onboarding and Qualification

Onboarding peut contenir une étape métier :

```text
qualification
```

mais ne doit pas posséder l'Aggregate Qualification.

Il peut référencer son état/résultat.

---

# 171. Relationship between Onboarding and Documents

Onboarding exige certains documents.

Mais :

```text
OnboardingRequirement
```

référence les types requis.

Les `SupplierDocument` restent des objets indépendants.

---

# 172. Relationship between Onboarding and Compliance

Même principe :

```text
onboarding requires compliance state
```

sans embarquer les checks.

---

# 173. Relationship between Relationship and Contract

Une SupplierRelationship peut référencer plusieurs Contracts.

```text
SupplierRelationship
1
│
└── 0..* ContractReference
```

mais Contract reste externe à PySRMKit.

---

# 174. Relationship between Relationship and Procurement

Procurement peut demander :

```text
eligible suppliers
```

à partir des Relationships qualifiées.

Il ne possède pas la Relationship.

---

# 175. Relationship between Supplier and Accounting

Accounting peut associer :

```text
SupplierId
↔ VendorAccountId
```

dans un mapping externe.

---

# 176. Relationship to Agents

Agents consomment des projections et use cases.

Ils ne naviguent pas directement l'object graph.

---

# 177. ERD — complete conceptual view

```text
                                      ┌─────────────────────────┐
                                      │        Supplier         │
                                      │      Aggregate Root     │
                                      └────────────┬────────────┘
                                                   │
          ┌───────────────┬───────────────┬────────┼───────────────┬───────────────┐
          │               │               │        │               │               │
          ▼               ▼               ▼        ▼               ▼               ▼
 ExternalIdentifier   Contact         Location   Document      Certification   Relationship
      (VO)            (Entity)        (Entity)   (Entity?)       (Entity?)      (AR)
                                          │                                      │
                                          ▼                                      │
                                       Address                                    │
                                         (VO)                                     │
                                                                                  │
                                      ┌───────────────────────────────────────────┤
                                      │                                           │
                                      ▼                                           ▼
                                 Qualification                                Lifecycle
                                     (AR)                                       (VO/state)
                                      │
                              ┌───────┼────────┐
                              ▼       ▼        ▼
                            Scope   Status   Decision
                            (VO)    (VO)      (VO)

Relationship also references:
    ComplianceCheck*
    RiskAssessment*
    Assessment*
    Incident*
    Segment
```

---

# 178. ERD — aggregate-only view

```text
Supplier AR
   │
   ├────────────► SupplierRelationship AR
   │                   │
   │                   ├────────► SupplierQualification AR
   │                   ├────────► RiskAssessment AR
   │                   ├────────► SupplierAssessment AR
   │                   └────────► SupplierIncident AR
   │
   ├────────────► SupplierAssessment AR
   ├────────────► RiskAssessment AR
   └────────────► SupplierIncident AR
```

Les lignes représentent des références métier, pas des ownerships forts.

---

# 179. Domain Relationship Matrix

| Source | Target | Relationship type | Ownership | Aggregate crossing |
|---|---|---|---|---:|
| Supplier | ExternalIdentifier | contains | Owns | No |
| Supplier | SupplierContact | contains | Owns | No |
| Supplier | SupplierLocation | contains | Owns | No |
| Supplier | SupplierRelationship | participates in | References | Yes |
| Relationship | Supplier | identifies external party | References | Yes |
| Relationship | InternalOrganization | context | References | External context |
| Relationship | Qualification | contextual relationship | References | Yes |
| Relationship | RiskAssessment | contextual relationship | References | Yes |
| Relationship | ComplianceCheck | contextual relationship | References | Maybe |
| Qualification | QualificationScope | contains | Owns | No |
| Assessment | Question/Answer | contains | Owns | No |
| RiskAssessment | RiskScore | contains | Owns | No |
| Document | DocumentReference | contains | Owns | No |
| Certification | CertificationScope | contains | Owns | No |

---

# 180. Relationship tests

Les relations doivent être testées via comportements.

Exemples :

```text
same Supplier can have multiple Relationships
```

```text
offboarding Relationship A
does not offboard Relationship B
```

```text
Qualification belongs to a specific scope
```

```text
RiskAssessment history remains independent
```

---

# 181. Aggregate boundary tests

Exemple :

```text
Supplier changes master name
without loading qualifications
```

Cela prouve que Qualification n'appartient pas au Supplier Aggregate.

---

# 182. Relationship isolation test

```text
suspend relationship A
```

ne doit pas modifier :

```text
relationship B
```

du même Supplier.

---

# 183. Qualification isolation test

Une Qualification Cybersecurity rejetée ne doit pas automatiquement invalider :

```text
IT Consulting qualification
```

si les scopes sont différents.

---

# 184. Multi-organization test

```text
Supplier S
Relationship R1 with Org A = ACTIVE
Relationship R2 with Org B = SUSPENDED
```

doit être valide.

---

# 185. Document reuse test

Un document global peut éventuellement satisfaire plusieurs requirements.

Le modèle ne doit pas forcer une duplication physique du fichier.

---

# 186. Certification scope test

Une certification scope à Location A ne doit pas être automatiquement considérée valide pour Location B.

---

# 187. Risk temporal test

Deux RiskAssessments à deux dates différentes restent deux objets distincts.

---

# 188. Incident effect test

Créer un Incident ne doit pas directement changer une Qualification sans policy/use case explicite.

---

# 189. Domain event relationship tests

Un cross-aggregate effet doit être observable par événement.

Exemple :

```text
SupplierIncidentReported
```

peut déclencher un use case de risk reassessment.

---

# 190. Architecture test — no aggregate graph

Éviter que :

```text
Supplier
```

importe directement :

```text
RiskAssessment
SupplierAssessment
SupplierIncident
```

si ces objets sont dans des aggregates séparés.

---

# 191. Repository test implication

Chaque Aggregate Root confirmé doit avoir un contract test de repository.

---

# 192. Query projection implication

Les vues jointes appartiennent au Query side.

Exemple :

```text
SupplierRelationshipSummary
```

peut agréger :

- Supplier name ;
- lifecycle ;
- qualification count ;
- current risk level.

Sans modifier les aggregates.

---

# 193. ERD documentation convention

Tout diagramme relationnel futur doit préciser son niveau :

```text
DOMAIN ERD
PERSISTENCE ERD
INTEGRATION ERD
READ MODEL ERD
```

pour éviter les confusions.

---

# 194. Domain ERD naming

Utiliser les noms métier :

```text
SupplierRelationship
Qualification
RiskAssessment
```

pas les futurs noms de tables :

```text
tbl_supplier_rel
qualif_hdr
risk_fact
```

---

# 195. Foreign-key thinking anti-pattern

Éviter de raisonner :

```text
"Should this have a foreign key?"
```

avant de poser :

```text
"What does this relationship mean?"
```

---

# 196. Many-to-many caution

Une relation many-to-many peut cacher une Entity métier.

Exemple :

```text
Supplier × InternalOrganization
```

n'est pas une simple join table :

```text
SupplierRelationship
```

porte du comportement.

---

# 197. Association Entity pattern

`SupplierRelationship` est un exemple de relation devenue Entity parce que l'association possède sa propre sémantique.

Ce concept est plus important que le fait technique d'avoir une table d'association.

---

# 198. Qualification as association entity

Même idée :

```text
Supplier/Relationship × Scope
```

devient :

```text
SupplierQualification
```

car l'association possède :

- status ;
- validity ;
- history ;
- evidence.

---

# 199. Temporal association

Une relation métier peut être valable sur une période.

Candidats :

```text
SupplierRelationship
Qualification
Certification
```

Le `DateRange` devient alors un Value Object commun.

---

# 200. Relationship validity period

`SupplierRelationship` pourrait porter :

```text
started_at
ended_at?
```

en plus de son lifecycle.

Le lifecycle reste plus riche qu'un simple DateRange.

---

# 201. Soft historical links

Les historiques doivent rester interprétables même si les objets référencés ont changé.

Exemple :

Une Qualification historique doit continuer à référencer le scope appliqué au moment de la décision.

---

# 202. Snapshot vs live reference

Question importante :

```text
Should historical decisions reference current policy inputs
or snapshot them?
```

Pour audit :

```text
decision-critical inputs
should often be snapshotted or evidenced.
```

---

# 203. Policy relationship

Policies ne sont pas possédées par les Entities.

Elles sont injectées/utilisées lors des décisions.

Exemple :

```text
QualificationPolicy
```

ne fait pas partie de :

```text
SupplierQualification state
```

---

# 204. Domain Service relationship

Même principe.

Un Domain Service orchestre éventuellement plusieurs concepts mais n'est pas "owned" par eux.

---

# 205. Repository relationship

Repository appartient à la boundary architecture.

Il ne fait pas partie de l'ERD.

---

# 206. Event relationship

DomainEvent représente une sortie comportementale de l'Aggregate.

Il n'est pas une child entity classique.

---

# 207. Audit relationship

AuditRecord peut référencer :

```text
aggregate_id
event_id
actor_reference
```

mais il appartient potentiellement à un audit subsystem séparé.

---

# 208. Relationship with History

L'historisation ne doit pas créer :

```text
SupplierHistory
```

comme God Object contenant tout.

Les histoires locales peuvent rester proches des aggregates et events.

---

# 209. Domain event stream by aggregate

Possible conceptual view :

```text
SupplierRelationshipId = R1

SupplierInvited
SupplierOnboardingStarted
SupplierQualified
SupplierActivated
SupplierSuspended
SupplierReactivated
```
---

# 210. Audit stream vs Event Sourcing

Cette chronologie n'implique pas :

```text
Event Sourcing
```

Le state courant peut rester persisté directement.

---

# 211. Relationship scope summary

## Supplier-global

```text
Identity
ExternalIdentifiers
Contacts
Locations
Organization structure
Global capabilities
Documents/certifications where intrinsic
```

## Relationship-specific

```text
Lifecycle
Qualification
Segmentation
Relationship activation/suspension
Compliance decisions
Risk appetite decisions
```

## Potentially both

```text
Documents
Certifications
Assessments
Risk
Performance
Incidents
```

---

# 212. Aggregate boundary summary

```text
Supplier
    master truth

SupplierRelationship
    relationship truth

SupplierQualification
    qualification truth

SupplierAssessment
    assessment truth

RiskAssessment
    risk observation/assessment truth

SupplierIncident
    incident truth
```

---

# 213. Key modeling decision #1

> **SupplierRelationship becomes a first-class Entity and strong Aggregate Root candidate.**

Cette décision structure :

- multi-organisation ;
- lifecycle ;
- qualification ;
- segmentation.

---

# 214. Key modeling decision #2

> **Operational lifecycle is primarily relationship-scoped.**

Le Supplier global n'est pas "suspended" universellement par défaut.

---

# 215. Key modeling decision #3

> **Qualification is relationship/scope-specific, not globally attached to Supplier.**

---

# 216. Key modeling decision #4

> **Supplier evidence and relationship decisions are distinct.**

Exemple :

```text
SupplierDocument
≠
ComplianceResult
```

---

# 217. Key modeling decision #5

> **Cross-aggregate references use identifiers instead of deep object graphs.**

---

# 218. Key modeling decision #6

> **Supplier remains small enough to represent canonical master identity.**

Il ne devient pas le container de tout le Supplier Domain.

---

# 219. Key modeling decision #7

> **Scorecards and 360 views are projections by default.**

Elles ne déterminent pas les Aggregate boundaries.

---

# 220. Design Concepts Applied

## DDD

```text
Aggregate
Aggregate Root
Entity
Value Object
Repository
Bounded Context
Association Entity
Domain Event
Domain Policy
Anti-Corruption Layer
```

## Principles

```text
Encapsulation
Information Hiding
High Cohesion
Low Coupling
Separation of Concerns
Dependency Inversion
KISS
YAGNI
```

## Architecture

```text
Aggregate reference by ID
Eventual consistency
Application orchestration
CQRS-friendly read models
```

---

# 221. Learning Map — SupplierRelationship

```text
Problem
    same Supplier behaves differently per internal organization
        │
        ▼
Modeling pressure
    association has state and lifecycle
        │
        ▼
DDD
    Association Entity
    Aggregate Root candidate
        │
        ▼
Object
    SupplierRelationship
```

---

# 222. Learning Map — Qualification

```text
Problem
    eligibility varies by scope
        │
        ▼
Relationship
    SupplierRelationship × QualificationScope
        │
        ▼
DDD
    Entity / Aggregate
        │
        ▼
Object
    SupplierQualification
```

---

# 223. Learning Map — Aggregate References

```text
Problem
    avoid large object graph
        │
        ▼
DDD principle
    aggregate boundaries
        │
        ▼
Technique
    reference by typed ID
        │
        ▼
Benefit
    lower coupling + independent transactions
```

---

# 224. Learning Map — Eventual Consistency

```text
Problem
    one business action influences several aggregates
        │
        ▼
Avoid
    one giant transaction graph
        │
        ▼
Approach
    Domain Event
    + Application orchestration
        │
        ▼
Consistency
    eventual where acceptable
```

---

# 225. Learning Map — Association Entity

```text
Supplier
    ×
InternalOrganization
        │
        ▼
Not just a join
        │
        ▼
SupplierRelationship
        │
        ├── lifecycle
        ├── status
        ├── segmentation
        └── qualification context
```

---

# 226. Anti-pattern — Bidirectional graph everywhere

À éviter :

```text
Supplier
    contains Relationships
        contain Supplier
            contains Relationships
                ...
```

---

# 227. Anti-pattern — ORM cascade determines aggregate

Un `cascade="all"` SQLAlchemy ne définit pas une Aggregate boundary.

---

# 228. Anti-pattern — database join = domain object

Certaines join tables sont techniques.

D'autres associations deviennent des Entities.

Le métier décide.

---

# 229. Anti-pattern — one aggregate per table

Même rappel.

Persistence structure ≠ aggregate structure.

---

# 230. Anti-pattern — one transaction for whole supplier universe

Ne pas tenter de rendre atomiques :

```text
Supplier
Relationship
Qualification
Risk
Performance
Incident
```

simultanément par défaut.

---

# 231. Anti-pattern — generic owner polymorphism

Éviter un modèle universel :

```text
owner_type
owner_id
```

avant besoin réel.

---

# 232. Anti-pattern — global supplier status

Éviter de mettre :

```text
ACTIVE
SUSPENDED
```

uniquement sur Supplier si la relation varie par organisation.

---

# 233. Anti-pattern — duplicate scope

Éviter de stocker le même organization/category/country dans plusieurs objets si l'un peut le fournir sans ambiguïté.

---

# 234. Anti-pattern — direct cross-aggregate mutation

Éviter :

```text
incident.resolve()
    directly calls
qualification.revoke()
```

Préférer orchestration explicite.

---

# 235. Testing checklist — relationships

```text
[ ] cardinality is meaningful
[ ] ownership is explicit
[ ] aggregate crossing is intentional
[ ] references use IDs where appropriate
[ ] global vs relationship scope is explicit
[ ] cross-aggregate effects are orchestrated
[ ] history is preserved
[ ] projections do not become aggregates accidentally
```

---

# 236. Review checklist — ERD

```text
[ ] Is this a domain ERD or persistence ERD?
[ ] Does each relationship have business meaning?
[ ] Is many-to-many hiding an association entity?
[ ] Is one-to-many really ownership?
[ ] Does the child have an independent lifecycle?
[ ] Could this relation cross aggregate boundaries?
[ ] Does navigation create an unnecessary object graph?
[ ] Is the scope global or relationship-specific?
```

---

# 237. Proposed repository boundaries

Repositories likely:

```text
SupplierRepository
SupplierRelationshipRepository
SupplierQualificationRepository
SupplierAssessmentRepository
RiskAssessmentRepository
SupplierIncidentRepository
```

Conditional:

```text
SupplierOnboardingRepository
SupplierDocumentRepository
SupplierCertificationRepository
ComplianceCheckRepository
```

---

# 238. Query boundaries

Cross-domain read operations should be exposed through queries/projections such as:

```text
GetSupplier360
ListQualifiedSuppliers
GetRelationshipRiskSummary
ListExpiringDocuments
GetSupplierScorecard
```

---

# 239. Read model example

```text
SupplierRelationshipSummary
├── SupplierId
├── supplier_name
├── relationship_id
├── organization_id
├── lifecycle_stage
├── qualification_summary
├── current_risk_level
├── compliance_status
└── segment
```

This is a projection.

Not an Aggregate Root.

---

# 240. Future ERDs

Plusieurs ERDs spécialisés pourront être créés :

```text
06A — Supplier Core ERD
06B — Qualification ERD
06C — Compliance & Risk ERD
06D — Assessment ERD
06E — Performance & Incident ERD
```

si la complexité le justifie.

---

# 241. Open Question — legal entity modeling

À préciser :

```text
Should each legal entity be its own Supplier?
```

Recommandation actuelle :

```text
yes, when it can independently participate in supplier relationships.
```

---

# 242. Open Question — global Supplier state

Faut-il un master lifecycle séparé ?

Probablement seulement :

```text
ACTIVE_MASTER / ARCHIVED
```

ou une notion similaire si le besoin apparaît.

Ne pas dupliquer le lifecycle relationnel.

---

# 243. Open Question — document aggregate boundary

Le document possède-t-il assez de lifecycle pour être Aggregate Root ?

À confirmer via use cases :

- submit ;
- verify ;
- reject ;
- supersede ;
- expire.

---

# 244. Open Question — certification aggregate boundary

Même question :

- issue ;
- verify ;
- renew ;
- revoke ;
- expire.

---

# 245. Open Question — compliance aggregate

Un `ComplianceCheck` suffit-il ?

Ou faut-il :

```text
ComplianceCase
```

comme Aggregate Root englobant plusieurs checks ?

Pas encore démontré.

---

# 246. Open Question — risk subject

Faut-il deux types explicites :

```text
SupplierRiskAssessment
RelationshipRiskAssessment
```

ou une structure commune ?

Décision différée pour éviter une abstraction prématurée.

---

# 247. Open Question — assessment subject

Même question pour :

```text
SupplierAssessment
RelationshipAssessment
QualificationAssessment
```

---

# 248. Open Question — performance scope

La Performance est-elle :

- Supplier-level ;
- Relationship-level ;
- Contract-level ;
- Category-level ?

Probablement plusieurs scopes.

Le modèle doit éviter un generic scope prématuré.

---

# 249. Open Question — capability relationship

Si Capability devient vérifiée/historisée, elle pourrait devenir :

```text
SupplierCapability
```

Entity séparée.

Pour le MVP :

```text
CapabilityCode
```

reste suffisant.

---

# 250. Decisions for `07`

Le prochain document devra formaliser les invariants découlant de ces relations.

Exemples :

```text
a relationship references exactly one Supplier
a qualification belongs to one relationship/scope
relationship lifecycle transitions are controlled
a qualification scope cannot be empty
offboarding one relationship does not delete Supplier
cross-aggregate mutation is forbidden
```

---

# 251. Proposed invariant ownership

| Invariant | Owner |
|---|---|
| canonical supplier identity | Supplier |
| external identifier consistency | Supplier |
| location identity | Supplier aggregate |
| relationship lifecycle | SupplierRelationship |
| qualification scope validity | SupplierQualification |
| qualification status transition | SupplierQualification |
| risk assessment validity | RiskAssessment |
| assessment consistency | SupplierAssessment |
| incident lifecycle | SupplierIncident |

---

# 252. Aggregate event ownership

```text
Supplier
    emits SupplierCreated / SupplierInformationUpdated

SupplierRelationship
    emits SupplierInvited / Activated / Suspended / Offboarded

SupplierQualification
    emits QualificationRequested / Qualified / Rejected / Revoked

RiskAssessment
    emits RiskAssessed / RiskChanged

SupplierAssessment
    emits AssessmentCompleted

SupplierIncident
    emits IncidentReported / IncidentResolved
```

Names remain candidates where not previously confirmed.

---

# 253. Domain ERD North Star

```text
                         Supplier
                      canonical identity
                            │
                            │ 1
                            ▼ *
                   SupplierRelationship
                    our relationship
                            │
              ┌─────────────┼──────────────┐
              │             │              │
              ▼             ▼              ▼
       Qualification     Risk         Compliance
              │
              ▼
            Scope

Supplier-global evidence:
Documents
Certifications

Cross-cutting observations:
Assessments
Performance
Incidents

Derived views:
Scorecards
Supplier360
```

---

# 254. Final relationship philosophy

PySRMKit doit privilégier :

```text
explicit relationships
over
generic polymorphism
```

```text
small aggregates
over
deep object graphs
```

```text
typed IDs
over
cross-aggregate object references
```

```text
application orchestration
over
hidden cross-aggregate mutation
```

```text
domain ERD
over
database-first thinking
```

---

# 255. Conclusion

Le modèle relationnel de PySRMKit s'organise désormais autour d'une distinction fondamentale :

```text
Supplier
    = canonical external party

SupplierRelationship
    = how an internal organization works with that Supplier
```

Cette séparation permet de modéliser correctement :

```text
multi-organization
lifecycle
qualification
segmentation
risk
compliance
```

sans imposer ces états globalement au Supplier.

La première proposition de frontières d'Aggregate est :

```text
Supplier
SupplierRelationship
SupplierQualification
SupplierAssessment
RiskAssessment
SupplierIncident
```

avec plusieurs objets encore conditionnels :

```text
SupplierOnboarding
SupplierDocument
SupplierCertification
ComplianceCheck
```

Le modèle adopte également une règle structurante :

> **Within an Aggregate: object references and immediate consistency.**

> **Across Aggregates: typed identifiers, explicit orchestration and eventual consistency when acceptable.**

Enfin, l'ERD reste volontairement un **modèle métier**, pas un schéma de base de données.

Le prochain document devra transformer ces relations en règles exécutables :

> **`07_PYSRMKIT_DOMAIN_INVARIANTS_AND_BUSINESS_RULES.md`**

Il devra définir précisément :

- les invariants ;
- les guards ;
- les préconditions ;
- les transitions autorisées ;
- les décisions métier ;
- les erreurs métier ;
- les policies ;
- la frontière entre invariant universel et règle configurable.