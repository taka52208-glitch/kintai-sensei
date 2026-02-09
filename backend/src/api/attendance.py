"""勤怠データAPI"""

import io
from typing import Annotated

import pandas as pd
import chardet
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.auth import StoreManagerUser
from src.models.employee import Employee
from src.models.store import Store
from src.models.attendance import AttendanceRecord
from src.services.detection import detect_issues
from src.services.plan_limits import check_employee_limit


router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_ROW_COUNT = 10000


def detect_encoding(content: bytes) -> str:
    """ファイルのエンコーディングを検出"""
    result = chardet.detect(content)
    return result["encoding"] or "utf-8"


def parse_csv(content: bytes) -> pd.DataFrame:
    """CSVをパース"""
    encoding = detect_encoding(content)
    try:
        df = pd.read_csv(io.BytesIO(content), encoding=encoding)
    except Exception:
        # Shift-JISでリトライ
        df = pd.read_csv(io.BytesIO(content), encoding="shift-jis")
    return df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """カラム名を正規化（ジョブカン/Airシフト対応）"""
    column_mapping = {
        # ジョブカン
        "スタッフコード": "employee_code",
        "スタッフ名": "name",
        "日付": "date",
        "出勤時刻": "clock_in",
        "退勤時刻": "clock_out",
        "休憩時間": "break_minutes",
        "勤務区分": "work_type",
        # Airシフト
        "従業員番号": "employee_code",
        "従業員名": "name",
        "出勤": "clock_in",
        "退勤": "clock_out",
        "休憩": "break_minutes",
        # 汎用
        "employee_id": "employee_code",
        "employee_name": "name",
    }

    df = df.rename(columns=column_mapping)
    return df


@router.post("/preview")
async def preview_upload(
    file: Annotated[UploadFile, File()],
    current_user: StoreManagerUser,
):
    """CSVプレビュー"""
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ファイルサイズが上限（{MAX_FILE_SIZE // 1024 // 1024}MB）を超えています",
        )

    try:
        df = parse_csv(content)
        df = normalize_columns(df)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSVの解析に失敗しました: {str(e)}",
        )

    if len(df) > MAX_ROW_COUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"行数が上限（{MAX_ROW_COUNT}行）を超えています（{len(df)}行）",
        )

    # 必須カラムチェック
    required = ["employee_code", "date"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"必須カラムがありません: {', '.join(missing)}",
        )

    return {
        "columns": list(df.columns),
        "row_count": len(df),
        "preview": df.head(10).to_dict(orient="records"),
    }


@router.post("/upload")
async def upload_attendance(
    file: Annotated[UploadFile, File()],
    store_id: Annotated[str, Form()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: StoreManagerUser,
):
    """CSV取り込み＆異常検知"""
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ファイルサイズが上限（{MAX_FILE_SIZE // 1024 // 1024}MB）を超えています",
        )

    try:
        df = parse_csv(content)
        df = normalize_columns(df)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSVの解析に失敗しました: {str(e)}",
        )

    if len(df) > MAX_ROW_COUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"行数が上限（{MAX_ROW_COUNT}行）を超えています（{len(df)}行）",
        )

    # store_id所有権検証
    if store_id:
        result = await db.execute(
            select(Store).where(
                Store.id == store_id,
                Store.organization_id == current_user.organization_id,
            )
        )
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="指定された店舗へのアクセス権限がありません",
            )

    record_count = 0
    skip_count = 0
    issue_count = 0

    for _, row in df.iterrows():
        # 従業員取得または作成
        employee_code = str(row.get("employee_code", ""))
        if not employee_code:
            continue

        result = await db.execute(
            select(Employee).where(
                Employee.organization_id == current_user.organization_id,
                Employee.employee_code == employee_code,
            )
        )
        employee = result.scalar_one_or_none()

        if employee is None:
            # プラン制限チェック
            allowed, message = await check_employee_limit(db, current_user.organization_id)
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=message,
                )
            employee = Employee(
                organization_id=current_user.organization_id,
                store_id=store_id if store_id else current_user.store_id,
                employee_code=employee_code,
                name=str(row.get("name", employee_code)),
            )
            db.add(employee)
            await db.flush()

        # 重複チェック（同一従業員+同一日付）
        record_date = pd.to_datetime(row.get("date")).date()
        existing = await db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.employee_id == employee.id,
                AttendanceRecord.date == record_date,
            )
        )
        if existing.scalar_one_or_none() is not None:
            skip_count += 1
            continue

        # 勤怠レコード作成
        attendance = AttendanceRecord(
            employee_id=employee.id,
            date=record_date,
            clock_in=pd.to_datetime(row.get("clock_in")).time() if pd.notna(row.get("clock_in")) else None,
            clock_out=pd.to_datetime(row.get("clock_out")).time() if pd.notna(row.get("clock_out")) else None,
            break_minutes=int(row.get("break_minutes")) if pd.notna(row.get("break_minutes")) else None,
            work_type=str(row.get("work_type")) if pd.notna(row.get("work_type")) else None,
        )
        db.add(attendance)
        await db.flush()
        record_count += 1

        # 異常検知
        issues = await detect_issues(db, attendance, current_user.organization_id)
        issue_count += len(issues)

    await db.commit()

    message = f"取り込みが完了しました（{record_count}件追加"
    if skip_count > 0:
        message += f"、{skip_count}件は既存データのためスキップ"
    message += "）"

    return {
        "message": message,
        "record_count": record_count,
        "skip_count": skip_count,
        "issue_count": issue_count,
    }
