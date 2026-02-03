"""Initial migration

Revision ID: 001
Revises:
Create Date: 2026-02-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Organizations
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Stores
    op.create_table(
        'stores',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('code', sa.String(20), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('store_id', sa.String(36), sa.ForeignKey('stores.id'), nullable=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('failed_login_attempts', sa.Integer(), default=0),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Employees
    op.create_table(
        'employees',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('store_id', sa.String(36), sa.ForeignKey('stores.id'), nullable=False),
        sa.Column('employee_code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Attendance Records
    op.create_table(
        'attendance_records',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('employee_id', sa.String(36), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('clock_in', sa.Time(), nullable=True),
        sa.Column('clock_out', sa.Time(), nullable=True),
        sa.Column('break_minutes', sa.Integer(), nullable=True),
        sa.Column('work_type', sa.String(20), nullable=True),
        sa.Column('imported_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Issues
    op.create_table(
        'issues',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('attendance_record_id', sa.String(36), sa.ForeignKey('attendance_records.id'), nullable=False),
        sa.Column('type', sa.String(30), nullable=False),
        sa.Column('severity', sa.String(10), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('rule_description', sa.Text(), nullable=False),
        sa.Column('detected_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Issue Logs
    op.create_table(
        'issue_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('issue_id', sa.String(36), sa.ForeignKey('issues.id'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('memo', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Correction Reasons
    op.create_table(
        'correction_reasons',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('issue_id', sa.String(36), sa.ForeignKey('issues.id'), nullable=False),
        sa.Column('template_type', sa.String(20), nullable=False),
        sa.Column('cause_category', sa.String(30), nullable=False),
        sa.Column('cause_detail', sa.Text(), nullable=True),
        sa.Column('action_taken', sa.String(30), nullable=False),
        sa.Column('prevention', sa.String(30), nullable=False),
        sa.Column('generated_text', sa.Text(), nullable=False),
        sa.Column('created_by', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Detection Rules
    op.create_table(
        'detection_rules',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('break_minutes_6h', sa.Integer(), default=45),
        sa.Column('break_minutes_8h', sa.Integer(), default=60),
        sa.Column('daily_work_hours_alert', sa.Integer(), default=10),
        sa.Column('night_start_hour', sa.Integer(), default=22),
        sa.Column('night_end_hour', sa.Integer(), default=5),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Reason Templates
    op.create_table(
        'reason_templates',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('template_type', sa.String(20), nullable=False),
        sa.Column('template_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Vocabulary Dicts
    op.create_table(
        'vocabulary_dicts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('original_word', sa.String(100), nullable=False),
        sa.Column('replacement_word', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('vocabulary_dicts')
    op.drop_table('reason_templates')
    op.drop_table('detection_rules')
    op.drop_table('correction_reasons')
    op.drop_table('issue_logs')
    op.drop_table('issues')
    op.drop_table('attendance_records')
    op.drop_table('employees')
    op.drop_table('users')
    op.drop_table('stores')
    op.drop_table('organizations')
