"""異常API"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.database import get_db
from src.core.auth import CurrentUser, StoreManagerUser
from src.models.user import UserRole
from src.models.issue import Issue, IssueLog, IssueStatus
from src.models.attendance import AttendanceRecord
from src.models.employee import Employee
from src.schemas.issue import (
    IssueResponse,
    IssueListResponse,
    IssueUpdateRequest,
    IssueLogResponse,
    IssueLogCreate,
    GenerateReasonRequest,
    GenerateReasonResponse,
    AttendanceRecordResponse,
)
from src.services.reason_generator import generate_reason_text


router = APIRouter()


def build_issue_response(issue: Issue) -> IssueResponse:
    """Issue -> IssueResponse 変換"""
    attendance = issue.attendance_record
    employee = attendance.employee

    attendance_response = None
    if attendance:
        attendance_response = AttendanceRecordResponse(
            id=str(attendance.id),
            date=str(attendance.date),
            clock_in=str(attendance.clock_in) if attendance.clock_in else None,
            clock_out=str(attendance.clock_out) if attendance.clock_out else None,
            break_minutes=attendance.break_minutes,
            work_type=attendance.work_type,
        )

    logs = [
        IssueLogResponse(
            id=str(log.id),
            user_id=str(log.user_id),
            user_name=log.user.name if log.user else "Unknown",
            action=log.action,
            memo=log.memo,
            created_at=log.created_at,
        )
        for log in (issue.logs or [])
    ]

    return IssueResponse(
        id=str(issue.id),
        attendance_record_id=str(issue.attendance_record_id),
        employee_id=str(employee.id),
        employee_name=employee.name,
        store_id=str(employee.store_id),
        store_name=employee.store.name if employee.store else "",
        date=str(attendance.date),
        type=issue.type if isinstance(issue.type, str) else issue.type.value,
        severity=issue.severity if isinstance(issue.severity, str) else issue.severity.value,
        status=issue.status if isinstance(issue.status, str) else issue.status.value,
        rule_description=issue.rule_description,
        detected_at=issue.detected_at,
        attendance_record=attendance_response,
        logs=logs,
    )


@router.get("", response_model=IssueListResponse)
async def list_issues(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    page: int = 1,
    page_size: int = Query(default=20, le=100),
    store_id: str | None = None,
    employee_id: str | None = None,
    type: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
):
    """異常一覧取得"""
    offset = (page - 1) * page_size

    # ベースクエリ
    base_query = (
        select(Issue)
        .join(AttendanceRecord)
        .join(Employee)
        .where(Employee.organization_id == current_user.organization_id)
    )

    # 店舗管理者は自店舗のみ
    if current_user.role == UserRole.STORE_MANAGER and current_user.store_id:
        base_query = base_query.where(Employee.store_id == current_user.store_id)

    # フィルタ
    if store_id:
        base_query = base_query.where(Employee.store_id == UUID(store_id))
    if employee_id:
        base_query = base_query.where(Employee.id == UUID(employee_id))
    if type:
        base_query = base_query.where(Issue.type == type)
    if severity:
        base_query = base_query.where(Issue.severity == severity)
    if status:
        base_query = base_query.where(Issue.status == status)

    # 総件数
    count_query = select(func.count()).select_from(base_query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # データ取得
    query = (
        base_query
        .options(
            joinedload(Issue.attendance_record).joinedload(AttendanceRecord.employee).joinedload(Employee.store),
            joinedload(Issue.logs).joinedload(IssueLog.user),
        )
        .order_by(Issue.detected_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    issues = result.scalars().unique().all()

    items = [build_issue_response(issue) for issue in issues]

    return IssueListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(
    issue_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """異常詳細取得"""
    query = (
        select(Issue)
        .options(
            joinedload(Issue.attendance_record).joinedload(AttendanceRecord.employee).joinedload(Employee.store),
            joinedload(Issue.logs).joinedload(IssueLog.user),
        )
        .where(Issue.id == issue_id)
    )
    result = await db.execute(query)
    issue = result.scalar_one_or_none()

    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="異常が見つかりません")

    # 権限チェック
    employee = issue.attendance_record.employee
    if employee.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="アクセス権限がありません")

    if current_user.role == UserRole.STORE_MANAGER and current_user.store_id:
        if employee.store_id != current_user.store_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="アクセス権限がありません")

    return build_issue_response(issue)


@router.put("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: str,
    request: IssueUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: StoreManagerUser,
):
    """異常更新（ステータス変更）"""
    query = (
        select(Issue)
        .options(
            joinedload(Issue.attendance_record).joinedload(AttendanceRecord.employee).joinedload(Employee.store),
            joinedload(Issue.logs).joinedload(IssueLog.user),
        )
        .where(Issue.id == issue_id)
    )
    result = await db.execute(query)
    issue = result.scalar_one_or_none()

    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="異常が見つかりません")

    # ステータス更新
    old_status = issue.status
    issue.status = IssueStatus(request.status)

    # 対応ログ追加
    log = IssueLog(
        issue_id=issue.id,
        user_id=current_user.id,
        action=f"status_change:{old_status.value}->{request.status}",
        memo=None,
    )
    db.add(log)

    await db.commit()
    await db.refresh(issue)

    return build_issue_response(issue)


@router.post("/{issue_id}/logs", response_model=IssueLogResponse)
async def add_issue_log(
    issue_id: str,
    request: IssueLogCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: StoreManagerUser,
):
    """対応ログ追加"""
    result = await db.execute(select(Issue).where(Issue.id == issue_id))
    issue = result.scalar_one_or_none()

    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="異常が見つかりません")

    log = IssueLog(
        issue_id=issue.id,
        user_id=current_user.id,
        action=request.action,
        memo=request.memo,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)

    return IssueLogResponse(
        id=str(log.id),
        user_id=str(log.user_id),
        user_name=current_user.name,
        action=log.action,
        memo=log.memo,
        created_at=log.created_at,
    )


@router.post("/{issue_id}/reason", response_model=GenerateReasonResponse)
async def generate_reason(
    issue_id: str,
    request: GenerateReasonRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: StoreManagerUser,
):
    """是正理由文生成"""
    query = (
        select(Issue)
        .options(
            joinedload(Issue.attendance_record).joinedload(AttendanceRecord.employee),
        )
        .where(Issue.id == issue_id)
    )
    result = await db.execute(query)
    issue = result.scalar_one_or_none()

    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="異常が見つかりません")

    # 理由文生成
    generated_text = await generate_reason_text(
        db=db,
        issue=issue,
        template_type=request.template_type,
        cause_category=request.cause_category,
        cause_detail=request.cause_detail,
        action_taken=request.action_taken,
        prevention=request.prevention,
        user=current_user,
    )

    return GenerateReasonResponse(
        generated_text=generated_text,
        correction_reason_id=str(issue_id),  # 簡略化
    )
