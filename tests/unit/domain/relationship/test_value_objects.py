"""Supplier Relationship Value Object tests."""

from uuid import uuid4

import pytest

from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierRelationshipId,
)


def test_relationship_id_has_value_equality_and_stable_string_representation() -> None:
    value = uuid4()

    left = SupplierRelationshipId(value)
    right = SupplierRelationshipId(value)

    assert left == right
    assert hash(left) == hash(right)
    assert str(left) == str(value)


def test_relationship_id_new_creates_distinct_identifiers() -> None:
    assert SupplierRelationshipId.new() != SupplierRelationshipId.new()


def test_internal_organization_id_is_a_non_blank_external_reference() -> None:
    organization_id = InternalOrganizationId("  ORG-PARIS  ")

    assert organization_id.value == "ORG-PARIS"
    assert str(organization_id) == "ORG-PARIS"

    with pytest.raises(ValueError):
        InternalOrganizationId("   ")
