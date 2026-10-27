"""Supplier Onboarding Value Object tests."""

from uuid import uuid4

import pytest

from pysrmkit.domain.onboarding.value_objects import (
    OnboardingId,
    OnboardingRequirement,
    OnboardingRequirementCode,
)


def test_onboarding_id_has_value_equality_and_stable_string_representation() -> None:
    value = uuid4()

    left = OnboardingId(value)
    right = OnboardingId(value)

    assert left == right
    assert hash(left) == hash(right)
    assert str(left) == str(value)


def test_onboarding_id_new_creates_distinct_identifiers() -> None:
    assert OnboardingId.new() != OnboardingId.new()


def test_requirement_code_is_normalized_and_non_blank() -> None:
    assert OnboardingRequirementCode(" legal_name ").value == "LEGAL_NAME"

    with pytest.raises(ValueError):
        OnboardingRequirementCode("   ")


def test_requirement_satisfaction_returns_a_new_value() -> None:
    original = OnboardingRequirement(
        code=OnboardingRequirementCode("LEGAL_NAME"),
        mandatory=True,
    )

    satisfied = original.satisfy()

    assert original.satisfied is False
    assert satisfied.satisfied is True
    assert satisfied.code == original.code
    assert satisfied.mandatory is True
    assert satisfied.satisfy() is satisfied
