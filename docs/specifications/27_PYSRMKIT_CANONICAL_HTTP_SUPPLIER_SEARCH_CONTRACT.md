# PySRMKit - Canonical HTTP Supplier Search Contract

**Document:** `27_PYSRMKIT_CANONICAL_HTTP_SUPPLIER_SEARCH_CONTRACT.md`  
**Cycle:** 4 - Multi-Consumer Integration Qualification  
**Milestone:** `0.4.0a4` (work in progress)  
**Lot:** A4-02 - Canonical HTTP Supplier Search  
**Date:** 2026-10-29  
**Status:** Implemented on PR branch; qualification pending

## 1. Motivation

A4-01 documented that the existing example HTTP endpoint,
`GET /suppliers?query=...`, is **not** equivalent to the public
`SuppliersAPI.search()` contract:

- Legacy HTTP `query` scans legal name, trading name, supplier type,
  country code and external identifier values, using repeated `list()`.
- The canonical Python search matches only legal and trading name; exact
  supplier-type and country-code filters are separate parameters.
- Legacy HTTP result order follows UUID-based listing, whereas canonical
  search orders by case-insensitive legal name and UUID ties.
- Legacy HTTP paginates after fetching all Suppliers; the SQL canonical
  adapter filters, sorts and paginates within the database.

Replacing the legacy implementation would silently break existing
consumers, including the Next.js dashboard demonstration.

## 2. Decision - additive, opt-in HTTP adapter

Add the route:

```text
GET /suppliers/search
```

as a **new** FastAPI example host endpoint. It delegates directly to:

```python
srm.suppliers.search(
    query=query,
    country_code=country_code,
    supplier_type=supplier_type,
    sort_by=sort_by,
    sort_order=sort_order,
    offset=offset,
    limit=limit,
)
```

Do **not** modify or deprecate `GET /suppliers`, including its
legacy `?query` search, in this milestone.

This is an **Expand-and-Contract** style migration boundary:
the canonical route is available for opt-in consumers while the
legacy route remains unchanged. No migration of the dashboard is
implied until a separately qualified A4-04 decision.

## 3. Transport contract

| Input | HTTP type | Default | Rule |
| --- | --- | --- | --- |
| `query` | optional string | absent | Max 100 chars at HTTP boundary; trimmed in public DTO; name matching |
| `country_code` | optional string | absent | Trimmed/validated as two-letter code by public DTO |
| `supplier_type` | optional string | absent | Max 100 chars; exact case-sensitive filter after trimming |
| `sort_by` | literal | `legal_name` | Only `legal_name` |
| `sort_order` | literal | `asc` | `asc` or `desc` |
| `offset` | integer | 0 | Nonnegative |
| `limit` | integer | 25 | Between 1 and 100 |

The Python `search()` default limit remains **100**; the opt-in
HTTP host defaults to **25**, intentionally retaining the existing
example HTTP pagination convention.

For a valid request, return HTTP **200** with the existing
`SupplierPageResponse` JSON shape:

```json
{
  "items": [
    {
      "supplier_id": "<UUID>",
      "legal_name": "Atlas Components",
      "trading_name": "Atlas",
      "supplier_type": "MANUFACTURER",
      "country_code": "FR",
      "external_identifiers": []
    }
  ],
  "total": 1,
  "offset": 0,
  "limit": 25
}
```

`total` counts filtered matches **before** pagination.
`items` preserve the canonical search ordering, not UUID listing
order. `offset` and `limit` in the JSON mirror the validated inputs.

HTTP type/constraint violations are handled by FastAPI validation
(**422**). Business-DTO `ValueError` (e.g. invalid country code)
is mapped to the same HTTP **422**, rather than leaking a server 500.
Unexpected runtime or persistence errors are **not** broadly caught
or converted to successful empty results.

## 4. Compatibility gates

A4-02 tests use the **same runtime** to compare HTTP and Python
results under both InMemory and file-backed SQLite:

- Canonical ASCII name search, asc/desc ordering and page boundaries.
- Country and supplier-type combined filters and DTO input normalization.
- Unfiltered canonical `search()` order, distinct from `list()`.
- Exact result UUID sequence, legal names, filtered total, offset and limit.
- Literal percent/underscore handling, empty result and read-only behavior.
- Invalid offset, limit, country, sort and max-size text return 422.
- Legacy `GET /suppliers?query=SERVICE` and external-ID search continue to
  return their original results. Canonical `/suppliers/search` does not
  silently inherit these additional search fields.

A4-03 will extend the **canonical HTTP transport contract** to real
PostgreSQL. A4-04 will validate the dashboard's deliberate use of the
legacy route until an explicit consumer migration is accepted.

## 5. Architecture and design learning

- **Ports & Adapters / DIP:** the FastAPI host calls the public Python
  Facade, not the ORM repository or Domain entities.
- **Anti-Corruption Layer:** transport validation and JSON mapping stay
  outside Core; immutable Views remain the application output.
- **Command-Query Separation:** this route is read-only and emits no
  Supplier command events.
- **Expand-and-Contract:** additive route avoids breaking existing
  consumer semantics.
- **Contract Testing / LSP:** compare observable API results without
  conflating legacy behavior with the canonical Port.
- **KISS / YAGNI:** no new persistence schema, adapter, framework
  dependency, full-text index or generic HTTP route generator.

## 6. Explicit limitations and exit gates

Unicode matching and name ordering remain backend-dependent beyond
the already qualified ASCII contract. No claim of production latency
is made. The example HTTP host is **not** promoted as PySRMKit's
canonical core API.

- [ ] A4-02 PR CI `quality`, `postgresql`, `integration` green.
- [ ] Merge exact qualified PR head into `main`.
- [ ] Post-merge main CI green.
- [ ] A4-03 real PostgreSQL HTTP transport tests.

The package remains `0.4.0a3` until the final A4 release gate.
