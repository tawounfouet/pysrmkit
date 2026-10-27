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
from pysrmkit.public.events import EventsAPI


class PySRMKit:
    """Stable facade grouping the public Supplier Domain capability APIs.

    Runtime factories expose explicit composition roots while keeping infrastructure
    dependencies outside the Domain and Application layers.
    """

    @classmethod
    def in_memory(cls) -> PySRMKit:
        """Build a complete local runtime backed by in-memory repositories."""
        from pysrmkit.public.composition import compose_in_memory

        (
            suppliers,
            relationships,
            onboardings,
            assessments,
            qualifications,
            events,
        ) = compose_in_memory()
        return cls(
            suppliers=suppliers,
            relationships=relationships,
            onboardings=onboardings,
            assessments=assessments,
            qualifications=qualifications,
            events=events,
        )

    @classmethod
    def sql(cls, engine: Engine) -> PySRMKit:
        """Build a SQLAlchemy-backed runtime around an externally owned Engine."""
        from pysrmkit.public.sql_composition import compose_sql

        (
            suppliers,
            relationships,
            onboardings,
            assessments,
            qualifications,
            events,
        ) = compose_sql(engine)
        return cls(
            suppliers=suppliers,
            relationships=relationships,
            onboardings=onboardings,
            assessments=assessments,
            qualifications=qualifications,
            events=events,
        )

    def __init__(
        self,
        *,
        suppliers: SuppliersAPI,
        relationships: RelationshipsAPI,
        onboardings: OnboardingsAPI,
        assessments: AssessmentsAPI,
        qualifications: QualificationsAPI,
        events: EventsAPI,
    ) -> None:
        self._suppliers = suppliers
        self._relationships = relationships
        self._onboardings = onboardings
        self._assessments = assessments
        self._qualifications = qualifications
        self._events = events

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

    @property
    def events(self) -> EventsAPI:
        """Typed synchronous public Domain Event subscription API."""
        return self._events
