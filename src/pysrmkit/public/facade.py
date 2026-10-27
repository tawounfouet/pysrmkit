"""Main public facade for PySRMKit."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine

from pysrmkit.public.capabilities import (
    AssessmentsAPI,
    OnboardingsAPI,
    QualificationsAPI,
    RelationshipsAPI,
    SuppliersAPI,
)


class PySRMKit:
    """Stable facade grouping the public Supplier Domain capability APIs.

    Runtime factories expose explicit composition roots while keeping infrastructure\n    dependencies outside the Domain and Application layers.
    """

    @classmethod
    def in_memory(cls) -> PySRMKit:
        """Build a complete local runtime backed by in-memory repositories."""
        from pysrmkit.public.composition import compose_in_memory

        suppliers, relationships, onboardings, assessments, qualifications = compose_in_memory()
        return cls(
            suppliers=suppliers,
            relationships=relationships,
            onboardings=onboardings,
            assessments=assessments,
            qualifications=qualifications,
        )

    @classmethod
    def sql(cls, engine: Engine) -> PySRMKit:
        """Build a SQLAlchemy-backed runtime around an externally owned Engine."""
        from pysrmkit.public.sql_composition import compose_sql

        suppliers, relationships, onboardings, assessments, qualifications = compose_sql(engine)
        return cls(
            suppliers=suppliers,
            relationships=relationships,
            onboardings=onboardings,
            assessments=assessments,
            qualifications=qualifications,
        )

    def __init__(
        self,
        *,
        suppliers: SuppliersAPI,
        relationships: RelationshipsAPI,
        onboardings: OnboardingsAPI,
        assessments: AssessmentsAPI,
        qualifications: QualificationsAPI,
    ) -> None:
        self._suppliers = suppliers
        self._relationships = relationships
        self._onboardings = onboardings
        self._assessments = assessments
        self._qualifications = qualifications

    @property
    def suppliers(self) -> SuppliersAPI:
        """Supplier capability API."""
        return self._suppliers

    @property
    def relationships(self) -> RelationshipsAPI:
        """SupplierRelationship capability API."""
        return self._relationships

    @property
    def onboardings(self) -> OnboardingsAPI:
        """Supplier Onboarding capability API."""
        return self._onboardings

    @property
    def assessments(self) -> AssessmentsAPI:
        """Supplier Assessment capability API."""
        return self._assessments

    @property
    def qualifications(self) -> QualificationsAPI:
        """Supplier Qualification capability API."""
        return self._qualifications
