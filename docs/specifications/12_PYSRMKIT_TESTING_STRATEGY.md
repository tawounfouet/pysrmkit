# PySRMKit — Testing Strategy

**Document :** `12_PYSRMKIT_TESTING_STRATEGY.md`  
**Projet :** PySRMKit  
**Domaine :** Supplier Relationship Management  
**Type :** Testing Architecture / Quality Strategy  
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
- `10_PYSRMKIT_PORTS_AND_REPOSITORY_CONTRACTS.md`
- `11_PYSRMKIT_REPOSITORY_AND_PACKAGE_ARCHITECTURE.md`
- `PYSRMKIT_SOFTWARE_DESIGN_LEARNING_CONVENTION.md`
- `PYSRMKIT_PRE_IMPLEMENTATION_SPECIFICATION_CUTOFF_AND_ITERATIVE_DOCUMENTATION_STRATEGY.md`

---

# 1. Objet du document

Ce document définit la stratégie de test de PySRMKit avant son bootstrap.

Il précise :

- quelles catégories de tests existent ;
- quelles responsabilités sont testées à quel niveau ;
- comment tester le Domain Model ;
- comment tester les Value Objects ;
- comment tester les Aggregates et leurs invariants ;
- comment tester les State Machines ;
- comment tester les Policies ;
- comment tester les Commands et Handlers ;
- comment tester les Repository Ports avec des contract tests ;
- comment tester les Adapters InMemory ;
- comment tester les règles d’architecture ;
- comment tester les Domain Events ;
- comment construire un scenario test de qualification local ;
- comment gérer fixtures, builders et données de test ;
- comment interpréter la couverture ;
- quels quality gates doivent être verts avant de considérer un milestone terminé.

Le document est conçu pour le premier Core local :

```text
Supplier
→ SupplierRelationship
→ Onboarding
→ Assessment
→ Qualification
```

Il ne définit pas encore en détail :

```text
database integration tests
HTTP API tests
browser tests
load tests
chaos tests
distributed system tests
broker tests
cloud integration tests
```

Ces catégories seront ajoutées uniquement lorsqu’une itération réelle les justifiera.

---

# 2. Position dans le baseline pré-bootstrap

```text
10 — Ports & Repository Contracts
        │
        ▼
11 — Repository & Package Architecture
        │
        ▼
12 — TESTING STRATEGY   ← ce document
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

Le `12` transforme les décisions précédentes en :

```text
EXECUTABLE EXPECTATIONS
```

---

# 3. Principe central

> **A design decision is not really protected until a test can detect its violation.**

PySRMKit utilise les tests non seulement pour détecter les bugs, mais aussi pour protéger :

- les invariants métier ;
- les transitions de lifecycle ;
- les contrats de ports ;
- les frontières d’Aggregate ;
- les règles de dépendance ;
- la substituabilité des adapters ;
- la sémantique des Domain Events.

---

# 4. Testing as executable architecture

La documentation explique :

```text
what should be true
```

Les tests vérifient :

```text
that it remains true
```

Exemple :

```text
SPEC:
Domain must not depend on Adapters

TEST:
architecture test fails if
pysrmkit.domain imports pysrmkit.adapters
```

---

# 5. Testing as deliberate practice

Le projet utilise volontairement les tests comme outil pédagogique.

Exemples :

```text
Value Object
    → equality / immutability tests

Aggregate Root
    → invariant tests

State Machine
    → transition matrix tests

Strategy
    → policy contract/behavior tests

Repository
    → repository contract tests

LSP
    → same tests across multiple adapters

DIP
    → architecture dependency tests

Domain Event
    → event emission tests
```

La répétition rend les concepts plus intuitifs.

---

# 6. Testing philosophy

PySRMKit privilégie :

```text
behavior
over
implementation detail
```

```text
domain language
over
technical mechanics
```

```text
determinism
over
realistic infrastructure in unit tests
```

```text
small tests
+
few meaningful scenario tests
```

---

# 7. Test pyramid — Core

Le premier Core suit une pyramide simple :

```text
                    ┌────────────────────┐
                    │   Scenario Tests   │
                    │     few / broad    │
                    └─────────▲──────────┘
                              │
                    ┌─────────┴──────────┐
                    │ Application Tests  │
                    │ handlers/use cases │
                    └─────────▲──────────┘
                              │
              ┌───────────────┴────────────────┐
              │ Contract / Architecture Tests │
              └───────────────▲────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │ Domain Unit Tests  │
                    │  many / focused    │
                    └────────────────────┘
```

---

# 8. Main test families

```text
1. Domain Unit Tests
2. Value Object Tests
3. Aggregate / Invariant Tests
4. State Transition Tests
5. Policy Tests
6. Domain Event Tests
7. Application Handler Tests
8. Repository Contract Tests
9. Adapter Tests
10. Architecture Tests
11. Scenario Tests
```

---

# 9. Tests directory baseline

Target :

```text
tests/
├── unit/
│   └── domain/
│       ├── supplier/
│       ├── relationship/
│       ├── onboarding/
│       ├── assessment/
│       └── qualification/
│
├── application/
│   ├── supplier/
│   ├── relationship/
│   ├── onboarding/
│   ├── assessment/
│   └── qualification/
│
├── contracts/
│   └── repositories/
│       └── memory/
│
├── architecture/
│
└── scenarios/
```

---

# 10. Test naming principle

Un test doit raconter un comportement.

Bon :

```text
test_relationship_cannot_be_activated_from_offboarded
```

Mauvais :

```text
test_activate_1
test_status
test_entity
```

---

# 11. Arrange / Act / Assert

Baseline recommandée :

```text
ARRANGE
    build state

ACT
    invoke behavior

ASSERT
    verify result
```

Le style doit rester lisible.

Aucune obligation d’ajouter des commentaires AAA à chaque test si la structure est déjà claire.

---

# 12. Given / When / Then

Pour les tests très métier :

```text
Given
When
Then
```

peut être plus naturel.

Exemple :

```text
Given a relationship in ONBOARDING
When qualification is approved
Then qualification becomes QUALIFIED
```

---

# 13. Test one behavior, not necessarily one assertion

La règle :

```text
one assertion per test
```

n’est pas retenue comme dogme.

Un test peut vérifier plusieurs conséquences cohérentes d’un même comportement :

```text
status changed
event recorded
reason preserved
```

si elles appartiennent au même résultat métier.

---

# 14. Domain Unit Tests

Les Domain Unit Tests doivent être :

```text
fast
deterministic
in-memory
infrastructure-free
```

Ils testent directement :

```text
Value Objects
Entities
Aggregates
Policies
Domain Errors
Domain Events
```

---

# 15. No mocks in pure Domain tests by default

Le Domain Model doit généralement pouvoir être testé sans mocks.

Si un Domain Unit Test nécessite :

```text
database mock
HTTP mock
Kafka mock
```

la frontière du domaine doit être re-questionnée.

---

# 16. Value Object Tests

Chaque Value Object critique doit tester :

```text
valid construction
invalid construction
value equality
immutability where contractual
behavior
```

---

# 17. SupplierId tests

Examples :

```text
test_supplier_id_is_value_equal_for_same_value
test_supplier_id_is_not_equal_to_other_id_type
```

selon implémentation.

---

# 18. CountryCode tests

Examples :

```text
test_country_code_accepts_supported_format
test_country_code_rejects_blank_value
test_country_code_normalization_is_explicit
```

Ne pas inventer des règles non décidées dans le domaine.

---

# 19. DateRange tests

```text
test_date_range_accepts_open_end
test_date_range_rejects_end_before_start
test_date_range_contains_date
```

si ces comportements sont implémentés.

---

# 20. QualificationScope tests

Tests minimum :

```text
test_scope_requires_meaningful_dimension
test_equal_scopes_are_value_equal
test_different_category_makes_different_scope
```

selon invariants `07`.

---

# 21. Entity Tests

Tester :

```text
identity semantics
business behavior
controlled state changes
```

Ne pas tester :

```text
every field getter
dataclass generated repr
private implementation
```

---

# 22. Aggregate Tests

Un Aggregate Test vérifie :

- invariant local ;
- transition valide ;
- transition invalide ;
- state final ;
- Domain Event produit ;
- absence d’event si opération rejetée.

---

# 23. Supplier Aggregate tests

Candidates :

```text
test_supplier_can_be_registered
test_supplier_can_add_external_identifier
test_supplier_rejects_duplicate_external_identifier
test_supplier_identity_remains_same_after_master_update
```

---

# 24. SupplierRelationship Aggregate tests

Candidates :

```text
test_relationship_starts_in_expected_stage
test_relationship_can_be_invited
test_relationship_can_start_onboarding
test_relationship_cannot_skip_required_transition
test_offboarded_relationship_cannot_be_activated
```

---

# 25. Qualification Aggregate tests

Candidates :

```text
test_qualification_can_be_requested_for_scope
test_qualification_can_be_approved
test_qualification_can_be_rejected
test_qualification_cannot_be_approved_from_invalid_state
test_qualification_preserves_scope
```

---

# 26. Assessment Aggregate tests

Candidates :

```text
test_assessment_can_record_answer
test_assessment_cannot_complete_when_required_answer_missing
test_completed_assessment_cannot_accept_new_answer
```

si les invariants correspondants existent.

---

# 27. Invariant Tests

Les invariants critiques doivent avoir un test positif et négatif.

Example :

```text
RULE:
Offboarded Relationship cannot be reactivated directly.

TEST A:
valid allowed transition succeeds.

TEST B:
forbidden transition raises Domain Error.
```

---

# 28. Invariant test naming

Préférer :

```text
test_offboarded_relationship_cannot_be_activated
```

à :

```text
test_invalid_transition
```

Le nom doit enseigner la règle.

---

# 29. State Machine Tests

Le lifecycle relationnel doit être testé comme une matrice.

Example conceptual:

| From | To | Expected |
|---|---|---|
| DISCOVERED | PROSPECTIVE | allowed |
| PROSPECTIVE | INVITED | allowed |
| INVITED | ONBOARDING | allowed |
| ONBOARDING | UNDER_REVIEW | allowed |
| QUALIFIED | ACTIVE | allowed if decision allows |
| OFFBOARDED | ACTIVE | forbidden |

La matrice exacte suit `07`.

---

# 30. Parametrized transition tests

`pytest.mark.parametrize` est adapté.

Example:

```python
@pytest.mark.parametrize(
    ("from_stage", "to_stage"),
    [
        (...),
        (...),
    ],
)
def test_allowed_relationship_transitions(...):
    ...
```

---

# 31. Forbidden transition matrix

Même approche pour les transitions interdites.

Cela rend la State Machine très visible.

---

# 32. State Pattern vs State Tests

Tester une State Machine ne signifie pas que le code utilise le GoF State Pattern.

La convention pédagogique doit maintenir cette distinction.

---

# 33. Policy Tests

Les Policies représentent les Strategy candidates les plus importantes.

Examples :

```text
QualificationPolicy
ActivationPolicy
RiskPolicy
CompliancePolicy
SegmentationPolicy
```

Pour le premier Core :

```text
QualificationPolicy
```

est prioritaire.

---

# 34. Policy test objective

Une Policy Test doit isoler :

```text
inputs
→ decision
```

sans persistence ni Handler.

---

# 35. QualificationPolicy tests

Candidates :

```text
test_policy_qualifies_when_all_required_conditions_are_met
test_policy_rejects_when_required_assessment_failed
test_policy_returns_reasons_for_rejection
test_policy_is_deterministic_for_same_context
```

---

# 36. Decision explainability tests

Une policy ne doit pas seulement retourner :

```text
True / False
```

si le modèle prévoit une `Decision`.

Tester :

```text
allowed/status
reasons
failed requirements
```

---

# 37. Strategy substitutability tests

Si plusieurs policies apparaissent plus tard :

```text
DefaultQualificationPolicy
CountrySpecificQualificationPolicy
```

une suite de tests de comportement partagé peut être introduite.

Pas nécessaire avant le second strategy.

---

# 38. Domain Event Tests

Chaque comportement métier significatif doit tester :

```text
correct event type
correct aggregate identity
correct occurred_at
correct domain payload
```

---

# 39. Event success test

Example :

```text
test_supplier_qualification_records_supplier_qualified_event
```

---

# 40. Event rejection test

Example :

```text
test_rejected_invalid_transition_records_no_success_event
```

---

# 41. Event order test

Pour plusieurs events dans le même Aggregate :

```text
pull_events()
```

doit préserver l’ordre.

---

# 42. Event collection test

Tests :

```text
test_pull_events_returns_pending_events
test_pull_events_clears_pending_events
```

---

# 43. Event timestamp determinism

Utiliser :

```text
FixedClock
```

ou timestamp explicitement fourni.

Éviter les assertions fragiles :

```text
datetime.now() ± 1 second
```

---

# 44. Application Handler Tests

Les Handler Tests vérifient :

```text
orchestration
repository interactions semantically
domain invocation
commit behavior if present
event dispatch
application errors
```

Ils ne réécrivent pas tous les Domain Tests.

---

# 45. Handler test environment

Baseline :

```text
InMemory repositories
FixedClock
InProcessDomainEventDispatcher or RecordingDispatcher
real Domain objects
```

Plutôt que de mocker tous les composants.

---

# 46. Why prefer fakes over mocks

Les fakes permettent de tester un flux réel sans infrastructure.

Ils réduisent les tests couplés à l’ordre exact des appels.

---

# 47. Mock usage

Mocks sont utiles lorsque le test doit vérifier une interaction coûteuse ou externe.

Exemple futur :

```text
SanctionsScreeningProvider
```

Mais pour les repositories InMemory du Core :

```text
prefer real fake adapter
```

---

# 48. RegisterSupplierHandler tests

Candidates :

```text
test_register_supplier_persists_supplier
test_register_supplier_returns_supplier_id
test_register_supplier_dispatches_supplier_created
test_register_supplier_rejects_duplicate_external_identifier
```

---

# 49. CreateSupplierRelationshipHandler tests

```text
test_create_relationship_requires_existing_supplier
test_create_relationship_rejects_duplicate_supplier_organization_pair
test_create_relationship_persists_new_relationship
test_create_relationship_dispatches_created_event
```

---

# 50. InviteSupplierRelationshipHandler tests

```text
test_invite_relationship_changes_stage
test_invite_relationship_persists_state
test_invite_relationship_dispatches_supplier_invited
```

---

# 51. StartOnboarding Handler tests

```text
test_start_onboarding_requires_valid_relationship_stage
test_start_onboarding_persists_transition
test_start_onboarding_dispatches_event
```

---

# 52. Assessment Handler tests

```text
test_complete_assessment_persists_completed_state
test_complete_assessment_dispatches_completed_event
```

---

# 53. Qualification Handler tests

```text
test_request_qualification_rejects_duplicate_current_scope
test_request_qualification_persists_qualification
test_evaluate_qualification_uses_policy
test_evaluate_qualification_persists_decision
test_evaluate_qualification_dispatches_qualified_event
test_evaluate_qualification_dispatches_rejected_event
```

---

# 54. Handler test boundary

Un Handler Test peut vérifier :

```text
state in repository after use case
```

et :

```text
recorded/dispatched events
```

sans connaître les private fields du Handler.

---

# 55. Application Error tests

Examples :

```text
SupplierNotFound
RelationshipNotFound
QualificationNotFound
DuplicateSupplierDetected
RelationshipAlreadyExists
```

Tester l’erreur stable de l’Application Layer.

---

# 56. Domain vs Application error tests

Si le Domain lève :

```text
InvalidLifecycleTransition
```

le Handler peut :

- laisser remonter ;
- traduire vers application error ;

selon stratégie.

Le test doit suivre le contrat décidé.

---

# 57. Repository Contract Tests

Les contract tests vérifient qu’un Adapter respecte le même contrat comportemental que les autres.
Ils sont fondamentaux pour :

```text
Repository Pattern
Liskov Substitution
Ports & Adapters
```

---

# 58. Contract test architecture

```text
Shared Contract Suite
        │
        ├── InMemory adapter
        ├── PostgreSQL adapter later
        └── other adapter later
```

---

# 59. SupplierRepository contract

Tests minimum :

```text
save then get returns same logical Supplier
unknown id returns None
updated state survives save/reload
find_by_external_identifier works
unknown external identifier returns None
multiple Suppliers are isolated
```

---

# 60. RelationshipRepository contract

```text
save/get round-trip
unknown id returns None
find_for_supplier_and_organization works
different organizations do not collide
lifecycle state survives save/reload
```

---

# 61. QualificationRepository contract

```text
save/get round-trip
unknown id returns None
find_current_for_scope works
different scopes do not collide
different relationships do not collide
updated status survives reload
```

---

# 62. AssessmentRepository contract

```text
save/get round-trip
unknown id returns None
answers survive persistence
completed status survives persistence
multiple assessments remain isolated
```

---

# 63. Contract fixture factory

Une contract suite peut demander :

```text
make_repository()
```

à la concrete test class.

Cela reste simple et explicite.

---

# 64. Contract tests and `Protocol`

Les tests ne vérifient pas seulement :

```text
type checker accepts implementation
```

Ils vérifient surtout :

```text
behavioral substitutability
```

---

# 65. InMemory Adapter Tests

Les adapters InMemory peuvent avoir des tests spécifiques en plus du contract.

Particulièrement :

```text
copy semantics
isolation
index maintenance
```

---

# 66. Shared-reference trap test

Important :

```text
loaded = repo.get(id)
loaded.change(...)
without repo.save(...)
```

ne doit pas forcément modifier silencieusement la persistence si l’Adapter est conçu pour simuler une vraie boundary.

Tester explicitement la sémantique retenue.

---

# 67. Deepcopy caveat

Si `deepcopy` est utilisé :

- tester qu’il ne casse pas les Value Objects ;
- tester que les Domain Events pending ne sont pas persistés par erreur ;
- tester que l’Aggregate rechargé conserve seulement l’état attendu.

---

# 68. Adapter Tests are not Domain Tests

Ne pas répéter les invariants du Supplier dans :

```text
test_in_memory_supplier_repository.py
```

Le repository doit préserver l’état, pas revalider le métier.

---

# 69. Clock Tests

`SystemClock` :

```text
returns timezone-aware UTC-ish current time
```

`FixedClock` :

```text
returns exact configured time
```

Si `advance()` existe plus tard :

```text
advance changes future now()
```

---

# 70. Event Dispatcher Tests

Minimum :

```text
dispatches event to registered handler
dispatches event to multiple handlers
preserves event order
unknown event with no handlers is safe
handler failure is visible
```

---

# 71. Architecture Tests

Les architecture tests protègent la dependency direction.

Ils sont obligatoires tôt.

---

# 72. Architecture Rule 001

```text
domain
MUST NOT import
application
```

---

# 73. Architecture Rule 002

```text
domain
MUST NOT import
ports
```

---

# 74. Architecture Rule 003

```text
domain
MUST NOT import
adapters
```

---

# 75. Architecture Rule 004

```text
application
MUST NOT import
concrete adapters
```

---

# 76. Architecture Rule 005

```text
ports
MUST NOT import
adapters
```

---

# 77. Architecture Rule 006

```text
domain
MUST NOT import
SQLAlchemy / FastAPI / Kafka SDK / cloud SDK
```

---

# 78. Architecture Rule 007

```text
adapters
MAY depend inward
```

on:

```text
ports
domain
application contracts where justified
```

---

# 79. Architecture test implementation

Deux options :

## Simple

Python AST/import inspection.

## Tool

`import-linter` or equivalent.

Recommendation :

> Start with the simplest reliable approach available at bootstrap.

Le `14` décidera l’outil exact.

---

# 80. Architecture Tests as fitness functions

Ces tests sont des :

```text
Architecture Fitness Functions
```

car ils protègent continuellement la structure voulue.

---

# 81. Scenario Tests

Un Scenario Test vérifie un parcours métier large.

Il utilise :

```text
real Domain
real Application Handlers
InMemory Adapters
FixedClock
InProcess dispatcher
```

sans DB ni API.

---

# 82. First reference scenario

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
CreateSupplierAssessment
        │
        ▼
CompleteSupplierAssessment
        │
        ▼
RequestSupplierQualification
        │
        ▼
EvaluateSupplierQualification
        │
        ├── QUALIFIED
        └── REJECTED
```

---

# 83. Scenario Test objective

Prouver que :

```text
the architecture works as a system
```

sans tester l’infrastructure externe.

---

# 84. Scenario test success path

`test_local_supplier_qualification_success.py`

peut vérifier :

- Supplier exists ;
- Relationship progressed correctly ;
- Assessment completed ;
- Qualification exists ;
- final status `QUALIFIED` ;
- expected Domain Events observed.

---

# 85. Scenario rejection path

Deuxième scenario possible :

```text
assessment insufficient
→ QualificationDecision rejected
→ status NOT_QUALIFIED
→ rejection event emitted
```

---

# 86. Scenario tests should be few

Ne pas transformer chaque edge case en scenario test.

Les edge cases restent dans les Domain Unit Tests.

---

# 87. Test data strategy

La test suite doit utiliser des données lisibles.

Example :

```text
Supplier legal name: "ACME France"
Country: "FR"
Category: "IT_SERVICES"
Organization: "ORG_FR"
```

Éviter les random values dans les assertions métier.

---

# 88. Deterministic IDs

Tests peuvent construire :

```text
SupplierId(UUID("..."))
```

ou helper déterministe.

Éviter de dépendre des UUID générés aléatoirement lorsque l’ID lui-même doit être asserté.

---

# 89. Random testing — later

Property-based testing peut devenir utile plus tard.

Mais ne pas introduire Hypothesis avant besoin réel.

---

# 90. Fixture philosophy

Fixtures doivent réduire le bruit, pas cacher le scénario.

Mauvais :

```text
supplier_complex_fixture
```

qui configure 40 choses invisibles.

Bon :

```text
supplier()
relationship(stage=...)
qualification(scope=...)
```

---

# 91. Fixture scope

Préférer :

```text
function scope
```

par défaut pour isolation.

---

# 92. `conftest.py`

Utiliser pour les fixtures vraiment transversales.

Ne pas y mettre toute la test factory du projet.

---

# 93. Test builders

Si la création d’Aggregates devient répétitive :

```text
tests/builders/
```

ou builders localisés peuvent être introduits.

---

# 94. Builder example

```python
relationship = (
    RelationshipBuilder()
    .with_stage(SupplierLifecycleStage.ONBOARDING)
    .build()
)
```

Mais ne pas ajouter ce pattern avant répétition réelle.

---

# 95. Object Mother — deferred

Pas nécessaire au MVP.

---

# 96. Fake objects

Fakes recommandés :

```text
InMemory repositories
FixedClock
RecordingDomainEventDispatcher
```

---

# 97. Recording dispatcher

Un adapter de test peut simplement accumuler :

```text
dispatched_events
```

pour assertions.

Il peut être distinct de `InProcessDomainEventDispatcher` si utile.

---

# 98. Stubs

Utiles plus tard pour :

```text
RiskDataProvider
CompanyRegistryProvider
SanctionsScreeningProvider
```

---

# 99. Mocks

Utiliser uniquement lorsque l’interaction elle-même est importante.

Exemple :

```text
external notification called once
```

Pas comme style par défaut.

---

# 100. Spy

Un recording fake peut souvent remplacer un Spy framework.

---

# 101. Test double vocabulary

Le projet doit distinguer :

```text
Fake
Stub
Mock
Spy
```

et ne pas appeler tout :

```text
mock
```

C’est cohérent avec la convention pédagogique.

---

# 102. Coverage philosophy

La couverture mesure :

```text
what code was executed
```

Elle ne mesure pas :

```text
whether the right behaviors were tested
```

---

# 103. Coverage target

Pour le Core :

> viser une couverture élevée sur `domain/` et `application/`, sans transformer le pourcentage en objectif absolu.

Une baseline pratique peut être :

```text
overall >= 90%
```

mais la vraie priorité est :

```text
100% of critical invariants
100% of lifecycle transition branches
100% of policy decision branches
```

---

# 104. Why not chase 100% overall

Des lignes comme :

```text
repr helpers
defensive impossible branches
simple package reexports
```

ne méritent pas nécessairement un test artificiel.

---

# 105. Branch coverage

Plus utile que line coverage pour :

```text
policies
state transitions
guards
```

Recommendation :

```text
enable branch coverage
```

si l’outil retenu le permet.

---

# 106. Critical-path coverage

Milestone qualification doit couvrir :

```text
success
rejection
invalid transition
duplicate request
not found
event emission
persistence round-trip
```

---

# 107. Mutation testing — deferred

Mutation testing peut être très utile plus tard pour tester la qualité des assertions.

Mais il n’est pas obligatoire avant le bootstrap.

---

# 108. Property-based testing — deferred

Peut devenir intéressant pour :

```text
Value Objects
DateRange
scores
state transitions
```

mais pas obligatoire initialement.

---

# 109. Snapshot testing — limited

Éviter les snapshots massifs du Domain Model.

Ils peuvent masquer des changements sémantiques.

Préférer assertions explicites.

---

# 110. Golden files — not needed

Pas nécessaire pour le Core.

---

# 111. Test speed budget

Le Core suite doit rester suffisamment rapide pour être lancée constamment.

Target conceptual :

```text
seconds, not minutes
```

pour le Core local.

---

# 112. Local feedback loop

Le développeur doit pouvoir exécuter :

```bash
pytest
```

à chaque changement.

---

# 113. Focused test commands

Examples :

```bash
pytest tests/unit/domain/qualification
pytest tests/application/qualification
pytest tests/contracts/repositories/memory
pytest tests/scenarios/test_local_supplier_qualification.py
```

---

# 114. CI test layers

Initial CI :

```text
lint
type check
unit/application/contract/architecture/scenario tests
coverage
```

Pas de matrix complexe avant besoin.

---

# 115. Type checking and tests

Static typing ne remplace pas les tests.

Tests ne remplacent pas le type checker.

Les deux protègent des catégories différentes d’erreurs.

---

# 116. Ruff and tests

Linting protège :

```text
style
common errors
import quality
```

mais ne valide pas l’architecture métier.

---

# 117. Quality Gate hierarchy

Un milestone ne passe pas si :

```text
tests fail
type check fails
architecture test fails
lint fails
```

---

# 118. Definition of Green

Pour le Core local :

```text
GREEN =
pytest passes
+
type checker passes
+
ruff passes
+
architecture rules pass
```

---

# 119. Milestone testing gate

Chaque milestone doit définir :

```text
new behavior tests
regression suite
architecture checks
```

avant merge/tag.

---

# 120. Test-first vs Test-after

PySRMKit ne force pas dogmatiquement TDD pour chaque ligne.

Baseline :

> **Critical domain rules should usually be test-defined before or together with implementation.**

---

# 121. TDD especially valuable for

```text
Value Object invariants
State transitions
Policies
Repository contracts
Application error behavior
```

---

# 122. Exploratory implementation

Pour une abstraction encore mal comprise :

```text
spike
→ learn
→ delete/refactor
→ write stable tests
```

est acceptable.

---

# 123. Red-Green-Refactor

La boucle reste très utile :

```text
RED
    test expresses desired behavior

GREEN
    simplest implementation

REFACTOR
    improve structure without changing behavior
```

---

# 124. Refactoring safety

La suite doit permettre de refactorer :

```text
internal file layout
private methods
policy implementation
repository adapter implementation
```

sans changer les tests métier si le comportement reste identique.

---

# 125. Avoid overspecified tests

Mauvais :

```text
assert private_method called twice
```

si ce détail n’est pas contractuel.

---

# 126. Behavior-based assertions

Bon :

```text
qualification.status == QUALIFIED
event is SupplierQualified
```

---

# 127. Time testing

Toujours préférer :

```text
fixed datetime
```

dans les tests métier.

---

# 128. Timezone testing

Les timestamps métier doivent être timezone-aware.

Ajouter au moins un test pour empêcher les naive datetimes si le contrat le requiert.

---

# 129. Event time

Event timestamp doit être exactement le temps de la transition fourni par `Clock`.

---

# 130. Exception testing

Utiliser :

```python
with pytest.raises(ExpectedDomainError):
    ...
```

et vérifier des attributs métier si utiles.

---

# 131. Exception message testing

Ne pas tester le texte complet sauf s’il fait partie d’un contrat public.

Préférer :

```text
error code
attributes
types
```

si disponibles.

---

# 132. Test factories and domain invariants

Les builders/fixtures ne doivent pas contourner les invariants via private field mutation.
Ils doivent utiliser :

- constructeurs valides ;
- public factory methods ;
- explicit test-only construction only if strictly necessary.

---

# 133. Invalid object testing

Pour tester un état impossible :

```text
prefer invoking invalid operation
```

rather than creating corrupt Aggregate via field mutation.

---

# 134. Persistence contract and pending events

Repository round-trip tests doivent décider si :

```text
pending Domain Events
```

sont persistés ou non.

Recommendation Core :

> pending events are application/runtime state, not persisted as Aggregate business state by InMemory repository.

---

# 135. Contract test for pending events

Possible :

```text
save aggregate with pending event
reload aggregate
pending event queue is empty
```

si cette sémantique est retenue.

---

# 136. Domain Event dispatcher vs repository tests

Ne pas tester le dispatcher dans les Repository Contract Tests.

Chaque boundary a ses propres tests.

---

# 137. Test isolation

Un test ne doit pas dépendre :

- de l’ordre des autres tests ;
- d’un global repository ;
- d’un global clock ;
- d’un global dispatcher.

---

# 138. Parallel test readiness

Même si pytest-xdist n’est pas utilisé initialement, les tests doivent éviter le state global qui empêcherait l’exécution parallèle.

---

# 139. Filesystem independence

Le Core test suite ne doit pas exiger :

```text
local secrets
user home configuration
network
database
```

---

# 140. Network policy

Les tests du baseline :

```text
NO NETWORK
```

par défaut.

Les futurs tests d’intégration seront explicitement séparés/marked.

---

# 141. Database policy

Le Core local :

```text
NO DATABASE
```

La persistence est représentée par InMemory adapters.

---

# 142. Environment variable policy

Les Domain/Application tests ne doivent pas dépendre de variables d’environnement.

Configuration belongs outside.

---

# 143. Test marks

Future marks possibles :

```text
integration
slow
network
postgresql
```

Pas nécessaires pour le Core pure local.

---

# 144. CI determinism

Un test qui passe seulement selon :

- timezone machine ;
- locale ;
- date courante ;
- order ;
- network ;

est considéré fragile.

---

# 145. Locale independence

Messages métier ne doivent pas être testés en fonction de la locale système.

---

# 146. UUID determinism

Si les Domain constructors génèrent UUID :

- tester type/existence ;
- ou injecter/explicit ID ;

sans hardcoder un UUID aléatoire.

---

# 147. Scenario composition

Le scenario test doit assembler manuellement :

```text
InMemorySupplierRepository
InMemorySupplierRelationshipRepository
InMemorySupplierAssessmentRepository
InMemorySupplierQualificationRepository
FixedClock
InProcessDomainEventDispatcher
QualificationPolicy
Handlers
```

---

# 148. Scenario test is also composition test

Il vérifie implicitement que :

```text
the ports and adapters can actually be wired together
```

sans container.

---

# 149. Example and scenario parity

`examples/local_qualification.py`

et :

```text
tests/scenarios/test_local_supplier_qualification.py
```

doivent suivre le même parcours conceptuel.

L’exemple montre.

Le test garantit.

---

# 150. Test scenario — success

Conceptual flow :

```text
supplier_id = register_supplier(...)

relationship_id = create_relationship(supplier_id, org_id)

invite_relationship(relationship_id)

start_onboarding(relationship_id)

assessment_id = create_assessment(...)

complete_assessment(assessment_id)

qualification_id = request_qualification(...)

decision = evaluate_qualification(qualification_id)

assert decision.approved
assert qualification.status == QUALIFIED
```

---

# 151. Test scenario — rejection

Même flow avec un assessment insuffisant.

Assertions :

```text
decision.approved == False
qualification.status == NOT_QUALIFIED
SupplierQualificationRejected emitted
```

---

# 152. Qualification test matrix

Minimum matrix :

```text
all conditions satisfied
one mandatory condition missing
assessment failed
invalid scope
duplicate current qualification
relationship missing
invalid qualification state
```

---

# 153. Relationship lifecycle test matrix

Minimum :

```text
allowed transitions
forbidden direct skips
suspension
offboarding
reactivation rules if implemented
```

---

# 154. Repository test matrix

For every adapter:

```text
create/save
get
update/save
unknown
domain lookup
isolation
copy semantics
```

---

# 155. Architecture test matrix

```text
domain ↛ application
domain ↛ ports
domain ↛ adapters
application ↛ adapters
ports ↛ adapters
domain ↛ frameworks
```

---

# 156. Testing levels vs ownership

| Test type | Main owner |
|---|---|
| Value Object | Domain |
| Entity/Aggregate | Domain |
| Policy | Domain |
| Domain Event | Domain |
| Handler | Application |
| Repository Contract | Port |
| InMemory Adapter | Adapter |
| Dependency Rule | Architecture |
| Qualification Scenario | Whole local Core |

---

# 157. Test doubles vs ownership

| Dependency | Test double |
|---|---|
| Repository | InMemory Fake |
| Clock | FixedClock |
| Event Dispatcher | InProcess / Recording Fake |
| Future Registry | Stub |
| Future External API | Stub/Fake |
| Complex interaction verification | Mock only if justified |

---

# 158. Test documentation rule

Un test doit être lisible comme une mini-spécification.

Si le test est incompréhensible sans inspecter 10 fixtures, il est trop abstrait.

---

# 159. Domain language in tests

Use :

```text
supplier
relationship
qualification
assessment
scope
activate
suspend
```

not:

```text
obj1
record
payload
data
item
```

---

# 160. Test comments

Comments should explain :

```text
why a business setup matters
```

not repeat code.

---

# 161. Test helper naming

Good:

```text
build_qualified_relationship()
```

Potentially bad:

```text
make_data()
setup_obj()
```

---

# 162. No test-only production backdoors

Avoid production methods such as:

```text
_force_status_for_test()
```

Tests should respect public/domain APIs.

---

# 163. Private field access

Can be tolerated sparingly in architecture/internal mechanism tests.

Not the default for business behavior tests.

---

# 164. Regression tests

Every fixed bug should ideally add a regression test reproducing the previous failure.

---

# 165. Refactoring tests

Do not add tests for code movement.

Existing behavior tests should already protect refactoring.

---

# 166. Contract test reuse

When PostgreSQL appears later :

```text
TestPostgreSQLSupplierRepository
```

must reuse the same:

```text
SupplierRepositoryContract
```

before adapter-specific tests.

---

# 167. Future integration tests

When PostgreSQL appears:

```text
tests/integration/postgresql/
```

can be introduced.

Not before.

---

# 168. Future API tests

When HTTP appears:

```text
tests/interfaces/http/
```

or integration API tests can be introduced.

Not part of baseline.

---

# 169. Future connector tests

Ivalua/SAP/Coupa adapters will require:

```text
contract mapping tests
fixture payload tests
sandbox integration tests
```

when implemented.

---

# 170. Future event-bus tests

If Kafka/Outbox appears:

```text
delivery
serialization
retry
deduplication
```

will receive separate test strategy.

---

# 171. Future performance tests

Not required before actual performance pressure.

---

# 172. Future security tests

Authorization/security integration comes with interface/runtime layer.

Core Domain tests still cover business guards independently.

---

# 173. Test maintenance rule

A test is valuable if it protects:

```text
business behavior
architecture boundary
public contract
regression
```

Delete or simplify tests that only protect accidental implementation details.

---

# 174. Flaky test policy

A flaky Core test is a defect.

Do not "rerun until green" as standard strategy.

---

# 175. Quarantine — not baseline

No need for flaky quarantine system in early Core.

Fix root cause.

---

# 176. CI quality gates — bootstrap target

Candidate:

```text
ruff check .
type checker
pytest --cov
```

Architecture tests are part of pytest.

---

# 177. Coverage gate candidate

Initial:

```text
--cov-fail-under=90
```

only if it does not encourage meaningless tests.

Can start slightly lower during bootstrap and raise with milestones.

---

# 178. Preferred quality gate philosophy

More important than raw coverage:

```text
critical invariant checklist
```

Milestone review should confirm all critical rules are tested.

---

# 179. Milestone test manifest

Each milestone in `13` should include:

```text
Required Test Families
Required Scenario
Required Architecture Gates
Expected Test Count?  [not a target]
Coverage impact
```

Avoid optimizing for number of tests.

---

# 180. Example milestone — Supplier Core

Tests required:

```text
SupplierId VO tests
ExternalIdentifier tests
Supplier Aggregate tests
SupplierCreated event tests
SupplierRepository contract
InMemorySupplierRepository contract execution
RegisterSupplier Handler tests
architecture rules
```

---

# 181. Example milestone — Relationship

Tests required:

```text
RelationshipId
Lifecycle stages
Allowed transitions
Forbidden transitions
events
repository contract
handlers
architecture rules
```

---

# 182. Example milestone — Qualification Domain

Tests required:

```text
QualificationScope
QualificationStatus
QualificationDecision
QualificationPolicy
Qualification Aggregate transitions
Domain Events
```

---

# 183. Example milestone — Qualification Application Flow

Tests required:

```text
request handler
evaluate handler
repository integration via InMemory
event dispatch
application errors
```

---

# 184. Example milestone — Local Core Qualification

Required:

```text
success scenario
rejection scenario
all CI quality gates
```

---

# 185. Testing and semantic versioning

Breaking behavior discovered through tests can inform future versioning.

But release strategy remains deferred.

---

# 186. Test fixtures as documentation

A fixture like:

```text
strategic_supplier_relationship()
```

should only exist when that concept is real.

Fixtures should not invent unsupported business taxonomy.

---

# 187. Test data realism

Use realistic-enough supplier examples, but avoid tying generic Core rules to one company or country.

---

# 188. Multi-country tests

At minimum, test that core types do not assume France-only rules where the model claims agnosticism.

Example:

```text
CountryCode("DE")
```

should be as structurally valid as:

```text
CountryCode("FR")
```

if ISO codes are the model.

---

# 189. Multi-organization tests

Critical scenario :

```text
Supplier S
Relationship R1 with Org A = ACTIVE/QUALIFIED
Relationship R2 with Org B = different state
```

Changes to R1 must not modify R2.

---

# 190. Aggregate isolation test

This is one of the most important architectural domain tests.

---

# 191. Cross-aggregate mutation test

Incident/Assessment/Qualification should not secretly mutate another Aggregate without application orchestration.

Can be tested indirectly via absence of state change.

---

# 192. Query tests — MVP

Queries are secondary before qualification.

For implemented Queries, test:

```text
no mutation
correct read result
not found semantics
```

---

# 193. Command tests vs Handler tests

Command dataclasses usually need little direct testing unless they validate application-level structure.

Focus on Handler and Domain behavior.

---

# 194. DTO tests

Do not test passive dataclasses mechanically.

Test mapping/validation behavior if non-trivial.

---

# 195. Mapper tests — future

Only once adapters introduce real mappings.

---

# 196. Serialization tests — future

Domain objects need not be JSON serializable by default.

Serialization contract tests belong to adapters/interfaces.

---

# 197. Public API tests — future

When stable imports are defined:

```text
import surface
deprecation
public symbols
```

can be tested.

---

# 198. Package import smoke test

At bootstrap:

```python
import pysrmkit
```

must succeed without side effects.

---

# 199. No-network smoke test

Importing package must not attempt external connections.

---

# 200. Test execution order

The suite must pass independently of random/order changes.

Optional future:

```text
pytest-randomly
```

if useful.

Not mandatory.

---

# 201. Test collection simplicity

Avoid dynamic test generation frameworks beyond pytest parametrization.

---

# 202. Pytest plugins

Keep plugin footprint small.

Likely initial:

```text
pytest
pytest-cov
```

No broad plugin stack before need.

---

# 203. Async testing — deferred

No `pytest-asyncio` unless async APIs appear.

---

# 204. Database containers — deferred

No Testcontainers before PostgreSQL milestone.

---

# 205. Test contracts as executable docs

The repository contract tests should be readable enough that a future adapter implementer can understand expected semantics directly from the tests.

---

# 206. Learning Map — Aggregate test

```text
Invariant
    │
    ▼
Test expresses forbidden behavior
    │
    ▼
Aggregate enforces rule
    │
    ▼
Domain Error
```

---

# 207. Learning Map — Policy test

```text
Business variation
    │
    ▼
Policy / Strategy
    │
    ▼
Input Context
    │
    ▼
Decision
    │
    ▼
Behavior Tests
```

---

# 208. Learning Map — Repository contract

```text
Repository Port
    │
    ▼
Shared Contract Tests
    │
    ├── InMemory Adapter
    └── PostgreSQL Adapter later
    │
    ▼
Liskov Substitution
```

---

# 209. Learning Map — Architecture test

```text
Dependency rule
    │
    ▼
Executable fitness function
    │
    ▼
Violation fails CI
```

---

# 210. Learning Map — Scenario test

```text
Business flow
    │
    ▼
Commands / Handlers
    │
    ▼
Domain
    │
    ▼
Ports / InMemory Adapters
    │
    ▼
Outcome
```

---

# 211. Anti-pattern — test everything through scenarios

Rejected.

Why:

- slow diagnosis ;
- huge setup ;
- poor edge case coverage ;
- brittle tests.

---
# 212. Anti-pattern — mock everything

Rejected.

Why:

- tests implementation details ;
- low confidence in composition ;
- easy to satisfy with wrong architecture.

---

# 213. Anti-pattern — only happy path

Rejected.

Critical negative paths are essential for domain modeling.

---

# 214. Anti-pattern — line coverage as quality

Rejected.

Coverage is a signal, not proof.

---

# 215. Anti-pattern — test private methods directly

Avoid unless internal mechanism is itself the contract.

---

# 216. Anti-pattern — shared global fixtures

Avoid mutable global test state.

---

# 217. Anti-pattern — random current time

Avoid `datetime.now()` directly in tests.

---

# 218. Anti-pattern — DB in every test

The Core should prove most behavior without persistence technology.

---

# 219. Anti-pattern — tests reproduce implementation

If the test implements the same `if` logic as the policy, it may repeat the bug.

Test business examples instead.

---

# 220. Anti-pattern — tests named after methods

Prefer business behavior over method names when possible.

---

# 221. Anti-pattern — fake not respecting contract

An InMemory fake that behaves differently from real persistence can invalidate tests.

Hence contract tests.

---

# 222. Anti-pattern — architecture rules only in docs

Dependency rules must be executable.

---

# 223. Anti-pattern — fixture abstraction too early

Avoid complex factories before repetition exists.

---

# 224. Testing Design Concepts Applied

```text
[PRINCIPLE: SRP]
[PRINCIPLE: DIP]
[PRINCIPLE: LSP]
[PRINCIPLE: Information Hiding]
[DDD: Aggregate]
[DDD: Value Object]
[DDD: Domain Event]
[DDD: Repository]
[PATTERN: Strategy]
[ARCH: Ports & Adapters]
[ARCH: Architecture Fitness Functions]
```

---

# 225. Core Testing Baseline

Before bootstrap implementation begins, the project accepts the following as its initial testing baseline:

```text
pytest
pytest-cov
ruff
pyright or mypy
architecture dependency checks
```

Exact versions/tool choice are fixed in the Bootstrap Plan.

---

# 226. Testing Definition of Done — per behavior

A new business behavior is done when:

```text
[ ] positive path tested
[ ] relevant negative path tested
[ ] invariant protected
[ ] event semantics tested if event exists
[ ] handler orchestration tested if application use case exists
[ ] architecture rules remain green
```

---

# 227. Testing Definition of Done — Repository Adapter

```text
[ ] implements Port
[ ] shared contract suite passes
[ ] adapter-specific edge cases pass
[ ] no infrastructure type leaks into Port
```

---

# 228. Testing Definition of Done — Milestone

```text
[ ] milestone behaviors implemented
[ ] unit tests green
[ ] application tests green
[ ] contract tests green
[ ] architecture tests green
[ ] scenario test updated where applicable
[ ] lint green
[ ] type check green
[ ] coverage remains acceptable
```

---

# 229. First Core Qualification Gate

The first local qualification milestone is considered qualified when:

```text
[ ] RegisterSupplier works
[ ] SupplierRelationship creation works
[ ] lifecycle progression works
[ ] Assessment creation/completion works
[ ] Qualification request works
[ ] QualificationPolicy returns explicit decision
[ ] approved qualification reaches QUALIFIED
[ ] rejected qualification reaches NOT_QUALIFIED
[ ] Domain Events are correct
[ ] InMemory repositories pass contract tests
[ ] application handlers pass
[ ] architecture rules pass
[ ] success scenario passes
[ ] rejection scenario passes
[ ] full pytest suite passes locally
```

---

# 230. Optional activation gate

If activation is included in the same early iteration:

```text
[ ] ActivationPolicy tested
[ ] relationship activation tested
[ ] invalid activation tested
[ ] SupplierActivated event tested
```

Not required for the first qualification cutoff.

---

# 231. Test report philosophy

The meaningful report is:

```text
which capabilities and invariants are protected
```

not:

```text
we have N tests.
```

---

# 232. Test count

No target number of tests.

A small precise suite is better than many redundant tests.

---

# 233. Evolution after bootstrap

Testing strategy expands only with implementation pressure.

Examples:

```text
PostgreSQL
    → integration + migration tests

HTTP
    → contract/API tests

Kafka
    → serialization/delivery tests

Ivalua
    → mapping + sandbox integration tests

Concurrency
    → conflict tests
```

---

# 234. Future testing documents

A separate Deep Dive may later be useful for:

```text
Persistence Testing
Connector Contract Testing
Integration Event Testing
Performance Testing
Security Testing
```

Not required now.

---

# 235. Testing and documentation loop

```text
SPEC
    │
    ▼
TEST
    │
    ▼
IMPLEMENTATION
    │
    ▼
FAILURE / FRICTION
    │
    ▼
REFINE SPEC
    │
    ▼
REFINE TEST
```

---

# 236. Testing north star

```text
DOMAIN RULE
    │
    ▼
FOCUSED TEST
    │
    ▼
IMPLEMENTATION
    │
    ▼
REGRESSION PROTECTION
```

---

# 237. Quality north star

The Core should be safe to refactor because:

```text
business semantics are tested
port behavior is tested
dependency direction is tested
end-to-end local scenario is tested
```

---

# 238. Final principles

> **Test behavior, not incidental implementation.**

> **Every critical invariant deserves an executable example.**

> **Every Repository adapter must pass the same contract.**

> **Architecture rules belong in CI, not only in diagrams.**

> **Scenario tests prove composition; unit tests prove semantics.**

> **Fakes are preferred when they provide more confidence than mocks.**

> **Coverage is useful, but critical behavior coverage matters more.**

> **The Core test suite must stay deterministic, local and fast.**

---

# 239. Next mandatory document

The next mandatory pre-bootstrap document is:

> **`13_PYSRMKIT_IMPLEMENTATION_ROADMAP.md`**

It must transform the architecture and testing baseline into executable milestones such as:

```text
0.1.0a1 — Repository Bootstrap
0.1.0a2 — Supplier Core
0.1.0a3 — Supplier Relationships
0.1.0a4 — Lifecycle
0.1.0a5 — Onboarding Core
0.1.0a6 — Qualification Domain
0.1.0a7 — Qualification Application Flow
0.1.0a8 — Local Core Qualification
```

Each milestone must define its own testing gate.

---

# 240. Conclusion

PySRMKit adopts a testing strategy in which tests are simultaneously:

```text
correctness mechanism
architecture protection
domain specification
regression safety net
pedagogical repetition
```

The first Core is intentionally qualified without external infrastructure.

Its confidence comes from:

```text
Domain Unit Tests
+
Invariant Tests
+
State Transition Tests
+
Policy Tests
+
Domain Event Tests
+
Application Handler Tests
+
Repository Contract Tests
+
Architecture Tests
+
Local Scenario Tests
```

This strategy turns the project’s software-design principles into executable constraints.

The final principle is:

> **If a rule matters enough to shape the architecture or the business model, it matters enough to be made executable in a test.**