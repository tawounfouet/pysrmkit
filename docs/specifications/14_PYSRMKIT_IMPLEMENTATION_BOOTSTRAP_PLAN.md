# PySRMKit — Implementation Bootstrap Plan

**Document :** `14_PYSRMKIT_IMPLEMENTATION_BOOTSTRAP_PLAN.md`  
**Projet :** PySRMKit  
**Domaine :** Supplier Relationship Management  
**Type :** Bootstrap Execution Plan  
**Statut :** Baseline finale pré-implémentation  
**Version du document :** 0.1.0  

**Documents de référence :**
- `00_PYSRMKIT_EXPRESSION_DU_BESOIN.md`
- `01_PYSRMKIT_REQUIREMENTS_ANALYSIS.md`
- `02_PYSRMKIT_PRODUCT_VISION_AND_ARCHITECTURE_PRINCIPLES.md`
- `03_PYSRMKIT_SYSTEM_ARCHITECTURE.md`
- `04_PYSRMKIT_DOMAIN_OBJECTS.md`
- `05_PYSRMKIT_ENTITIES_AND_VALUE_OBJECTS.md`
- `06_PYSRMKIT_DOMAIN_RELATIONSHIPS_AND_ERD.md`
- `07_PYSRMKIT_DOMAIN_INVARIANTS_AND_BUSINESS_RULES.md`
- `08_PYSRMKIT_COMMANDS_QUERIES_AND_USE_CASES.md`
- `09_PYSRMKIT_DOMAIN_EVENTS_AND_EVENT_MODEL.md`
- `10_PYSRMKIT_PORTS_AND_REPOSITORY_CONTRACTS.md`
- `11_PYSRMKIT_REPOSITORY_AND_PACKAGE_ARCHITECTURE.md`
- `12_PYSRMKIT_TESTING_STRATEGY.md`
- `13_PYSRMKIT_IMPLEMENTATION_ROADMAP.md`
- `PYSRMKIT_SOFTWARE_DESIGN_LEARNING_CONVENTION.md`
- `PYSRMKIT_PRE_IMPLEMENTATION_SPECIFICATION_CUTOFF_AND_ITERATIVE_DOCUMENTATION_STRATEGY.md`

---

# 1. Objet du document

Ce document décrit **l’exécution concrète du bootstrap initial de PySRMKit**.

Il traduit le milestone :

```text
0.1.0a1 — Repository Bootstrap
```

en étapes opérationnelles précises.

Il répond notamment aux questions suivantes :

> Quels dossiers faut-il créer en premier ?

> Quels fichiers sont nécessaires au commit initial ?

> Comment configurer `pyproject.toml` ?

> Quels outils de qualité faut-il activer ?

> Comment installer le package en local ?

> Comment vérifier que le `src/ layout` fonctionne ?

> Comment introduire les premiers architecture tests ?

> Comment configurer la CI ?

> Quel ordre de commits utiliser ?

> Quel est le point exact où le bootstrap est considéré comme terminé ?

Ce document est volontairement opérationnel.

Après son exécution :

> **la phase de spécification générale s’arrête et l’implémentation du Core commence.**

---

# 2. Principe directeur

Le bootstrap doit être :

```text
minimal
explicit
repeatable
green
```

Il ne doit pas chercher à créer toute l’architecture future.

Il doit uniquement produire une fondation fiable permettant de commencer :

```text
0.1.0a2 — Supplier Core
```

---

# 3. Résultat attendu du bootstrap

À la fin du bootstrap, le repository doit être capable de :

```text
install locally
import pysrmkit
run lint
run type checking
run tests
run architecture checks
run CI
```

avec :

```text
no business feature yet
```

ou seulement les primitives minimales nécessaires au fonctionnement de l’architecture.

---

# 4. Non-objectifs du bootstrap

Le bootstrap ne doit pas encore implémenter :

```text
Supplier Aggregate
SupplierRelationship
Qualification
Assessment
Onboarding
Repositories métier
Application Handlers métier
Database
API
CLI produit
Message broker
External integration
```

Le milestone `0.1.0a1` construit l’atelier.

Il ne fabrique pas encore le produit.

---

# 5. Repository initialization

Si le repository n’existe pas encore :

```bash
mkdir pysrmkit
cd pysrmkit
git init
```

Puis :

```bash
git branch -M main
```

Si le repository GitHub existe déjà :

```bash
git clone <repository-url>
cd pysrmkit
```

---

# 6. Python version

Baseline recommandée :

```text
Python >= 3.11
```

Raison :

- typing moderne ;
- `dataclasses` matures ;
- `StrEnum` disponible ;
- performances correctes ;
- large compatibilité.

La version exacte minimale pourra être ajustée selon l’écosystème Py*Kit.

---

# 7. Virtual environment

Le bootstrap local doit utiliser un environnement isolé.

Exemple standard :

```bash
python -m venv .venv
source .venv/bin/activate
```

Alternative acceptable :

```text
uv
poetry
conda
```

mais le projet ne doit pas dépendre conceptuellement de l’un de ces outils.

---

# 8. Initial repository tree

Créer :

```text
pysrmkit/
├── .github/
│   └── workflows/
├── docs/
│   └── specifications/
├── examples/
├── src/
│   └── pysrmkit/
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

# 9. Minimal package tree

Créer :

```text
src/pysrmkit/
├── __init__.py
├── domain/
│   └── __init__.py
├── application/
│   └── __init__.py
├── ports/
│   └── __init__.py
└── adapters/
    └── __init__.py
```

Ne pas créer encore :

```text
supplier/
relationship/
qualification/
assessment/
risk/
compliance/
```

tant que les milestones correspondants n’ont pas commencé.

---

# 10. Test tree

Créer :

```text
tests/
├── unit/
├── application/
├── contracts/
├── architecture/
└── scenarios/
```

Les dossiers peuvent rester vides jusqu’à leur premier test, à l’exception de `architecture/` qui doit recevoir immédiatement les premiers fitness tests.

---

# 11. Documentation placement

Les documents `00 → 14` doivent être copiés dans :

```text
docs/specifications/
```

Les noms complets sont conservés.

Exemple :

```text
docs/specifications/
├── 00_PYSRMKIT_EXPRESSION_DU_BESOIN.md
├── ...
├── 13_PYSRMKIT_IMPLEMENTATION_ROADMAP.md
└── 14_PYSRMKIT_IMPLEMENTATION_BOOTSTRAP_PLAN.md
```

---

# 12. `pyproject.toml` responsibilities

`pyproject.toml` doit centraliser :

```text
build system
project metadata
Python requirement
package discovery
dev dependencies
pytest configuration
coverage configuration
ruff configuration
type checker configuration
```

Objectif :

> éviter la fragmentation de configuration au bootstrap.

---

# 13. Build backend

Baseline simple recommandée :

```text
hatchling
```

ou :

```text
setuptools
```

Le choix exact est réversible.

Le Core ne doit pas dépendre de fonctionnalités propriétaires du build backend.

---

# 14. Candidate project metadata

Exemple conceptuel :

```toml
[project]
name = "pysrmkit"
version = "0.1.0a1"
description = "Technology-agnostic Python domain framework for Supplier Relationship Management"
requires-python = ">=3.11"
```

Ne pas figer ici les classifiers ou URLs si le repository n’est pas encore créé.

---

# 15. Runtime dependencies

Target :

```text
dependencies = []
```

Le Core doit viser :

> **zero mandatory third-party runtime dependencies**

pendant ce premier cycle.

---

# 16. Dev dependencies

Minimum recommandé :

```text
pytest
pytest-cov
ruff
pyright
```

Alternative :

```text
mypy
```

à la place de `pyright`.

---

# 17. Type checker decision

Baseline recommandée :

```text
pyright
```

Raisons :

- rapide ;
- bon support moderne de typing ;
- excellent feedback sur Protocols ;
- configuration simple.

Le choix reste réversible.

---

# 18. Ruff

Ruff doit couvrir :

```text
lint
import hygiene
common Python mistakes
```

Le formatting automatique peut également être activé.

Candidate commands :

```bash
ruff check .
ruff format --check .
```

---

# 19. Pytest

Minimum config :

```text
testpaths = ["tests"]
```

et éventuellement :

```text
addopts = "-ra"
```

La couverture sera ajoutée directement aux commandes CI ou à la configuration.

---

# 20. Coverage

Candidate bootstrap threshold :

```text
80%
```

au tout premier skeleton

puis montée rapide vers :

```text
90%+
```

à partir des vrais milestones métier.

Pourquoi ne pas imposer 90% dès `a1` :

le repository contient principalement du scaffolding.

---

# 21. Branch coverage

Activer :

```text
branch = true
```

dès que possible.

Particulièrement utile à partir :

```text
0.1.0a4 — Lifecycle
0.1.0a6 — Qualification
```

---

# 22. `.gitignore`

Minimum :

```text
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.pyright/
.mypy_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.DS_Store
```

---

# 23. Package version

Pour `0.1.0a1`, le package doit exposer une version.

Deux options :

```text
hardcoded __version__
```

ou :

```text
importlib.metadata
```

Baseline pragmatique :

```python
__version__ = "0.1.0a1"
```

acceptable au bootstrap.

Une stratégie plus avancée sera traitée dans le document de release/versioning ultérieur.

---

# 24. `src/pysrmkit/__init__.py`

Doit rester minimal.

Exemple :

```python
"""PySRMKit public package."""

__version__ = "0.1.0a1"
```

Pas de réexports massifs.

Pas d’initialisation implicite.

---

# 25. Import smoke test

Créer :

```text
tests/test_import.py
```

ou sous :

```text
tests/unit/test_import.py
```

Test :

```python
def test_package_can_be_imported():
    import pysrmkit

    assert pysrmkit.__version__ == "0.1.0a1"
```

---

# 26. Editable installation

Commande attendue :

```bash
python -m pip install -e .
```

Puis :

```bash
python -c "import pysrmkit; print(pysrmkit.__version__)"
```

Résultat :

```text
0.1.0a1
```

---

# 27. Initial architecture tests

Les règles de dépendance doivent être testées dès `a1`.

Minimum :

```text
domain ↛ application
domain ↛ ports
domain ↛ adapters
application ↛ adapters
ports ↛ adapters
```

---

# 28. Architecture test implementation — bootstrap

Approche simple recommandée :

```text
inspect Python import graph
```

via un test Python/AST léger.

Alternative :

```text
import-linter
```

si cela simplifie réellement la règle.

---

# 29. Preferred bootstrap architecture test

Créer :

```text
tests/architecture/test_dependency_rules.py
```

Le test peut parcourir :

```text
src/pysrmkit/domain/
src/pysrmkit/application/
src/pysrmkit/ports/
```

et inspecter les imports interdits.

---

# 30. Why architecture tests from day one

Si les règles sont ajoutées seulement après plusieurs milestones :

```text
architecture drift
```

peut déjà être installée.

Le coût est beaucoup plus faible lorsqu’elles existent dès le début.

---

# 31. Test for side-effect-free import

Le package doit pouvoir être importé sans :

```text
network access
file creation
thread creation
database connection
```

Un simple smoke test protège partiellement cette propriété.

---

# 32. Initial CI workflow

Créer :

```text
.github/workflows/ci.yml
```

Trigger minimum :

```text
push
pull_request
```

---

# 33. CI Python version

Au bootstrap :

```text
one Python version
```

suffit.

Exemple :

```text
3.11
```

Une matrix multi-version viendra plus tard si nécessaire.

---

# 34. CI steps

Ordre recommandé :

```text
checkout
setup-python
install package + dev dependencies
ruff check
ruff format --check
pyright
pytest + coverage
```

---

# 35. CI fail-fast principle

Toute violation de :

```text
lint
typing
tests
architecture
```

doit rendre la CI rouge.

---

# 36. Initial README

Le README bootstrap doit rester court.

Il doit expliquer :

```text
What is PySRMKit?
Current status
Architecture principles
Local setup
How to run tests
Roadmap pointer
```

---

# 37. README status statement

Exemple :

```text
Status: Early alpha — Domain Core under active construction.
```

---

# 38. README architecture summary

Inclure :

```text
Domain
Application
Ports
Adapters
```

avec une phrase par couche.

---

# 39. README development commands

Minimum :

```bash
python -m pip install -e .
ruff check .
pyright
pytest
```

---

# 40. CHANGELOG

Créer :

```text
CHANGELOG.md
```

avec :

```text
## Unreleased
```

ou directement :

```text
## 0.1.0a1
```

selon workflow retenu.

---

# 41. LICENSE

Le choix de licence doit être confirmé explicitement par le propriétaire du projet.

Ne pas inventer une licence sans décision.

Si déjà standardisée dans les autres Py*Kit, réutiliser la même convention.

---

# 42. Initial examples directory

Créer :

```text
examples/README.md
```

ou laisser `examples/` vide.

Ne pas créer `local_qualification.py` avant `0.1.0a8`.

---

# 43. Initial docs index

Optionnel mais utile :

```text
docs/specifications/README.md
```

avec table :

```text
00 → 14
```

et statut :

```text
Pre-Implementation Baseline
```

---

# 44. First local verification sequence

Après création des fichiers :

```bash
python -m pip install -e .
```

Puis :

```bash
python -c "import pysrmkit; print(pysrmkit.__version__)"
```

Puis :

```bash
ruff check .
```

Puis :

```bash
ruff format --check .
```

Puis :

```bash
pyright
```

Puis :

```bash
pytest
```

---

# 45. Definition of Green — bootstrap

Le repository est GREEN si :

```text
package import works
ruff green
format check green
type check green
pytest green
architecture tests green
CI green
```

---

# 46. Initial commit sequence

Recommended sequence:

```text
chore: initialize pysrmkit repository
```

Puis :

```text
build: configure Python package and development tooling
```

Puis :

```text
test: add architecture fitness baseline
```

Puis :

```text
ci: add initial quality pipeline
```

Puis :

```text
docs: add pre-implementation specification baseline
```

Ces commits peuvent être combinés si le repository est initialisé en une seule opération, mais la séparation améliore la lisibilité historique.

---

# 47. Alternative single bootstrap commit

Acceptable :

```text
chore: bootstrap pysrmkit repository
```

si l’ensemble est cohérent et testé.

---
# 48. Branch strategy

Pour le bootstrap initial :

```text
main
```

peut être utilisé directement si le repository est personnel et vide.

Une fois le Core commencé :

```text
feature branches
+
PR
+
CI
```

est recommandé.

---

# 49. Tagging

À la fin de `0.1.0a1`, un tag Git est possible :

```text
v0.1.0a1
```

mais pas obligatoire si le projet préfère ne taguer qu’après milestones fonctionnels.

---

# 50. PyPI publication

Explicitly out of scope.

`0.1.0a1` peut rester local/GitHub-only.

---

# 51. First architecture fitness checks

Le bootstrap doit au minimum pouvoir détecter une violation volontaire.

Exemple test pédagogique :

si :

```python
# domain/foo.py
from pysrmkit.adapters import something
```

alors :

```text
architecture test fails
```

Cette preuve valide réellement le mécanisme.

---

# 52. No runtime frameworks

Ne pas ajouter au bootstrap :

```text
FastAPI
Pydantic
SQLAlchemy
Django
Celery
Kafka clients
```

---

# 53. No DI framework

Ne pas ajouter :

```text
dependency-injector
punq
injector
```

---

# 54. No generic base abstractions

Ne pas créer :

```text
BaseEntity
BaseValueObject
BaseRepository
BaseService
BaseHandler
```

pendant `a1`.

Les abstractions doivent émerger du code réel.

---

# 55. No placeholder domain classes

Ne pas créer :

```python
class Supplier:
    pass
```

simplement pour remplir le package.

Supplier arrive réellement dans `0.1.0a2`.

---

# 56. No placeholder adapters

Ne pas créer :

```text
postgresql/
kafka/
ivalua/
```

vide.

---

# 57. No speculative configuration

Ne pas ajouter :

```text
database URL
broker URL
cloud region
OAuth config
```

avant besoin.

---

# 58. Bootstrap security hygiene

Même sans security subsystem :

- aucun secret dans le repository ;
- `.env` local ignoré si utilisé plus tard ;
- pas de token dans CI ;
- pas de credentials de test réels.

---

# 59. Python package import policy

`import pysrmkit` doit être :

```text
fast
safe
side-effect free
```

---

# 60. Type checker strictness

Le bootstrap peut démarrer avec un niveau strict raisonnable.

Objectif :

```text
catch real typing errors
```

sans bloquer le projet avec une configuration extrême dès le premier commit.

La strictness peut augmenter progressivement.

---

# 61. Ruff rule strategy

Commencer avec règles utiles et compréhensibles.

Avoid:

```text
enabling every possible rule
+
hundreds of ignores
```

Préférer une baseline claire.

---

# 62. Test coverage config

Candidate:

```text
source = ["pysrmkit"]
branch = true
```

Exclusions possibles :

```text
pragma: no cover
TYPE_CHECKING
```

avec parcimonie.

---

# 63. Initial package metadata

Candidate fields:

```text
name
version
description
readme
requires-python
license
authors
keywords
classifiers
project URLs
```

Seuls les champs connus doivent être renseignés.

Ne pas inventer de metadata.

---

# 64. Distribution name vs import name

Both:

```text
pysrmkit
```

to keep simple.

---

# 65. Build verification

Optional at `a1` but useful:

```bash
python -m build
```

if `build` dev dependency is included.

This verifies:

```text
wheel
sdist
```

No publication required.

---

# 66. Packaging test

Optional:

```text
build wheel
install wheel in clean env
import pysrmkit
```

Can be deferred until release cycle if local editable install is enough.

---

# 67. Architecture documentation in code

Module docstrings can briefly state roles.

Example:

```python
"""Domain model for PySRMKit."""
```

Avoid verbose architecture essays in every file.

---

# 68. Docstring convention

Important classes introduced later should mention concepts when useful:

```text
DDD role
responsibility
invariants
```

Example:

```python
class Supplier:
    """
    Aggregate Root representing the canonical supplier identity.
    """
```

But not before the class actually exists.

---

# 69. Comment convention

Comments explain:

```text
why
trade-off
invariant
architectural reason
```

not obvious syntax.

---

# 70. Learning convention integration

The bootstrap already practices:

```text
Hexagonal Architecture
Dependency Inversion
Architecture Fitness Functions
src layout
CI quality gates
```

No need to force business design patterns before business code exists.

---

# 71. `0.1.0a1` file manifest

Minimum recommended files:

```text
.gitignore
README.md
CHANGELOG.md
LICENSE                     # once license decision exists
pyproject.toml

.github/workflows/ci.yml

src/pysrmkit/__init__.py
src/pysrmkit/domain/__init__.py
src/pysrmkit/application/__init__.py
src/pysrmkit/ports/__init__.py
src/pysrmkit/adapters/__init__.py

tests/test_import.py
tests/architecture/test_dependency_rules.py

docs/specifications/...
```

---

# 72. Optional files

Can be added if useful:

```text
docs/specifications/README.md
examples/README.md
CONTRIBUTING.md
```

Not mandatory.

---

# 73. Bootstrap commands — candidate exact sequence

```bash
git init
git branch -M main

python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

ruff check .
ruff format --check .
pyright
pytest
```

Exact extras syntax depends on final `pyproject.toml`.

---

# 74. Dev extras

Candidate:

```toml
[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-cov",
    "ruff",
    "pyright",
]
```

This keeps runtime dependency-free.

---

# 75. CI installation

CI can use:

```bash
pip install -e ".[dev]"
```

for the first cycle.

No need for complex lock strategy yet unless project policy requires one.

---

# 76. Dependency locking

Not mandatory for package libraries in the same way as applications.

A lock file can be used for local reproducibility but should not constrain consumers.

Decision can be deferred.

---

# 77. Pre-commit hooks

Optional.

Useful later:

```text
ruff
format
```

but not required to qualify `a1`.

---

# 78. Makefile / task runner

Not required.

Commands are simple enough.

If repetitive later, add:

```text
Makefile
justfile
task runner
```

only when useful.

---

# 79. No Docker

The bootstrap does not require Docker.

This is intentional.

---

# 80. Local-first philosophy

A new contributor should be able to go from clone to green with only:

```text
Python
Git
```

plus package installation.

---

# 81. CI parity

CI commands must mirror local commands as closely as possible.

Avoid:

```text
local green
CI uses totally different toolchain
```

---

# 82. First failure drill

Before declaring bootstrap complete, intentionally break one rule:

Example:

```text
introduce forbidden import
```

Verify:

```text
architecture test fails
```

Then revert.

This demonstrates that the fitness function works.

---

# 83. Second failure drill

Introduce a lint violation.

Verify:

```text
ruff fails
```

Then revert.

---

# 84. Third failure drill

Introduce type mismatch in a temporary line.

Verify:

```text
type checker fails
```

Then revert.

---

# 85. Why failure drills matter

A quality gate that has never been observed failing may be misconfigured.

The bootstrap should prove that:

```text
red is possible
green means something
```

---

# 86. Bootstrap Definition of Done

`0.1.0a1` is DONE when:

```text
[ ] repository initialized
[ ] src layout exists
[ ] package metadata exists
[ ] editable installation works
[ ] import pysrmkit works
[ ] version reports 0.1.0a1
[ ] pytest works
[ ] ruff works
[ ] formatter check works
[ ] type checker works
[ ] architecture tests work
[ ] CI runs same checks
[ ] all checks green
[ ] specs 00–14 stored in repository
[ ] README explains local setup
[ ] no speculative infrastructure dependency exists
```

---

# 87. Stop condition

When the bootstrap DoD is satisfied:

> **Do not add more generic architecture scaffolding.**

Move directly to:

```text
0.1.0a2 — Supplier Core
```

---

# 88. Transition to Supplier Core

The first post-bootstrap implementation starts by creating:

```text
domain/supplier/
```

Then:

```text
SupplierId
ExternalIdentifier
SupplierIdentity
Supplier
SupplierCreated
```

Then:

```text
SupplierRepository
InMemorySupplierRepository
RegisterSupplier
RegisterSupplierHandler
```

with tests.

---

# 89. First Supplier Core test

The first real business test should likely be a Value Object or Aggregate creation test.

Example conceptually:

```text
test_supplier_can_be_registered_with_valid_identity
```

This marks the transition from architecture bootstrap to Domain implementation.

---

# 90. No more general specs rule

After bootstrap:

```text
IMPLEMENT
→ OBSERVE
→ SPECIFY ONLY CONCRETE NEW PROBLEM
```

Do not continue automatically with:

```text
15
16
17
18
...
```

unless a real implementation need appears.

---

# 91. Bootstrap milestone retrospective

Before starting `a2`, answer briefly:

```text
Did the src layout work?
Did architecture tests feel useful?
Did any tooling create unnecessary friction?
Is the package structure still clear?
Are local and CI commands identical enough?
```

Only adjust what reality proves necessary.

---

# 92. Anti-pattern — toolchain overengineering

Avoid:

```text
tox + nox + hatch + poetry + uv + make + pre-commit
```

all at once.

One simple path is enough.

---

# 93. Anti-pattern — 100 configuration files

Centralize in:

```text
pyproject.toml
```

when supported.

---

# 94. Anti-pattern — empty abstraction tree

Do not create all future modules.

---

# 95. Anti-pattern — CI before local commands work

Local baseline first.

Then encode the same commands in CI.

---

# 96. Anti-pattern — hidden setup step

README must document every required bootstrap command.

---

# 97. Anti-pattern — local machine assumptions

Avoid scripts depending on:

```text
specific home path
specific IDE
specific shell customization
```

---

# 98. Anti-pattern — environment-specific business logic

None should exist at this stage.

---

# 99. Anti-pattern — framework leakage from bootstrap

Adding SQLAlchemy "because we will need it later" is explicitly rejected.

---

# 100. Anti-pattern — release engineering too early

No Trusted Publishing, release workflows, SBOM or signing required for `a1`.

They will be added before actual publication.

---

# 101. Architecture Learning Map

```text
Repository Tree
    │
    ▼
Layer boundaries
    │
    ▼
Import rules
    │
    ▼
Architecture test
    │
    ▼
CI gate
```

This converts architecture from diagram into executable constraint.

---

# 102. Tooling Learning Map

```text
Code
    │
    ├── Ruff
    ├── Type Checker
    ├── Pytest
    └── Coverage
        │
        ▼
Quality Gate
        │
        ▼
CI
```

---

# 103. Packaging Learning Map

```text
src/
    │
    ▼
installed package
    │
    ▼
real import path
    │
    ▼
avoids accidental local imports
```

---

# 104. Bootstrap North Star

```text
CLONE
    │
    ▼
INSTALL
    │
    ▼
IMPORT
    │
    ▼
LINT
    │
    ▼
TYPE CHECK
    │
    ▼
TEST
    │
    ▼
CI GREEN
    │
    ▼
READY FOR DOMAIN CODE
```

---

# 105. Final execution checklist

## Repository

```text
[ ] Git initialized
[ ] main branch
[ ] .gitignore
```

## Package

```text
[ ] pyproject.toml
[ ] src layout
[ ] version
[ ] import smoke test
```

## Quality

```text
[ ] ruff
[ ] formatter
[ ] pyright/mypy
[ ] pytest
[ ] coverage
```

## Architecture

```text
[ ] domain/application/ports/adapters created
[ ] dependency rules encoded
[ ] failure drill performed
```

## CI

```text
[ ] GitHub workflow
[ ] same local commands
[ ] green run
```

## Docs

```text
[ ] README
[ ] CHANGELOG
[ ] specifications 00–14
```

---

# 106. Bootstrap completion statement

When all checklist items are satisfied, record:

```text
PySRMKit 0.1.0a1 — Repository Bootstrap
QUALIFIED LOCALLY
```

Optionally create:

```text
docs/releases/v0.1.0a1.md
```

only if release documentation is useful.

---

# 107. Immediate next action

After `0.1.0a1` is qualified:

```text
START 0.1.0a2 — Supplier Core
```

The next work item is no longer documentation.

It is code.

---

# 108. Final principles

> **Bootstrap only what the next milestone actually needs.**

> **Make local commands and CI tell the same truth.**

> **Prove architecture rules by making them fail once.**

> **Keep the Core runtime dependency-free until a real requirement says otherwise.**

> **Do not pre-create future capabilities.**

> **Once the repository is green, stop scaffolding and implement the domain.**

---

# 109. Conclusion
This bootstrap plan is the final document of the pre-implementation baseline.

It turns PySRMKit from:

```text
documented architecture
```

into:

```text
executable development environment
```

The bootstrap does not attempt to deliver supplier functionality.

Its responsibility is narrower and more important:

```text
create a trustworthy place
where supplier functionality can now be implemented safely.
```

At the end of `0.1.0a1`, PySRMKit must be:

```text
installable
importable
linted
typed
tested
architecture-checked
CI-qualified
```

and still remain:

```text
small
clean
framework-light
infrastructure-free
```

From that point onward, the project changes phase.

The guiding loop becomes:

```text
IMPLEMENT
    │
    ▼
TEST
    │
    ▼
OBSERVE
    │
    ▼
REFACTOR
    │
    ▼
SPECIFY ONLY WHEN REAL PRESSURE APPEARS
```

The final rule is:

> **The bootstrap is complete when architecture stops being a plan and becomes an executable constraint.**