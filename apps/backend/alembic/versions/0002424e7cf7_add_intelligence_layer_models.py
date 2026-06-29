"""add_intelligence_layer_models

Revision ID: 0002424e7cf7
Revises: 04d7c5bea0ad
Create Date: 2026-06-27 11:33:51.691341

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0002424e7cf7"
down_revision: Union[str, None] = "04d7c5bea0ad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. domain_confidences
    op.create_table(
        "domain_confidences",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("family_id", sa.UUID(), nullable=False),
        sa.Column("member_id", sa.UUID(), nullable=False),
        sa.Column("domain", sa.String(length=100), nullable=False),
        sa.Column("completeness", sa.Float(), nullable=False),
        sa.Column("freshness", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence_count", sa.Integer(), nullable=False),
        sa.Column(
            "last_updated", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False
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
        sa.UniqueConstraint("member_id", "domain", name="uq_domain_confidence_member_domain"),
    )
    op.create_index("idx_domain_confidences_member", "domain_confidences", ["member_id"], unique=False)

    # 2. health_insights
    op.create_table(
        "health_insights",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("family_id", sa.UUID(), nullable=False),
        sa.Column("member_id", sa.UUID(), nullable=False),
        sa.Column("insight_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("structured_data", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("source_entity_id", sa.UUID(), nullable=True),
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

    # 3. follow_ups
    op.create_table(
        "follow_ups",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("family_id", sa.UUID(), nullable=False),
        sa.Column("member_id", sa.UUID(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("source_entity_id", sa.UUID(), nullable=True),
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


def downgrade() -> None:
    op.drop_table("follow_ups")
    op.drop_table("health_insights")
    op.drop_index("idx_domain_confidences_member", table_name="domain_confidences")
    op.drop_table("domain_confidences")
