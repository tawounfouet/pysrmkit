# PySRMKit — Domain Invariants and Business Rules

**Document :** `07_PYSRMKIT_DOMAIN_INVARIANTS_AND_BUSINESS_RULES.md`  
**Projet :** PySRMKit  
**Domaine :** Supplier Relationship Management  
**Type :** Domain Modeling — Invariants, Guards, Policies, Decisions et Domain Errors  
**Statut :** Baseline de règles métier pré-implémentation  
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

---

# 1. Objet du document

Ce document formalise les **invariants et règles métier du Supplier Domain** de PySRMKit.

Il précise :

- quelles règles doivent toujours être vraies ;
- quelles règles sont locales à un Aggregate ;
- quelles règles traversent plusieurs Aggregates ;
- quelles règles dépendent d’un contexte externe ;
- quelles validations appartiennent aux Value Objects ;
- quelles préconditions appartiennent aux use cases ;
- quelles décisions doivent être exprimées par des Policies ;
- quelles erreurs relèvent du Domain ;
- quels comportements sont interdits ;
- comment protéger les frontières définies dans le `06`;
- comment préparer le `08` sans déplacer la logique métier dans les Handlers.

Le principe directeur est :

> **Le Domain protège la vérité métier qu’il possède.  
> L’Application orchestre les faits nécessaires à cette vérité.**

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
06 — Relationships & ERD
        │
        ▼
07 — INVARIANTS & BUSINESS RULES   ← ce document
        │
        ▼
08 — Commands, Queries & Use Cases
```

Le `07` transforme donc :

```text
objects
+
relationships
+
aggregate boundaries
```

en :

```text
valid states
+
valid transitions
+
guards
+
decisions
+
errors
```

---

# 3. Convention pédagogique appliquée

Pour chaque règle importante, le raisonnement suit autant que possible :

```text
BUSINESS RULE
    │
    ▼
RULE TYPE
    │
    ├── Value Object validation
    ├── Aggregate invariant
    ├── Guard
    ├── Policy
    ├── Application precondition
    └── External fact
    │
    ▼
OWNER
    │
    ▼
FAILURE MODE
    │
    ▼
TEST
```

L’objectif est de pouvoir reconnaître progressivement :

```text
"Cette règle appartient à l'Aggregate."
```

ou :

```text
"Cette règle nécessite une Policy."
```

sans devoir réciter une définition théorique.

---

# 4. Invariant — définition retenue

Un **invariant** est une règle qui doit rester vraie pour qu’un objet ou un Aggregate reste dans un état métier valide.

Exemple :

```text
A SupplierQualification cannot be QUALIFIED
without a valid QualificationScope.
```

Un invariant n’est pas :

```text
une validation UI
une contrainte HTTP
une règle de formulaire
une limitation SQL
```

même si ces couches peuvent également la renforcer.

---

# 5. Aggregate invariant

Un Aggregate Root doit pouvoir garantir ses propres invariants **sans charger un graphe arbitraire d’autres Aggregates**.

Exemple :

```text
SupplierRelationship
```

peut garantir :

```text
OFFBOARDED → ACTIVE
```

est interdit.

Il ne peut pas garantir seul :

```text
all required compliance checks across external evidence are valid
```

si ces faits appartiennent à d’autres Aggregates.

---

# 6. Value Object validation

Un Value Object protège principalement :

```text
validity of the value itself
```

Exemples :

```text
CountryCode
ExternalIdentifier
QualificationScope
RiskScore
DateRange
Percentage
EmailAddress
```

Une instance invalide ne devrait idéalement pas pouvoir être construite.

---

# 7. Guard — définition retenue

Un Guard contrôle si une opération métier peut être exécutée **dans l’état courant**.

Exemple :

```text
SupplierQualification.apply_decision(...)
```

peut vérifier :

```text
qualification.status == PENDING
```

avant d’appliquer la décision.

---

# 8. Policy — définition retenue

Une Policy exprime une règle métier :

- variable ;
- configurable ;
- dépendante de plusieurs faits ;
- ou sans owner naturel dans une seule Entity.

Exemples :

```text
QualificationPolicy
ActivationPolicy
CompliancePolicy
RiskPolicy
SegmentationPolicy
```

---

# 9. Domain Decision

Une Policy devrait souvent produire un résultat explicite :

```text
QualificationDecision
ActivationDecision
ComplianceDecision
RiskDecision
SegmentationDecision
```

plutôt que :

```text
True / False
```

afin de conserver :

```text
decision
reasons
failed_rules
evidence summary
```

---

# 10. Application precondition

Une précondition applicative concerne principalement :

```text
finding required aggregates
checking cross-instance uniqueness
collecting external facts
authorization context
```

Exemple :

```text
Supplier exists before creating SupplierRelationship.
```

Le nouvel Aggregate `SupplierRelationship` ne peut pas vérifier seul l’existence du Supplier.

---

# 11. External fact

Un fait provenant de l’extérieur :

```text
sanctions screening result
company registry status
tax validation
credit/risk provider data
```

n’est pas lui-même une décision métier.

Il constitue :

```text
input/evidence
```

pour une Policy ou un Aggregate.

---

# 12. Rule placement heuristic

Question 1 :

> Cette règle peut-elle être évaluée uniquement avec l’état interne de l’Aggregate ?

Si oui :

```text
Aggregate invariant / guard
```

Question 2 :

> La règle dépend-elle de plusieurs faits métier ou d’une stratégie variable ?

Si oui :

```text
Domain Policy
```

Question 3 :

> La règle consiste-t-elle surtout à trouver des données ou coordonner plusieurs Aggregates ?

Si oui :

```text
Application Layer
```

---

# 13. Première règle globale — Supplier ≠ SupplierRelationship

Invariant conceptuel fondamental :

```text
Supplier
```

représente :

```text
canonical supplier identity
```

alors que :

```text
SupplierRelationship
```

représente :

```text
our relationship with that Supplier
in an internal organizational context
```

Par conséquent :

```text
relationship lifecycle
qualification
segment
activation/suspension
```

ne doivent pas être assimilés à l’identité globale du Supplier.

---

# 14. Deuxième règle globale — relationship-scoped decisions stay relationship-scoped

Une décision sur :

```text
Relationship R1 / Org A
```

ne doit pas modifier automatiquement :

```text
Relationship R2 / Org B
```

du même Supplier.

Exemple :

```text
R1 = SUSPENDED
```

n’implique pas :

```text
R2 = SUSPENDED
```

sans règle explicite de propagation.

---

# 15. Troisième règle globale — cross-Aggregate reference by ID

Les Aggregates se référencent prioritairement avec :

```text
typed IDs
```

et non via graphe d’objets complet.

Cette règle réduit le risque de créer :

```text
implicit distributed aggregate
```

---

# 16. Quatrième règle globale — historical facts are not casually deleted

Pour les objets historiques :

```text
Qualification
Assessment
RiskAssessment
Incident
ComplianceCheck
PerformanceMeasurement
```

la stratégie métier privilégie :

```text
new record
status transition
supersession
revocation
expiration
```

plutôt que :

```text
hard delete
```

---

# 17. Cinquième règle globale — evidence ≠ decision

Exemples :

```text
SupplierDocument
SupplierCertification
AssessmentAnswer
ComplianceCheck
RiskObservation
```

sont des faits ou preuves.

Ils ne deviennent pas automatiquement :

```text
Qualified
Compliant
Low Risk
Active
```

sans décision explicite.

---

# 18. SupplierId invariant

`SupplierId` doit identifier un Supplier de manière stable.

Règles :

```text
non-empty
immutable
not interchangeable semantically with other IDs
```

Un `SupplierId` ne doit pas être utilisé là où un :

```text
QualificationId
RelationshipId
AssessmentId
```

est attendu.

---

# 19. SupplierIdentity invariant

`SupplierIdentity` doit rester cohérente.

Candidates :

```text
legal_name required
country/jurisdiction valid when present
legal identifiers structurally valid
```

Le modèle ne doit pas accepter une identité complètement vide.

---

# 20. ExternalIdentifier invariant

Un `ExternalIdentifier` candidate structure :

```text
scheme/type
value
issuer/jurisdiction?
```

Règles :

```text
type required
value required
normalized representation explicit
```

---

# 21. ExternalIdentifier uniqueness — local

À l’intérieur d’un `Supplier` :

```text
same exact ExternalIdentifier
```

ne doit pas être ajouté deux fois.

Owner :

```text
Supplier Aggregate
```

---

# 22. ExternalIdentifier uniqueness — global

La règle :

```text
one canonical external identifier should not map to conflicting Suppliers
```

traverse plusieurs Aggregates.

Elle nécessite :

```text
Repository lookup
+
Application orchestration
```

et éventuellement une contrainte technique de persistence.

Elle n’appartient pas uniquement à un Supplier isolé.

---

# 23. SupplierContact invariant

Candidates :

```text
contact id stable
contact belongs to one Supplier Aggregate
at least one meaningful communication identity if required
```

La validité des champs :

```text
EmailAddress
PhoneNumber
```

appartient aux Value Objects correspondants.

---

# 24. EmailAddress invariant

Un `EmailAddress` doit protéger sa validité structurale selon la règle retenue.

Éviter d’introduire une validation RFC complète si elle n’est pas nécessaire.

KISS s’applique.

---

# 25. SupplierLocation invariant

Une `SupplierLocation` conserve :

```text
stable identity
address value
activation/deactivation state if modeled
```

Un changement d’adresse ne doit pas nécessiter de changer l’identité de la Location.

---

# 26. Address invariant

Une `Address` est un Value Object.

Les règles dépendent de son niveau de structuration.

Le Core générique ne doit pas imposer une adresse française.

---

# 27. CountryCode invariant

Recommandation :

```text
ISO-like normalized country code
```

Un `CountryCode` ne doit pas encoder des règles spécifiques à un seul pays dans le type générique.

---

# 28. CategoryCode invariant

Un `CategoryCode` représente une référence de taxonomie.

Le Core doit pouvoir manipuler :

```text
external taxonomy
internal taxonomy
```

sans supposer une source particulière.

---

# 29. SupplierCapability invariant

Si `SupplierCapability` possède une identité/lifecycle :

```text
capability code required
status valid
```

Si elle reste Value Object :

```text
equality by value
```

La décision finale dépendra de l’implémentation réelle.

---

# 30. Supplier aggregate invariant summary

Le Supplier Aggregate protège au minimum :

```text
canonical identity
local identifier uniqueness
contact/location ownership
category/capability consistency
```

Il ne protège pas directement :

```text
relationship lifecycle
relationship qualification
relationship activation
cross-organization rules
```

---

# 31. SupplierRelationship identity invariant

Une `SupplierRelationship` doit référencer exactement :

```text
1 SupplierId
1 InternalOrganizationId
```

et conserver son :

```text
SupplierRelationshipId
```

stable.

---

# 32. Relationship uniqueness rule

Candidate :

```text
one current relationship
per Supplier + InternalOrganization
```

selon type de relationship.

Cette règle traverse plusieurs instances.

Owner :

```text
Application + Repository-assisted rule
```

pas uniquement un Aggregate isolé.

---

# 33. Relationship lifecycle invariant

La lifecycle state appartient au :

```text
SupplierRelationship
```

et non au Supplier canonique.

---

# 34. Reference lifecycle states

Baseline :

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

`REJECTED` appartient plutôt à une décision de qualification/review et doit être traité avec prudence pour ne pas mélanger :

```text
relationship lifecycle
```

et :

```text
qualification outcome
```

---

# 35. Lifecycle state representation

Baseline recommandée :

```text
Enum
+
explicit transition rules
```

Pas de GoF State Pattern tant que le comportement ne le justifie pas.

---

# 36. Lifecycle transition invariant

Une transition n’est valide que si :

```text
source stage
+
target stage
+
required business context
```

sont compatibles.

---

# 37. Lifecycle transition table — initial reference

Le tableau exact pourra évoluer, mais la première baseline peut utiliser :

| From | To | Baseline |
|---|---|---|
| DISCOVERED | PROSPECTIVE | allowed |
| DISCOVERED | INVITED | possibly allowed by business policy |
| PROSPECTIVE | INVITED | allowed |
| INVITED | ONBOARDING | allowed |
| ONBOARDING | UNDER_REVIEW | allowed |
| UNDER_REVIEW | QUALIFIED | allowed after qualification decision |
| QUALIFIED | ACTIVE | allowed after activation decision |
| ACTIVE | SUSPENDED | allowed with reason |
| ACTIVE | BLOCKED | allowed with reason |
| ACTIVE | INACTIVE | allowed if business semantics require |
| SUSPENDED | ACTIVE | revalidation required |
| BLOCKED | ACTIVE | exceptional / explicit revalidation |
| any valid live state | OFFBOARDED | allowed with reason/policy |
| OFFBOARDED | ACTIVE | forbidden by default |

Le code ne doit pas être généré aveuglément depuis ce tableau avant validation finale des use cases.

---

# 38. No arbitrary lifecycle mutation

Interdit :

```python
relationship.stage = SupplierLifecycleStage.ACTIVE
```

depuis l’extérieur.

Préférer des comportements :

```text
invite()
start_onboarding()
mark_qualified()
activate()
suspend()
offboard()
```

qui protègent les guards.

---

# 39. INVITED guard

Une Relationship ne devrait devenir `INVITED` que depuis un état autorisé.

L’invitation doit être un fait relationnel.

---

# 40. ONBOARDING guard

`ONBOARDING` suppose que la relation a franchi les étapes nécessaires selon le parcours retenu.

Le Handler ne doit pas forcer cet état directement.

---

# 41. UNDER_REVIEW guard

`UNDER_REVIEW` peut exiger :

```text
minimum onboarding readiness
```

si cette règle est retenue.

Si plusieurs facts externes sont nécessaires :

```text
OnboardingReadinessPolicy
```

peut devenir utile.

Ne pas l’introduire avant pression réelle.

---

# 42. QUALIFIED lifecycle guard

Important :

```text
relationship lifecycle QUALIFIED
```

ne doit être atteint qu’après une décision de qualification valide.

Le Relationship Aggregate ne doit pas recalculer lui-même toute la QualificationPolicy.

Il peut recevoir :

```text
QualificationDecision / qualification fact
```

et vérifier qu’elle permet la transition.

---

# 43. ACTIVE guard

L’activation est plus riche qu’un simple :

```text
status = ACTIVE
```

Elle peut dépendre de :

```text
qualification readiness
compliance readiness
risk readiness
document readiness
```

Par conséquent :

```text
ActivationPolicy
```

est la bonne abstraction si plusieurs faits sont nécessaires.

---

# 44. Activation decision invariant

Une `ActivationDecision` doit expliciter :

```textallowed
reasons
failed_rules
evaluated_at?
```

Si :

```text
allowed = False
```

`SupplierRelationship.activate(...)` doit refuser la transition.

---

# 45. SUSPENDED invariant

Une suspension doit conserver :

```text
reason
occurred_at
```

ou information équivalente si le modèle l’exige.

Une suspension ne doit pas être indistinguable d’un simple état inactif.

---

# 46. BLOCKED invariant

`BLOCKED` représente une interdiction plus forte que `SUSPENDED` si cette différence est conservée.

Candidates :

```text
BLOCKED
    explicit prohibition / critical reason

SUSPENDED
    temporary hold / remediation possible
```

Le modèle ne doit pas avoir deux états synonymes.

---

# 47. Reactivation invariant

Une réactivation ne doit pas être :

```text
set ACTIVE
```

sans réévaluation.

Elle doit potentiellement vérifier :

```text
qualification still valid
compliance still acceptable
risk still acceptable
suspension/block reason resolved
```

---

# 48. OFFBOARDED invariant

`OFFBOARDED` est terminal par défaut.

L’offboarding :

```text
does not delete Supplier
does not delete evidence
does not erase history
```

---

# 49. Relationship segment invariant

`SupplierSegment` appartient prioritairement au contexte relationnel.

Le segment peut être :

```text
assigned
```

ou :

```text
calculated via SegmentationPolicy
```

mais ne doit pas être confondu avec l’identité du Supplier.

---

# 50. SupplierOnboarding invariant

Un `SupplierOnboarding` représente une progression métier.

Il ne doit pas devenir un workflow engine générique.

---

# 51. Onboarding ownership

Baseline :

```text
SupplierRelationship
    owns or references current onboarding
```

selon frontière finale.

La règle essentielle :

```text
onboarding is relationship-scoped
```

dans le premier modèle.

---

# 52. OnboardingRequirement invariant

Une exigence d’onboarding doit avoir :

```text
requirement identity/code
mandatory/optional semantics
status or satisfaction result
```

si ces dimensions sont réellement implémentées.

---

# 53. Onboarding completion invariant

Un onboarding ne peut être considéré complet si une exigence :

```text
mandatory
```

reste non satisfaite.

Cette règle appartient :

```text
Onboarding Aggregate/Entity
```

si toutes les requirements sont internes.

---

# 54. Onboarding progress

`OnboardingProgress` est plutôt :

```text
Domain Result / Projection
```

Il ne doit pas devenir la source de vérité si les requirements sont les données canoniques.

---

# 55. Onboarding vs workflow rule

Ces actions :

```text
assign reviewer
send reminder
wait 48h
escalate
```

ne sont pas des invariants du Supplier Domain.

Elles appartiennent :

```text
workflow/application orchestration
```

---

# 56. SupplierQualification identity invariant

Une Qualification possède :

```text
QualificationId
RelationshipId
QualificationScope
QualificationStatus
```

et conserve une identité stable dans le temps.

---

# 57. Qualification scope invariant

Une Qualification sans scope significatif est interdite.

Question toujours obligatoire :

> **Qualified for what?**

---

# 58. QualificationScope dimensions

Candidate dimensions :

```text
InternalOrganizationId?
CategoryCode?
CountryCode?
BusinessUnit?
Capability?
```

Le type doit représenter explicitement les dimensions retenues.

Éviter :

```text
dict[str, Any]
```

comme cœur du domaine.

---

# 59. Qualification is not global by default

Éviter :

```text
supplier.is_qualified = True
```

sans scope.

Un Supplier peut être :

```text
qualified for Category A
not qualified for Category B
qualified in Country X
not qualified in Country Y
```

---

# 60. Qualification uniqueness rule

Candidate :

```text
only one current Qualification
per Relationship + QualificationScope
```

La règle traverse plusieurs Qualification Aggregate instances.

Owner :

```text
Application + QualificationRepository lookup
```

---

# 61. Qualification status baseline

Candidate :

```text
PENDING
QUALIFIED
NOT_QUALIFIED
REVOKED
EXPIRED
```

Éviter de multiplier les états tant que les use cases ne les exigent pas.

---

# 62. Qualification initial status

Une Qualification nouvellement demandée commence dans :

```text
PENDING
```

ou état équivalent défini.

Elle ne naît pas directement `QUALIFIED`.

---

# 63. Qualification decision invariant

Une `QualificationDecision` doit représenter explicitement :

```text
outcome
reasons
failed_requirements?
evaluated_at?
```

---

# 64. QualificationPolicy invariant

La `QualificationPolicy` doit être déterministe pour les mêmes faits métier, hors dépendance explicitement temporelle.

Elle ne doit pas appeler directement :

```text
database
HTTP API
vendor SDK
```

Les faits sont collectés avant son évaluation.

---

# 65. Qualification input architecture

Préférer :

```text
QualificationContext
    assessment facts
    compliance facts
    risk facts
    evidence facts
```

si la policy devient riche.

Éviter un Handler avec une longue série de `if`.

---

# 66. Apply decision guard

`SupplierQualification.apply_decision(...)` n’accepte une décision que depuis un état autorisé.

Exemple :

```text
PENDING → QUALIFIED
PENDING → NOT_QUALIFIED
```

mais :

```text
REVOKED → QUALIFIED
```

ne doit pas être implicitement permis.

---

# 67. Qualification approval invariant

Un outcome `QUALIFIED` doit correspondre à :

```text
decision approved
```

Il ne doit pas être possible de créer :

```text
status = QUALIFIED
decision = rejected
```

---

# 68. Qualification rejection invariant

Un rejet doit conserver une explication exploitable.

Éviter :

```text
status = NOT_QUALIFIED
reason = None
```

si le métier exige la traçabilité.

---

# 69. Qualification revocation invariant

`REVOKED` signifie :

```text
qualification previously valid
+
explicit business decision
```

Il est distinct de :

```text
NOT_QUALIFIED
EXPIRED
```

---

# 70. Qualification expiration invariant

`EXPIRED` signifie :

```text
validity ended because time window ended
```

et non :

```text
explicit rejection
```

---

# 71. Qualification renewal rule

Une renewal peut :

```text
create a new Qualification
```

plutôt que réécrire silencieusement l’historique.

Baseline recommandée :

> préserver la traçabilité temporelle.

La mécanique exacte sera décidée lors de l’implémentation de renewal.

---

# 72. SupplierAssessment invariant

Une Assessment représente une évaluation identifiable dans le temps.

Elle conserve :

```text
AssessmentId
AssessmentType
subject/scope
questions snapshot
answers
scores
decision
```

selon périmètre implémenté.

---

# 73. Assessment question snapshot rule

Les questions utilisées pour une Assessment doivent pouvoir rester historiquement compréhensibles même si un template externe évolue.

Par défaut :

```text
AssessmentQuestion
```

est un snapshot/value object interne.

---

# 74. Assessment answer invariant

Une réponse doit correspondre à une question existante de l’Assessment.

Interdit :

```text
answer unknown_question_id
```

---

# 75. Mandatory answer guard

Si une question est mandatory :

```text
assessment.complete()
```

doit refuser tant qu’elle n’a pas de réponse valide.

---

# 76. Completed assessment guard

Une Assessment `COMPLETED` ne devrait plus accepter de nouvelles réponses sans workflow explicite de correction/réouverture.

---

# 77. AssessmentScore invariant

Un score doit respecter son domaine numérique.

Exemple :

```text
Percentage → 0..100
```

si le score utilise ce Value Object.

---

# 78. AssessmentDecision

Une Assessment peut produire un `AssessmentDecision`.

Ce résultat ne doit pas être confondu automatiquement avec :

```text
QualificationDecision
```

---

# 79. Assessment evidence rule

`EvidenceReference` pointe vers une preuve.

Il ne doit pas contenir arbitrairement :

```text
file bytes
external SDK object
```

---

# 80. SupplierDocument invariant

Un document possède :

```text
SupplierDocumentId
DocumentType
DocumentReference
verification status
validity metadata
```

selon implémentation.

---

# 81. DocumentReference invariant

`DocumentReference` identifie un contenu stocké ailleurs.

Le Domain ne doit pas dépendre d’un :

```text
S3 object
Azure Blob object
filesystem handle
```

---

# 82. Document validity invariant

Si :

```text
expiration_date
```

existe :

```text
expiration_date >= issue_date
```

si `issue_date` existe également.

---

# 83. Document verification invariant

`VERIFIED` suppose qu’une vérification a réellement eu lieu selon les règles applicables.

Le simple upload ne signifie pas :

```text
verified
```

---

# 84. Document supersession rule

Un nouveau document remplaçant un ancien ne doit pas effacer l’ancien historique.

Préférer :

```text
superseded
```

ou lien de remplacement.

---

# 85. SupplierCertification invariant

Une Certification possède :

```text
type
scope
issuer?
validity
status
```

selon modèle.

---

# 86. Certification scope rule

Une certification peut être :

```text
global supplier
site-specific
country-specific
capability/category-specific
```

Le scope doit rester explicite.

---

# 87. Certification expiration

Une certification expirée ne doit pas être considérée valide dans une décision sans règle explicite d’exception.

---

# 88. ComplianceRequirement invariant

Une Requirement est une référence métier identifiable :

```text
requirement code
domain/jurisdiction?
```

Elle ne doit pas être remplacée par une string opaque sans vocabulaire.

---

# 89. ComplianceCheck invariant

Un ComplianceCheck représente :

```text
a check actually performed
```

et doit conserver :

```text
requirement
subject/relationship
result
performed_at
evidence refs
```

selon implémentation.

---

# 90. ComplianceResult vs ComplianceDecision

Important :

```text
ComplianceResult
```

peut représenter le résultat d’un check.

```text
ComplianceDecision
```

peut agréger plusieurs checks/règles.

Ne pas les confondre.

---

# 91. CompliancePolicy

Une CompliancePolicy peut décider :

```text
COMPLIANT
NON_COMPLIANT
REVIEW_REQUIRED
```

selon les facts collectés.

Elle ne doit pas transformer directement les external provider payloads en état final sans mapping explicite.

---

# 92. Compliance evidence rule

Un provider externe disant :

```text
"match found"
```

est un fait.

La conséquence :

```text
block relationship
```

est une décision métier séparée.

---

# 93. RiskAssessment invariant

Un RiskAssessment est temporel.

Il doit conserver au minimum :

```text
subject
risk type
assessment time
score/level
source/evidence
```

selon modèle.

---

# 94. Risk history invariant

Une nouvelle évaluation de risque ne doit pas écraser silencieusement l’ancienne.

Préférer :

```text
append new RiskAssessment
```

puis calculer :

```text
CurrentRiskProfile
```

comme projection.

---

# 95. RiskScore invariant

Un `RiskScore` protège :

```text
numeric range
scale semantics
```

Le score doit préciser son échelle ou utiliser un type connu.

---

# 96. RiskLevel invariant

Un `RiskLevel` :

```text
LOW
MEDIUM
HIGH
CRITICAL
```

ou autre taxonomie doit rester un concept métier explicite.

---

# 97. RiskPolicy

Une RiskPolicy peut mapper :

```text
observations
scores
provider facts
```

vers :

```text
RiskDecision
```

Le mapping ne doit pas être dispersé dans les Handlers.

---

# 98. Risk decision vs relationship transition

Un `HIGH_RISK` outcome n’implique pas automatiquement :

```text
SUSPENDED
```

sauf si une Policy métier l’ordonne.

Cross-Aggregate consequence :

```text
event / subsequent command
```

---

# 99. SupplierIncident invariant

Un Incident possède :

```text
IncidentId
type
severity
status
occurred_at
subject
impact?
```

selon modèle.

---

# 100. Incident status transition

Candidate progression :

```text
OPEN
IN_REVIEW
RESOLVED
CLOSED
```

si ces états sont retenus.

Le détail doit être introduit uniquement lorsque les use cases Incident sont implémentés.

---

# 101. Incident resolution invariant

Un Incident ne doit pas être `RESOLVED` sans résolution/raison correspondante si le modèle exige cette information.

---

# 102. Incident effect rule

`ReportSupplierIncident` ne doit pas directement :

```text
mutate RiskAssessment
mutate Qualification
mutate SupplierRelationship
```

Le Domain Event :

```text
SupplierIncidentReported
```

permet à l’Application Layer d’orchestrer les conséquences.

---

# 103. PerformanceMeasurement invariant

Une mesure de performance doit contenir :

```text
metric
value
period/time
subject
```

---

# 104. Performance period invariant

Une période :

```text
start <= end
```

si les deux bornes existent.

---

# 105. Scorecard rule

`SupplierScorecard` est par défaut :

```text
projection / derived read model
```

et non owner des mesures de performance.

Il ne doit pas devenir la source canonique si ses données sont dérivées.

---

# 106. SupplierSegment invariant

Un segment est une classification.

Il peut être :

```text
manually assigned
policy-derived
```

mais le mode doit rester explicite si cela influence audit/explication.

---

# 107. SegmentationPolicy

Une SegmentationPolicy peut prendre :
```text
spend/dependency
risk
performance
strategic importance
```

et retourner :

```text
SegmentationDecision
```

Sans ces inputs, ne pas inventer une policy trop tôt.

---

# 108. Organization structure rule

Un Supplier représentant une legal entity doit rester distinct d’une structure de groupe si plusieurs legal entities existent.

Éviter :

```text
one giant Supplier object
containing every subsidiary as nested mutable state
```

---

# 109. Supplier-to-Supplier relationship

Parent/subsidiary links entre legal entities peuvent être modélisés comme relation dédiée.

Ils ne doivent pas être confondus avec :

```text
SupplierRelationship
```

qui représente la relation entre Supplier et organisation interne.

---

# 110. InternalOrganization invariant

`InternalOrganizationId` est une référence vers un autre contexte.

PySRMKit ne doit pas devenir le master data system des organisations internes.

---

# 111. Contract boundary rule

Les Contracts appartiennent à PyContractKit ou au Contract Domain.

PySRMKit peut conserver :

```text
ContractReference
```

mais ne doit pas importer le Contract Aggregate complet dans le Supplier Aggregate.

---

# 112. Procurement boundary rule

PySRMKit décrit :

```text
supplier relationship readiness
```

PyProcurementKit décrit :

```text
sourcing
purchase orders
procurement processes
```

Une décision Procurement ne doit pas être cachée dans SupplierRelationship.

---

# 113. Accounting boundary rule

Vendor account, invoices et payments appartiennent principalement au Finance/Accounting Domain.

PySRMKit peut référencer :

```text
VendorAccountId
```

si nécessaire.

---

# 114. Domain error — définition

Un Domain Error signifie :

> une opération demandée viole la vérité métier du domaine.

Exemples :

```text
InvalidLifecycleTransition
InvalidQualificationScope
QualificationDecisionNotAllowed
ActivationRequirementsNotMet
AssessmentIncomplete
```

---

# 115. Domain error ≠ Not Found

```text
SupplierNotFound
```

est généralement :

```text
Application Error
```

parce que le Domain Aggregate n’a jamais reçu l’objet à manipuler.

---

# 116. Domain error ≠ Infrastructure Error

```text
DatabaseUnavailable
HTTPTimeout
KafkaFailure
```

ne sont pas des Domain Errors.

---

# 117. Domain error naming

Préférer un nom exprimant la règle :

```text
InvalidLifecycleTransition
DuplicateExternalIdentifier
AssessmentIncomplete
```

à :

```text
BusinessRuleException
ValidationException
DomainException
```

trop génériques.

---

# 118. Error payload

Une Domain Error peut exposer :

```text
rule code
current state
requested action
reason
```

si utile.

Éviter d’en faire un transport HTTP.

---

# 119. Validation categories

Il faut distinguer :

```text
Structural Validation
Domain Invariant
Application Precondition
Policy Decision
Infrastructure Validation
```

---

# 120. Structural validation example

```text
CountryCode("FR")
```

est structurally valid.

Owner :

```text
CountryCode
```

---

# 121. Domain invariant example

```text
OFFBOARDED relationship cannot activate
```

Owner :

```text
SupplierRelationship
```

---

# 122. Application precondition example

```text
Supplier must exist before Relationship creation
```

Owner :

```text
CreateSupplierRelationshipHandler
```

via Repository.

---

# 123. Policy example

```text
relationship may activate only if qualification/compliance/risk readiness passes
```

Owner :

```text
ActivationPolicy
```

with Application collecting facts.

---

# 124. Infrastructure validation example

```text
database column max length
HTTP JSON schema
```

Owner :

```text
Adapter/interface
```

unless the same constraint is truly a business rule.

---

# 125. Rule configuration

Certains business thresholds peuvent être configurables.

Exemple :

```text
minimum assessment score
required certifications
risk threshold
```

La configuration doit alimenter une Policy.

Elle ne doit pas être lue directement depuis :

```text
environment variables
```

au cœur du Domain.

---

# 126. Policy Strategy pattern

Une Policy interchangeable correspond naturellement au :

```text
Strategy Pattern
```

lorsque plusieurs stratégies existent réellement.

Exemple :

```text
QualificationPolicy
    ├── DefaultQualificationPolicy
    └── CountrySpecificQualificationPolicy
```

Seulement si cette variation apparaît.

---

# 127. No premature Specification Pattern

Des règles individuelles peuvent éventuellement devenir :

```text
Specification objects
```

mais ne pas introduire un framework `Specification` avant besoin.

Simple Policy + functions/rules est suffisant au départ.

---

# 128. Policy composition

Si une Policy contient plusieurs règles :

```text
rule_1
rule_2
rule_3
```

elle peut les évaluer explicitement.

Cette collection n’est pas automatiquement :

```text
Chain of Responsibility
```

---

# 129. Decision explainability

Les Decisions doivent permettre à :

```text
tests
UI
agents
audit
```

de comprendre pourquoi une décision a été prise.

C’est particulièrement important pour :

```text
Qualification
Activation
Compliance
Risk
Segmentation
```

---

# 130. Decision immutability

Un `QualificationDecision` ou `ActivationDecision` représente le résultat d’une évaluation.

Baseline :

```text
immutable Value Object / Domain Result
```

---

# 131. Time-dependent rules

Les règles temporelles doivent recevoir un temps explicite.

Exemple :

```text
qualification.is_valid(at)
document.is_expired(at)
certification.is_valid(at)
```

Éviter :

```python
datetime.now()
```

dispersé dans le Domain.

---

# 132. Clock boundary

Le temps courant est collecté par :

```text
Application via Clock
```

puis transmis au Domain.

Cette règle rend les tests déterministes.

---

# 133. Validity window invariant

Pour tout `DateRange` :

```text
start <= end
```

lorsque `end` existe.

---

# 134. Current vs historical

`current` n’est pas nécessairement un champ persisté.

Il peut être dérivé de :

```text
status
validity
supersession
time
```

---

# 135. Expiration semantics

Expiration peut être :

```text
derived dynamically
```

ou :

```text
persisted via explicit command/event
```

Le choix doit rester cohérent.

Ne pas modifier silencieusement l’état pendant une Query.

---

# 136. No mutation in Query

Une Query ne doit pas déclencher implicitement :

```text
expire
revoke
suspend
```

si ces actions sont métier.

---

# 137. Cross-Aggregate consistency

Entre Aggregates, PySRMKit accepte :

```text
eventual consistency
```

lorsque la cohérence immédiate n’est pas nécessaire à un invariant unique.

---

# 138. Strong consistency rule

Si deux objets doivent toujours être modifiés atomiquement pour protéger un invariant central :

> re-questionner la frontière d’Aggregate.

---

# 139. Application coordination rule

Le Handler peut :

```text
load A
load B
gather facts
invoke Policy
call behavior on A
save A
```

Il ne doit pas :

```text
manually mutate A/B fields
```

---

# 140. Domain Service rule

Introduire un Domain Service uniquement si une règle métier :

```text
does not naturally belong
to an Entity / Value Object / Policy
```

Ne pas créer `SupplierDomainService` comme fourre-tout.

---

# 141. Generic `validate()` anti-pattern

Éviter :

```python
supplier.validate()
```

qui retourne une longue liste de règles sans contexte.

Les invariants doivent être protégés au moment où les opérations sont exécutées.

---

# 142. Boolean flag anti-pattern

Éviter la prolifération :

```text
is_qualified
is_active
is_compliant
is_risky
is_blocked
```

si les concepts ont déjà :

```text
statuses
decisions
scopes
validity
```

---

# 143. Primitive obsession anti-pattern

Éviter :

```text
status: str
country: str
scope: dict
risk: float
```

pour les concepts importants.

Utiliser :

```text
Enums
Value Objects
typed IDs
Domain Results
```

---

# 144. Anemic Aggregate anti-pattern

Mauvais :

```python
relationship.status = "ACTIVE"
```

avec toute la logique dans Handler.

Bon :

```python
relationship.activate(decision, occurred_at)
```

---

# 145. Fat Handler anti-pattern

Mauvais :

```python
if (
    qualification.status == "QUALIFIED"
    and risk.score < 80
    and compliance.ok
    and all(doc.valid for doc in docs)
):
    relationship.status = "ACTIVE"
```

Bon :

```text
facts
    ↓
ActivationPolicy.evaluate(...)
    ↓
ActivationDecision
    ↓
relationship.activate(decision)
```

---

# 146. ORM invariant anti-pattern

Ne pas compter uniquement sur :

```text
NOT NULL
CHECK
FOREIGN KEY
```

pour protéger la vérité métier.

La persistence renforce les invariants ; elle ne les remplace pas.

---

# 147. Setter anti-pattern

Éviter des setters publics génériques :

```text
set_status
set_score
set_qualified
```

Préférer des verbes métier.

---

# 148. Delete history anti-pattern

Ne pas supprimer une Qualification parce qu’elle n’est plus valable.

Préférer :

```text
revoke
expire
supersede
```

---

# 149. Relationship leakage anti-pattern

Ne pas placer :

```text
supplier.lifecycle_stage
```

sur le Supplier canonique si la lifecycle est contextuelle à une organisation.

---

# 150. Scope leakage anti-pattern

Ne pas interpréter une Qualification scope-specific comme qualification globale.

---

# 151. Evidence leakage anti-pattern

Ne pas rendre `SupplierDocument` propriétaire de la décision Compliance.

---

# 152. Domain event rule

Un Domain Event n’est enregistré qu’après une transition métier valide.

Exemple :

```text
activation rejected
→ no SupplierActivated event
```

---

# 153. Event/state consistency

Si :

```text
SupplierQualified
```

est produit, l’Aggregate doit être dans un état compatible avec ce fait.

---

# 154. No event from failed guard

Une exception de Guard doit laisser :

```text
state unchanged
pending success events unchanged
```

---

# 155. SupplierCreated invariant

`SupplierCreated` ne doit être produit qu’une fois lors de la création logique du Supplier.

Une reconstruction depuis Repository ne doit pas recréer cet event.

---

# 156. Qualification event rules

Candidate mapping :

```text
request()
    → SupplierQualificationRequested

apply approved decision
    → SupplierQualified

apply rejected decision
    → SupplierQualificationRejected

revoke()
    → SupplierQualificationRevoked

expire()
    → SupplierQualificationExpired
```

---

# 157. Relationship event rules

Candidate mapping :

```text
invite()
    → SupplierInvited

start_onboarding()
    → SupplierOnboardingStarted

activate()
    → SupplierActivated

suspend()
    → SupplierSuspended

offboard()
    → SupplierOffboarded
```

---

# 158. Auditability rule

Pour les transitions importantes, conserver autant que nécessaire :

```text
reason
occurred_at
decision explanation
actor context outside or alongside domain
```

---

# 159. Actor boundary

Le Domain peut recevoir une référence d’acteur si la règle métier en dépend réellement.

Mais il ne doit pas dépendre de :

```text
OAuth token
JWT
IAM SDK
```

---

# 160. Authorization ≠ business invariant

Question :

```text
Can this user invoke ActivateSupplier?
```

= Authorization/Application/IAM.

Question :

```text
Can this relationship be activated?
```

= Domain.

---

# 161. Multi-organization isolation invariant

Given:

```text
Supplier S
Relationship R1 / Org A
Relationship R2 / Org B
```

une qualification/suspension sur `R1` ne change pas `R2` sans règle explicite.

Ce test est obligatoire dans le Core.

---

# 162. Multi-country agnosticism invariant

Le Domain Core ne doit pas coder en dur :

```text
France-only identifiers
France-only documents
France-only compliance
```

dans ses primitives génériques.

Des Policies/adapters country-specific peuvent être ajoutés.

---

# 163. Supplier type variation

Si certaines règles varient selon :

```text
legal entity
individual
public body
association
```

cette variation doit être portée explicitement par :

```text
SupplierType
+
Policy
```

pas par `if` dispersés.

---

# 164. Mandatory documentation rule

Un Document peut être required selon :

```text
country
category
supplier type
risk
relationship
```

C’est un bon candidat :

```text
DocumentRequirementPolicy
```

plus tard.

---

# 165. Qualification prerequisite rule

Pour le premier Core local, la QualificationPolicy peut utiliser :

```text
completed assessment
minimum score
required answers
```

comme facts.

Elle ne doit pas immédiatement dépendre de Documents/Compliance/Risk tant que ces capabilities ne sont pas implémentées.

---

# 166. First Core invariant scope

Le premier cycle `0.1.0a1 → a8` doit protéger principalement :

```text
Supplier identity
Relationship uniqueness/context
Relationship lifecycle
Onboarding readiness
Assessment completion
Qualification scope
Qualification decision
Qualification state transitions
Domain event consistency
```

---

# 167. Deferred invariants

Ces familles sont documentées conceptuellement mais ne doivent pas bloquer le premier Core :

```text
Document verification
Certification validity
Compliance aggregation
Risk aggregation
Performance scorecard
Incident lifecycle
Segmentation
Activation across all trust dimensions
```

---

# 168. Invariant implementation order

Recommended:

```text
Value Object constructor invariants
        │
        ▼
Aggregate local invariants
        │
        ▼
State machine guards
        │
        ▼Policies
        │
        ▼
Application cross-instance preconditions
```

---

# 169. Tests — Value Object

Every critical Value Object should have:

```text
valid construction
invalid construction
value equality
immutability where relevant
```

---

# 170. Tests — Aggregate invariant

For every critical invariant:

```text
positive test
negative test
state unchanged on failure
```

---

# 171. Tests — Lifecycle

Use:

```text
allowed transition matrix
forbidden transition matrix
```

---

# 172. Tests — Policy

For a Policy:

```text
same facts → same decision
approved path
rejected path
reasons
boundary thresholds
```

---

# 173. Tests — Cross-Aggregate rule

Use Application tests with:

```text
InMemory repositories
```

for:

```text
global identifier uniqueness
relationship uniqueness
current qualification uniqueness
```

---

# 174. Tests — Multi-organization

Must prove independent state for multiple Relationships on same Supplier.

---

# 175. Tests — Historical records

When implemented, ensure newer:

```text
RiskAssessment
Qualification
PerformanceMeasurement
```

does not erase older records.

---

# 176. Rule IDs — optional

Rules may later receive stable IDs:

```text
QUAL-001
LIFECYCLE-003
```

for explainability/configuration.

Not mandatory for the Core.

---

# 177. Domain rule catalog — Core

Candidate compact catalog:

```text
SUP-001 Supplier identity must be valid
SUP-002 External identifiers unique within Supplier

REL-001 Relationship references one Supplier and one InternalOrganization
REL-002 Relationship uniqueness enforced per context
REL-003 Lifecycle stage changes only via valid transition
REL-004 Offboarded relationship cannot activate directly
REL-005 Suspension/offboarding require reason where configured

ONB-001 Mandatory onboarding requirements must be satisfied before completion

ASM-001 Assessment answers must refer to known questions
ASM-002 Mandatory questions answered before completion
ASM-003 Completed assessment is immutable by default

QUAL-001 Qualification requires explicit scope
QUAL-002 Qualification starts pending
QUAL-003 Only current pending qualification can receive first decision
QUAL-004 Approved decision ↔ QUALIFIED
QUAL-005 Rejected decision ↔ NOT_QUALIFIED
QUAL-006 Current qualification uniqueness per relationship + scope

EVT-001 Success event only after successful state transition
EVT-002 Rehydration does not recreate historical creation events
```

---

# 178. Rule catalog extensibility

Future families:

```text
DOC-*
CERT-*
COMP-*
RISK-*
PERF-*
INC-*
SEG-*
ACT-*
```

will be added only with corresponding implementation.

---

# 179. Business rule documentation template

For future rules:

```text
Rule ID
Name
Business statement
Owner
Inputs
Invariant/Policy/Precondition classification
Failure
Event impact
Tests
```

---

# 180. Example — REL-004

```text
Rule ID:
REL-004

Name:
Offboarded relationship cannot activate directly

Classification:
Aggregate Guard

Owner:
SupplierRelationship

Input:
current lifecycle stage
activation decision

Failure:
InvalidLifecycleTransition

Event:
No SupplierActivated

Tests:
forbidden transition
state unchanged
no event
```

---

# 181. Example — QUAL-006

```text
Rule ID:
QUAL-006

Name:
One current qualification per relationship and scope

Classification:
Cross-instance business rule / Application precondition

Owner:
Application orchestration + QualificationRepository lookup

Failure:
CurrentQualificationAlreadyExists

Tests:
same relationship + same scope rejected
different scope allowed
different relationship allowed
```

---

# 182. Example — Activation rule

```text
Rule:
Relationship can activate only if ActivationPolicy allows it.

Classification:
Policy + Aggregate Guard

Application:
collects facts

Domain Policy:
produces ActivationDecision

Aggregate:
enforces decision before state transition
```

---

# 183. Application Layer contract prepared by this document

The `08` can safely assume:

```text
Handlers orchestrate
Policies decide
Aggregates enforce
Value Objects validate
Repositories locate state
```

---

# 184. Handler rule

A Handler may write:

```text
qualification = repo.get(...)
decision = policy.evaluate(context)
qualification.apply_decision(decision)
repo.save(qualification)
```

It should not write:

```text
qualification.status = QUALIFIED
```

---

# 185. Query rule

Queries can expose derived states:

```text
is_current
is_expired
readiness
```

without mutating source Aggregates.

---

# 186. Readiness projection rule

A `RelationshipReadiness` projection can aggregate:

```text
onboarding
qualification
compliance
risk
documents
```

but it is not itself the owner of these invariants.

---

# 187. Consistency and transaction rule

One command generally protects one main Aggregate transaction.

If multiple Aggregate writes become necessary:

```text
Application transaction / UnitOfWork
```

may coordinate them.

Do not merge Aggregates only to simplify transactions.

---

# 188. Concurrency note

Optimistic concurrency may later protect:

```text
stale Aggregate updates
```

but it is a technical/application concern layered around domain rules.

---

# 189. Idempotency note

Repeated Commands may need idempotency.

Example:

```text
InviteRelationship
```

called twice.

Two possibilities:

```text
second call is no-op
```

or:

```text
InvalidLifecycleTransition
```

The semantic choice belongs to each use case.

---

# 190. Idempotency is not universal

Do not make every domain method silently idempotent.

Some duplicate actions should surface an error because they reveal misuse.

---

# 191. Policy purity

Policies should ideally be:

```text
side-effect free
```

Input facts in, Decision out.

This improves:

```text
testing
explainability
reuse
```

---

# 192. Policy clock

If a Policy depends on time :

```text
evaluate(context, at)
```

or context contains explicit evaluation time.

Avoid hidden system clock.

---

# 193. Domain invariants and Python exceptions

Python implementation candidate:

```text
typed domain exceptions
```

rather than:

```text
assert
```

for expected invalid business operations.

---

# 194. `assert` rule

`assert` can protect developer assumptions internally.

It should not be the primary mechanism for business rule failure because Python can disable assertions.

---

# 195. Constructor vs factory

If construction requires multiple invariants and emits events:

```text
classmethod create(...)
```

can be clearer than unrestricted `__init__`.

But do not force factories for simple Value Objects.

---

# 196. Rehydration rule

Persistence rehydration must rebuild valid Aggregates without:

```text
emitting creation events
re-running external Policies
```

This may motivate internal constructors/mappers later.

---

# 197. Persistence ignorance

Domain invariants must not reference:

```text
database IDs generated after commit
ORM session
lazy-loaded relation
```

as a requirement.

---

# 198. No lazy business rule

A business invariant should not depend on whether an ORM relationship happened to be loaded.

---

# 199. Design Concepts Applied

## DDD

```text
Aggregate
Value Object
Entity
Domain Policy
Domain Service
Domain Result
Domain Event
Ubiquitous Language
```

## Principles

```text
SRP
OCP
DIP
Information Hiding
High Cohesion
Low Coupling
KISS
YAGNI
```

## Patterns

```text
Strategy — Policies where variation exists
State Machine — Lifecycle semantics
Repository-assisted rules — cross-instance lookup
```

Not automatically:

```text
GoF State
Specification
Chain of Responsibility
Observer
```

---

# 200. Learning Map — invariant

```text
Business truth
    │
    ▼
Aggregate invariant
    │
    ▼
Guard
    │
    ▼
Domain Error
    │
    ▼
Focused test
```

---

# 201. Learning Map — Policy

```text
Business decision varies
    │
    ▼
Collect facts
    │
    ▼
Policy
    │
    ▼
Decision object
    │
    ▼
Aggregate applies allowed transition
```

---

# 202. Learning Map — cross-instance rule

```text
Rule spans multiple Aggregate instances
    │
    ▼
Repository lookup
    │
    ▼
Application precondition
    │
    ▼
Domain Aggregate created/mutated safely
```

---

# 203. Learning Map — evidence

```text
Evidence
    │
    ▼
Facts
    │
    ▼
Policy
    │
    ▼
Decision
    │
    ▼
State transition
```

---

# 204. Anti-pattern checklist

Reject:

```text
business logic only in handlers
generic set_status()
global qualification boolean
relationship lifecycle on Supplier
evidence treated as decision
generic validate() god method
ORM constraints as only invariants
history deletion
country-specific assumptions in generic primitives
hidden datetime.now()
policies calling infrastructure directly
```

---

# 205. Core readiness checklist

Before implementing the first Core, the following rules must be sufficiently understood:

```text
[ ] Supplier identity validity
[ ] local external identifier uniqueness
[ ] relationship identity/scope
[ ] relationship uniqueness lookup
[ ] lifecycle transition guards
[ ] onboarding completion rule
[ ] assessment completion rule
[ ] qualification scope validity
[ ] qualification current-instance uniqueness
[ ] qualification decision transitions
[ ] event/state consistency
[ ] multi-organization isolation
```

---

# 206. Deferred questions

Open questions intentionally left for implementation pressure:

```text
Is SupplierOnboarding a separate Aggregate Root?
Is SupplierAssessment always separate Aggregate Root?
How rich should QualificationContext become?
Does activation belong in the first cycle after qualification?
Should qualification renewal create a new Aggregate instance?
Do we need stable Rule IDs immediately?
When is Specification Pattern justified?
When does UnitOfWork become necessary?
```

---

# 207. First Core business rule sequence

```text
Valid Supplier
    │
    ▼
Valid SupplierRelationship
    │
    ▼
Valid Lifecycle progression
    │
    ▼
Valid Onboarding
    │
    ▼
Complete Assessment
    │
    ▼
Qualification request with explicit scope
    │
    ▼
QualificationPolicy
    │
    ▼
QualificationDecision
    │
    ├── QUALIFIED
    └── NOT_QUALIFIED
```

---

# 208. Qualification success rule — first vertical slice

For the first local scenario:

```text
relationship exists
onboarding state acceptable
assessment completed
qualification scope valid
policy requirements satisfied
```

then:

```text
QualificationDecision = approved
SupplierQualification → QUALIFIED
SupplierQualified event
```

The exact numerical thresholds belong to the first concrete Policy implementation, not this generic spec unless already required by business requirements.

---

# 209. Qualification rejection rule — first vertical slice

If required business conditions are not met:

```text
QualificationDecision = rejected
SupplierQualification → NOT_QUALIFIED
SupplierQualificationRejected event
reasons preserved
```

---

# 210. First-cycle scope discipline

The first Core must not delay qualification because Documents/Risk/Compliance are not implemented.

Instead:

```text
QualificationPolicy v0
```

uses only the facts available in the first vertical slice.

Future iterations can enrich the Policy input without breaking the concept.

---

# 211. Rule evolution principle

A business rule may evolve.

The important requirement is:

```text
rule has a clear owner
decision is explicit
tests protect current behavior
```

not that the first formulation is permanent.

---

# 212. Spec ↔ code feedback

If implementation reveals an impossible or awkward invariant:

```text
do not hack around the spec
```

Instead:

```text
revisit model
update document
update test
refactor code
```

---

# 213. Acceptance criteria — this document

The rule model is sufficiently clear if:

```text
[ ] Value Object validation boundary is understood
[ ] Aggregate invariants are identified
[ ] lifecycle guard ownership is clear
[ ] relationship/global scopes are separated
[ ] Qualification requires explicit scope
[ ] Policy vs Handler responsibility is clear
[ ] evidence vs decision is clear
[ ] cross-instance uniqueness belongs outside one Aggregate
[ ] Domain Errors are distinguished from Application/Infrastructure errors
[ ] first Core rules are testable
```

---

# 214. Rule placement North Star

```text
VALUE VALIDITY
    → Value Object

LOCAL BUSINESS TRUTH
    → Aggregate

STATE-DEPENDENT OPERATION
    → Guard

VARIABLE MULTI-FACT DECISION
    → Policy + Decision

CROSS-INSTANCE LOOKUP
    → Application + Repository

TECHNICAL CONSTRAINT
    → Adapter / Infrastructure
```

---

# 215. Final principles

> **An Aggregate protects only the invariants it truly owns.**

> **A Handler orchestrates; it does not become the business rule engine.**

> **A Policy evaluates variable business decisions from explicit facts.**

> **A Decision object explains the result.**

> **Evidence is not a decision.**

> **Relationship-scoped state must not leak into global Supplier identity.**

> **History is preserved rather than rewritten.**

> **Invalid operations do not mutate state and do not emit success events.**

---

# 216. Transition to `08`

With these invariants established, the next document can define:

```text
Commands
Queries
Handlers
Use Cases
Application Results
Application Errors
Transaction Boundaries
```

while respecting the rule:

```text
Application Layer
    coordinates the business

Domain Layer
    decides and protects the business
```

---

# 217. Conclusion

PySRMKit’s business rules are deliberately distributed according to the kind of truth they protect.

```text
Value Objects
    protect valid values

Aggregates
    protect local consistency

Guards
    protect state transitions

Policies
    produce explainable decisions

Application Handlers
    gather and orchestrate facts

Repositories
    support cross-instance discovery

Adapters
    handle technology
```

This division prevents two common failures:

```text
anemic domain model
```

and:

```text
god application service
```

For the first implementation cycle, the most important rules are those required to execute a real vertical slice:

```text
Supplier
→ Relationship
→ Lifecycle
→ Onboarding
→ Assessment
→ Qualification
```

The guiding principle is:

> **Put each rule where it can be enforced with the least knowledge and the strongest guarantee.**