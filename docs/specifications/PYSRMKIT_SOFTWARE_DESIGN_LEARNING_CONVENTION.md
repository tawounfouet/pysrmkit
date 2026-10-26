# PySRMKit — Software Design Learning Convention

**Document :** `PYSRMKIT_SOFTWARE_DESIGN_LEARNING_CONVENTION.md`  
**Projet :** PySRMKit  
**Domaine :** Supplier Relationship Management / Software Design  
**Type :** Convention d'apprentissage, de conception et de documentation  
**Statut :** Convention fondatrice  
**Version du document :** 0.1.0  
**Portée :** Spécifications, architecture, code, docstrings, commentaires, tests, revues et documentation pédagogique

---

# 1. Objet du document

Ce document formalise une intuition structurante pour PySRMKit :

> **Utiliser le développement réel du framework comme support de pratique délibérée de la conception logicielle.**

L'objectif n'est pas seulement de construire un framework Supplier Relationship Management.

L'objectif est également d'utiliser PySRMKit comme un terrain d'apprentissage continu permettant de manipuler, dans un contexte réel :

- les concepts du domaine ;
- le Domain-Driven Design ;
- les principes de conception ;
- les design patterns ;
- les architectural patterns ;
- les primitives Python ;
- les pratiques de test ;
- les mécanismes d'intégration ;
- les choix d'architecture ;
- les compromis de conception.

L'apprentissage recherché ne repose pas principalement sur la mémorisation de définitions isolées.

Il repose sur :

```text
rencontrer
→ comprendre
→ nommer
→ appliquer
→ tester
→ documenter
→ revoir
→ réutiliser
→ intérioriser
```

---

# 2. Intuition fondatrice

Dans les préparations classiques aux entretiens techniques, les concepts sont souvent étudiés sous forme de listes :

```text
SOLID
Strategy
Factory
Adapter
Observer
CQRS
Hexagonal Architecture
Repository
Aggregate
Value Object
...
```

Cette approche permet de connaître les définitions.

Elle ne garantit cependant pas la capacité à reconnaître :

- quand un concept devient pertinent ;
- pourquoi il est pertinent ;
- quel problème il résout ;
- quelles alternatives existaient ;
- quand il ne faut pas l'utiliser ;
- comment il se matérialise dans un vrai codebase.

PySRMKit adopte une approche inverse.

```text
PROBLÈME RÉEL
    │
    ▼
CONTRAINTE
    │
    ▼
PRINCIPE
    │
    ▼
PATTERN ÉVENTUEL
    │
    ▼
MODÈLE
    │
    ▼
IMPLÉMENTATION
    │
    ▼
TEST
    │
    ▼
RÉTROACTION
```

Le concept de conception est appris **dans son contexte d'apparition**.

---

# 3. Objectif pédagogique

L'objectif pédagogique est de passer progressivement de :

```text
"Je connais la définition de Strategy."
```

à :

```text
"Je reconnais immédiatement une variation d'algorithme
qui doit être encapsulée derrière une abstraction stable."
```

Puis à :

```text
"Je sais aussi quand Strategy serait excessif
et qu'une simple fonction suffit."
```

L'apprentissage recherché est donc une transformation :

```text
connaissance déclarative
        ↓
compréhension contextuelle
        ↓
reconnaissance de forme
        ↓
intuition de conception
        ↓
jugement d'ingénierie
```

---

# 4. PySRMKit comme projet-école de production

PySRMKit doit conserver une double nature.

## 4.1 Framework réel

Il doit rester :

- cohérent ;
- maintenable ;
- testable ;
- extensible ;
- réutilisable ;
- publiable ;
- utilisable dans des applications réelles.

## 4.2 Support de pratique délibérée

Il doit également permettre de manipuler consciemment :

```text
DDD
SOLID
DRY
KISS
YAGNI
Separation of Concerns
Information Hiding
Dependency Inversion
Design Patterns
Architectural Patterns
Testing Patterns
Python idioms
```

Ces deux objectifs ne doivent pas entrer en contradiction.

Le projet pédagogique ne doit jamais dégrader la qualité du produit.

---

# 5. Principe directeur

La règle fondamentale est :

> **On ne choisit jamais un pattern pour apprendre le pattern. On identifie le pattern lorsqu'il émerge naturellement d'un problème réel.**

Ainsi :

```text
BAD

"We need to use Strategy somewhere
because we want to practice Strategy."
```

devient :

```text
GOOD

"Qualification rules vary by organization
while the caller should remain stable.

This is a variation-of-algorithm problem.

Strategy is an appropriate model."
```

---

# 6. Anti-Cargo-Cult Principle

PySRMKit doit explicitement éviter le **pattern cargo cult**.

Un pattern ne doit jamais être introduit uniquement parce qu'il :

- est connu ;
- est populaire ;
- apparaît dans les livres ;
- est demandé en entretien ;
- est considéré comme "senior" ;
- semble architecturalement élégant.

Pour chaque pattern ou principe mentionné, la documentation doit pouvoir répondre à :

```text
1. Quel problème existe réellement ?
2. Quelle variation ou contrainte observons-nous ?
3. Pourquoi une solution simple ne suffit-elle plus ?
4. Quel concept résout cette difficulté ?
5. Quelles alternatives ont été envisagées ?
6. Quel coût supplémentaire introduisons-nous ?
```

---

# 7. KISS et YAGNI comme contrepoids

L'apprentissage des patterns doit être équilibré par :

- **KISS** — Keep It Simple;
- **YAGNI** — You Aren't Gonna Need It.

Ces principes empêchent PySRMKit de devenir un catalogue artificiel de patterns.

Exemples :

```text
Si une fonction pure suffit
→ ne pas créer une hiérarchie Strategy.

Si un constructeur suffit
→ ne pas créer une Factory abstraite.

Si deux branches explicites suffisent
→ ne pas créer une Chain of Responsibility.

Si un callback simple suffit
→ ne pas créer un Observer framework.
```

L'apprentissage comprend donc aussi :

> **savoir ne pas appliquer un pattern.**

---

# 8. Noms naturels avant noms de patterns

Le code doit utiliser des noms correspondant :

- au domaine ;
- à la responsabilité ;
- à l'intention.

Il ne doit pas utiliser le nom du pattern comme substitut à un vrai nom.

## Mauvais exemple

```python
class QualificationStrategyPattern:
    ...
```

## Bon exemple

```python
class QualificationPolicy:
    ...
```

Le pattern peut être documenté :

```python
class QualificationPolicy(Protocol):
    """
    Defines a replaceable supplier qualification policy.

    Design concepts:
        - Strategy Pattern
        - Dependency Inversion Principle
        - Open/Closed Principle

    Domain role:
        Encapsulates organization-specific qualification rules.
    """
```

Règle :

> **Le nom du code exprime le métier ou l'intention.  
> La documentation exprime les concepts de conception utilisés.**

---

# 9. Niveaux d'analyse d'un concept

Chaque composant significatif peut être étudié selon plusieurs niveaux.

```text
1. Métier / Domaine
2. DDD
3. Principes de conception
4. Design Patterns
5. Architecture
6. Python
7. Testing
8. Runtime / Infrastructure
```

---

# 10. Niveau 1 — Métier / Domaine

Première question :

> Quel problème métier ce composant représente-t-il ?

Exemples :

```text
Supplier
Qualification
Risk
Certification
Assessment
SupplierRelationship
```

Questions :

- quelle réalité métier est modélisée ?
- quelle règle existe ?
- quelle décision doit être prise ?
- quel invariant doit être protégé ?

Le raisonnement ne doit pas commencer par la technologie.

---

# 11. Niveau 2 — DDD

Une fois le problème métier identifié, on demande :

> Quel building block DDD correspond à cette responsabilité ?

Possibilités :

```text
Entity
Value Object
Aggregate
Aggregate Root
Domain Service
Domain Policy
Domain Event
Repository
Factory
Specification
Bounded Context
Anti-Corruption Layer
```

Le pattern DDD doit être justifié par la responsabilité métier.

---

# 12. Niveau 3 — Principes de conception

On identifie ensuite les principes qui guident la solution.

Principes possibles :

```text
Single Responsibility Principle
Open/Closed Principle
Liskov Substitution Principle
Interface Segregation Principle
Dependency Inversion Principle

DRY
KISS
YAGNI

Separation of Concerns
Information Hiding
Encapsulation
High Cohesion
Low Coupling
Composition over Inheritance
Explicit Dependencies
```

Le principe doit expliquer une propriété de la conception.

---

# 13. Niveau 4 — Design Patterns

Les patterns GoF ou assimilés ne sont utilisés que lorsqu'ils correspondent réellement au problème.

Familles principales :

## Creational

```text
Factory Method
Abstract Factory
Builder
Prototype
Singleton
```

## Structural

```text
Adapter
Bridge
Composite
Decorator
Facade
Flyweight
Proxy
```

## Behavioral

```text
Strategy
Observer
Command
State
Iterator
Mediator
Chain of Responsibility
Template Method
Visitor
```

PySRMKit ne cherchera pas à tous les utiliser.

---

# 14. Niveau 5 — Architectural Patterns

Certains problèmes concernent l'organisation globale du système.

Patterns potentiellement pertinents :

```text
Layered Architecture
Hexagonal Architecture
Ports and Adapters
Clean Architecture
CQRS
Event-Driven Architecture
Modular Monolith
Microservices
Event Sourcing
```

Une distinction doit être maintenue entre :

```text
design pattern
```

et :

```text
architectural pattern
```

---

# 15. Niveau 6 — Mécanismes Python

Une conception abstraite doit finalement être matérialisée dans le langage.

Mécanismes potentiels :

```text
Protocol
ABC
dataclass
frozen dataclass
Enum
Generic
TypeVar
Callable
Context Manager
Iterator
Generator
Descriptor
Exception hierarchy
Composition
Delegation
Dependency Injection
```

L'apprentissage doit relier :

```text
concept architectural
        ↓
abstraction de conception
        ↓
mécanisme Python concret
```

---

# 16. Niveau 7 — Testing

Le test fait partie de la compréhension du design.

Types de tests :

```text
Domain Unit Test
Invariant Test
Policy Test
Contract Test
Application Test
Integration Test
Architecture Test
Property-Based Test
State Transition Test
```

Un concept non testable est souvent un concept encore mal isolé.

---

# 17. Niveau 8 — Runtime et infrastructure

Enfin, la conception peut être observée dans son environnement d'exécution :

```text
Persistence
Network
Messaging
Concurrency
Async
Threads
Processes
Scheduling
Runtime
OS
Cloud
```

Cette couche doit rester clairement distinguée du domaine.

---

# 18. La chaîne d'apprentissage de référence

PySRMKit utilisera cette chaîne comme modèle pédagogique :

```text
PROBLÈME MÉTIER
        │
        ▼
CONCEPT DU DOMAINE
        │
        ▼
INVARIANT / VARIATION
        │
        ▼
PRINCIPE DE CONCEPTION
        │
        ▼
PATTERN ÉVENTUEL
        │
        ▼
DDD ROLE
        │
        ▼
MÉCANISME PYTHON
        │
        ▼
OBJET DU CODE
        │
        ▼
TEST
        │
        ▼
DOCUMENTATION
```

---

# 19. Exemple de référence — Qualification

## 19.1 Problème métier

Chaque organisation peut appliquer ses propres critères de qualification fournisseur.

Exemples :

```text
Financial qualification
Cybersecurity qualification
Construction qualification
ESG qualification
```

## 19.2 Variation

L'algorithme de décision varie.

Le consommateur doit cependant pouvoir utiliser une interface stable.

## 19.3 Principes

```text
Open/Closed Principle
Dependency Inversion Principle
Single Responsibility Principle
```

## 19.4 Pattern

```text
Strategy Pattern
```

## 19.5 DDD

```text
Domain Policy
```

## 19.6 Python

```text
Protocol
```

## 19.7 Objet métier

```text
QualificationPolicy
```

## 19.8 Implémentations possibles

```text
DefaultQualificationPolicy
CybersecurityQualificationPolicy
ConstructionQualificationPolicy
CustomOrganizationQualificationPolicy
```

---

# 20. Exemple de référence — Repository

## Problème

Le domaine doit charger et sauvegarder des Suppliers sans dépendre de la technologie de stockage.

## Principe

```text
Dependency Inversion Principle
Separation of Concerns
Information Hiding
```

## Pattern

```text
Repository Pattern
```

## Architecture

```text
Ports and Adapters
Hexagonal Architecture
```

## Python

```text
Protocol
```

## Objet

```text
SupplierRepository
```

## Implémentations

```text
InMemorySupplierRepository
PostgreSQLSupplierRepository
MongoSupplierRepository
```

---

# 21. Exemple de référence — Adapter

## Problème

Le modèle d'un système externe diffère du modèle canonique PySRMKit.

Exemple :

```text
Ivalua Supplier JSON
```

ne doit pas devenir directement :

```text
Supplier
```

## Principe

```text
Dependency Inversion
Information Hiding
Separation of Concerns
```

## Pattern

```text
Adapter
```

## DDD

```text
Anti-Corruption Layer
```

## Objet

```text
IvaluaSupplierAdapter
```

---

# 22. Exemple de référence — Lifecycle

Le vocabulaire doit être précis.

PySRMKit possède un :

```text
Supplier Lifecycle State Machine
```

Cela ne signifie pas automatiquement que l'implémentation utilisera :

```text
GoF State Pattern
```

Les deux concepts sont différents.

## State Machine

Décrit :

```text
states
transitions
guards
```

## State Pattern

Déplace les comportements dépendant de l'état dans des objets représentant les états.

PySRMKit doit documenter explicitement cette distinction.

---

# 23. Exemple de référence — Command

De même :

```text
ActivateSupplierCommand
```

dans une architecture CQRS

n'implique pas automatiquement :

```text
GoF Command Pattern
```

Les termes se ressemblent mais les niveaux d'abstraction diffèrent.

La documentation devra préciser :

```text
CQRS Command
```

ou :

```text
GoF Command Pattern
```

lorsque nécessaire.

---

# 24. Exemple de référence — Domain Event

```text
SupplierQualified
```

est un :

```text
Domain Event
```

Il ne signifie pas automatiquement :

```text
Observer Pattern
```

Un Domain Event exprime un fait métier.

Observer décrit une structure de notification entre objets.

Une implémentation peut utiliser Observer, mais ce n'est pas une identité conceptuelle.

---

# 25. Convention documentaire

À partir de ce document, les spécifications significatives de PySRMKit pourront utiliser une section standard :

```text
DESIGN CONCEPTS APPLIED
```

Exemple :

```markdown
## Design Concepts Applied

### Domain / DDD
- Domain Policy

### Principles
- Open/Closed Principle
- Dependency Inversion Principle

### Design Pattern
- Strategy

### Python Mechanism
- Protocol

### Why
Qualification rules vary by organization while consumers
must remain independent of concrete implementations.
```

Cette section n'est ajoutée que si elle apporte réellement de la valeur.

---

# 26. Convention pour les docstrings

Les classes structurantes peuvent utiliser un bloc de documentation du type :

```python
class QualificationPolicy(Protocol):
    """
    Evaluate whether a supplier satisfies qualification requirements.

    Domain role:
        Domain Policy.

    Design:
        - Strategy Pattern
        - Open/Closed Principle
        - Dependency Inversion Principle

    Rationale:
        Qualification rules vary by organization while callers
        depend on a stable contract.
    """
```

Les docstrings ne doivent pas devenir des dissertations.

Elles doivent conserver :

- responsabilité ;
- contrat ;
- concept ;
- justification utile.

---

# 27. Convention pour les commentaires

Les commentaires doivent expliquer :

```text
WHY
```

plutôt que :

```text
WHAT
```

Mauvais :

```python
# Loop over qualifications.
for qualification in qualifications:
    ...
```

Meilleur :

```python
# Keep qualification evaluation independent from supplier lifecycle
# so organizations can replace the policy without changing the aggregate.
```

Les concepts de design doivent apparaître uniquement lorsqu'ils expliquent un choix non évident.

---

# 28. Convention de nommage

Les noms doivent suivre la sémantique réelle.

Préférer :

```text
QualificationPolicy
SupplierRepository
RiskAssessment
SupplierLifecycle
SupplierFactory
IvaluaSupplierAdapter
```

à :

```text
StrategyManager
RepositoryImplPatternFactory
StateHandler
DomainHelper
GenericService
```

Le pattern est une propriété de la conception.

Il n'est pas nécessairement le nom de l'objet.

---

# 29. Convention pour les tests

Les tests doivent aussi rendre les concepts visibles.

## Invariant

```python
def test_supplier_cannot_activate_without_required_qualification():
    ...
```

## State Transition

```python
def test_offboarded_supplier_cannot_transition_to_active():
    ...
```

## Policy

```python
def test_cybersecurity_policy_requires_iso_27001():
    ...
```

## Repository Contract

```python
def test_repository_can_round_trip_supplier():
    ...
```

## Architecture Rule

```text
domain must not import SQLAlchemy
domain must not import FastAPI
domain must not import Kafka clients
```

Ainsi, les tests deviennent aussi un support d'apprentissage architectural.

---

# 30. Architecture Fitness Functions

Certaines conventions pourront être automatisées.

Exemples :

```text
DOMAIN
must not depend on
INFRASTRUCTURE
```

```text
DOMAIN
must not import
sqlalchemy
fastapi
boto3
azure
kafka
```

```text
ADAPTERS
may depend on
PORTS
```

```text
APPLICATION
may depend on
DOMAIN
```

Ces règles rendent les principes architecturalement exécutables.

---

# 31. Learning Tags

Lorsqu'il est utile d'identifier explicitement un concept dans une spécification, la convention suivante pourra être utilisée :

```text
[DDD: Domain Policy]
[PRINCIPLE: Dependency Inversion]
[PATTERN: Strategy]
[ARCH: Ports and Adapters]
[PYTHON: Protocol]
[TEST: Contract Test]
```

Ces tags sont destinés principalement :

- aux documents pédagogiques ;
- aux deep dives ;
- aux ADR ;
- aux code reviews pédagogiques.

Ils ne doivent pas envahir chaque ligne du code.

---

# 32. Design Decision Record

Une décision importante pourra suivre ce format :

```text
CONTEXT
What problem are we solving?

FORCES
What constraints and variations exist?

DECISION
What design was selected?

CONCEPTS
Which principles/patterns apply?

ALTERNATIVES
What else could have been done?

CONSEQUENCES
What do we gain and what do we pay?
```

Cette convention permet d'apprendre non seulement le résultat mais le raisonnement de conception.

---

# 33. Problem Before Pattern

Cette règle doit apparaître dans toutes les discussions de design :

```text
PROBLEM
    ↓
FORCES
    ↓
SIMPLE SOLUTION?
    ↓
PATTERN IF NEEDED
```

Jamais :

```text
PATTERN
    ↓
Find somewhere to use it
```

---

# 34. Pattern Evidence

Un pattern peut être considéré comme réellement présent lorsqu'il existe une preuve observable.

Exemple Strategy :

```text
- family of interchangeable behaviors;
- stable consumer;
- behavior selected independently;
- implementations satisfy same contract.
```

Si ces caractéristiques n'existent pas, il ne faut pas étiqueter artificiellement le code "Strategy".

---

# 35. Principle Evidence

Même règle pour SOLID.

Par exemple, dire qu'un code applique DIP suppose réellement :

```text
High-level policy
    depends on abstraction

Low-level detail
    implements abstraction
```

Il ne suffit pas d'avoir créé une interface.

---

# 36. Apprentissage par répétition distribuée

La répétition sera naturellement distribuée dans plusieurs domaines.

Exemple :

```text
Strategy
    ↓
QualificationPolicy
RiskPolicy
SegmentationPolicy
PerformancePolicy
```

Puis dans d'autres Py*Kit :

```text
PricingPolicy
AllocationPolicy
RetryPolicy
SchedulingPolicy
```

La répétition à travers des contextes différents permet de généraliser le concept.

---

# 37. Transfert inter-projets

L'objectif n'est pas seulement d'apprendre PySRMKit.

Il est de pouvoir transférer les formes reconnues vers :

```text
PyCRMKit
PyAccountingKit
PyProcurementKit
PyContractKit
PyRuntimeKit
PyAgentsKit
PyScheduleKit
```

Un concept est réellement intériorisé lorsqu'il est reconnu dans un nouveau domaine sans avoir besoin d'une fiche de révision.

---

# 38. Boucle d'apprentissage

Pour chaque sujet important :

```text
1. Observe a real problem
2. Formulate the problem
3. Identify forces
4. Propose simplest valid solution
5. Identify applicable principles
6. Identify pattern if one truly exists
7. Implement
8. Test
9. Document
10. Review after usage
11. Refactor if necessary
12. Reuse the mental model elsewhere
```

---

# 39. Revue après implémentation

Une fois une capacité implémentée, une revue pédagogique peut répondre à :

```text
What problem did we solve?

Which concepts emerged?

Which principle mattered most?

Which pattern did we actually use?

Which pattern did we deliberately avoid?

What Python feature expressed the design?

What test protects the design?

What would we do differently now?
```

---

# 40. Niveau d'explicitation selon le contexte

Tous les artefacts n'ont pas besoin du même niveau pédagogique.

## Specs

Fort niveau d'explication.

## ADR

Très fort niveau de justification.

## Domain docs

Fort niveau de vocabulaire DDD.

## Docstrings

Court et ciblé.

## Code

Noms naturels.

## Comments

Seulement pour les décisions non évidentes.

## Tests

Noms comportementaux.

## README public

Pédagogie utile sans surcharge académique.

---

# 41. Taxonomie de référence

PySRMKit maintiendra progressivement une taxonomie des concepts réellement utilisés.

Exemple :

```text
DOMAIN MODELING
├── Entity
├── Value Object
├── Aggregate
├── Aggregate Root
├── Domain Service
├── Domain Policy
├── Domain Event
├── Repository
└── Factory

PRINCIPLES
├── SOLID
├── DRY
├── KISS
├── YAGNI
├── Separation of Concerns
├── Information Hiding
└── Composition over Inheritance

DESIGN PATTERNS
├── Strategy
├── Adapter
├── Factory
├── State        [only if truly implemented]
└── Observer     [only if truly implemented]

ARCHITECTURE
├── Hexagonal
├── Clean Architecture
├── CQRS-friendly
├── Event-Driven
└── Modular Monolith friendly
```

Cette taxonomie doit refléter l'implémentation réelle.

---

# 42. Concepts à ne pas confondre

Une partie importante de l'apprentissage consiste à distinguer les homonymes.

```text
State Machine
≠
GoF State Pattern
```

```text
CQRS Command
≠
GoF Command Pattern
```

```text
Domain Event
≠
Observer Pattern
```

```text
Repository DDD
≠
Generic Data Access Repository
```

```text
Domain Service
≠
Application Service
```

```text
Factory DDD
≠
Every helper that creates an object
```

```text
Dependency Injection
≠
Dependency Inversion
```

```text
Event-Driven Architecture
≠
Event Sourcing
```

Cette distinction doit être explicitement documentée lorsqu'une ambiguïté est probable.

---

# 43. Architecture et patterns comme vocabulaire vivant

Le but final est que le vocabulaire architectural devienne naturel.

Exemple :

```text
"This rule varies by organization."
    → policy / strategy candidate

"This external model leaks into our domain."
    → adapter / anti-corruption layer

"These objects must remain transactionally consistent."
    → aggregate boundary question

"This use case only coordinates domain operations."
    → application service

"This behavior does not belong naturally to one entity."
    → domain service candidate

"We need to react after a meaningful business change."
    → domain event
```

Cette capacité de reconnaissance est l'objectif pédagogique réel.

---

# 44. Relation avec les entretiens techniques

Cette convention ne vise pas directement les entretiens.

Cependant, elle doit produire un effet secondaire utile.

Au lieu de répondre :

> "Strategy permet d'encapsuler une famille d'algorithmes interchangeables."

il devient possible de répondre :

> "Dans PySRMKit, nous l'utilisons pour les QualificationPolicy car les critères varient selon l'organisation tandis que l'application dépend d'un contrat stable. Cela nous permet de respecter OCP et DIP sans polluer le Supplier aggregate avec des branches spécifiques."

La connaissance devient :

```text
définition
+
expérience
+
trade-offs
+
exemple réel
```

---

# 45. Documentation comme mécanisme d'apprentissage

La documentation n'est pas uniquement destinée aux utilisateurs externes.

Elle sert aussi à :

- rendre le raisonnement explicite ;
- stabiliser le vocabulaire ;
- détecter les confusions ;
- créer une mémoire du design ;
- faciliter la revue ;
- renforcer la répétition.

Écrire :

```text
Why is this Strategy?
```

oblige à vérifier que le pattern est réellement présent.

---

# 46. Code review comme répétition

Les revues de code pourront inclure des questions comme :

```text
What responsibility does this object own?

Is this domain or application logic?

Which invariant is protected?

Is this variation stable enough to justify a Strategy?

Is the interface expressing DIP or just adding ceremony?

Could composition be simpler than inheritance?

Is this abstraction needed today?

Does this adapter prevent model leakage?
```

Ces questions deviennent progressivement des réflexes.

---

# 47. Refactoring comme apprentissage

Un pattern n'a pas nécessairement besoin d'être anticipé.

Il peut émerger après répétition.

Exemple :

```text
v1
simple conditional
```

puis :

```text
v2
several qualification variants
```

puis :

```text
v3
extract QualificationPolicy
```

Ce chemin est pédagogiquement important.

Il montre **pourquoi** le pattern devient nécessaire.

---

# 48. Pattern Evolution Log

Pour certains composants majeurs, la documentation pourra conserver une courte évolution :

```text
Initial design:
simple conditional

Observed pressure:
5 qualification variants

Refactoring:
Strategy via QualificationPolicy

Result:
stable consumer, replaceable policy implementations
```

Cela rend visible la naissance du pattern.

---

# 49. Conventions pour les prochains documents PySRMKit

À partir de `03_PYSRMKIT_SYSTEM_ARCHITECTURE.md`, les documents devront, lorsque pertinent, préciser :

```text
Problem
Design decision
DDD concepts
Principles
Patterns
Python mechanism
Trade-offs
Testing implication
```

Ils ne doivent pas se limiter à :

```text
"We use Hexagonal Architecture."
```

Ils doivent expliquer :

```text
why
where
how
and with what consequence.
```

---

# 50. Application au futur document 03

`03_PYSRMKIT_SYSTEM_ARCHITECTURE.md` devra notamment rendre explicites :

## Hexagonal / Ports and Adapters

Pourquoi :

```text
isoler le domaine des technologies externes
```

## Dependency Inversion

Matérialisation :

```text
ports defined inward
adapters implemented outward
```

## Layering

Séparation :

```text
Domain
Application
Ports
Adapters
Interfaces
```

## CQRS

Préciser :

```text
friendly
optional
not necessarily full CQRS
```

## Event-Driven

Préciser :

```text
domain events first
transport later
```

---

# 51. Application aux futurs Domain Objects

Les documents :

```text
04_PYSRMKIT_DOMAIN_OBJECTS.md
05_PYSRMKIT_ENTITIES_AND_VALUE_OBJECTS.md
```

devront explicitement identifier :

```text
Entity
Value Object
Aggregate
Aggregate Root
Domain Service
Domain Policy
Factory
Repository
```

avec justification.

---

# 52. Application aux invariants

`07_PYSRMKIT_DOMAIN_INVARIANTS_AND_BUSINESS_RULES.md` devra notamment manipuler :

```text
Encapsulation
Information Hiding
Design by Contract
Tell, Don't Ask
Invariant
Policy
Specification
```

uniquement lorsqu'ils sont effectivement pertinents.

---

# 53. Application aux Commands / Queries

`08_PYSRMKIT_COMMANDS_QUERIES_AND_USE_CASES.md` devra distinguer :

```text
Application Command
Application Query
Command Handler
Application Service
Domain Operation
CQRS
GoF Command Pattern
```

afin d'éviter les confusions de vocabulaire.

---

# 54. Application aux adapters

Les futurs documents d'intégration devront manipuler explicitement :

```text
Adapter Pattern
Ports and Adapters
Anti-Corruption Layer
Dependency Inversion
Mapping
Translation Boundary
```

---

# 55. Application aux tests

La future stratégie de tests devra relier :

```text
test type
↔
design property
```

Exemples :

```text
Invariant Test
↔
Domain correctness

Contract Test
↔
Liskov / Port compatibility

Architecture Test
↔
Dependency rule

Policy Test
↔
Strategy behavior

State Transition Test
↔
Lifecycle model
```

---

# 56. Définition de réussite pédagogique

Cette démarche sera considérée comme réussie lorsque :

1. les concepts peuvent être reconnus sans réciter leur définition ;
2. les patterns sont identifiés à partir des forces du problème ;
3. le code conserve des noms naturels ;
4. les documents expliquent les décisions sans jargon décoratif ;
5. les patterns inutiles sont rejetés consciemment ;
6. les mêmes concepts sont reconnus dans d'autres Py*Kit ;
7. les réponses techniques peuvent s'appuyer sur des expériences concrètes ;
8. les tests protègent les décisions architecturales ;
9. les refactorings révèlent naturellement de nouveaux patterns ;
10. la qualité pédagogique n'introduit pas de complexité artificielle.

---

# 57. Formule synthétique

La méthode PySRMKit peut être résumée ainsi :

```text
DON'T MEMORIZE THE PATTERN.

RECOGNIZE THE PROBLEM.
UNDERSTAND THE FORCES.
APPLY THE SIMPLEST DESIGN.
NAME THE CONCEPT.
TEST THE DECISION.
REPEAT UNTIL IT BECOMES INTUITION.
```

---

# 58. Boucle finale

```text
I READ
Strategy Pattern
        │
        ▼
I UNDERSTAND
interchangeable behavior
        │
        ▼
I ENCOUNTER
QualificationPolicy
RiskPolicy
SegmentationPolicy
        │
        ▼
I IMPLEMENT
Protocol + implementations
        │
        ▼
I TEST
behavior + contracts
        │
        ▼
I DOCUMENT
why the pattern fits
        │
        ▼
I RECOGNIZE IT AGAIN
in another domain
        │
        ▼
I INTERNALIZE IT
```

---

# 59. North Star pédagogique

La North Star de cette convention est :

> **Transformer chaque problème réel rencontré dans PySRMKit en une opportunité de comprendre profondément la conception logicielle, sans jamais sacrifier la simplicité ni la qualité du produit au profit de la démonstration académique.**

PySRMKit doit donc devenir simultanément :

```text
A production-oriented Supplier Domain framework
+
A deliberate-practice environment for software design
```

---

# 60. Conclusion

PySRMKit ne sera pas seulement développé avec de bons principes de conception.

Ces principes devront être :

```text
observés
nommés
justifiés
implémentés
testés
documentés
révisés
réutilisés
```

La répétition se fera naturellement au fil du projet.

L'objectif n'est pas de transformer chaque fichier en cours de design patterns.

L'objectif est de rendre visible le raisonnement suffisamment souvent pour que les concepts deviennent progressivement intuitifs.

La règle finale reste :

> **Le problème vient avant le pattern.  
> Le métier vient avant la technologie.  
> La simplicité vient avant la sophistication.  
> La compréhension vient avant la mémorisation.**

Cette convention devient la référence pédagogique et méthodologique pour les prochaines étapes de conception et d'implémentation de PySRMKit.