"""Value Objects and results for Supplier Assessment."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Self
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class AssessmentId:
    """Stable internal identity of a SupplierAssessment Aggregate."""

    value: UUID

    @classmethod
    def new(cls) -> Self:
        return cls(uuid4())

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class AssessmentType:
    """Reference value describing the business kind of an assessment."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().upper()
        if not normalized:
            raise ValueError("AssessmentType value is required")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class AssessmentQuestion:
    """Question snapshot owned by one assessment execution."""

    code: str
    mandatory: bool = True
    maximum_score: int = 100

    def __post_init__(self) -> None:
        code = self.code.strip().upper()
        if not code:
            raise ValueError("AssessmentQuestion code is required")
        if self.maximum_score <= 0:
            raise ValueError("AssessmentQuestion maximum_score must be positive")
        object.__setattr__(self, "code", code)


@dataclass(frozen=True, slots=True)
class AssessmentAnswer:
    """Scored answer to one question snapshot."""

    question_code: str
    score: int

    def __post_init__(self) -> None:
        code = self.question_code.strip().upper()
        if not code:
            raise ValueError("AssessmentAnswer question_code is required")
        if self.score < 0:
            raise ValueError("AssessmentAnswer score cannot be negative")
        object.__setattr__(self, "question_code", code)


@dataclass(frozen=True, slots=True)
class AssessmentScore:
    """Percentage assessment score in the inclusive range 0..100."""

    value: int

    def __post_init__(self) -> None:
        if not 0 <= self.value <= 100:
            raise ValueError("AssessmentScore value must be between 0 and 100")


class AssessmentDecision(StrEnum):
    """Optional assessment-level decision kept distinct from QualificationDecision."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
