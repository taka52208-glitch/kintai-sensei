"""レポートAPI"""

import io
import csv
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

from src.core.database import get_db
from src.core.auth import StoreManagerUser
from src.models.user import UserRole
from src.models.issue import Issue
from src.models.attendance import AttendanceRecord
from src.models.employee import Employee


router = APIRouter()

# 日本語フォント登録
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
JP_FONT = "HeiseiKakuGo-W5"

# 異常種別のラベル
ISSUE_TYPE_LABELS = {
    "missing_clock_in": "出勤打刻漏れ",
    "missing_clock_out": "退勤打刻漏れ",
    "insufficient_break": "休憩不足",
    "overtime": "長時間労働",
    "night_work": "深夜勤務",
    "inconsistency": "不整合",
}

# ステータスのラベル
STATUS_LABELS = {
    "pending": "未対応",
    "in_progress": "対応中",
    "completed": "完了",
}

# 重要度のラベル
SEVERITY_LABELS = {
    "high": "高",
    "medium": "中",
    "low": "低",
}


class ReportRequest(BaseModel):
    """レポート生成リクエスト"""
    store_id: str | None = None
    month: str  # YYYY-MM
    format: str = "pdf"  # pdf or csv
    mask_personal_info: bool = False


def mask_name(name: str) -> str:
    """名前をマスクする"""
    if len(name) <= 1:
        return "*"
    return name[0] + "*" * (len(name) - 1)


def _get_str(val: object) -> str:
    """Enum or str を str に変換"""
    return val if isinstance(val, str) else val.value


@router.post("")
async def generate_report(
    request: ReportRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: StoreManagerUser,
):
    """レポート生成"""
    # 対象月の範囲を計算
    year, month = map(int, request.month.split("-"))
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month + 1, 1).date()

    # ベースクエリ
    base_query = (
        select(Issue)
        .join(AttendanceRecord)
        .join(Employee)
        .where(Employee.organization_id == current_user.organization_id)
        .where(AttendanceRecord.date >= start_date)
        .where(AttendanceRecord.date < end_date)
    )

    # 店舗管理者は自店舗のみ
    if current_user.role == UserRole.STORE_MANAGER and current_user.store_id:
        base_query = base_query.where(Employee.store_id == current_user.store_id)
    elif request.store_id:
        base_query = base_query.where(Employee.store_id == request.store_id)

    # データ取得
    query = (
        base_query
        .options(
            joinedload(Issue.attendance_record)
            .joinedload(AttendanceRecord.employee)
            .joinedload(Employee.store),
        )
        .order_by(AttendanceRecord.date, Employee.employee_code)
    )
    result = await db.execute(query)
    issues = result.scalars().unique().all()

    if request.format == "csv":
        return _generate_csv(request, issues)
    else:
        return _generate_pdf(request, issues)


def _generate_csv(request: ReportRequest, issues: list) -> StreamingResponse:
    """CSV生成"""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([f"勤怠異常レポート - {request.month}"])
    writer.writerow([f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
    writer.writerow([])

    # サマリー
    writer.writerow(["【サマリー】"])
    writer.writerow(["異常種別", "件数"])
    type_counts: dict[str, int] = {}
    for issue in issues:
        t = _get_str(issue.type)
        type_counts[t] = type_counts.get(t, 0) + 1
    for t, count in sorted(type_counts.items()):
        writer.writerow([ISSUE_TYPE_LABELS.get(t, t), count])
    writer.writerow(["合計", len(issues)])
    writer.writerow([])

    # ステータス別
    writer.writerow(["ステータス", "件数"])
    status_counts: dict[str, int] = {}
    for issue in issues:
        s = _get_str(issue.status)
        status_counts[s] = status_counts.get(s, 0) + 1
    for s, count in sorted(status_counts.items()):
        writer.writerow([STATUS_LABELS.get(s, s), count])
    writer.writerow([])

    # 詳細一覧
    writer.writerow(["【詳細一覧】"])
    writer.writerow(["日付", "店舗", "従業員コード", "従業員名", "異常種別", "重要度", "詳細", "ステータス"])
    for issue in issues:
        attendance = issue.attendance_record
        employee = attendance.employee
        store = employee.store
        emp_name = mask_name(employee.name) if request.mask_personal_info else employee.name

        writer.writerow([
            str(attendance.date),
            store.name if store else "",
            employee.employee_code,
            emp_name,
            ISSUE_TYPE_LABELS.get(_get_str(issue.type), _get_str(issue.type)),
            SEVERITY_LABELS.get(_get_str(issue.severity), _get_str(issue.severity)),
            issue.rule_description,
            STATUS_LABELS.get(_get_str(issue.status), _get_str(issue.status)),
        ])

    content = output.getvalue()
    return StreamingResponse(
        iter([content.encode("utf-8-sig")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=report-{request.month}.csv"},
    )


def _generate_pdf(request: ReportRequest, issues: list) -> StreamingResponse:
    """PDF生成（reportlab）"""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=20 * mm,
        bottomMargin=15 * mm,
    )

    # スタイル定義
    style_title = ParagraphStyle(
        "Title", fontName=JP_FONT, fontSize=16, leading=22, spaceAfter=6,
    )
    style_subtitle = ParagraphStyle(
        "Subtitle", fontName=JP_FONT, fontSize=10, leading=14, textColor=colors.grey,
    )
    style_heading = ParagraphStyle(
        "Heading", fontName=JP_FONT, fontSize=12, leading=16, spaceBefore=12, spaceAfter=6,
    )
    style_body = ParagraphStyle(
        "Body", fontName=JP_FONT, fontSize=9, leading=12,
    )
    style_disclaimer = ParagraphStyle(
        "Disclaimer", fontName=JP_FONT, fontSize=7, leading=10, textColor=colors.grey,
    )

    elements: list = []

    # タイトル
    mask_label = "（個人情報マスク済）" if request.mask_personal_info else ""
    elements.append(Paragraph(f"勤怠異常レポート - {request.month}{mask_label}", style_title))
    elements.append(Paragraph(
        f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M')}　|　勤怠先生",
        style_subtitle,
    ))
    elements.append(Spacer(1, 10 * mm))

    # 集計
    type_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    for issue in issues:
        t = _get_str(issue.type)
        s = _get_str(issue.status)
        type_counts[t] = type_counts.get(t, 0) + 1
        status_counts[s] = status_counts.get(s, 0) + 1

    # サマリーテーブル（種別×ステータス 並べて表示）
    elements.append(Paragraph("サマリー", style_heading))

    summary_data = [["異常種別", "件数", "", "ステータス", "件数"]]
    type_items = sorted(type_counts.items())
    status_items = sorted(status_counts.items())
    max_rows = max(len(type_items), len(status_items))
    for i in range(max_rows):
        row = []
        if i < len(type_items):
            row += [ISSUE_TYPE_LABELS.get(type_items[i][0], type_items[i][0]), str(type_items[i][1])]
        else:
            row += ["", ""]
        row.append("")
        if i < len(status_items):
            row += [STATUS_LABELS.get(status_items[i][0], status_items[i][0]), str(status_items[i][1])]
        else:
            row += ["", ""]
        summary_data.append(row)
    summary_data.append(["合計", str(len(issues)), "", "", ""])

    summary_table = Table(summary_data, colWidths=[55 * mm, 20 * mm, 10 * mm, 40 * mm, 20 * mm])
    summary_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), JP_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#1976d2")),
        ("BACKGROUND", (3, 0), (4, 0), colors.HexColor("#1976d2")),
        ("TEXTCOLOR", (0, 0), (1, 0), colors.white),
        ("TEXTCOLOR", (3, 0), (4, 0), colors.white),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("ALIGN", (4, 0), (4, -1), "RIGHT"),
        ("GRID", (0, 0), (1, -1), 0.5, colors.lightgrey),
        ("GRID", (3, 0), (4, -1), 0.5, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("ROWBACKGROUNDS", (3, 1), (4, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 8 * mm))

    # 詳細一覧
    elements.append(Paragraph("異常一覧", style_heading))

    if not issues:
        elements.append(Paragraph("該当する異常データはありません。", style_body))
    else:
        detail_data = [["日付", "店舗", "従業員", "異常種別", "重要度", "ステータス"]]
        for issue in issues:
            attendance = issue.attendance_record
            employee = attendance.employee
            store = employee.store
            emp_name = mask_name(employee.name) if request.mask_personal_info else employee.name

            detail_data.append([
                str(attendance.date),
                store.name if store else "",
                emp_name,
                ISSUE_TYPE_LABELS.get(_get_str(issue.type), _get_str(issue.type)),
                SEVERITY_LABELS.get(_get_str(issue.severity), _get_str(issue.severity)),
                STATUS_LABELS.get(_get_str(issue.status), _get_str(issue.status)),
            ])

        detail_table = Table(
            detail_data,
            colWidths=[25 * mm, 28 * mm, 30 * mm, 35 * mm, 18 * mm, 22 * mm],
            repeatRows=1,
        )
        detail_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), JP_FONT),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976d2")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (4, 0), (4, -1), "CENTER"),
            ("ALIGN", (5, 0), (5, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
        ]))
        elements.append(detail_table)

    # 免責注記
    elements.append(Spacer(1, 10 * mm))
    elements.append(Paragraph(
        "※ 本レポートは勤怠データに基づく異常の疑いを機械的に検知した結果であり、"
        "法令違反の確定判断を行うものではありません。最終判断は社会保険労務士等の専門家にご確認ください。",
        style_disclaimer,
    ))

    doc.build(elements)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report-{request.month}.pdf"},
    )
