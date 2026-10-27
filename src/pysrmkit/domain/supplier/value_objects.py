"""Value Objects owned by the Supplier Core capability."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4

from pysrmkit.domain.supplier.errors import InvalidExternalIdentifier, InvalidSupplierIdentity


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


@dataclass(frozen=True, slots=True)
class SupplierId:
    """Stable internal identity of a Supplier Entity."""

    value: UUID

    @classmethod
    def new(cls) -> Self:
        return cls(uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class CountryCode:
    """ISO-like alpha-2 country reference used by the generic Supplier domain."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().upper()
        if len(normalized) != 2 or not normalized.isalpha():
            raise ValueError("CountryCode must contain exactly two alphabetic characters")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ExternalIdentifier:
    """External identifier attached to the canonical Supplier identity."""

    kind: str
    value: str
    source_system: str | None = None
    jurisdiction: CountryCode | None = None

    def __post_init__(self) -> None:
        kind = self.kind.strip().upper()
        value = self.value.strip()
        if not kind:
            raise InvalidExternalIdentifier("External identifier kind is required")
        if not value:
            raise InvalidExternalIdentifier("External identifier value is required")

        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "source_system", _optional_text(self.source_system))


@dataclass(frozen=True, slots=True)
class SupplierIdentity:
    """Descriptive legal/commercial identity of a Supplier Entity."""

    legal_name: str
    trading_name: str | None = None
    supplier_type: str | None = None
    country: CountryCode | None = None

    def __post_init__(self) -> None:
        legal_name = self.legal_name.strip()
        if not legal_name:
            raise InvalidSupplierIdentity("Supplier legal_name is required")

        object.__setattr__(self, "legal_name", legal_name)
        object.__setattr__(self, "trading_name", _optional_text(self.trading_name))
        object.__setattr__(self, "supplier_type", _optional_text(self.supplier_type))


@dataclass(frozen=True, slots=True)
class Address:
    """Multi-country postal address represented by value."""

    line1: str
    city: str
    country: CountryCode
    postal_code: str | None = None
    region: str | None = None
    line2: str | None = None

    def __post_init__(self) -> None:
        line1 = self.line1.strip()
        city = self.city.strip()
        if not line1:
            raise ValueError("Address line1 is required")
        if not city:
            raise ValueError("Address city is required")

        object.__setattr__(self, "line1", line1)
        object.__setattr__(self, "city", city)
        object.__setattr__(self, "postal_code", _optional_text(self.postal_code))
        object.__setattr__(self, "region", _optional_text(self.region))
        object.__setattr__(self, "line2", _optional_text(self.line2))


@dataclass(frozen=True, slots=True)
class CategoryCode:
    """Stable reference into an internal or external supplier taxonomy."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("CategoryCode value is required")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class CapabilityCode:
    """Lightweight reference to a capability a Supplier can provide."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("CapabilityCode value is required")
        object.__setattr__(self, "value", normalized)
