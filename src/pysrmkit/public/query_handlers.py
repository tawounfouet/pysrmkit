"""Public query handlers mapping Domain Aggregates to immutable Views."""

from __future__ import annotations

from pysrmkit.application.assessment.errors import SupplierAssessmentNotFound
from pysrmkit.application.onboarding.errors import SupplierOnboardingNotFound
from pysrmkit.application.qualification.errors import SupplierQualificationNotFound
from pysrmkit.application.relationship.errors import (
    SupplierNotFound,
    SupplierRelationshipNotFound,
)
from pysrmkit.domain.qualification.entities import SupplierQualification
from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import CountryCode
from pysrmkit.ports.queries.supplier import SupplierPage, SupplierQueryService, SupplierSearchService
from pysrmkit.ports.repositories.assessment import SupplierAssessmentRepository
from pysrmkit.ports.repositories.onboarding import SupplierOnboardingRepository
from pysrmkit.ports.repositories.qualification import SupplierQualificationRepository
from pysrmkit.ports.repositories.relationship import SupplierRelationshipRepository
from pysrmkit.ports.repositories.supplier import SupplierRepository
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
    AssessmentAnswerView,
    AssessmentQuestionView,
    AssessmentView,
    OnboardingRequirementView,
    OnboardingView,
    QualificationView,
    SupplierPageView,
    SupplierRelationshipView,
    SupplierView,
)


class GetSupplierHandler:
    def __init__(self, repository: SupplierRepository) -> None:
        self._repository = repository

    def handle(self, query: GetSupplier) -> SupplierView:
        supplier = self._repository.get(query.supplier_id)
        if supplier is None:
            raise SupplierNotFound(f"Supplier {query.supplier_id} does not exist")
        return _supplier_view(supplier)


class ListSuppliersHandler:
    def __init__(self, query_service: SupplierQueryService) -> None:
        self._query_service = query_service

    def handle(self, query: ListSuppliers) -> SupplierPageView:
        page = self._query_service.list_suppliers(offset=query.offset, limit=query.limit)
        return _supplier_page_view(page, offset=query.offset, limit=query.limit)


class SearchSuppliersHandler:
    """Translate a validated public query into a persistence-agnostic search.

    Application Handler + Dependency Inversion: matching and sorting belong to
    the SupplierSearchService adapter, never to this orchestration boundary.
    """

    def __init__(self, query_service: SupplierSearchService) -> None:
        self._query_service = query_service

    def handle(self, query: SearchSuppliersQuery) -> SupplierPageView:
        country = CountryCode(query.country_code) if query.country_code is not None else None
        page = self._query_service.search_suppliers(
            query=query.query,
            country_code=country,
            supplier_type=query.supplier_type,
            sort_by=query.sort_by,
            sort_order=query.sort_order,
            offset=query.offset,
            limit=query.limit,
        )
        return _supplier_page_view(page, offset=query.offset, limit=query.limit)


class GetSupplierRelationshipHandler:
    def __init__(self, repository: SupplierRelationshipRepository) -> None:
        self._repository = repository

    def handle(self, query: GetSupplierRelationship) -> SupplierRelationshipView:
        relationship = self._repository.get(query.relationship_id)
        if relationship is None:
            raise SupplierRelationshipNotFound(
                f"SupplierRelationship {query.relationship_id} does not exist"
            )
        return SupplierRelationshipView(
            relationship_id=relationship.id,
            supplier_id=relationship.supplier_id,
            organization_id=relationship.organization_id,
            stage=relationship.stage,
        )


class GetOnboardingForRelationshipHandler:
    def __init__(self, repository: SupplierOnboardingRepository) -> None:
        self._repository = repository

    def handle(self, query: GetOnboardingForRelationship) -> OnboardingView:
        onboarding = self._repository.find_for_relationship(query.relationship_id)
        if onboarding is None:
            raise SupplierOnboardingNotFound(
                f"SupplierRelationship {query.relationship_id} has no onboarding"
            )
        progress = onboarding.progress
        return OnboardingView(
            onboarding_id=onboarding.id,
            relationship_id=onboarding.relationship_id,
            started_at=onboarding.started_at,
            requirements=tuple(
                OnboardingRequirementView(
                    code=requirement.code,
                    mandatory=requirement.mandatory,
                    satisfied=requirement.satisfied,
                )
                for requirement in onboarding.requirements
            ),
            completed_at=onboarding.completed_at,
            completed=onboarding.is_complete,
            ready_for_completion=progress.ready_for_completion,
            missing_mandatory_requirements=progress.missing_mandatory_requirements,
        )


class GetAssessmentHandler:
    def __init__(self, repository: SupplierAssessmentRepository) -> None:
        self._repository = repository

    def handle(self, query: GetAssessment) -> AssessmentView:
        assessment = self._repository.get(query.assessment_id)
        if assessment is None:
            raise SupplierAssessmentNotFound(
                f"SupplierAssessment {query.assessment_id} does not exist"
            )
        return AssessmentView(
            assessment_id=assessment.id,
            relationship_id=assessment.relationship_id,
            assessment_type=assessment.assessment_type,
            created_at=assessment.created_at,
            questions=tuple(
                AssessmentQuestionView(
                    code=question.code,
                    mandatory=question.mandatory,
                    maximum_score=question.maximum_score,
                )
                for question in assessment.questions
            ),
            answers=tuple(
                AssessmentAnswerView(
                    question_code=answer.question_code,
                    score=answer.score,
                )
                for answer in assessment.answers
            ),
            completed_at=assessment.completed_at,
            completed=assessment.is_complete,
            score=assessment.score,
            decision=assessment.decision,
            required_answers_complete=assessment.required_answers_complete,
            missing_mandatory_question_codes=assessment.missing_mandatory_question_codes,
        )


class GetQualificationHandler:
    def __init__(self, repository: SupplierQualificationRepository) -> None:
        self._repository = repository

    def handle(self, query: GetQualification) -> QualificationView:
        qualification = self._repository.get(query.qualification_id)
        if qualification is None:
            raise SupplierQualificationNotFound(
                f"SupplierQualification {query.qualification_id} does not exist"
            )
        return _qualification_view(qualification)


class GetCurrentQualificationForScopeHandler:
    def __init__(self, repository: SupplierQualificationRepository) -> None:
        self._repository = repository

    def handle(self, query: GetCurrentQualificationForScope) -> QualificationView:
        qualification = self._repository.find_current_for_scope(
            query.relationship_id,
            query.scope,
        )
        if qualification is None:
            raise SupplierQualificationNotFound(
                "No current SupplierQualification exists for this Relationship and Scope"
            )
        return _qualification_view(qualification)


def _qualification_view(qualification: SupplierQualification) -> QualificationView:
    decision = qualification.decision
    return QualificationView(
        qualification_id=qualification.id,
        relationship_id=qualification.relationship_id,
        scope=qualification.scope,
        requested_at=qualification.requested_at,
        status=qualification.status,
        approved=decision.approved if decision is not None else None,
        reasons=decision.reasons if decision is not None else (),
        failed_requirements=decision.failed_requirements if decision is not None else (),
        decided_at=decision.decided_at if decision is not None else None,
    )


def _supplier_page_view(page: SupplierPage, *, offset: int, limit: int) -> SupplierPageView:
    """Project one persistence-neutral result into an immutable public page."""
    return SupplierPageView(
        items=tuple(_supplier_view(supplier) for supplier in page.suppliers),
        total=page.total,
        offset=offset,
        limit=limit,
    )


def _supplier_view(supplier: Supplier) -> SupplierView:
    identity = supplier.identity
    return SupplierView(
        supplier_id=supplier.id,
        legal_name=identity.legal_name,
        trading_name=identity.trading_name,
        supplier_type=identity.supplier_type,
        country=identity.country,
        external_identifiers=supplier.external_identifiers,
    )
