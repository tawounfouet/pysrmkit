"""A3-01 deterministic Supplier discovery corpus and expected observations.

This file is test infrastructure, not a production-domain data contract.
ASCII cases are normative. Unicode cases are probes until A3 policy is decided.
"""

from dataclasses import dataclass
from typing import Literal, Protocol
from uuid import UUID

from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import (
    CountryCode,
    ExternalIdentifier,
    SupplierId,
    SupplierIdentity,
)
from pysrmkit.ports.queries.supplier import SupplierSearchService
from pysrmkit.ports.repositories.supplier import SupplierRepository


@dataclass(frozen=True, slots=True)
class SupplierSeed:
    """Fixed canonical identity, independent of creation order or uuid4."""

    code: str
    id_number: int
    legal_name: str
    trading_name: str | None = None
    supplier_type: str | None = None
    country_code: str | None = None

    @property
    def supplier_id(self) -> SupplierId:
        return SupplierId(UUID(int=self.id_number))

    def create(self) -> Supplier:
        return Supplier.reconstitute(
            supplier_id=self.supplier_id,
            identity=SupplierIdentity(
                legal_name=self.legal_name,
                trading_name=self.trading_name,
                supplier_type=self.supplier_type,
                country=CountryCode(self.country_code) if self.country_code is not None else None,
            ),
            external_identifiers=(
                ExternalIdentifier(kind="CORPUS", value=f"A3-{self.id_number:04d}"),
            ),
        )


# All names are ASCII so Python casefold and SQL lower yield the same contract.
# The fixed UUIDs make sorting tie-break assertions exact and reproducible.
ASCII_SUPPLIERS: tuple[SupplierSeed, ...] = (
    SupplierSeed("atlas-a", 1, "Atlas Components", "Atlas", "MANUFACTURER", "FR"),
    SupplierSeed("atlas-b", 2, "Atlas Components", None, "MANUFACTURER", "FR"),
    SupplierSeed("atlas-service", 3, "atlas Logistics", None, "SERVICE", "FR"),
    SupplierSeed("asteria", 4, "Asteria Research", "Atlas Research", "SERVICE", "DE"),
    SupplierSeed("boreal-a", 5, "Boreal Works", None, "SERVICE", "FR"),
    SupplierSeed("boreal-b", 6, "Boreal Works", "North", "MANUFACTURER", "FR"),
    SupplierSeed("cedar", 7, "Cedar Labs", None, "MANUFACTURER", "US"),
    SupplierSeed("delta", 8, "Delta_% Supply", None, "SERVICE", "FR"),
    SupplierSeed("percent", 9, "Percent%Works", None, "SERVICE", "FR"),
    SupplierSeed("under", 10, "Under_Score", None, "SERVICE", "DE"),
    SupplierSeed("zeta", 11, "Zeta Solutions", "Atlas Z", None, "FR"),
    SupplierSeed("no-country", 12, "No Country Vendor"),
    SupplierSeed("nimbus", 13, "Nimbus Services", None, "SERVICE", "FR"),
)


@dataclass(frozen=True, slots=True)
class SearchCase:
    """One expected read-port observation over the complete ASCII corpus."""

    name: str
    expected_codes: tuple[str, ...]
    total: int
    query: str | None = None
    country_code: str | None = None
    supplier_type: str | None = None
    sort_order: Literal["asc", "desc"] = "asc"
    offset: int = 0
    limit: int = 100


SEARCH_CASES: tuple[SearchCase, ...] = (
    SearchCase(
        "all-ascending",
        (
            "atlas-a", "atlas-b", "atlas-service", "asteria",
            "boreal-a", "boreal-b", "cedar", "delta", "nimbus",
            "no-country", "percent", "under", "zeta",
        ),
        13,
    ),
    SearchCase(
        "all-descending-first-five",
        ("zeta", "under", "percent", "no-country", "nimbus"),
        13,
        sort_order="desc",
        limit=5,
    ),
    SearchCase(
        "legal-and-trading-name-contains",
        ("atlas-a", "atlas-b", "atlas-service", "asteria", "zeta"),
        5,
        query="aTlAs",
    ),
    SearchCase(
        "country-and-type-filters",
        ("atlas-a", "atlas-b", "boreal-b"),
        3,
        country_code="FR",
        supplier_type="MANUFACTURER",
    ),
    SearchCase("duplicate-legal-name-desc", ("boreal-a", "boreal-b"), 2,
               query="Boreal", sort_order="desc"),
    SearchCase("trading-name-only", ("boreal-b",), 1, query="north"),
    SearchCase("second-full-page", ("atlas-service", "asteria"), 5,
               query="atlas", offset=2, limit=2),
    SearchCase("last-partial-page", ("zeta",), 5, query="atlas", offset=4, limit=2),
    SearchCase("beyond-final-page", (), 5, query="atlas", offset=100, limit=5),
    SearchCase("no-match", (), 0, query="unfindable", limit=1),
    SearchCase("literal-percent", ("delta", "percent"), 2, query="%"),
    SearchCase("literal-underscore", ("delta", "under"), 2, query="_"),
    SearchCase("supplier-type-exact-case", (), 0, supplier_type="service"),
    SearchCase(
        "supplier-type-service",
        ("atlas-service", "asteria", "boreal-a", "delta",
         "nimbus", "percent", "under"),
        7,
        supplier_type="SERVICE",
    ),
    SearchCase("country-de", ("asteria", "under"), 2, country_code="DE"),
    SearchCase("missing-country-identity", ("no-country",), 1, query="No Country"),
    SearchCase("country-excludes-missing", (), 0, query="No Country", country_code="FR"),
    SearchCase("absent-supplier-type", ("no-country",), 1, query="No Country",
               supplier_type=None),
)


@dataclass(frozen=True, slots=True)
class UnicodeProbe:
    """Informative fixture, not a cross-backend pass/fail assertion yet."""

    name: str
    legal_name: str
    query: str
    issue: str


UNICODE_PROBES: tuple[UnicodeProbe, ...] = (
    UnicodeProbe("sharp-s", "Straße GmbH", "STRASSE", "casefold differs from SQL lower"),
    UnicodeProbe("accented-case", "Étoile", "étoile", "SQL case handling may diverge"),
    UnicodeProbe("accent-insensitivity", "Café", "cafe", "accent-insensitive search is TBD"),
    UnicodeProbe("unicode-normalization", "Cafe\u0301", "Café", "NFC/NFD policy is TBD"),
    UnicodeProbe("turkish-i", "İSTANBUL", "istanbul", "locale-aware casing is TBD"),
)


class SearchableSupplierRepository(SupplierRepository, SupplierSearchService, Protocol):
    """Test-only intersecting Protocol; no change to production Ports."""


def seed_ascii_corpus(repository: SupplierRepository) -> None:
    """Seed stable identities without creating or dispatching Domain Events."""
    for entry in ASCII_SUPPLIERS:
        repository.save(entry.create())


def expected_supplier_ids(case: SearchCase) -> tuple[SupplierId, ...]:
    """Explicit case codes -> stable Supplier identifiers, without re-sorting."""
    ids = {entry.code: entry.supplier_id for entry in ASCII_SUPPLIERS}
    return tuple(ids[code] for code in case.expected_codes)
