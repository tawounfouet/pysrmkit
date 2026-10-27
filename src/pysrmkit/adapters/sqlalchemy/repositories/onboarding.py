"""SQLAlchemy implementation of SupplierOnboardingRepository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.mappers.onboarding import (
    apply_onboarding_state,
    new_onboarding_record,
    onboarding_from_record,
)
from pysrmkit.adapters.sqlalchemy.models.onboarding import SupplierOnboardingRecord
from pysrmkit.domain.onboarding.entities import SupplierOnboarding
from pysrmkit.domain.onboarding.value_objects import OnboardingId
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


class SqlAlchemySupplierOnboardingRepository:
    """Session-scoped SQLAlchemy SupplierOnboarding repository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, onboarding_id: OnboardingId) -> SupplierOnboarding | None:
        record = self._session.get(SupplierOnboardingRecord, onboarding_id.value)
        if record is None:
            return None
        return onboarding_from_record(record)

    def save(self, onboarding: SupplierOnboarding) -> None:
        record = self._session.get(SupplierOnboardingRecord, onboarding.id.value)
        if record is None:
            self._session.add(new_onboarding_record(onboarding))
            return
        apply_onboarding_state(record, onboarding)

    def find_for_relationship(
        self,
        relationship_id: SupplierRelationshipId,
    ) -> SupplierOnboarding | None:
        statement = select(SupplierOnboardingRecord).where(
            SupplierOnboardingRecord.relationship_id == relationship_id.value
        )
        record = self._session.scalar(statement)
        if record is None:
            return None
        return onboarding_from_record(record)
