"""add_preventive_and_explainability

Revision ID: 59af751be01d
Revises: 0002424e7cf7
Create Date: 2026-06-27 12:14:56.964024

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "59af751be01d"
down_revision: Union[str, None] = "0002424e7cf7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. preventive_observations
    op.create_table(
        "preventive_observations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("family_id", sa.UUID(), nullable=False),
        sa.Column("member_id", sa.UUID(), nullable=False),
        sa.Column("observation_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("structured_data", sa.JSON(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False
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

    # 2. explainability_traces
    op.create_table(
        "explainability_traces",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("family_id", sa.UUID(), nullable=False),
        sa.Column("member_id", sa.UUID(), nullable=False),
        sa.Column("target_entity_type", sa.String(length=50), nullable=False),
        sa.Column("target_entity_id", sa.UUID(), nullable=False),
        sa.Column("reasoning_source", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("memories_used", sa.JSON(), nullable=True),
        sa.Column("timeline_events_referenced", sa.JSON(), nullable=True),
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


def downgrade() -> None:
    op.drop_table("explainability_traces")
    op.drop_table("preventive_observations")
