"""Commands for Supplier application use cases."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExternalIdentifierInput:
    """Primitive input used to construct an ExternalIdentifier in the Handler."""

    kind: str
    value: str
    source_system: str | None = None
    jurisdiction_code: str | None = None


@dataclass(frozen=True, slots=True)
class RegisterSupplier:
    """Intent to register a new canonical Supplier."""

    legal_name: str
    trading_name: str | None = None
    supplier_type: str | None = None
    country_code: str | None = None
    external_identifiers: tuple[ExternalIdentifierInput, ...] = ()
