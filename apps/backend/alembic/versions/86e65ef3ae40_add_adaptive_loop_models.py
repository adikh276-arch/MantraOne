"""add_adaptive_loop_models

Revision ID: 86e65ef3ae40
Revises: 59af751be01d
Create Date: 2026-06-27 13:03:40.857170

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "86e65ef3ae40"
down_revision: Union[str, None] = "59af751be01d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # knowledge_gaps
    op.create_table(
        "knowledge_gaps",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("family_id", sa.UUID(), nullable=False),
        sa.Column("member_id", sa.UUID(), nullable=False),
        sa.Column("domain", sa.String(length=100), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("clinical_priority", sa.String(length=50), nullable=False),
        sa.Column("suggested_action", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["family_id"],
            ["families.id"],
        ),
        sa.ForeignKeyConstraint(
            ["member_id"],
            ["family_members.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # next_actions
    op.create_table(
        "next_actions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("family_id", sa.UUID(), nullable=False),
        sa.Column("member_id", sa.UUID(), nullable=False),
        sa.Column("action_type", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.Float(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("execution_strategy", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "generated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["family_id"],
            ["families.id"],
        ),
        sa.ForeignKeyConstraint(
            ["member_id"],
            ["family_members.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # user_fatigue_metrics
    op.create_table(
        "user_fatigue_metrics",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("member_id", sa.UUID(), nullable=False),
        sa.Column("questions_asked", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("questions_answered", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("questions_ignored", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("average_response_latency_mins", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("last_interaction_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["member_id"],
            ["family_members.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("member_id"),
    )

    # clinical_outcomes
    op.create_table(
        "clinical_outcomes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("family_id", sa.UUID(), nullable=False),
        sa.Column("member_id", sa.UUID(), nullable=False),
        sa.Column("diagnosis", sa.String(length=255), nullable=True),
        sa.Column("treatment_plan", sa.Text(), nullable=False),
        sa.Column("resolved_status", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("doctor_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["family_id"],
            ["families.id"],
        ),
        sa.ForeignKeyConstraint(
            ["member_id"],
            ["family_members.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # intervention_observations
    op.create_table(
        "intervention_observations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("family_id", sa.UUID(), nullable=False),
        sa.Column("member_id", sa.UUID(), nullable=False),
        sa.Column("intervention_type", sa.String(length=100), nullable=False),
        sa.Column("target_metric", sa.String(length=100), nullable=False),
        sa.Column("baseline", sa.String(length=255), nullable=True),
        sa.Column("current_status", sa.Text(), nullable=False),
        sa.Column("efficacy_status", sa.String(length=50), nullable=False),
        sa.Column(
            "evaluated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["family_id"],
            ["families.id"],
        ),
        sa.ForeignKeyConstraint(
            ["member_id"],
            ["family_members.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("intervention_observations")
    op.drop_table("clinical_outcomes")
    op.drop_table("user_fatigue_metrics")
    op.drop_table("next_actions")
    op.drop_table("knowledge_gaps")
