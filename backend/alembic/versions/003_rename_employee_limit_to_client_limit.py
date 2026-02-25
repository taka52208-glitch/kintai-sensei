"""Rename employee_limit to client_limit

Revision ID: 003
Revises: 002
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('organizations', 'employee_limit', new_column_name='client_limit')
    # デフォルト値を3に変更（社労士向け：顧問先3社）
    op.execute("UPDATE organizations SET client_limit = 3 WHERE client_limit = 10")


def downgrade() -> None:
    op.execute("UPDATE organizations SET client_limit = 10 WHERE client_limit = 3")
    op.alter_column('organizations', 'client_limit', new_column_name='employee_limit')
