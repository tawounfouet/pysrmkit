# PySRMKit — Repository and Package Architecture

**Document :** `11_PYSRMKIT_REPOSITORY_AND_PACKAGE_ARCHITECTURE.md`  
**Projet :** PySRMKit  
**Domaine :** Supplier Relationship Management  
**Type :** Repository Topology / Python Package Architecture  
**Statut :** Baseline pré-implémentation  
**Version du document :** 0.1.0  

**Documents de référence :**
- `02_PYSRMKIT_PRODUCT_VISION_AND_ARCHITECTURE_PRINCIPLES.md`
- `03_PYSRMKIT_SYSTEM_ARCHITECTURE.md`
- `04_PYSRMKIT_DOMAIN_OBJECTS.md`
- `05_PYSRMKIT_ENTITIES_AND_VALUE_OBJECTS.md`
- `06_PYSRMKIT_DOMAIN_RELATIONSHIPS_AND_ERD.md`
- `07_PYSRMKIT_DOMAIN_INVARIANTS_AND_BUSINESS_RULES.md`
- `08_PYSRMKIT_COMMANDS_QUERIES_AND_USE_CASES.md`
- `09_PYSRMKIT_DOMAIN_EVENTS_AND_EVENT_MODEL.md`
- `10_PYSRMKIT_PORTS_AND_REPOSITORY_CONTRACTS.md`
- `PYSRMKIT_SOFTWARE_DESIGN_LEARNING_CONVENTION.md`
- `PYSRMKIT_PRE_IMPLEMENTATION_SPECIFICATION_CUTOFF_AND_ITERATIVE_DOCUMENTATION_STRATEGY.md`

---

# 1. Objet du document

Ce document définit l’architecture physique du repository Python PySRMKit.

Il précise :

- la structure du dépôt Git ;
- le `src/ layout` ;
- les packages Python principaux ;
- les frontières entre Domain, Application, Ports et Adapters ;
- le découpage par capability ;
- le placement des Commands, Queries, Handlers, Events et Policies ;
- le placement des Repository Protocols ;
- le placement des adapters InMemory ;
- le layout des tests ;
- le placement des contract tests ;
- le placement des exemples ;
- la distinction API publique / modules internes ;
- les règles d’import ;
- les règles de dépendance ;
- les conventions de nommage ;
- les règles destinées à empêcher les cycles et les fuites architecturales.

Ce document doit permettre au bootstrap de commencer sans improviser la structure du repository.

---

# 2. Position dans le baseline pré-bootstrap

```text
09 — Domain Events
        │
        ▼
10 — Ports & Repository Contracts
        │
        ▼
11 — REPOSITORY & PACKAGE ARCHITECTURE   ← ce document
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

---

# 3. Objectif architectural

La structure du code doit rendre visibles les choix d’architecture.

Un développeur ouvrant le repository doit pouvoir reconnaître immédiatement :

```text
Domain
Application
Ports
Adapters
Tests
Examples
```

et comprendre :

```text
what depends on what
```

sans devoir lire toute la documentation.

---

# 4. Principe central

> **The package structure must reinforce the architecture instead of hiding it.**

Le filesystem ne doit pas être une simple organisation esthétique.

Il doit rendre les frontières difficiles à violer accidentellement.

---

# 5. Layer-first vs Feature-first vs Hybrid

Trois stratégies ont été considérées.

## 5.1 Layer-first

```text
domain/
application/
ports/
adapters/
```

Avantages :

- architecture très visible ;
- excellent support pédagogique ;
- dependency rules simples.

Inconvénients :

- une capability est répartie dans plusieurs dossiers ;
- navigation plus coûteuse à grande échelle.

## 5.2 Feature-first

```text
supplier/
relationship/
qualification/
assessment/
```

avec chaque feature contenant :

```text
domain/
application/
ports/
adapters/
```

Avantages :

- forte cohésion ;
- navigation locale excellente.

Inconvénients :

- frontières architecturales moins visibles ;
- risque de duplication de structure ;
- plus complexe pour un framework de domaine transversal.

## 5.3 Hybrid

Approche retenue :

> **Layer-first at the top level, capability-oriented inside each layer.**

Exemple :

```text
domain/
    supplier/
    relationship/
    qualification/
    assessment/

application/
    supplier/
    relationship/
    qualification/
    assessment/
```

---

# 6. Décision

PySRMKit adopte un **Hybrid Layer-First / Capability-Oriented Architecture**.

Cette décision équilibre :

```text
architectural clarity
+
domain cohesion
+
pedagogical visibility
+
future scalability
```

---

# 7. Repository root — target structure

```text
pysrmkit/
├── .github/
│   └── workflows/
│
├── docs/
│
├── examples/
│
├── src/
│   └── pysrmkit/
│
├── tests/
│
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
└── .gitignore
```

Des fichiers additionnels pourront être ajoutés plus tard :

```text
CONTRIBUTING.md
SECURITY.md
CODE_OF_CONDUCT.md
```

mais ne sont pas requis pour le premier bootstrap.

---

# 8. `src/` layout

PySRMKit utilise :

```text
src/
└── pysrmkit/
```

plutôt qu’un package directement à la racine.

---

# 9. Pourquoi `src/` layout

Le `src/` layout évite que les tests importent accidentellement le repository local au lieu du package installé.

Il améliore :

- réalisme du packaging ;
- détection des erreurs d’import ;
- compatibilité PyPI ;
- discipline de bootstrap.

---

# 10. Top-level package target

```text
src/
└── pysrmkit/
    ├── __init__.py
    │
    ├── domain/
    ├── application/
    ├── ports/
    ├── adapters/
    └── _internal/
```

`_internal/` est optionnel et ne doit être introduit que lorsqu’une vraie infrastructure partagée apparaît.

Pour le MVP :

```text
domain/
application/
ports/
adapters/
```

suffisent.

---

# 11. Dependency direction

La direction générale doit rester :

```text
Adapters
    ↓
Ports / Application
    ↓
Domain
```

Le Domain ne dépend pas de l’Application.

Le Domain ne dépend pas des Adapters.

Les Ports peuvent importer les types Domain nécessaires à leurs contrats.

---

# 12. Dependency rule — simplified

```text
DOMAIN
    depends on
    Python stdlib + domain-local types

APPLICATION
    depends on
    DOMAIN + PORTS

PORTS
    depend on
    DOMAIN types

ADAPTERS
    depend on
    PORTS + DOMAIN + APPLICATION contracts where appropriate
```

---

# 13. Forbidden dependencies

```text
domain
    MUST NOT import
    application

domain
    MUST NOT import
    ports

domain
    MUST NOT import
    adapters

application
    MUST NOT import
    concrete adapters

ports
    MUST NOT import
    adapters
```

---

# 14. Domain package

Target :

```text
src/pysrmkit/domain/
├── __init__.py
├── common/
├── supplier/
├── relationship/
├── onboarding/
├── qualification/
└── assessment/
```

Les capabilities suivantes sont différées :

```text
documents/
certification/
compliance/
risk/
performance/
incident/
segmentation/
```

jusqu’à leur implémentation réelle.

---

# 15. `domain/common/`

Contient uniquement les primitives réellement partagées.

Candidate :

```text
domain/common/
├── __init__.py
├── events.py
├── errors.py
└── time.py?
```

Ne pas créer un fourre-tout :

```text
utils.py
helpers.py
common.py
```

---

# 16. `domain/supplier/`

Candidate :

```text
domain/supplier/
├── __init__.py
├── entities.py
├── value_objects.py
├── events.py
├── errors.py
└── policies.py?
```

Pour le MVP, `policies.py` ne doit exister que si une vraie policy supplier-level apparaît.

---

# 17. Supplier package responsibilities

Contient :

```text
Supplier
SupplierId
SupplierIdentity
ExternalIdentifier
SupplierContact
SupplierLocation
Address
CountryCode
CategoryCode
CapabilityCode
SupplierCreated
supplier-specific domain errors
```

---

# 18. `domain/relationship/`

Candidate :

```text
domain/relationship/
├── __init__.py
├── entities.py
├── value_objects.py
├── lifecycle.py
├── events.py
├── errors.py
└── policies.py
```

---

# 19. Relationship package responsibilities

Contient :

```text
SupplierRelationship
SupplierRelationshipId
InternalOrganizationId
SupplierLifecycleStage
SupplierSegment
LifecycleTransitionReason
ActivationDecision
ActivationPolicy
relationship lifecycle events
relationship domain errors
```

---

# 20. `domain/onboarding/`

Candidate :

```text
domain/onboarding/
├── __init__.py
├── entities.py
├── value_objects.py
├── events.py
└── errors.py
```

Le package ne doit pas devenir un moteur de workflow générique.

---

# 21. `domain/qualification/`

Candidate :

```text
domain/qualification/
├── __init__.py
├── entities.py
├── value_objects.py
├── policies.py
├── events.py
└── errors.py
```

---

# 22. Qualification responsibilities

Contient :

```text
SupplierQualification
QualificationId
QualificationScope
QualificationStatus
QualificationDecision
QualificationPolicy
qualification events
qualification errors
```

---

# 23. `domain/assessment/`

Candidate :

```text
domain/assessment/
├── __init__.py
├── entities.py
├── value_objects.py
├── events.py
└── errors.py
```

---

# 24. Assessment responsibilities

Contient :

```text
SupplierAssessment
AssessmentId
AssessmentType
AssessmentQuestion
AssessmentAnswer
AssessmentScore
AssessmentDecision
assessment events
assessment errors
```

---

# 25. File granularity rule

Ne pas créer une classe par fichier dès le départ.

Mauvais MVP :

```text
supplier_id.py
supplier.py
supplier_identity.py
external_identifier.py
address.py
country_code.py
...
```

si cela produit une fragmentation inutile.

Préférer initialement :

```text
entities.py
value_objects.py
events.py
errors.py
policies.py
```

par capability.

---

# 26. Split trigger

Séparer un fichier lorsque :

- il devient difficile à naviguer ;
- plusieurs objets possèdent une complexité importante ;
- un objet devient une sous-capability autonome ;
- les imports deviennent difficiles à contrôler.

---

# 27. Application package

Target :

```text
src/pysrmkit/application/
├── __init__.py
├── supplier/
├── relationship/
├── onboarding/
├── qualification/
└── assessment/
```

---

# 28. Application per capability

Chaque capability contient ses use cases.

Exemple :

```text
application/supplier/
├── __init__.py
├── commands.py
├── queries.py
├── handlers.py
└── results.py
```

---

# 29. Alternative vertical-slice files

Si le nombre de use cases augmente, on pourra évoluer vers :

```text
application/supplier/
├── register_supplier.py
├── update_supplier_identity.py
├── add_external_identifier.py
└── get_supplier.py
```

Cette migration sera guidée par la taille réelle.

---

# 30. MVP choice

Pour le bootstrap :

> **Use grouped files per capability first.**

Donc :

```text
commands.py
queries.py
handlers.py
results.py
```

---

# 31. Why grouped files initially

- moins de fichiers ;
- architecture claire ;
- navigation simple ;
- évite 40 modules quasi vides ;
- meilleur fit pour un package `0.1.0a*`.

---

# 32. Application Supplier

Candidate :

```text
application/supplier/
├── commands.py
├── handlers.py
├── results.py
└── queries.py
```

Use cases :

```text
RegisterSupplier
UpdateSupplierIdentity
AddSupplierExternalIdentifier
```

---

# 33. Application Relationship

Use cases :

```text
CreateSupplierRelationship
InviteSupplierRelationship
StartSupplierOnboarding
ActivateSupplierRelationship
SuspendSupplierRelationship
ReactivateSupplierRelationship
OffboardSupplierRelationship
```

---

# 34. Application Qualification

Use cases :

```text
RequestSupplierQualification
EvaluateSupplierQualification
ApproveSupplierQualification
RejectSupplierQualification
RevokeSupplierQualification
```

---

# 35. Application Assessment

Use cases :

```text
CreateSupplierAssessment
RecordAssessmentAnswer
CompleteSupplierAssessment
```

---

# 36. Application Onboarding

Use cases :

```text
StartSupplierOnboarding
CompleteSupplierOnboarding
GetOnboardingProgress
```

Attention :

`StartSupplierOnboarding` touche la Relationship et l’Onboarding.

Le package exact du Handler doit refléter le **use case principal**, pas nécessairement l’Aggregate qu’il touche.

---

# 37. Cross-capability orchestration

Un Handler peut importer plusieurs domain capabilities.

Exemple :

```text
EvaluateSupplierQualificationHandler
```

peut dépendre de :

```text
assessment
qualification
relationship
```

C’est acceptable dans Application.

---

# 38. Domain cross-import rule

Le Domain doit minimiser les imports entre capabilities.

Lorsque possible, utiliser :

```text
typed IDs
Value Objects partagés explicitement
```

plutôt que des Aggregate references.

---

# 39. Ports package

Target :

```text
src/pysrmkit/ports/
├── __init__.py
├── repositories/
├── clock.py
├── events.py
└── unit_of_work.py?
```

---

# 40. Repository ports

```text
ports/repositories/
├── __init__.py
├── supplier.py
├── relationship.py
├── qualification.py
└── assessment.py
```

---

# 41. Why repository per module

Contrairement aux domain Value Objects, les repository contracts sont peu nombreux et représentent des frontières explicites.

Un module par Repository :

- rend les imports clairs ;
- évite un fichier monolithique ;
- facilite contract tests ;
- prépare l’évolution indépendante.

---

# 42. Port example

```text
ports/repositories/supplier.py
```

contient :

```text
SupplierRepository
```

uniquement.

---

# 43. Clock Port

```text
ports/clock.py
```

contient :

```text
Clock
```

---

# 44. Events Port

```text
ports/events.py
```

contient :

```text
DomainEventDispatcher
```

éventuellement types applicatifs de dispatch.

---

# 45. Unit of Work placement

Si retenu :

```text
ports/unit_of_work.py
```

Le document `10` le laisse optionnel.

Le bootstrap peut créer le module uniquement lorsque le roadmap confirme son utilisation.

---

# 46. Why top-level `ports/`

Le choix d’un package top-level `ports/` rend la notion hexagonale explicite.

Il évite aussi de faire croire que Repository appartient au Domain Model lui-même.

---

# 47. Alternative `application/ports`

Possible mais non retenue au baseline.

Raison :

`ports/` doit rester visuellement identifiable comme frontière architecturale.

---

# 48. Adapters package

Target MVP :

```text
src/pysrmkit/adapters/
├── __init__.py
├── memory/
├── clock/
└── events/
```

---

# 49. Memory adapters

```text
adapters/memory/
├── __init__.py
├── supplier_repository.py
├── relationship_repository.py
├── qualification_repository.py
└── assessment_repository.py
```

---

# 50. Clock adapters

```text
adapters/clock/
├── __init__.py
├── system.py
└── fixed.py
```

`FixedClock` peut éventuellement vivre sous `testing/` plus tard.

Pour le Core, le garder comme adapter simple est acceptable.

---

# 51. Event adapters

```text
adapters/events/
├── __init__.py
└── in_process.py
```

contient :

```text
InProcessDomainEventDispatcher
```

---

# 52. Future adapters

Ils ne doivent pas exister au bootstrap :

```text
adapters/postgresql/
adapters/ivalua/adapters/sap/
adapters/kafka/
adapters/s3/
```

Ils seront ajoutés seulement lorsqu’une itération les exige.

---

# 53. Adapter naming rule

Le nom de l’adapter doit expliciter la technologie.

```text
InMemorySupplierRepository
SystemClock
InProcessDomainEventDispatcher
```

Contrairement aux Ports :

```text
SupplierRepository
Clock
DomainEventDispatcher
```

---

# 54. Public package API

Le package racine :

```text
pysrmkit/__init__.py
```

doit rester minimal.

Ne pas réexporter immédiatement tout le framework.

---

# 55. Public API early baseline

Au tout début :

```python
__version__
```

peut suffire.

Puis réexports contrôlés plus tard.

---

# 56. Why avoid broad reexports early

Une API publique prématurée rend plus coûteux :

- refactoring ;
- déplacement de modules ;
- renommage ;
- stabilisation.

Durant `0.x`, le package interne doit pouvoir évoluer.

---

# 57. Capability-level `__init__.py`

Peut réexporter les types principaux de la capability.

Exemple :

```python
from .entities import Supplier
from .value_objects import SupplierId
```

Mais pas obligatoire au premier commit.

---

# 58. Internal API rule

Les consumers internes peuvent importer depuis les modules précis.

Exemple :

```python
from pysrmkit.domain.supplier.entities import Supplier
```

jusqu’à stabilisation de la surface publique.

---

# 59. `_internal/` package

Ne pas créer avant besoin.

Possible future uses :

```text
serialization helpers
mapping support
generic utilities
```

Mais le risque est d’en faire un nouveau `utils/`.

---

# 60. No `utils.py` policy

Éviter :

```text
utils.py
helpers.py
misc.py
common_utils.py
```

sans cohésion claire.

Chaque helper doit appartenir à un concept identifiable.

---

# 61. Tests root

Target :

```text
tests/
├── unit/
├── application/
├── contracts/
├── architecture/
└── scenarios/
```

---

# 62. Unit tests

```text
tests/unit/
└── domain/
    ├── supplier/
    ├── relationship/
    ├── onboarding/
    ├── qualification/
    └── assessment/
```

---

# 63. Supplier domain tests

Examples :

```text
test_supplier_identity.py
test_external_identifiers.py
test_supplier_contacts.py
```

---

# 64. Relationship domain tests

```text
test_relationship_lifecycle.py
test_relationship_transitions.py
test_relationship_events.py
```

---

# 65. Qualification domain tests

```text
test_qualification_scope.py
test_qualification_policy.py
test_qualification_transitions.py
test_qualification_events.py
```

---

# 66. Assessment domain tests

```text
test_assessment_completion.py
test_assessment_scoring.py
test_assessment_events.py
```

---

# 67. Application tests

Target :

```text
tests/application/
├── supplier/
├── relationship/
├── onboarding/
├── qualification/
└── assessment/
```

Tests :

```text
Command → Handler → Repository Port
```

avec adapters InMemory ou fakes.

---

# 68. Contract tests

Target :

```text
tests/contracts/
└── repositories/
    ├── supplier_contract.py
    ├── relationship_contract.py
    ├── qualification_contract.py
    └── assessment_contract.py
```

---

# 69. Adapter contract tests

Concrete adapter suites :

```text
tests/contracts/repositories/memory/
├── test_supplier_repository.py
├── test_relationship_repository.py
├── test_qualification_repository.py
└── test_assessment_repository.py
```

---

# 70. Alternative shared fixture structure

Possible :

```text
tests/contracts/repositories/
├── base_supplier.py
├── base_relationship.py
...
└── memory/
```

Le `12` détaillera la stratégie exacte.

---

# 71. Architecture tests

Target :

```text
tests/architecture/
├── test_dependency_rules.py
├── test_domain_independence.py
└── test_adapter_boundaries.py
```

---

# 72. Architecture test examples

```text
domain does not import application
domain does not import ports
domain does not import adapters
application does not import concrete adapters
ports do not import adapters
```

---

# 73. Scenario tests

Target :

```text
tests/scenarios/
└── test_local_supplier_qualification.py
```

Ce test représente le premier vertical slice de référence.

---

# 74. Scenario purpose

Il doit démontrer :

```text
RegisterSupplier
→ CreateRelationship
→ Invite
→ Onboarding
→ Assessment
→ RequestQualification
→ EvaluateQualification
→ QUALIFIED / REJECTED
```

---

# 75. Examples directory

Target :

```text
examples/
├── README.md
└── local_qualification.py
```

---

# 76. Example philosophy

Les exemples doivent être :

- exécutables ;
- petits ;
- orientés use case ;
- indépendants d’infrastructure externe.

---

# 77. Example imports

Un exemple doit idéalement utiliser la même surface d’application qu’un consumer réel.

Il ne doit pas modifier directement les private fields des Aggregates.

---

# 78. `docs/` directory

Le repository pourra contenir :

```text
docs/
├── architecture/
├── domain/
├── implementation/
└── adr/
```

Mais la structure documentaire détaillée peut être ajustée plus tard.

---

# 79. Current specification storage

Les documents `00–14` peuvent être regroupés dans :

```text
docs/specifications/
```

avec noms conservés.

---

# 80. Suggested docs layout

```text
docs/
├── specifications/
├── architecture/
├── adr/
├── releases/
└── guides/
```

Pour le bootstrap, seul :

```text
docs/specifications/
```

est nécessaire.

---

# 81. ADR directory

Future :

```text
docs/adr/
```

pour les décisions structurantes qui émergeront du code.

Ne pas produire 30 ADR avant bootstrap.

---

# 82. CI directory

GitHub Actions :

```text
.github/workflows/
├── ci.yml
└── release.yml   # future
```

Au bootstrap :

```text
ci.yml
```

suffit.

---

# 83. CI initial responsibilities

```text
install
lint
type check
tests
```

Release automation est différée.

---

# 84. `pyproject.toml`

Centralise :

```text
build system
package metadata
dependencies
optional dependencies
pytest
ruff
type checker
coverage
```

Éviter la multiplication initiale :

```text
setup.py
setup.cfg
requirements.txt
tox.ini
```

sauf besoin réel.

---

# 85. Initial runtime dependencies

Objectif :

> **zero or near-zero mandatory runtime dependencies.**

Le Domain Core doit fonctionner principalement avec la standard library.

---

# 86. Dev dependencies

Candidats :

```text
pytest
pytest-cov
ruff
pyright or mypy
```

Possiblement :

```text
import-linter
```

si retenu pour architecture tests.

---

# 87. Python version

À figer au bootstrap selon stratégie projet.

Recommendation générale :

```text
Python >= 3.11
```

ou version cohérente avec l’écosystème Py*Kit.

Le bootstrap plan décidera.

---

# 88. Package typing

Si le package est destiné à être typé publiquement :

```text
py.typed
```

pourra être ajouté.

---

# 89. Suggested source tree — MVP complete

```text
src/
└── pysrmkit/
    ├── __init__.py
    │
    ├── domain/
    │   ├── __init__.py
    │   │
    │   ├── common/
    │   │   ├── __init__.py
    │   │   └── events.py
    │   │
    │   ├── supplier/
    │   │   ├── __init__.py
    │   │   ├── entities.py
    │   │   ├── value_objects.py
    │   │   ├── events.py
    │   │   └── errors.py
    │   │
    │   ├── relationship/
    │   │   ├── __init__.py
    │   │   ├── entities.py
    │   │   ├── value_objects.py
    │   │   ├── lifecycle.py
    │   │   ├── policies.py
    │   │   ├── events.py
    │   │   └── errors.py
    │   │
    │   ├── onboarding/
    │   │   ├── __init__.py
    │   │   ├── entities.py
    │   │   ├── value_objects.py
    │   │   ├── events.py
    │   │   └── errors.py
    │   │
    │   ├── qualification/
    │   │   ├── __init__.py
    │   │   ├── entities.py
    │   │   ├── value_objects.py
    │   │   ├── policies.py
    │   │   ├── events.py
    │   │   └── errors.py
    │   │
    │   └── assessment/
    │       ├── __init__.py
    │       ├── entities.py
    │       ├── value_objects.py
    │       ├── events.py
    │       └── errors.py
    │
    ├── application/
    │   ├── __init__.py
    │   ├── supplier/
    │   ├── relationship/
    │   ├── onboarding/
    │   ├── qualification/
    │   └── assessment/
    │
    ├── ports/
    │   ├── __init__.py
    │   ├── clock.py
    │   ├── events.py
    │   └── repositories/
    │       ├── __init__.py
    │       ├── supplier.py
    │       ├── relationship.py
    │       ├── qualification.py
    │       └── assessment.py
    │
    └── adapters/
        ├── __init__.py
        ├── memory/
        │   ├── __init__.py
        │   ├── supplier_repository.py
        │   ├── relationship_repository.py
        │   ├── qualification_repository.py
        │   └── assessment_repository.py
        ├── clock/
        │   ├── __init__.py
        │   ├── system.py
        │   └── fixed.py
        └── events/
            ├── __init__.py
            └── in_process.py
```

---

# 90. Suggested application subtrees

Example :

```text
application/supplier/
├── __init__.py
├── commands.py
├── handlers.py
├── queries.py
└── results.py
```

Même forme initiale pour :

```text
relationship
onboarding
qualification
assessment
```

---

# 91. Avoid empty modules

Ne pas créer tous les fichiers de l’arbre s’ils restent vides pendant plusieurs milestones.

Le tree est une **target architecture**, pas une obligation de générer tout au commit initial.

---

# 92. Bootstrap minimal tree

`0.1.0a1` peut commencer avec :

```text
src/pysrmkit/
├── __init__.py
├── domain/
│   └── common/
├── application/
├── ports/
└── adapters/

tests/
├── unit/
├── application/
├── contracts/
├── architecture/
└── scenarios/
```

Puis les capabilities apparaissent milestone par milestone.

---

# 93. No empty architecture theater

Le repository ne doit pas contenir :

```text
60 empty __init__.py files
```

simplement pour ressembler à une architecture complète.

---

# 94. Capability introduction rule

Créer un package capability lorsqu’un vrai type/use case est introduit.

Exemple :

```text
qualification/
```

apparaît au milestone Qualification.

---

# 95. Import direction — concrete

Allowed :

```text
application.qualification
    imports
domain.qualification

application.qualification
    imports
ports.repositories.qualification
```

Forbidden :

```text
domain.qualification
    imports
application.qualification
```

---

# 96. Adapter direction — concrete

Allowed :

```text
adapters.memory.qualification_repository
    imports
ports.repositories.qualification
domain.qualification
```

Forbidden :

```text
ports.repositories.qualification
    imports
adapters.memory.qualification_repository
```

---

# 97. Cross-domain imports

Allowed with restraint :

```text
domain.qualification
    imports
SupplierRelationshipId
```

si ce typed ID est réellement nécessaire.

Mais éviter :

```text
domain.qualification
    imports
SupplierRelationship Aggregate
```

si une ID suffit.

---

# 98. Common typed IDs question

Deux options :

```text
IDs defined in owning capability
```

ou :

```text
all IDs in domain/common/ids.py
```

Baseline retenue :

> **IDs stay with their owning capability.**

Exemple :

```text
SupplierId
    domain/supplier/value_objects.py

SupplierRelationshipId
    domain/relationship/value_objects.py
```

---

# 99. Why keep IDs with capability

- ownership clair ;
- vocabulaire local ;
- évite un `common/ids.py` gigantesque ;
- meilleur DDD.

---

# 100. Event base type

Un type commun :

```text
DomainEvent
```

peut vivre dans :

```text
domain/common/events.py
```

Les concrete events restent dans leurs capabilities.

---

# 101. Shared errors

Ne pas créer un énorme :

```text
domain/common/errors.py
```

si les erreurs sont capability-specific.

Possible base :

```text
DomainError
```

seulement si elle apporte un réel bénéfice.

---

# 102. Policy placement

Policies métier restent dans :

```text
domain/<capability>/policies.py
```

Pas dans :

```text
application/policies.py
```

si elles représentent une décision métier.

---

# 103. Handler placement

Handlers restent dans :

```text
application/<capability>/handlers.py
```

Ils ne doivent pas vivre dans `domain`.

---

# 104. Repository Port placement

```text
ports/repositories/
```

et non :

```text
adapters/
```

---

# 105. Repository Adapter placement

```text
adapters/memory/
```

et futur :

```text
adapters/postgresql/
```

---

# 106. DTO / Read Model placement

Pour le MVP :

```text
application/<capability>/results.py
```

ou `queries.py`.

Si les read models deviennent nombreux :

```text
application/read_models/
```

pourra émerger plus tard.

---

# 107. Query side future

Ne pas créer aujourd’hui :

```text
read_model/
projection/
search/
cache/
```

sans use case concret.

---

# 108. Composition Root

Le Core a besoin d’un endroit où assembler :

```text
handlers
repositories
clock
dispatcher
policies
```

---

# 109. Composition root placement

Pour le MVP local :

```text
examples/local_qualification.py
```

peut jouer ce rôle.

Il construit explicitement :

```text
InMemory repositories
Fixed/SystemClock
InProcess dispatcher
Policies
Handlers
```

---

# 110. No DI framework

Pas besoin de :

```text
dependency-injector
punq
wired
container framework
```
au premier Core.

Construction manuelle.

---

# 111. Why manual DI

- dépendances visibles ;
- excellent support pédagogique ;
- pas de magie ;
- aucun runtime dependency ;
- architecture testable.

---

# 112. Future composition package

Si la composition devient complexe :

```text
pysrmkit/bootstrap/
```

ou :

```text
pysrmkit/composition/
```

pourra être ajouté.

Pas maintenant.

---

# 113. Public Facade — deferred

Une future façade :

```python
srm = PySRMKit(...)
```

est possible.

Mais elle ne doit pas apparaître avant que les use cases soient stables.

---

# 114. Naming — modules

Use :

```text
snake_case.py
```

Examples :

```text
supplier_repository.py
value_objects.py
local_qualification.py
```

---

# 115. Naming — classes

Use :

```text
PascalCase
```

Examples :

```text
SupplierRelationship
QualificationScope
SupplierRepository
```

---

# 116. Naming — Ports

No prefix:

```text
IRepository
AbstractRepository
BaseRepository
```

unless semantically justified.

---

# 117. Naming — adapters

Use technology + role:

```text
InMemorySupplierRepository
PostgreSQLSupplierRepository
SystemClock
```

---

# 118. Naming — events

Past tense:

```text
SupplierQualified
SupplierActivated
```

---

# 119. Naming — commands

Imperative business verb:

```text
RegisterSupplier
RequestSupplierQualification
```

---

# 120. Naming — queries

Question-like semantic:

```text
GetSupplier
FindSupplierByExternalIdentifier
```

---

# 121. Naming — tests

Test file names should describe capability or behavior.

Good:

```text
test_relationship_lifecycle.py
test_qualification_policy.py
```

Avoid:

```text
test_entities.py
```

when too broad.

---

# 122. Internal imports

Prefer absolute imports:

```python
from pysrmkit.domain.supplier.value_objects import SupplierId
```

rather than deep relative imports.

---

# 123. Why absolute imports

- clearer dependency graph ;
- easier refactoring ;
- architecture tooling compatibility ;
- explicit package boundaries.

---

# 124. Circular imports

Common causes :

```text
entities importing policies
policies importing entities
events importing full aggregate
cross-capability aggregate references
```

Rule :

> Design around types and responsibilities, not around import hacks.

---

# 125. TYPE_CHECKING

`typing.TYPE_CHECKING` can be used sparingly.

It must not become a way to hide a bad dependency cycle.

---

# 126. Forward references

Acceptable for local typing.

Not a substitute for correct module boundaries.

---

# 127. `__all__`

Not required initially.

Can be introduced when public surface stabilizes.

---

# 128. Private naming

Prefix internal implementation details with `_` when useful.

Examples :

```text
_domain_events
_record_event
```

---

# 129. No business logic in `__init__.py`

`__init__.py` should primarily expose/import symbols.

Avoid hidden initialization side effects.

---

# 130. No global registries at import time

Avoid:

```text
global event bus registration
global repository instances
global container
```

during imports.

Composition should be explicit.

---

# 131. Import side effects

Packages should be safe to import.

Importing:

```python
import pysrmkit
```

must not:

- connect to DB ;
- create files ;
- initialize brokers ;
- start threads ;
- register network clients.

---

# 132. Dependency-free Domain

The Domain should rely only on:

```text
Python standard library
typing
dataclasses
enum
datetime
uuid
decimal where needed
```

unless a compelling reason emerges.

---

# 133. Pydantic placement

Pydantic, if introduced later, belongs primarily to:

```text
interfaces
transport DTOs
configuration
```

not automatically to the Domain Model.

---

# 134. SQLAlchemy placement

Future:

```text
adapters/postgresql/
```

not:

```text
domain/
```

---

# 135. FastAPI placement

If an HTTP package is added later:

```text
interfaces/http/
```

or separate integration package.

Not part of current Core.

---

# 136. CLI placement

Future:

```text
interfaces/cli/
```

or external package.

For MVP, examples suffice.

---

# 137. Interface layer status

The baseline Core does not require a top-level:

```text
interfaces/
```

package yet.

Primary adapters will be added when a real API/CLI is implemented.

---

# 138. Why no interfaces package now

Because:

```text
no HTTP
no CLI
no agent tool adapter
```

is required to prove the Core.

YAGNI.

---

# 139. Testing imports

Tests may import internal modules explicitly.

They are allowed to inspect domain behavior.

But scenario tests should prefer the Application surface.

---

# 140. Contract tests dependency

Contract tests import:

```text
Port
Domain fixtures
Concrete Adapter under test
```

This is expected.

---

# 141. Architecture tests dependency

Architecture tests inspect package imports.

They are intentionally outside the production dependency graph.

---

# 142. Fixture placement

Shared fixtures :

```text
tests/conftest.py
```

only when genuinely shared.

Avoid a gigantic fixture file.

Capability-specific fixtures can live near capability tests.

---

# 143. Test builders

If object construction becomes repetitive:

```text
tests/builders/
```

may emerge.

Not required initially.

---

# 144. Test Object Mother pattern

Do not introduce automatically.

Use simple fixture functions/builders first.

---

# 145. Example package boundary

The `examples/` directory is not part of the installed package unless explicitly configured.

It demonstrates consumer usage.

---

# 146. Docs and source parity

When package topology changes materially:

```text
11_PYSRMKIT_REPOSITORY_AND_PACKAGE_ARCHITECTURE.md
```

must be updated.

---

# 147. Architecture fitness

The package layout is expected to be enforced through tests.

Not only documented.

---

# 148. Proposed architecture rules

```text
RULE-ARCH-001
domain must not depend on application

RULE-ARCH-002
domain must not depend on ports

RULE-ARCH-003
domain must not depend on adapters

RULE-ARCH-004
application must not depend on concrete adapters

RULE-ARCH-005
ports must not depend on adapters

RULE-ARCH-006
adapters may depend inward

RULE-ARCH-007
domain must not import infrastructure frameworks
```

---

# 149. Core dependency graph

```text
                  ┌──────────────┐
                  │   Domain     │
                  └──────▲───────┘
                         │
               ┌─────────┴─────────┐
               │                   │
        ┌──────┴──────┐      ┌────┴────┐
        │ Application │      │  Ports  │
        └──────▲──────┘      └────▲────┘
               │                   │
               └─────────┬─────────┘
                         │
                    ┌────┴────┐
                    │ Adapters │
                    └─────────┘
```

Nuance :

Application dépend aussi des Ports.

Ports importent certains types Domain.

---

# 150. Better dependency representation

```text
Domain
  ▲   ▲
  │   │
Ports Application
  ▲      ▲
  └──┬───┘
     │
  Adapters
```

Application may depend on both Domain and Ports.

---

# 151. Architecture concepts practiced

Ce package layout permet de manipuler concrètement :

```text
Hexagonal Architecture
Ports & Adapters
Dependency Inversion
Separation of Concerns
High Cohesion
Low Coupling
Package by Capability
Application Layer
Domain Layer
```

---

# 152. Learning map — package structure

```text
Business Capability
        │
        ▼
Domain package
        │
        ▼
Application package
        │
        ▼
Port
        │
        ▼
Adapter
```

---

# 153. Learning map — dependency inversion

```text
application/qualification/handlers.py
        │
        ▼
ports/repositories/qualification.py
        ▲
        │
adapters/memory/qualification_repository.py
```

---

# 154. Learning map — cohesion

```text
Supplier-specific domain concepts
        │
        ▼
domain/supplier/
```

rather than:

```text
domain/entities/
domain/value_objects/
domain/events/
```

globally across the whole product.

---

# 155. Why not global `entities/`

Rejected structure:

```text
domain/
├── entities/
├── value_objects/
├── events/
└── policies/
```

Why rejected:

- low domain cohesion ;
- unrelated capabilities mixed ;
- increasingly huge folders ;
- difficult navigation.

---

# 156. Why not pure feature-first

Rejected initial structure:

```text
supplier/
├── domain/
├── application/
├── ports/
└── adapters/
```

because:

- duplicates architecture repeatedly ;
- complicates shared infrastructure ;
- less pedagogically obvious at repository level.

---

# 157. Hybrid compromise

Top-level layer visibility:

```text
domain/
application/
ports/
adapters/
```

Inside:

```text
supplier/
relationship/
qualification/
```

This is the chosen compromise.

---

# 158. Future package scalability

When future capabilities appear:

```text
domain/risk/
application/risk/
ports/repositories/risk.py
adapters/memory/risk_repository.py
```

Only if `RiskAssessment` is confirmed as independently persisted.

---

# 159. Capability introduction example

Iteration Risk:

```text
domain/risk/
application/risk/
ports/repositories/risk.py
adapters/memory/risk_repository.py
tests/unit/domain/risk/
tests/application/risk/
```

The topology remains predictable.

---

# 160. External integration packages

Future Ivalua:

```text
adapters/ivalua/
├── client.py
├── mapper.py
├── supplier_adapter.py
└── errors.py
```

depending on real integration needs.

---

# 161. Anti-Corruption Layer placement

Vendor mapping stays under adapter/integration packages.

Never:

```text
domain/supplier/ivalua.py
```

---

# 162. Persistence package future

Possible:

```text
adapters/postgresql/
├── models/
├── mappers/
├── repositories/
└── unit_of_work.py
```

The Repository Ports remain unchanged.

---

# 163. Event broker future

Possible:

```text
adapters/events/kafka/
```

or:

```text
adapters/kafka/
```

when integration event transport exists.

---

# 164. Public API future

Potential stabilized imports:

```python
from pysrmkit import PySRMKit
```

or:

```python
from pysrmkit.domain import SupplierId
```

are explicitly deferred.

---

# 165. `py.typed`

When typed public API becomes part of package contract:

```text
src/pysrmkit/py.typed
```

will be added.

---

# 166. Version location

Recommendation:

```text
importlib.metadata
```

or generated package metadata.

Avoid duplicated version strings.

The release/versioning document will decide later.

---

# 167. Example local composition

Conceptual:

```python
supplier_repo = InMemorySupplierRepository()
relationship_repo = InMemorySupplierRelationshipRepository()
assessment_repo = InMemorySupplierAssessmentRepository()
qualification_repo = InMemorySupplierQualificationRepository()

clock = SystemClock()
dispatcher = InProcessDomainEventDispatcher()

register_supplier = RegisterSupplierHandler(
    repository=supplier_repo,
    clock=clock,
    dispatcher=dispatcher,
)
```

This composition should remain possible without framework magic.

---

# 168. No service locator

Avoid:

```python
container.resolve(RegisterSupplierHandler)
```

in the first Core.

Manual construction first.

---

# 169. No global singleton repositories

Each runtime/test owns explicit repository instances.

---

# 170. Repository lifetime

InMemory repositories live for the duration of the composition root.

A future web adapter may scope repositories/UoW per request.

Not a Domain concern.

---

# 171. Package stability levels

## Stable conceptually

```text
domain
application
ports
adapters
```

## Iterative internally

```text
exact file names
grouped vs one-use-case-per-file
public reexports
composition package
```

---

# 172. Refactor-friendly rule

The topology should support moving:

```text
commands.py
```

into:

```text
register_supplier.py
update_supplier.py
```

later without changing architectural direction.

---

# 173. Module size heuristic

Consider splitting when:

- > several hundred meaningful lines ;
- many unrelated imports ;
- many use cases ;
- multiple distinct responsibilities.

No hard numeric rule.

---

# 174. `common/` governance

An object enters `common/` only if:

1. at least two capabilities use it ;
2. it has one clear meaning ;
3. moving it avoids duplication without hiding ownership.

---

# 175. Common package anti-pattern

Bad:

```text
common/
├── utils.py
├── helpers.py
├── constants.py
└── misc.py
```

---

# 176. Constants

Domain constants should usually live near the concept they describe.

Avoid global constants file.

---

# 177. Enums

Lifecycle enums live with their capability.

Example:

```text
domain/relationship/lifecycle.py
```

---

# 178. Exceptions

Domain errors live with the capability that raises them.

Application errors may live under:

```text
application/errors.py
```
if truly shared.

---

# 179. Application common

A package:

```text
application/common/
```

may emerge later for:

```text
ApplicationError
ExecutionContext
```

but should not be created before use.

---

# 180. Port common

Avoid generic abstractions unless necessary.

Do not create:

```text
BaseRepository
BasePort
PortError
```

without pressure.

---

# 181. Adapter common

Same rule.

No:

```text
BaseAdapter
```

for ceremony.

---

# 182. Test package imports

Tests are not installed as part of runtime package.

No need for `tests/__init__.py` unless tooling requires it.

---

# 183. Repository package tree — full MVP

```text
pysrmkit/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   └── specifications/
├── examples/
│   └── local_qualification.py
├── src/
│   └── pysrmkit/
│       ├── __init__.py
│       ├── domain/
│       ├── application/
│       ├── ports/
│       └── adapters/
├── tests/
│   ├── unit/
│   ├── application/
│   ├── contracts/
│   ├── architecture/
│   └── scenarios/
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
└── .gitignore
```

---

# 184. Milestone-aware topology

## `0.1.0a1 — Bootstrap`

```text
package skeleton
test skeleton
CI
lint/type config
```

## `0.1.0a2 — Supplier Core`

Add:

```text
domain/supplier
application/supplier
ports/repositories/supplier.py
adapters/memory/supplier_repository.py
tests supplier
```

## `0.1.0a3 — Relationship`

Add relationship equivalents.

## `0.1.0a5 — Onboarding`

Add onboarding package.

## `0.1.0a6 — Qualification`

Add qualification package.

---

# 185. Package creation should follow milestones

Do not create:

```text
risk/
compliance/
performance/
incident/
```

before their milestones.

---

# 186. Architecture test before feature growth

By `0.1.0a2`, dependency rules should already be executable.

This prevents drift before the codebase grows.

---

# 187. Packaging acceptance criteria

The architecture is acceptable if:

```text
[ ] src layout is used
[ ] Domain is infrastructure-independent
[ ] Application imports Ports, not adapters
[ ] Ports contain contracts only
[ ] Adapters live outside Core
[ ] capabilities are cohesive
[ ] no global entity/value-object folders
[ ] no generic utils/helpers dumping ground
[ ] tests mirror architectural concerns
[ ] scenario test has a dedicated place
[ ] examples compose the Core manually
```

---

# 188. Dependency acceptance criteria

```text
[ ] domain → stdlib/domain only
[ ] application → domain + ports
[ ] ports → domain types
[ ] adapters → ports + inward layers
[ ] no adapter imported from domain/application
```

---

# 189. Test topology acceptance criteria

```text
[ ] unit/domain tests
[ ] application handler tests
[ ] repository contract tests
[ ] architecture tests
[ ] local qualification scenario tests
```

---

# 190. Deferred topology topics

Not required before local qualification:

```text
interfaces/http/
interfaces/cli/
bootstrap/
composition/
adapters/postgresql/
adapters/kafka/
adapters/ivalua/
read_models/
projections/
migrations/
deployment/
```

---

# 191. Documentation evolution rule

If the code reveals that:

```text
application/<capability>/commands.py
```

becomes too large, split it.

If `domain/common/` grows too much, re-evaluate ownership.

If imports cycle, revisit boundaries before using import hacks.

---

# 192. No folder is sacred

The architecture principles are stable.

The exact filesystem is allowed to evolve.

---

# 193. Stable vs reversible decisions

Harder to change later:

```text
top-level dependency direction
domain/application separation
ports/adapters distinction
capability ownership
```

Easy to change later:

```text
commands.py vs one file per command
exact __init__.py reexports
example filenames
```

---

# 194. Package design principle

> **Optimize for semantic locality first, mechanical symmetry second.**

Do not create identical subfolders everywhere just for visual symmetry.

---

# 195. Repository design principle

> **The repository tree should tell the architecture story.**

A developer should see:

```text
domain
application
ports
adapters
```

and infer the dependency direction.

---

# 196. Pedagogical objective

The filesystem becomes a repeated visual reminder of:

```text
Domain
    is central

Application
    orchestrates

Ports
    define needs

Adapters
    implement technology
```

---

# 197. Learning Map

```text
BUSINESS CAPABILITY
        │
        ▼
domain/<capability>
        │
        ▼
application/<capability>
        │
        ▼
ports/<contract>
        │
        ▼
adapters/<technology>
        │
        ▼
tests at each boundary
```

---

# 198. Pattern map

## Hexagonal Architecture

Visible through:

```text
ports/
adapters/
```

## Repository Pattern

Visible through:

```text
ports/repositories/
adapters/memory/*repository.py
```

## Strategy Pattern

Visible through:

```text
domain/qualification/policies.py
```

## CQRS-lite

Visible through:

```text
application commands/queries
```

without separate distributed infrastructure.

---

# 199. Anti-pattern — package by technical class type

Avoid global:

```text
entities/
repositories/
services/
models/
```

because it destroys capability locality.

---

# 200. Anti-pattern — package by framework

Avoid:

```text
sqlalchemy_models/
pydantic_models/
fastapi_routes/
```

inside the Core.

Framework-specific code belongs to adapters/interfaces.

---

# 201. Anti-pattern — giant `services.py`

Avoid:

```text
application/services.py
```

with every use case.

---

# 202. Anti-pattern — giant `models.py`

Avoid putting:

```text
Supplier
Relationship
Qualification
Assessment
```

into one huge file.

---

# 203. Anti-pattern — adapter leakage

Avoid:

```text
domain/supplier/postgresql_repository.py
```

---

# 204. Anti-pattern — ports importing adapters

Forbidden.

---

# 205. Anti-pattern — convenience import cycles

Do not use broad reexports if they introduce cycles.

---

# 206. Anti-pattern — empty future packages

Do not scaffold all future capabilities.

---

# 207. Anti-pattern — premature plugin system

No plugin registry/package loading mechanism before actual extension pressure.

---

# 208. Anti-pattern — DI container as architecture

Dependency Injection is a principle.

A container is merely one possible tool.

Manual composition is baseline.

---

# 209. Bootstrap target

After this document, the bootstrap should no longer ask:

```text
Where does SupplierRepository live?
Where do events live?
Where do handlers live?
Where do memory adapters live?
Where do contract tests live?
```

The answers are already defined.

---

# 210. Core directory map

```text
src/pysrmkit/
│
├── domain/          # Business model
│
├── application/     # Use-case orchestration
│
├── ports/           # Core-facing contracts
│
└── adapters/        # Replaceable technology implementations
```

---

# 211. Test directory map

```text
tests/
│
├── unit/            # Domain behavior
├── application/     # Handler orchestration
├── contracts/       # Adapter substitutability
├── architecture/    # Dependency rules
└── scenarios/       # End-to-end local business flows
```

---

# 212. Documentation directory map

```text
docs/
└── specifications/
    ├── 00_...
    ├── 01_...
    ├── ...
    └── 14_...
```

---

# 213. Examples map

```text
examples/
└── local_qualification.py
```

Later:

```text
local_activation.py
postgresql_qualification.py
ivalua_supplier_sync.py
```

only when corresponding capabilities exist.

---

# 214. Final architecture tree

```text
PySRMKit
│
├── Domain
│   ├── Supplier
│   ├── Relationship
│   ├── Onboarding
│   ├── Assessment
│   └── Qualification
│
├── Application
│   ├── Commands
│   ├── Queries
│   ├── Handlers
│   └── Results
│
├── Ports
│   ├── Repositories
│   ├── Clock
│   └── Domain Event Dispatcher
│
├── Adapters
│   ├── InMemory Repositories
│   ├── Clock adapters
│   └── In-process Event Dispatcher
│
└── Tests
    ├── Domain Unit
    ├── Application
    ├── Contracts
    ├── Architecture
    └── Scenarios
```

---

# 215. Final decisions

PySRMKit adopts:

```text
src layout
```

```text
top-level layer-first architecture
```

```text
capability-oriented subpackages
```

```text
explicit ports/
```

```text
technology-named adapters/
```

```text
manual dependency injection
```

```text
tests organized by architectural responsibility
```

```text
incremental package creation by milestone
```

---

# 216. Final rules

> **Domain code lives by business capability.**

> **Application code lives by use-case capability.**

> **Ports define inward-facing contracts.**

> **Adapters name the technology they adapt.**

> **Tests mirror the architecture.**

> **No empty future architecture.**

> **No framework-specific code in the Core.**

> **No dependency injection magic before explicit composition becomes painful.**

---

# 217. Next mandatory document

The next mandatory pre-bootstrap document is:

> **`12_PYSRMKIT_TESTING_STRATEGY.md`**

It must define:

```text
test pyramid
domain unit tests
policy tests
state-machine tests
handler tests
repository contract tests
architecture tests
scenario tests
coverage philosophy
test naming
fixtures/builders
qualification gates
```

---

# 218. Conclusion

PySRMKit now has a concrete package architecture aligned with its domain and architecture principles.

The chosen model is:

```text
Layer-first
    +
Capability-oriented
```

This preserves the visual clarity of Hexagonal Architecture while maintaining strong business cohesion.

The baseline package structure is:

```text
domain/
application/
ports/
adapters/
```

with capabilities such as:

```text
supplier/
relationship/
onboarding/
assessment/
qualification/
```

introduced incrementally as each milestone is implemented.

The architecture deliberately avoids:

```text
empty package scaffolding
GenericRepository abstractions
global utils
DI frameworks
framework-specific domain code
future adapter placeholders
```

The filesystem therefore becomes part of the pedagogical model.

Every time the developer navigates:

```text
domain
→ application
→ ports
→ adapters
```

the dependency direction and architectural responsibilities are reinforced.

The final principle is:

> **Make the architecture visible in the tree.  
> Make the dependencies visible in the imports.  
> Make the boundaries executable in the tests.**