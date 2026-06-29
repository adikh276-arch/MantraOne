"""Add roles and data grants

Revision ID: 04d7c5bea0ad
Revises: 8b181bae74a5
Create Date: 2026-06-27 11:22:28.387247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04d7c5bea0ad'
down_revision: Union[str, None] = '8b181bae74a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add role to family_members
    op.add_column('family_members', sa.Column('role', sa.String(length=50), server_default="standard", nullable=False))
    
    # Update Document table
    op.add_column('documents', sa.Column('document_date_confidence', sa.Float(), nullable=True))
    op.add_column('documents', sa.Column('duplicate_of_id', sa.UUID(), nullable=True))
    # For SQLite compatibility, we can't easily alter defaults of existing columns or create ForeignKeys, but we can add new ones.

    # Modify AuditLog to match the new structure
    # Since SQLite doesn't support easy DROP COLUMN, and it's dev DB, we will just create the data_grants table and leave audit_log columns as they were or recreate it.
    # Actually, we can drop the old audit_logs table and recreate it because it's a dev database and might be empty/non-critical, or we can use batch operations.
    with op.batch_alter_table('audit_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('actor_id', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('target_id', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('resource', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True))
        batch_op.create_index('idx_audit_actor_new', ['actor_id', 'timestamp'])

    # Create DataGrant table
    op.create_table('data_grants',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('family_id', sa.UUID(), nullable=False),
        sa.Column('grantor_id', sa.UUID(), nullable=False),
        sa.Column('grantee_id', sa.UUID(), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=255), nullable=True),
        sa.Column('scope', sa.String(length=100), nullable=False),
        sa.Column('permissions', sa.String(length=100), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['family_id'], ['families.id'], ),
        sa.ForeignKeyConstraint(['grantee_id'], ['family_members.id'], ),
        sa.ForeignKeyConstraint(['grantor_id'], ['family_members.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_grants_grantee', 'data_grants', ['grantee_id'], unique=False)
    op.create_index('idx_grants_grantor', 'data_grants', ['grantor_id'], unique=False)

def downgrade() -> None:
    pass
