"""Supplier Core Value Object tests."""

from uuid import uuid4

import pytest

from pysrmkit.domain.supplier.errors import InvalidExternalIdentifier, InvalidSupplierIdentity
from pysrmkit.domain.supplier.value_objects import (
    Address,
    CapabilityCode,
    CategoryCode,
    CountryCode,
    ExternalIdentifier,
    SupplierId,
    SupplierIdentity,
)


def test_supplier_id_has_value_equality_and_stable_string_representation() -> None:
    value = uuid4()

    left = SupplierId(value)
    right = SupplierId(value)

    assert left == right
    assert hash(left) == hash(right)
    assert str(left) == str(value)


def test_supplier_id_new_creates_distinct_identifiers() -> None:
    assert SupplierId.new() != SupplierId.new()


def test_supplier_identity_requires_a_non_blank_legal_name() -> None:
    with pytest.raises(InvalidSupplierIdentity):
        SupplierIdentity(legal_name="   ")


def test_supplier_identity_normalizes_optional_text() -> None:
    identity = SupplierIdentity(
        legal_name="  ACME France  ",
        trading_name="  ACME  ",
        supplier_type="  COMPANY  ",
        country=CountryCode("fr"),
    )

    assert identity.legal_name == "ACME France"
    assert identity.trading_name == "ACME"
    assert identity.supplier_type == "COMPANY"
    assert identity.country == CountryCode("FR")


def test_external_identifier_requires_kind_and_value() -> None:
    with pytest.raises(InvalidExternalIdentifier):
        ExternalIdentifier(kind="", value="123")

    with pytest.raises(InvalidExternalIdentifier):
        ExternalIdentifier(kind="SIREN", value="   ")


def test_external_identifier_has_normalized_value_semantics() -> None:
    identifier = ExternalIdentifier(
        kind=" siren ",
        value=" 123456789 ",
        source_system=" registry ",
        jurisdiction=CountryCode("fr"),
    )

    assert identifier == ExternalIdentifier(
        kind="SIREN",
        value="123456789",
        source_system="registry",
        jurisdiction=CountryCode("FR"),
    )


def test_country_code_normalizes_alpha_two_and_rejects_invalid_value() -> None:
    assert CountryCode(" fr ") == CountryCode("FR")

    with pytest.raises(ValueError):
        CountryCode("FRA")

    with pytest.raises(ValueError):
        CountryCode("1F")


def test_address_is_multi_country_and_requires_line_and_city() -> None:
    address = Address(
        line1="  1 Supplier Street ",
        city=" Paris ",
        country=CountryCode("FR"),
        postal_code=" 75001 ",
    )

    assert address.line1 == "1 Supplier Street"
    assert address.city == "Paris"
    assert address.postal_code == "75001"

    with pytest.raises(ValueError):
        Address(line1="", city="Paris", country=CountryCode("FR"))

    with pytest.raises(ValueError):
        Address(line1="1 Supplier Street", city="", country=CountryCode("FR"))


def test_category_and_capability_codes_are_lightweight_non_blank_values() -> None:
    assert CategoryCode(" IT_SERVICES ").value == "IT_SERVICES"
    assert CapabilityCode(" DATA_ENGINEERING ").value == "DATA_ENGINEERING"

    with pytest.raises(ValueError):
        CategoryCode(" ")

    with pytest.raises(ValueError):
        CapabilityCode(" ")
