# PySRMKit - Supplier Query Contract (ADR)

**Document:** `22_PYSRMKIT_SUPPLIER_QUERY_CONTRACT_ADR.md`
**Cycle:** 4 - `0.4.0a2`
**Packages:** A2-01 through A2-07
**Date:** 2026-10-29
**Status:** Accepted and implemented for A2-01 through A2-07 on PR #32; full adapter parity remains deferred to A3

## Context

The existing `SuppliersAPI.list(offset, limit)` is a stable public entry point. Its
`SupplierQueryService.list_suppliers()` port supports basic listing and already
has InMemory and SQL implementations. A demonstrator may filter pages in the
FastAPI host, but that is not a scalable supplier discovery contract.

The framework must own the semantics of supplier discovery without moving
domain invariants into HTTP, SQLAlchemy, or a particular dashboard.

## Decision

1. Keep `SuppliersAPI.list()`, `SupplierQueryService`, and `SupplierPage`
   backwards compatible.
2. Add a distinct public `suppliers.search(...)`, implemented during A2-04 and
   connected to standard runtimes during A2-06.
3. Use an immutable internal `SearchSuppliersQuery` DTO, with explicit
   validation, whitespace normalization and a pagination limit of 100.
4. Introduce an optional `SupplierSearchService` Protocol instead of adding
   an abstract method to `SupplierQueryService`. A consumer that implements
   only the listing port remains valid. This implements Interface Segregation.
5. Keep the new port in `pysrmkit.ports.queries.supplier`, independent of the
   internal `public._queries` DTO. `SearchSuppliersHandler` translates the public
   inputs into typed port parameters, including `CountryCode`.
6. Reuse `SupplierPage(suppliers, total)` for the internal read result and
   `SupplierPageView(items, total, offset, limit)` at the public boundary.
7. Require read-only behavior: queries do not change aggregates or emit
   Domain Events.

## Query scope

- Text: partial, case-insensitive search over `legal_name` and
  `trading_name`, pending shared adapter qualification.
- Country: equality on validated `CountryCode`.
- Supplier type: equality on `supplier_type`.
- Sort: `legal_name`, `asc` or `desc`, with `SupplierId` as the stable
  tie-break.
- Total: number of matches **after filtering and before pagination**.
- Pagination: `offset >= 0`, `1 <= limit <= 100`.
- Empty optional textual filters: no filter.
- External supplier identifiers: deferred; not included in the first search
  signature.
- Unicode accent/case equivalence across InMemory, SQLite and PostgreSQL:
  **not yet qualified**. Native SQL collations alone cannot guarantee it.

## Port boundary

```text
FastAPI / CLI / Dashboard
         |
         v
Public SuppliersAPI.search [implemented A2-04]
         |
         v
SearchSuppliersQuery + Handler [implemented A2-02/A2-05]
         |
         v
SupplierSearchService Protocol [implemented A2-03]
         |
         +--> InMemory search adapter [implemented A2-06]
         +--> SQLAlchemy search adapter [implemented A2-06]
```

The existing `SuppliersAPI.list` -> `SupplierQueryService` path stays
independently supported.

## Qualification gates

- A2-02: immutable DTO tests, invalid and boundary values, correct
  normalization; CI green.
- A2-03: new optional Protocol, structural-typing test and regression proving
  the existing listing adapter still satisfies its original Protocol; CI green.
- A2-04/A2-05: public API, handler and immutable view mapping, implemented.
- A2-06: memory and SQLAlchemy search, composition roots and shared tests, CI-qualified.
- A2-07: regression tests, public examples and release qualification pending final CI.
- A3: **shared behavioral suite** over InMemory, SQLite, PostgreSQL,
  including Unicode and deterministic tie-breaking.

## Non-goals

No mandatory database/HTTP dependency, full CQRS infrastructure, external
search engine, distributed search, fuzzy matching, or changes to Supplier
domain invariants.

## Design concepts

- **Command-Query Separation** - reads must not modify domain state.
- **Interface Segregation Principle** - clients depend only on supported
  query capabilities.
- **Dependency Inversion / Ports & Adapters** - handlers depend on a protocol.
- **DTO and immutable data** - validated input independent of transport.
- **Liskov Substitution + Contract Testing** - future adapters must provide
  equivalent observable behavior.
- **KISS / YAGNI** - no search infrastructure without demonstrated need.

**Delivery note:** This ADR records the design and implementation on the
`0.4.0a2` candidate branch. The milestone can be closed only after all PR
quality/CI gates, merge and main-branch verification. Unicode/collation
substitutability and full PostgreSQL search qualification are reserved for A3.
