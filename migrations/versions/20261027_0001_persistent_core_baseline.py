"""Create the Persistent Core relational baseline.

Revision ID: 20261027_0001
Revises:
Create Date: 2026-10-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261027_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the complete Persistent Core schema."""

    op.create_table(
        "suppliers",
        sa.Column("supplier_id", sa.Uuid(), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=False),
        sa.Column("trading_name", sa.String(length=255), nullable=True),
        sa.Column("supplier_type", sa.String(length=100), nullable=True),
        sa.Column("country_code", sa.String(length=2), nullable=True),
        sa.PrimaryKeyConstraint("supplier_id", name="pk_suppliers"),
    )

    op.create_table(
        "supplier_external_identifiers",
        sa.Column("identifier_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("supplier_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=100), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("source_system", sa.String(length=100), nullable=False),
        sa.Column("jurisdiction", sa.String(length=2), nullable=False),
        sa.ForeignKeyConstraint(
            ["supplier_id"],
            ["suppliers.supplier_id"],
            name="fk_supplier_external_identifiers_supplier_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("identifier_id", name="pk_supplier_external_identifiers"),
        sa.UniqueConstraint(
            "kind",
            "value",
            "source_system",
            "jurisdiction",
            name="uq_supplier_external_identifier_identity",
        ),
    )
    op.create_index(
        "ix_supplier_external_identifiers_supplier_id",
        "supplier_external_identifiers",
        ["supplier_id"],
        unique=False,
    )

    op.create_table(
        "supplier_relationships",
        sa.Column("relationship_id", sa.Uuid(), nullable=False),
        sa.Column("supplier_id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.String(length=255), nullable=False),
        sa.Column("stage", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ["supplier_id"],
            ["suppliers.supplier_id"],
            name="fk_supplier_relationships_supplier_id",
        ),
        sa.PrimaryKeyConstraint("relationship_id", name="pk_supplier_relationships"),
        sa.UniqueConstraint(
            "supplier_id",
            "organization_id",
            name="uq_supplier_relationship_supplier_organization",
        ),
    )
    op.create_index(
        "ix_supplier_relationships_supplier_id",
        "supplier_relationships",
        ["supplier_id"],
        unique=False,
    )

    op.create_table(
        "supplier_onboardings",
        sa.Column("onboarding_id", sa.Uuid(), nullable=False),
        sa.Column("relationship_id", sa.Uuid(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["relationship_id"],
            ["supplier_relationships.relationship_id"],
            name="fk_supplier_onboardings_relationship_id",
        ),
        sa.PrimaryKeyConstraint("onboarding_id", name="pk_supplier_onboardings"),
        sa.UniqueConstraint(
            "relationship_id",
            name="uq_supplier_onboarding_relationship",
        ),
    )
    op.create_index(
        "ix_supplier_onboardings_relationship_id",
        "supplier_onboardings",
        ["relationship_id"],
        unique=False,
    )

    op.create_table(
        "supplier_onboarding_requirements",
        sa.Column("requirement_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("onboarding_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("mandatory", sa.Boolean(), nullable=False),
        sa.Column("satisfied", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["onboarding_id"],
            ["supplier_onboardings.onboarding_id"],
            name="fk_supplier_onboarding_requirements_onboarding_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "requirement_id",
            name="pk_supplier_onboarding_requirements",
        ),
        sa.UniqueConstraint(
            "onboarding_id",
            "code",
            name="uq_supplier_onboarding_requirement_code",
        ),
    )
    op.create_index(
        "ix_supplier_onboarding_requirements_onboarding_id",
        "supplier_onboarding_requirements",
        ["onboarding_id"],
        unique=False,
    )

    op.create_table(
        "supplier_assessments",
        sa.Column("assessment_id", sa.Uuid(), nullable=False),
        sa.Column("relationship_id", sa.Uuid(), nullable=False),
        sa.Column("assessment_type", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("decision", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(
            ["relationship_id"],
            ["supplier_relationships.relationship_id"],
            name="fk_supplier_assessments_relationship_id",
        ),
        sa.PrimaryKeyConstraint("assessment_id", name="pk_supplier_assessments"),
    )
    op.create_index(
        "ix_supplier_assessments_created_at",
        "supplier_assessments",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_supplier_assessments_relationship_id",
        "supplier_assessments",
        ["relationship_id"],
        unique=False,
    )

    op.create_table(
        "supplier_assessment_questions",
        sa.Column("question_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("assessment_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("mandatory", sa.Boolean(), nullable=False),
        sa.Column("maximum_score", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["assessment_id"],
            ["supplier_assessments.assessment_id"],
            name="fk_supplier_assessment_questions_assessment_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("question_id", name="pk_supplier_assessment_questions"),
        sa.UniqueConstraint(
            "assessment_id",
            "code",
            name="uq_supplier_assessment_question_code",
        ),
    )
    op.create_index(
        "ix_supplier_assessment_questions_assessment_id",
        "supplier_assessment_questions",
        ["assessment_id"],
        unique=False,
    )

    op.create_table(
        "supplier_assessment_answers",
        sa.Column("answer_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("assessment_id", sa.Uuid(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["assessment_id"],
            ["supplier_assessments.assessment_id"],
            name="fk_supplier_assessment_answers_assessment_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["supplier_assessment_questions.question_id"],
            name="fk_supplier_assessment_answers_question_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("answer_id", name="pk_supplier_assessment_answers"),
        sa.UniqueConstraint(
            "assessment_id",
            "question_id",
            name="uq_supplier_assessment_answer_question",
        ),
    )
    op.create_index(
        "ix_supplier_assessment_answers_assessment_id",
        "supplier_assessment_answers",
        ["assessment_id"],
        unique=False,
    )

    op.create_table(
        "supplier_qualifications",
        sa.Column("qualification_id", sa.Uuid(), nullable=False),
        sa.Column("relationship_id", sa.Uuid(), nullable=False),
        sa.Column("scope_organization_id", sa.String(length=255), nullable=False),
        sa.Column("scope_category_code", sa.String(length=100), nullable=False),
        sa.Column("scope_country_code", sa.String(length=2), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("decision_approved", sa.Boolean(), nullable=True),
        sa.Column("decision_resulting_status", sa.String(length=50), nullable=True),
        sa.Column("decision_decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "scope_organization_id <> '' OR scope_category_code <> '' OR scope_country_code <> ''",
            name="ck_supplier_qualification_non_empty_scope",
        ),
        sa.CheckConstraint(
            "(decision_approved IS NULL "
            "AND decision_resulting_status IS NULL "
            "AND decision_decided_at IS NULL) OR "
            "(decision_approved IS NOT NULL "
            "AND decision_resulting_status IS NOT NULL "
            "AND decision_decided_at IS NOT NULL)",
            name="ck_supplier_qualification_decision_completeness",
        ),
        sa.ForeignKeyConstraint(
            ["relationship_id"],
            ["supplier_relationships.relationship_id"],
            name="fk_supplier_qualifications_relationship_id",
        ),
        sa.PrimaryKeyConstraint("qualification_id", name="pk_supplier_qualifications"),
    )
    op.create_index(
        "ix_supplier_qualifications_relationship_id",
        "supplier_qualifications",
        ["relationship_id"],
        unique=False,
    )
    op.create_index(
        "uq_current_supplier_qualification_scope",
        "supplier_qualifications",
        [
            "relationship_id",
            "scope_organization_id",
            "scope_category_code",
            "scope_country_code",
        ],
        unique=True,
        sqlite_where=sa.text("status NOT IN ('REVOKED', 'EXPIRED')"),
        postgresql_where=sa.text("status NOT IN ('REVOKED', 'EXPIRED')"),
    )

    op.create_table(
        "supplier_qualification_decision_reasons",
        sa.Column("reason_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("qualification_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("value", sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(
            ["qualification_id"],
            ["supplier_qualifications.qualification_id"],
            name=("fk_supplier_qualification_decision_reasons_qualification_id"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "reason_id",
            name="pk_supplier_qualification_decision_reasons",
        ),
    )
    op.create_index(
        "ix_supplier_qualification_decision_reasons_qualification_id",
        "supplier_qualification_decision_reasons",
        ["qualification_id"],
        unique=False,
    )

    op.create_table(
        "supplier_qualification_failed_requirements",
        sa.Column("failed_requirement_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("qualification_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["qualification_id"],
            ["supplier_qualifications.qualification_id"],
            name=("fk_supplier_qualification_failed_requirements_qualification_id"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "failed_requirement_id",
            name="pk_supplier_qualification_failed_requirements",
        ),
    )
    op.create_index(
        "ix_supplier_qualification_failed_requirements_qualification_id",
        "supplier_qualification_failed_requirements",
        ["qualification_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the Persistent Core schema."""

    op.drop_table("supplier_qualification_failed_requirements")
    op.drop_table("supplier_qualification_decision_reasons")
    op.drop_table("supplier_qualifications")
    op.drop_table("supplier_assessment_answers")
    op.drop_table("supplier_assessment_questions")
    op.drop_table("supplier_assessments")
    op.drop_table("supplier_onboarding_requirements")
    op.drop_table("supplier_onboardings")
    op.drop_table("supplier_relationships")
    op.drop_table("supplier_external_identifiers")
    op.drop_table("suppliers")
