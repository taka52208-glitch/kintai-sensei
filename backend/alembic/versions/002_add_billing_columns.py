"""Add billing columns to organizations

Revision ID: 002
Revises: 001
Create Date: 2026-02-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('organizations', sa.Column('plan', sa.String(20), nullable=False, server_default='free'))
    op.add_column('organizations', sa.Column('stripe_customer_id', sa.String(255), nullable=True))
    op.add_column('organizations', sa.Column('stripe_subscription_id', sa.String(255), nullable=True))
    op.add_column('organizations', sa.Column('employee_limit', sa.Integer(), nullable=False, server_default='10'))


def downgrade() -> None:
    op.drop_column('organizations', 'employee_limit')
    op.drop_column('organizations', 'stripe_subscription_id')
    op.drop_column('organizations', 'stripe_customer_id')
    op.drop_column('organizations', 'plan')
