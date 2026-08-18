"""add users table for authentication

Revision ID: 0002_add_users_table
Revises: 0001_create_initial_tables
Create Date: 2026-08-17
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002_add_users_table'
down_revision = '0001_create_initial_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_admin', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index(
        'ix_users_created_at', 'users', ['created_at'], unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_users_created_at', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
