"""SQLAlchemy persistence records for PySRMKit Aggregates."""

from pysrmkit.adapters.sqlalchemy.models.assessment import (
    AssessmentAnswerRecord,
    AssessmentQuestionRecord,
    SupplierAssessmentRecord,
)
from pysrmkit.adapters.sqlalchemy.models.onboarding import (
    OnboardingRequirementRecord,
    SupplierOnboardingRecord,
)
from pysrmkit.adapters.sqlalchemy.models.qualification import (
    QualificationDecisionReasonRecord,
    QualificationFailedRequirementRecord,
    SupplierQualificationRecord,
)
from pysrmkit.adapters.sqlalchemy.models.relationship import SupplierRelationshipRecord
from pysrmkit.adapters.sqlalchemy.models.supplier import (
    SupplierExternalIdentifierRecord,
    SupplierRecord,
)

__all__ = [
    "AssessmentAnswerRecord",
    "AssessmentQuestionRecord",
    "OnboardingRequirementRecord",
    "QualificationDecisionReasonRecord",
    "QualificationFailedRequirementRecord",
    "SupplierAssessmentRecord",
    "SupplierExternalIdentifierRecord",
    "SupplierOnboardingRecord",
    "SupplierQualificationRecord",
    "SupplierRecord",
    "SupplierRelationshipRecord",
]
