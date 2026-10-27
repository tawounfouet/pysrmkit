"""Main public facade for PySRMKit."""

from __future__ import annotations

from pysrmkit.public.capabilities import (
    AssessmentsAPI,
    OnboardingsAPI,
    QualificationsAPI,
    RelationshipsAPI,
    SuppliersAPI,
)


class PySRMKit:
    """Stable facade grouping the public Supplier Domain capability APIs.

    Runtime factories are intentionally not defined in 0.3.0a1. The InMemory and
    SQL composition roots belong to the following Cycle 3 milestones.
    """

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
