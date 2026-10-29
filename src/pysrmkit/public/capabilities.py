"""Stable capability-oriented Python API for PySRMKit."""

from __future__ import annotations

from typing import Literal

from pysrmkit.application.assessment.commands import (
    AssessmentQuestionInput,
    CompleteSupplierAssessment,
    CreateSupplierAssessment,
    RecordAssessmentAnswer,
)
from pysrmkit.application.assessment.results import (
    CompleteSupplierAssessmentResult,
    CreateSupplierAssessmentResult,
)
from pysrmkit.application.onboarding.commands import (
    CompleteSupplierOnboarding,
    OnboardingRequirementInput,
    SatisfyOnboardingRequirement,
)
from pysrmkit.application.onboarding.queries import GetOnboardingProgress
from pysrmkit.application.qualification.commands import (
    EvaluateSupplierQualification,
    RequestSupplierQualification,
)
from pysrmkit.application.qualification.results import (
    EvaluateSupplierQualificationResult,
    RequestSupplierQualificationResult,
)
from pysrmkit.application.relationship.commands import (
    CreateSupplierRelationship,
    InviteSupplierRelationship,
    StartSupplierOnboarding,
)
from pysrmkit.application.relationship.results import CreateSupplierRelationshipResult
from pysrmkit.application.supplier.commands import ExternalIdentifierInput, RegisterSupplier
from pysrmkit.application.supplier.results import RegisterSupplierResult
from pysrmkit.domain.assessment.value_objects import (
    AssessmentDecision,
    AssessmentId,
)
from pysrmkit.domain.onboarding.value_objects import (
    OnboardingId,
    OnboardingProgress,
    OnboardingRequirementCode,
)
from pysrmkit.domain.qualification.value_objects import (
    QualificationId,
    QualificationScope,
)
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId
from pysrmkit.public._handler import Handler
from pysrmkit.public._queries import (
    GetAssessment,
    GetCurrentQualificationForScope,
    GetOnboardingForRelationship,
    GetQualification,
    GetSupplier,
    GetSupplierRelationship,
    ListSuppliers,
    SearchSuppliersQuery,
)
from pysrmkit.public.views import (
    AssessmentView,
    OnboardingView,
    QualificationView,
    SupplierPageView,
    SupplierRelationshipView,
    SupplierView,
)


class SuppliersAPI:
    """Public entry points for canonical Supplier use cases."""

    def __init__(
        self,
        *,
        register_supplier: Handler[RegisterSupplier, RegisterSupplierResult],
        get_supplier: Handler[GetSupplier, SupplierView],
        list_suppliers: Handler[ListSuppliers, SupplierPageView] | None = None,
        search_suppliers: Handler[SearchSuppliersQuery, SupplierPageView] | None = None,
    ) -> None:
        self._register_supplier = register_supplier
        self._get_supplier = get_supplier
        self._list_suppliers = list_suppliers
        self._search_suppliers = search_suppliers

    def register(
        self,
        *,
        legal_name: str,
        trading_name: str | None = None,
        supplier_type: str | None = None,
        country_code: str | None = None,
        external_identifiers: tuple[ExternalIdentifierInput, ...] = (),
    ) -> RegisterSupplierResult:
        """Register a canonical Supplier using application-friendly primitive inputs."""
        return self._register_supplier.handle(
            RegisterSupplier(
                legal_name=legal_name,
                trading_name=trading_name,
                supplier_type=supplier_type,
                country_code=country_code,
                external_identifiers=external_identifiers,
            )
        )

    def get(self, *, supplier_id: SupplierId) -> SupplierView:
        """Return an immutable Supplier snapshot or raise SupplierNotFound."""
        return self._get_supplier.handle(GetSupplier(supplier_id=supplier_id))

    def list(self, *, offset: int = 0, limit: int = 100) -> SupplierPageView:
        """Return one deterministic, bounded page of Suppliers."""
        if self._list_suppliers is None:
            raise NotImplementedError("Supplier listing is not configured for this runtime")
        return self._list_suppliers.handle(ListSuppliers(offset=offset, limit=limit))

    def search(
        self,
        *,
        query: str | None = None,
        country_code: str | None = None,
        supplier_type: str | None = None,
        sort_by: Literal["legal_name"] = "legal_name",
        sort_order: Literal["asc", "desc"] = "asc",
        offset: int = 0,
        limit: int = 100,
    ) -> SupplierPageView:
        """Request a filtered Supplier page through an optional query handler.

        Design concepts:
            - Facade: consumers receive a stable, capability-oriented API.
            - Immutable DTO: validation and normalization are transport-independent.
            - Dependency Inversion: the facade only knows a typed Handler protocol.
        """
        if self._search_suppliers is None:
            raise NotImplementedError("Supplier search is not configured for this runtime")
        return self._search_suppliers.handle(
            SearchSuppliersQuery(
                query=query,
                country_code=country_code,
                supplier_type=supplier_type,
                sort_by=sort_by,
                sort_order=sort_order,
                offset=offset,
                limit=limit,
            )
        )


class RelationshipsAPI:
    """Public entry points for SupplierRelationship lifecycle use cases."""

    def __init__(
        self,
        *,
        create_relationship: Handler[
            CreateSupplierRelationship,
            CreateSupplierRelationshipResult,
        ],
        invite_relationship: Handler[InviteSupplierRelationship, None],
        start_onboarding: Handler[StartSupplierOnboarding, None],
        get_relationship: Handler[GetSupplierRelationship, SupplierRelationshipView],
    ) -> None:
        self._create_relationship = create_relationship
        self._invite_relationship = invite_relationship
        self._start_onboarding = start_onboarding
        self._get_relationship = get_relationship

    def create(
        self,
        *,
        supplier_id: SupplierId,
        organization_id: str,
    ) -> CreateSupplierRelationshipResult:
        """Create the relationship between a Supplier and one internal organization."""
        return self._create_relationship.handle(
            CreateSupplierRelationship(
                supplier_id=supplier_id,
                organization_id=InternalOrganizationId(organization_id),
            )
        )

    def invite(self, *, relationship_id: SupplierRelationshipId) -> None:
        """Invite an existing SupplierRelationship."""
        self._invite_relationship.handle(
            InviteSupplierRelationship(relationship_id=relationship_id)
        )

    def start_onboarding(
        self,
        *,
        relationship_id: SupplierRelationshipId,
        requirements: tuple[OnboardingRequirementInput, ...] = (),
    ) -> None:
        """Move a relationship into onboarding with an explicit requirement snapshot."""
        self._start_onboarding.handle(
            StartSupplierOnboarding(
                relationship_id=relationship_id,
                requirements=requirements,
            )
        )

    def get(self, *, relationship_id: SupplierRelationshipId) -> SupplierRelationshipView:
        """Return an immutable SupplierRelationship snapshot."""
        return self._get_relationship.handle(GetSupplierRelationship(relationship_id))


class OnboardingsAPI:
    """Public entry points for Supplier Onboarding use cases."""

    def __init__(
        self,
        *,
        satisfy_requirement: Handler[SatisfyOnboardingRequirement, None],
        complete_onboarding: Handler[CompleteSupplierOnboarding, None],
        get_progress: Handler[GetOnboardingProgress, OnboardingProgress],
        get_for_relationship: Handler[GetOnboardingForRelationship, OnboardingView],
    ) -> None:
        self._satisfy_requirement = satisfy_requirement
        self._complete_onboarding = complete_onboarding
        self._get_progress = get_progress
        self._get_for_relationship = get_for_relationship

    def satisfy_requirement(
        self,
        *,
        onboarding_id: OnboardingId,
        requirement_code: str,
    ) -> None:
        """Mark one onboarding requirement as satisfied."""
        self._satisfy_requirement.handle(
            SatisfyOnboardingRequirement(
                onboarding_id=onboarding_id,
                requirement_code=OnboardingRequirementCode(requirement_code),
            )
        )

    def complete(self, *, onboarding_id: OnboardingId) -> None:
        """Complete an onboarding whose mandatory requirements are satisfied."""
        self._complete_onboarding.handle(CompleteSupplierOnboarding(onboarding_id=onboarding_id))

    def progress(self, *, onboarding_id: OnboardingId) -> OnboardingProgress:
        """Return computed onboarding progress."""
        return self._get_progress.handle(GetOnboardingProgress(onboarding_id=onboarding_id))

    def get_for_relationship(self, *, relationship_id: SupplierRelationshipId) -> OnboardingView:
        """Return the relationship onboarding snapshot."""
        return self._get_for_relationship.handle(GetOnboardingForRelationship(relationship_id))


class AssessmentsAPI:
    """Public entry points for Supplier Assessment use cases."""

    def __init__(
        self,
        *,
        create_assessment: Handler[
            CreateSupplierAssessment,
            CreateSupplierAssessmentResult,
        ],
        record_answer: Handler[RecordAssessmentAnswer, None],
        complete_assessment: Handler[
            CompleteSupplierAssessment,
            CompleteSupplierAssessmentResult,
        ],
        get_assessment: Handler[GetAssessment, AssessmentView],
    ) -> None:
        self._create_assessment = create_assessment
        self._record_answer = record_answer
        self._complete_assessment = complete_assessment
        self._get_assessment = get_assessment

    def create(
        self,
        *,
        relationship_id: SupplierRelationshipId,
        assessment_type: str,
        questions: tuple[AssessmentQuestionInput, ...],
    ) -> CreateSupplierAssessmentResult:
        """Create a relationship-scoped assessment."""
        return self._create_assessment.handle(
            CreateSupplierAssessment(
                relationship_id=relationship_id,
                assessment_type=assessment_type,
                questions=questions,
            )
        )

    def record_answer(
        self,
        *,
        assessment_id: AssessmentId,
        question_code: str,
        score: int,
    ) -> None:
        """Record or replace one assessment answer before completion."""
        self._record_answer.handle(
            RecordAssessmentAnswer(
                assessment_id=assessment_id,
                question_code=question_code,
                score=score,
            )
        )

    def complete(
        self,
        *,
        assessment_id: AssessmentId,
        decision: AssessmentDecision | None = None,
    ) -> CompleteSupplierAssessmentResult:
        """Complete an assessment and return its application result."""
        return self._complete_assessment.handle(
            CompleteSupplierAssessment(
                assessment_id=assessment_id,
                decision=decision,
            )
        )

    def get(self, *, assessment_id: AssessmentId) -> AssessmentView:
        """Return an immutable SupplierAssessment snapshot."""
        return self._get_assessment.handle(GetAssessment(assessment_id))


class QualificationsAPI:
    """Public entry points for Supplier Qualification use cases."""

    def __init__(
        self,
        *,
        request_qualification: Handler[
            RequestSupplierQualification,
            RequestSupplierQualificationResult,
        ],
        evaluate_qualification: Handler[
            EvaluateSupplierQualification,
            EvaluateSupplierQualificationResult,
        ],
        get_qualification: Handler[GetQualification, QualificationView],
        get_current_for_scope: Handler[GetCurrentQualificationForScope, QualificationView],
    ) -> None:
        self._request_qualification = request_qualification
        self._evaluate_qualification = evaluate_qualification
        self._get_qualification = get_qualification
        self._get_current_for_scope = get_current_for_scope

    def request(
        self,
        *,
        relationship_id: SupplierRelationshipId,
        scope: QualificationScope,
    ) -> RequestSupplierQualificationResult:
        """Request one scoped Supplier qualification."""
        return self._request_qualification.handle(
            RequestSupplierQualification(
                relationship_id=relationship_id,
                scope=scope,
            )
        )

    def evaluate(
        self,
        *,
        qualification_id: QualificationId,
    ) -> EvaluateSupplierQualificationResult:
        """Evaluate a pending qualification through the configured domain policy."""
        return self._evaluate_qualification.handle(
            EvaluateSupplierQualification(qualification_id=qualification_id)
        )

    def get(self, *, qualification_id: QualificationId) -> QualificationView:
        """Return an immutable SupplierQualification snapshot."""
        return self._get_qualification.handle(GetQualification(qualification_id))

    def get_current_for_scope(
        self,
        *,
        relationship_id: SupplierRelationshipId,
        scope: QualificationScope,
    ) -> QualificationView:
        """Return the current qualification for a Relationship and Scope."""
        return self._get_current_for_scope.handle(
            GetCurrentQualificationForScope(relationship_id=relationship_id, scope=scope)
        )
