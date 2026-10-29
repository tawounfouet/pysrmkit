# PySRMKit - Supplier Search Unicode and Collation Policy (ADR)

**Document:** `24_PYSRMKIT_SUPPLIER_SEARCH_UNICODE_COLLATION_POLICY.md`  
**Cycle:** 4 - `0.4.0a3` Query Adapter Qualification  
**Work package:** A3-06 - Unicode & Collation Policy  
**Date:** 2026-10-29  
**Status:** Accepted and qualified on main (PR #36, CI #245); Unicode portability is explicitly limited

## 1. Context

The same **18 named ASCII search contract scenarios** and related
compatibility checks execute against InMemory, SQLite and PostgreSQL.
The PostgreSQL qualification was merged in PR #35, CI #240.

However, the adapters currently implement different string operations:

- InMemory: Python `str.casefold()` for matching and sorting.
- SQLAlchemy SQLite/PostgreSQL: SQL `lower(column)` for matching and
  name sorting; the query uses Python `str.lower()`.
- SQL `lower()` and Unicode case folding are not interchangeable:
  results depend on the engine, collation, locale and normalization form.
  SQLite's built-in `lower()` generally handles ASCII rather than the
  full Unicode case mapping.

Silently treating all three as equivalent would violate the substitutability
assumption of the `SupplierSearchService` Port.

## 2. Decision: two explicitly separated guarantees

**Normative portable guarantee (current alpha):**

- Partial search on `legal_name` or `trading_name` with ASCII case-insensitive
  matching for ASCII supplier names and ASCII queries.
- Exact `country_code` and `supplier_type` filtering, SQL wildcard escaping,
  filtered `total`, immutable views and bounded pagination.
- Deterministic ordering for ASCII legal names: ASCII case-insensitive
  legal name, then Supplier UUID ascending, including descending names.
- The same 13-seed / 18-scenario corpus is a required contract on all three
  adapters. The preexisting `list_suppliers()` UUID ordering is unchanged.

**Unicode search (non-ASCII text or Unicode-only case distinctions):**

- Unicode supplier names and search strings remain accepted; no silent ASCII
  coercion, accent removal or data loss is introduced.
- **Match inclusion and sort position are currently backend/locale-dependent.**
  No general claim of accent insensitivity, Unicode case-insensitivity, NFC/NFD
  equivalence, transliteration or language-specific collation is made.
- The Unicode probes are *characterization tests*, not a common oracle. They
  record observed matches while checking read-only behavior and canonical
  identity. They must not be silently marked `xfail` or used as evidence that
  cross-backend Unicode parity has been achieved.
- A deployment which requires language-neutral consistent Unicode discovery
  must treat this as a **known limitation**, not rely on provider-specific
  behavior in cross-database migrations.

This is a **contract-scoping decision**, not a claim that the two SQL dialects
produce the same Unicode answers.

## 3. Unicode diagnostics

The shared `UNICODE_PROBES` fixture contains:

| Probe | Supplier legal name | Query | Question |
| --- | --- | --- | --- |
| `sharp-s` | `Straße GmbH` | `STRASSE` | Does `ß` fold to `ss`? |
| `accented-case` | `Étoile` | `étoile` | Is Unicode capitalization recognized? |
| `accent-insensitivity` | `Café` | `cafe` | Are diacritics intentionally removed? |
| `unicode-normalization` | decomposed `Cafe\\u0301` | `Café` | Are NFC and NFD equivalent? |
| `turkish-i` | `İSTANBUL` | `istanbul` | Is locale-specific casing applied? |

Execution is parameterized over InMemory, SQLite and real PostgreSQL in
`tests/contracts/queries/test_supplier_unicode_diagnostics.py`.
Each case seeds one supplier in an isolated store, performs a read and verifies
that the returned aggregate identity, count and persisted state remain valid.

CI prints `UNICODE_PROBE backend=<...> case=<...> matched=<...>` for each
backend and probe. This is observable diagnostic evidence, **not** a
cross-backend equality assertion.

### Measured observations - CI #241 (2026-10-29)

| Probe | InMemory | SQLite | PostgreSQL 18 in CI |
| --- | --- | --- | --- |
| `sharp-s` | Match | No match | No match |
| `accented-case` | Match | No match | Match |
| `accent-insensitivity` | No match | No match | No match |
| `unicode-normalization` | No match | No match | No match |
| `turkish-i` | No match | No match | Match |

**Evidence:** [PR #36 CI #241](https://github.com/tawounfouet/pysrmkit/actions/runs/40886646863).
The `quality` job prints the InMemory/SQLite results (10 diagnostic
executions). The `postgresql` job prints the five PostgreSQL observations
against the live PostgreSQL 18 CI service.

These are **observed results for the specific CI environment**, not
universal assertions about arbitrary PostgreSQL collations, locales,
extensions or SQLite builds. In particular, `Étoile`/ `étoile` and
`İSTANBUL`/ `istanbul` differ between SQLite and that PostgreSQL
environment. They must not become a cross-adapter equality assertion
without a consciously chosen normalization strategy.

## 4. Options evaluated

| Option | Trade-off | Decision |
| --- | --- | --- |
| Declare `lower()` equivalent to `casefold()` | False for many Unicode cases | Rejected |
| Normalize with Python `NFC + casefold`, then scan all SQL rows | Portable but requires full-table scans and in-process sorting/counting before pagination; not scalable | Rejected as default |
| Depend on database ICU/unaccent/collation extensions | Engine-specific, platform and locale dependent | Rejected as universal contract |
| Normalize and persist dedicated search/sort keys | Portable semantics possible with versioned normalization, schema migrations, indexes and backfill | Future explicit design decision |
| Guarantee portable ASCII and document Unicode variance | Matches current verified behavior without migrations | **Accepted for this alpha milestone** |

## 5. Evolution path for strict Unicode equivalence

If cross-database Unicode identity search becomes a product requirement,
make it an explicit architecture change with:

1. A normative normalization function, e.g. `NFC(text).casefold()`;
   decide separately whether accent removal is desired.
2. Versioned derived `legal_name_search_key`,
   `trading_name_search_key` and `legal_name_sort_key` storage,
   while keeping original domain names unchanged.
3. Transactional updates of keys on every rename/registration and a
   reproducible schema migration plus backfill for existing suppliers.
4. SQL query plans and indexes appropriate to equality/substring matching.
   `contains` predicates need separate plan evaluation; B-tree alone may
   not optimize arbitrary substrings.
5. The same Unicode oracle and deterministic ties across all adapters,
   restart/reload tests and fixture-based evidence.

A text normalization policy must not be conflated with language-aware sort
collation, locale-sensitive case rules or fuzzy relevance ranking. Normalizing
a key solves a **specific** comparison problem; it does not automatically
provide linguistic search semantics.

## 6. Boundaries and compatibility

- The `SupplierSearchService` port and public `SuppliersAPI.search()` are
  not changed by this ADR.
- Domain data is stored as originally provided after the Domain's existing
  whitespace normalization.
- No new mandatory runtime dependencies, indexes or migrations.
- `list_suppliers()`, Domain Events and transactional boundaries remain
  unchanged.
- A3-07 may characterize SQL `lower()` substring query plans, but this
  ADR does not claim production-scale performance.

## 7. Qualification gates

- [x] Shared ASCII contract on all three adapters - PR #35, main CI #240.
- [x] Unicode diagnostic matrix captured in PR #36 CI #241 on InMemory, SQLite and live PostgreSQL 18.
- [x] PR #36 CI #244 and post-merge main CI #245 fully green across quality, PostgreSQL and integration.
- [x] ADR comparison matrix reconciled with observed outcomes in CI #241.

A3-04/A3-07 query plan observations were subsequently qualified on main
in CI #249 (PR #37). Only the final `0.4.0a3` version/qualification
candidate release gates remain open at the time of this update.

## 8. Software design learning concepts

**Contract Testing** tests what a Port promises, rather than accidental
database behavior. **Liskov Substitution Principle** applies to the declared
ASCII query semantics only until the contract is expanded. **Separation of
Concerns** keeps Unicode policy independent of Domain identities and SQL
adapters. **KISS/YAGNI** avoids a schema migration without a chosen product
requirement. **ADR / Evidence-Based Design** makes limitations discoverable,
explicit and revisitable.
