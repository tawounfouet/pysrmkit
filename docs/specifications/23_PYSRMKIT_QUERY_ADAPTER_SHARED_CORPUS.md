# PySRMKit - Shared Supplier Query Contract Corpus

**Document:** `23_PYSRMKIT_QUERY_ADAPTER_SHARED_CORPUS.md`  
**Cycle:** 4 - `0.4.0a3` Query Adapter Qualification  
**Work package:** A3-01 - Deterministic Shared Query Corpus  
**Date:** 2026-10-29  
**Status:** Implemented in draft PR; CI qualification pending

## 1. Context and problem

The `0.4.0a2` milestone made `SuppliersAPI.search()` operational in
InMemory and SQLAlchemy adapters and was qualified on `main` in CI #231.
However, the shared search assertions in that milestone covered InMemory and
SQLite, **not** a full three-backend contract on real PostgreSQL.

The `0.4.0a3` plan calls first for **A3-01 - a deterministic common corpus
with expected results**, then for implementation/qualification of all three
adapters. This document records a fixed set of observations rather than
assuming that existing implementations are already substitutable.

## 2. Architecture decision

Use a **test-owned shared corpus**, not a production fixture dependency.

```text
tests/contracts/queries/corpus.py
  |-- 13 fixed Supplier seeds (UUID(int=1..13))
  |-- SEARCH_CASES: named scenario + complete expected page
  |-- UNICODE_PROBES: diagnostic scenarios, NOT yet normative
  +-- seed_ascii_corpus(repository)
         |
         v
tests/contracts/queries/test_supplier_search_contract.py
  |-- SupplierSearchContract (abstract pytest behavior)
  |-- TestInMemorySupplierSearchContract
  +-- TestSqliteSupplierSearchContract
           |
           +-- TestPostgresqlSupplierSearchContract [planned A3-05]
```

- Each seed has a stable `SupplierId`, independent of process order and
  `uuid4()`, a domain `SupplierIdentity`, and a unique `CORPUS` external
  identifier for identity-preservation checks.
- The test-only `SearchableSupplierRepository` Protocol composes
  `SupplierRepository`, the original `SupplierQueryService` and the
  `SupplierSearchService` without changing any production port.
- An adapter joins the contract by implementing only
  `make_repository()` and providing a fresh session/store per test.
- Data is seeded by `Supplier.reconstitute()`; no artificial SupplierCreated
  event is generated.
- The expected sequence is manually specified per scenario rather than
  calculated with the same sorting/filtering logic under test. This avoids
  a tautological oracle.

## 3. ASCII contract cases

The fixed corpus has **13** suppliers and deliberately covers duplicate
names, mixed case, trading names, null country/type, country/type filters,
SQL wildcard literal matching, and all relevant ordering boundaries.

| Dimension | Named scenarios |
| --- | --- |
| Full sort | `all-ascending`, `all-descending-first-five` |
| Search fields | `legal-and-trading-name-contains`, `trading-name-only` |
| Combined filters | `country-and-type-filters`, `country-de` |
| Type semantics | `supplier-type-service`, `supplier-type-exact-case` |
| Deterministic ties | `duplicate-legal-name-desc` |
| Pagination | `second-full-page`, `last-partial-page`, `beyond-final-page` |
| Empty results | `no-match` |
| SQL literal wildcard | `literal-percent`, `literal-underscore` |
| Null and missing values | `missing-country-identity`, `country-excludes-missing` |

Additional assertions retain the original UUID-ordered `list_suppliers()`
contract and preserve the canonical Supplier identity, including external
identifiers. The total is always the **filtered count before pagination**.

The initial suite is intentionally ASCII-only. Case insensitive ASCII text
matching can be compared across Python and SQL without adopting a particular
Unicode normalization or database collation policy.

## 4. Unicode probes - NOT a normative contract yet

`UNICODE_PROBES` records unresolved questions for A3-04/A3-05/A3-06:

| Probe | Source vs query | Qualification question |
| --- | --- | --- |
| Sharp S | `Straße` vs `STRASSE` | Python `casefold` vs SQL `lower` |
| Accented case | `Étoile` vs `étoile` | SQLite/PostgreSQL case handling |
| Accent equivalence | `Café` vs `cafe` | Should accents be ignored? |
| NFC/NFD | `Cafe\u0301` vs `Café` | Should canonical equivalents match? |
| Turkish I | `İSTANBUL` vs `istanbul` | Unicode vs locale-specific case |

These cases deliberately have **no expected pass/fail search result**.
The existing Python, SQLite and PostgreSQL implementations may differ;
A3 must record this divergence and choose a policy *before* imposing
shared assertions. Do not silently `xfail` real differences or pretend
that an ASCII contract proves complete internationalization support.

## 5. Contract execution and expansion

A3-01 supplies a reusable abstract suite instantiated for:

1. InMemory - direct `InMemorySupplierRepository`.
2. SQLite - `SqlAlchemySupplierRepository` with a fresh schema and Session.

A3-05 must instantiate the same abstract test class with a real PostgreSQL
repository and a clean isolated test database, without duplicating
the oracle. A3-06 then hardens boundaries, Unicode decisions and
read-only behavior in all three backends.

## 6. Quality gates

- [ ] `ruff check .`, `ruff format --check .`, `pyright`.
- [ ] Shared ASCII scenarios green on InMemory and SQLite in CI `quality`.
- [ ] Existing `list_suppliers()` compatibility green.
- [ ] Existing CI `postgresql` and `integration` jobs green.
- [ ] A3-01 PR merged and post-merge `main` qualified.

The above checklist will be updated only with verified CI evidence.
The full `0.4.0a3` milestone remains open until all **three adapters**
pass one shared contract suite.

## 7. Pedagogical design concepts

- **Contract Testing / Liskov Substitution Principle (LSP):**
  equivalent observable results from different Port implementations.
- **Dependency Inversion (DIP) / Ports and Adapters:** test behavior
  against Protocols rather than SQL or in-memory details.
- **Test Fixture / Test Data Builder:** stable, readable seeds and
  manually authored expected outcomes.
- **Separation of Concerns:** Unicode policy and SQL performance are
  separately analyzed, not baked into an accidental oracle.
- **KISS / YAGNI:** no new runtime dependencies, caching, or external
  search engine; no speculative indexing.

## 8. Subsequent A3 packages

- **A3-02/A3-03:** existing memory and SQL search implementations are already
  present from A2-06; now they are subjected to stricter contract evidence.
- **A3-04:** analyze SQLite qualification and query plan boundaries.
- **A3-05:** add PostgreSQL shared-suite instantiation.
- **A3-06:** close cross-adapter behavior, null/edge and Unicode policy.
- **A3-07:** characterize query plans and index needs *only if evidenced*.

**Non-goal:** This document does not claim completion of `0.4.0a3`
or full Unicode equivalence.
