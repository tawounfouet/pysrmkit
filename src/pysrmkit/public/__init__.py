"""Stable public Python API surface for PySRMKit."""

from pysrmkit.application.assessment.commands import AssessmentQuestionInput
from pysrmkit.application.assessment.results import (
    CompleteSupplierAssessmentResult,
    CreateSupplierAssessmentResult,
)
from pysrmkit.application.onboarding.commands import OnboardingRequirementInput
from pysrmkit.application.qualification.results import (
    EvaluateSupplierQualificationResult,
    RequestSupplierQualificationResult,
)
from pysrmkit.application.relationship.errors import (
    RelationshipAlreadyExists,
    SupplierNotFound,
    SupplierRelationshipNotFound,
)
from pysrmkit.application.relationship.results import CreateSupplierRelationshipResult
from pysrmkit.application.supplier.commands import ExternalIdentifierInput
from pysrmkit.application.supplier.results import RegisterSupplierResult
from pysrmkit.domain.assessment.value_objects import AssessmentDecision, AssessmentId
from pysrmkit.domain.onboarding.value_objects import OnboardingId
from pysrmkit.domain.qualification.value_objects import (
    QualificationId,
    QualificationScope,
    QualificationStatus,
)
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierLifecycleStage,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import CategoryCode, CountryCode, SupplierId
from pysrmkit.public.capabilities import (
    AssessmentsAPI,
    OnboardingsAPI,
    QualificationsAPI,
    RelationshipsAPI,
    SuppliersAPI,
)
from pysrmkit.public.errors import (
    PersistenceConflict,
    PersistenceError,
    PersistenceUnavailable,
    PySRMKitError,
)
from pysrmkit.public.facade import PySRMKit
from pysrmkit.public.views import (
    AssessmentView,
    OnboardingView,
    QualificationView,
    SupplierRelationshipView,
    SupplierView,
)

__all__ = [
    "AssessmentDecision",
    "AssessmentId",
    "AssessmentQuestionInput",
    "AssessmentView",
    "AssessmentsAPI",
    "CategoryCode",
    "CompleteSupplierAssessmentResult",
    "CountryCode",
    "CreateSupplierAssessmentResult",
    "CreateSupplierRelationshipResult",
    "EvaluateSupplierQualificationResult",
    "ExternalIdentifierInput",
    "InternalOrganizationId",
    "OnboardingId",
    "OnboardingRequirementInput",
    "OnboardingView",
    "OnboardingsAPI",
    "PersistenceConflict",
    "PersistenceError",
    "PersistenceUnavailable",
    "PySRMKit",
    "PySRMKitError",
    "QualificationId",
    "QualificationScope",
    "QualificationStatus",
    "QualificationView",
    "QualificationsAPI",
    "RegisterSupplierResult",
    "RelationshipAlreadyExists",
    "RelationshipsAPI",
    "RequestSupplierQualificationResult",
    "SupplierId",
    "SupplierLifecycleStage",
    "SupplierNotFound",
    "SupplierRelationshipId",
    "SupplierRelationshipNotFound",
    "SupplierRelationshipView",
    "SupplierView",
    "SuppliersAPI",
]
