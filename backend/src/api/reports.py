"""レポートAPI"""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.core.auth import StoreManagerUser


router = APIRouter()


class ReportRequest(BaseModel):
    """レポート生成リクエスト"""
    store_id: str | None = None
    month: str  # YYYY-MM
    format: str = "pdf"  # pdf or csv
    mask_personal_info: bool = False


@router.post("")
async def generate_report(
    request: ReportRequest,
    current_user: StoreManagerUser,
):
    """レポート生成"""
    # TODO: 実際のレポート生成実装
    # 今は仮のCSVを返す

    if request.format == "csv":
        content = "日付,従業員,異常種別,ステータス\n2024-01-01,山田太郎,打刻漏れ,完了\n"
        return StreamingResponse(
            iter([content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=report-{request.month}.csv"},
        )
    else:
        # PDF生成は後で実装
        content = b"%PDF-1.4 dummy"
        return StreamingResponse(
            iter([content]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report-{request.month}.pdf"},
        )
