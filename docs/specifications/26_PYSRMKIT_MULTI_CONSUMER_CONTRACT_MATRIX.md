# PySRMKit - Multi-Consumer Contract and Integration Plan

**Document:** `26_PYSRMKIT_MULTI_CONSUMER_CONTRACT_MATRIX.md`  
**Cycle:** 4 - Industrialisation & Integration Qualification  
**Milestone:** `0.4.0a4` - Multi-Consumer Integration Qualification (proposed scope)  
**Work package:** A4-01 - Consumer Contract Inventory and Characterization  
**Date:** 2026-10-29  
**Status:** A4-01 through A4-06 qualified on main (release CI #270)

## 1. Source of scope and decision status

The Cycle 4 README/CHANGELOG identifies `0.4.0a1` through `0.4.0a5`
as reproducibility, query contracts, **multi-consumer** and end-to-end CI
qualification. The repository does **not** currently define a detailed A4
work-package breakdown. The proposed A4 sequence below is a **new planning
decision** based on implemented consumers and evidence, not a claim that
the frozen `13_PYSRMKIT_IMPLEMENTATION_ROADMAP.md` already specifies it.
That frozen roadmap only covered the initial `0.1.x` Core cycle.

The third Cycle 4 milestone `0.4.0a3` is already qualified on `main`
(CI #253). Its portable Supplier search contract is ASCII-scoped, with
Unicode/collation differences documented and SQL plans measured.

## 2. Consumers found in the repository

```text
Python Consumer
  -> PySRMKit.in_memory() / PySRMKit.sql(engine)
  -> SuppliersAPI.search() [canonical read/query contract]
  -> SupplierSearchService Port
  -> InMemory / SQLAlchemy

FastAPI example host
  -> GET /suppliers?query=...
  -> _search_suppliers()
  -> SuppliersAPI.list() for all pages
  -> Python-side matching and slicing

Next.js dashboard demonstration
  -> HTTP /suppliers API
  -> dashboard UI, E2E browser journey
```

The FastAPI implementation remains in `examples/http_api.py`, not in
the domain/application layer; the dashboard is an independent demonstration
repository used by CI. This architecture distinction matters: PySRMKit's
**public Python API**, not the HTTP host, is the business contract.

## 3. Observed contract differences

| Dimension | Python `suppliers.search()` | FastAPI `GET /suppliers?query` |
| --- | --- | --- |
| Text match fields | Legal or trading name | Legal/trading name, Supplier Type, Country Code, external ID values |
| Text case behavior | ASCII portable; Unicode backend-specific | Python `casefold()` on fetched Views |
| Sorting | Case-insensitive legal name, UUID tie-break | Legacy `list()` UUID ordering |
| Pagination | Filter/count/order/paginate in adapter | Fetch all pages; filter and slice in Python |
| Combined filters | Country Code, Supplier Type | Not yet exposed as query parameters |
| Scalar validation | Immutable `SearchSuppliersQuery` | FastAPI query `offset >= 0`, `1 <= limit <= 100`, `query` max 100 |
| Transport | Typed immutable `SupplierPageView` | JSON `SupplierPageResponse` |
| Dependency | No HTTP or ORM runtime required | Optional FastAPI/SQLAlchemy example |

**Risk:** Replacing the old HTTP `query` path with
`srm.suppliers.search(query=...)` would silently remove matching by
Supplier Type/Country/External ID and change the ordering/pagination
semantics consumed by the existing Next.js demonstration.

A successful browser smoke test is not evidence of complete API parity.
The differences must be made explicit **before** refactoring.

## 4. A4-01 executable characterization

`tests/consumers/test_supplier_search_contract.py` parameterizes a
single runtime over **InMemory and SQLite**, then consumes the same
supplier state from the Python API and an in-process FastAPI TestClient.

The tests assert:

1. Same result *identity set* for shared ASCII legal/trading-name queries
   when the whole result set fits on one page; no false ordering guarantee.
2. Unfiltered HTTP listing preserves the public legacy `list()` result,
   including UUID order, pagination and totals.
3. HTTP Supplier Type search intentionally returns results that
   `suppliers.search(query=...)` does not promise.
4. HTTP external-ID search intentionally returns results that
   `suppliers.search(query=...)` does not promise.
5. HTTP finds matches beyond the first 100 records, preserving its
   current full-scan search behavior, without pretending it is efficient.

These are **characterization tests**: they document the actual consumer
contracts, including drift, rather than asserting unsupported parity.

## 5. Proposed A4 rollout - not yet a frozen roadmap

| Lot | Proposed scope | Exit gate |
| --- | --- | --- |
| A4-01 | Inventory and characterize Python, FastAPI and dashboard read contracts | Tests and CI green, documented drift |
| A4-02 | Introduce an explicit **canonical HTTP search surface** which delegates to `suppliers.search()`, preserving legacy `GET /suppliers` behavior | Matching filter/count/order contract and error mapping in HTTP tests |
| A4-03 | Qualify canonical HTTP search over InMemory, SQLite and PostgreSQL | Shared transport tests and CI PostgreSQL green |
| A4-04 | Verify Next.js dashboard intentionally retains the legacy HTTP surface | Browser E2E checks vendor-code search and confirms legacy/canonical divergence |
| A4-05 | Qualify cross-consumer pagination, validation, errors and data isolation | Regression matrix complete |
| A4-06 | Finalize `0.4.0a4` version, evidence report and main-branch CI | PR and post-merge all green |

A4-02 selects the additive `GET /suppliers/search` route and preserves
`GET /suppliers?query` unchanged. The transport contract, 422 mapping,
pagination defaults and compatibility gates are recorded in
[ADR 27](27_PYSRMKIT_CANONICAL_HTTP_SUPPLIER_SEARCH_CONTRACT.md).
The A4-02 implementation and CI are a separate PR.

Non-goals at A4-01: no production API changes, no new SQL index, no
new domain rules, no mandatory dependency, no public CLI, no HTTP
interface promoted as the canonical Supplier domain API.

## 6. Architecture and design learning

- **Ports & Adapters:** HTTP is an adapter/consumer of the public Python
  facade, not a replacement for the `SupplierSearchService` contract.
- **Anti-Corruption Layer:** JSON shape and HTTP status/validation can
  differ from typed business objects without redefining business meaning.
- **Interface Segregation / DIP:** consumers use narrow business APIs;
  the port stays free of FastAPI and SQLAlchemy.
- **Contract Testing and Characterization Testing:** assert proven
  equivalences while recording legacy divergences for safe migration.
- **Strangler Fig / Expand-and-Contract (candidate):** add the canonical
  HTTP path without removing the old endpoint, then migrate consumers
  only when tests prove compatibility.
- **KISS / YAGNI:** no new CLI or generic transport abstraction merely
  to count additional consumers.

## 7. Qualification

- [x] `0.4.0a3` baseline source qualified (main CI #253).
- [x] A4-01 tests pass on InMemory and SQLite under `quality`.
- [x] A4-01 PR #40 CI #256 `quality`, `postgresql`, `integration` green.
- [x] A4-01 merged as `5b57e07` and post-merge `main` CI #257 qualified.
- [x] A4-02 `/suppliers/search` opt-in route qualified (PR #41, main CI #259).
- [x] A4-03 real PostgreSQL HTTP parity qualified (PR #42, main CI #262).
- [x] A4-04 Next.js legacy consumer qualified (PR #43, main CI #265).
- [x] A4-05 regression and isolation qualified (PR #44, main CI #268).
- [x] A4-06 release PR #45 CI #269 and post-merge main CI #270 qualified.

**Source-release status:** `0.4.0a4` qualified on main via PR #45
and CI #270. No Git tag or PyPI publication is implied.

## 8. A4-04 dashboard consumer decision

The dashboard's `app/lib/data.ts` uses `GET /suppliers` with `offset`,
`limit` and optional `query`; it does not consume the opt-in
`GET /suppliers/search` endpoint. This distinction is intentionally
retained under A4-04. The browser E2E adds real API and browser tests
for vendor code `SUP-008` and country `FI`, protecting the legacy UI
contract. See [A4-04 dashboard qualification](../qualification/0.4.0a4-a4-04-dashboard.md).

A4-04 does not modify the external Next.js repository. The tested
external revision is resolved at CI checkout; exact reproducibility
across future updates would require a pinned commit.
