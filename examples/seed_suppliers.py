"""Idempotent Supplier seed for the FastAPI and Next.js integration demo."""

from __future__ import annotations

import os
from dataclasses import dataclass

from pysrmkit import PySRMKit
from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.public import ExternalIdentifierInput

DEFAULT_DATABASE_URL = "postgresql+psycopg://postgres@localhost:5432/pysrmkit"
SOURCE_SYSTEM = "NEXT_DASHBOARD_DEMO"


@dataclass(frozen=True, slots=True)
class SeedSupplier:
    vendor_code: str
    legal_name: str
    trading_name: str
    supplier_type: str
    country_code: str


SUPPLIERS = (
    SeedSupplier("SUP-001", "Asteria Components SAS", "Asteria", "MANUFACTURER", "FR"),
    SeedSupplier("SUP-002", "Boreal Freight AB", "Boreal", "LOGISTICS", "SE"),
    SeedSupplier("SUP-003", "Cobalt Cloud GmbH", "Cobalt Cloud", "SERVICES", "DE"),
    SeedSupplier("SUP-004", "Delta Packaging BV", "Delta", "MANUFACTURER", "NL"),
    SeedSupplier("SUP-005", "Eira Consulting Ltd", "Eira", "SERVICES", "GB"),
    SeedSupplier("SUP-006", "Faro Energia SA", "Faro", "ENERGY", "ES"),
    SeedSupplier("SUP-007", "Gaia Materials SRL", "Gaia", "DISTRIBUTOR", "IT"),
    SeedSupplier("SUP-008", "Helios Data Oy", "Helios", "SERVICES", "FI"),
)


def _existing_vendor_codes(srm: PySRMKit) -> set[str]:
    codes: set[str] = set()
    offset = 0
    limit = 100

    while True:
        page = srm.suppliers.list(offset=offset, limit=limit)
        for supplier in page.items:
            codes.update(
                identifier.value
                for identifier in supplier.external_identifiers
                if identifier.kind == "LOCAL_VENDOR_CODE"
                and identifier.source_system == SOURCE_SYSTEM
            )
        offset += len(page.items)
        if offset >= page.total or not page.items:
            return codes


def seed_suppliers(srm: PySRMKit) -> tuple[int, int]:
    """Register missing demo Suppliers and return created/skipped counts."""
    existing_codes = _existing_vendor_codes(srm)
    created = 0

    for supplier in SUPPLIERS:
        if supplier.vendor_code in existing_codes:
            continue
        srm.suppliers.register(
            legal_name=supplier.legal_name,
            trading_name=supplier.trading_name,
            supplier_type=supplier.supplier_type,
            country_code=supplier.country_code,
            external_identifiers=(
                ExternalIdentifierInput(
                    kind="LOCAL_VENDOR_CODE",
                    value=supplier.vendor_code,
                    source_system=SOURCE_SYSTEM,
                ),
            ),
        )
        created += 1

    return created, len(SUPPLIERS) - created


def main() -> None:
    database_url = os.getenv("PYSRMKIT_DATABASE_URL", DEFAULT_DATABASE_URL)
    engine = create_persistence_engine(database_url)
    try:
        created, skipped = seed_suppliers(PySRMKit.sql(engine))
    finally:
        engine.dispose()

    print(f"Seeded {created} Suppliers; skipped {skipped} existing Suppliers")


if __name__ == "__main__":
    main()
