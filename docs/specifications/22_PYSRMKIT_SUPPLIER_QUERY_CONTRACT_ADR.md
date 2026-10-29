# PySRMKit - Supplier Query Contract (ADR)

**Document:** `22_PYSRMKIT_SUPPLIER_QUERY_CONTRACT_ADR.md`
**Cycle:** 4 - `0.4.0a2`
**Packages:** A2-01 through A2-07
**Date:** 2026-10-29
**Status:** Accepted for A2-02/A2-03 contract boundaries; adapter semantics pending A2-06/A3

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
2. Add a distinct public `suppliers.search(...)` in a later A2 package; it is
   **not implemented** by the initial DTO/Port work.
3. Use an immutable internal `SearchSuppliersQuery` DTO, with explicit
   validation, whitespace normalization and a pagination limit of 100.
4. Introduce an optional `SupplierSearchService` Protocol instead of adding
   an abstract method to `SupplierQueryService`. A consumer that implements
   only the listing port remains valid. This implements Interface Segregation.
5. Keep the new port in `pysrmkit.ports.queries.supplier`, independent of the
   internal `public._queries` DTO. A future handler will adapt the public
   input into the port's typed parameters, including `CountryCode`.
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
Public SuppliersAPI.search [A2-04]
         |
         v
SearchSuppliersQuery + Handler [A2-05]
         |
         v
SupplierSearchService Protocol [A2-03]
         |
         +--> InMemory search adapter [A3-02]
         +--> SQLAlchemy search adapter [A3-03]
```

The existing `SuppliersAPI.list` -> `SupplierQueryService` path stays
independently supported.

## Qualification gates

- A2-02: immutable DTO tests, invalid and boundary values, correct
  normalization; CI green.
- A2-03: new optional Protocol, structural-typing test and regression proving
  the existing listing adapter still satisfies its original Protocol; CI green.
- A2-04/A2-05: public API, handler and immutable view mapping.
- A2-06/A2-07: complete filtering/pagination/counting and compatibility tests.
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

**Delivery note:** This ADR records an accepted *contract design*, not
completion of the `0.4.0a2` milestone or its adapters.
