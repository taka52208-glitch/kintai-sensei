"""異常検知サービス"""

from datetime import date, datetime, time, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.attendance import AttendanceRecord
from src.models.issue import Issue, IssueType, IssueSeverity
from src.models.settings import DetectionRule
from src.config import settings as app_settings


async def get_detection_rules(db: AsyncSession, organization_id: UUID) -> dict:
    """検知ルールを取得"""
    result = await db.execute(
        select(DetectionRule).where(DetectionRule.organization_id == organization_id)
    )
    rule = result.scalar_one_or_none()

    if rule:
        return {
            "break_minutes_6h": rule.break_minutes_6h,
            "break_minutes_8h": rule.break_minutes_8h,
            "daily_work_hours_alert": rule.daily_work_hours_alert,
            "night_start_hour": rule.night_start_hour,
            "night_end_hour": rule.night_end_hour,
        }
    else:
        return {
            "break_minutes_6h": app_settings.default_break_minutes_6h,
            "break_minutes_8h": app_settings.default_break_minutes_8h,
            "daily_work_hours_alert": app_settings.default_daily_work_hours_alert,
            "night_start_hour": app_settings.default_night_start_hour,
            "night_end_hour": app_settings.default_night_end_hour,
        }


_REF_DATE = date(2000, 1, 1)


def calc_work_hours(clock_in: time | None, clock_out: time | None) -> float | None:
    """勤務時間を計算（時間単位）"""
    if clock_in is None or clock_out is None:
        return None

    dt_in = datetime.combine(_REF_DATE, clock_in)
    dt_out = datetime.combine(_REF_DATE, clock_out)

    # 日跨ぎ対応
    if dt_out < dt_in:
        dt_out += timedelta(days=1)

    diff = dt_out - dt_in
    return diff.total_seconds() / 3600


def _time_to_minutes(t: time) -> int:
    """time → 深夜0時起点の分数"""
    return t.hour * 60 + t.minute


def is_night_work(clock_in: time | None, clock_out: time | None, night_start: int, night_end: int) -> bool:
    """深夜勤務を含むか判定（深夜帯をまたぐシフトにも対応）"""
    if clock_in is None or clock_out is None:
        return False

    in_m = _time_to_minutes(clock_in)
    out_m = _time_to_minutes(clock_out)
    ns = night_start * 60   # 例: 22*60=1320
    ne = night_end * 60     # 例: 5*60=300

    # 日跨ぎシフトの場合、退勤を +24h で表現
    if out_m <= in_m:
        out_m += 24 * 60

    # 深夜帯も同様（22:00-5:00 → 1320-1740）
    if ne <= ns:
        ne += 24 * 60

    # シフト [in_m, out_m] と 深夜帯 [ns, ne] の重なり判定
    if in_m < ne and out_m > ns:
        return True

    # 深夜帯が翌日にもかかる場合: [ns-1440, ne-1440] もチェック
    if ns >= 24 * 60:
        if in_m < (ne - 24 * 60) and out_m > (ns - 24 * 60):
            return True

    return False


async def detect_issues(
    db: AsyncSession,
    attendance: AttendanceRecord,
    organization_id: UUID,
) -> list[Issue]:
    """異常を検知してIssueを作成"""
    rules = await get_detection_rules(db, organization_id)
    issues: list[Issue] = []

    clock_in = attendance.clock_in
    clock_out = attendance.clock_out
    break_minutes = attendance.break_minutes or 0
    work_hours = calc_work_hours(clock_in, clock_out)

    # R001: 出勤打刻漏れ
    if clock_in is None and clock_out is not None:
        issue = Issue(
            attendance_record_id=attendance.id,
            type=IssueType.MISSING_CLOCK_IN,
            severity=IssueSeverity.HIGH,
            rule_description="出勤打刻がありません（退勤打刻のみ）",
        )
        db.add(issue)
        issues.append(issue)

    # R002: 退勤打刻漏れ
    if clock_in is not None and clock_out is None:
        issue = Issue(
            attendance_record_id=attendance.id,
            type=IssueType.MISSING_CLOCK_OUT,
            severity=IssueSeverity.HIGH,
            rule_description="退勤打刻がありません（出勤打刻のみ）",
        )
        db.add(issue)
        issues.append(issue)

    # R003, R004: 休憩不足
    if work_hours is not None:
        if work_hours > 8 and break_minutes < rules["break_minutes_8h"]:
            issue = Issue(
                attendance_record_id=attendance.id,
                type=IssueType.INSUFFICIENT_BREAK,
                severity=IssueSeverity.HIGH,
                rule_description=f"8時間超勤務で休憩が{rules['break_minutes_8h']}分未満です（実績: {break_minutes}分）",
            )
            db.add(issue)
            issues.append(issue)
        elif work_hours > 6 and break_minutes < rules["break_minutes_6h"]:
            issue = Issue(
                attendance_record_id=attendance.id,
                type=IssueType.INSUFFICIENT_BREAK,
                severity=IssueSeverity.HIGH,
                rule_description=f"6時間超勤務で休憩が{rules['break_minutes_6h']}分未満です（実績: {break_minutes}分）",
            )
            db.add(issue)
            issues.append(issue)

    # R005: 長時間労働
    if work_hours is not None and work_hours > rules["daily_work_hours_alert"]:
        issue = Issue(
            attendance_record_id=attendance.id,
            type=IssueType.OVERTIME,
            severity=IssueSeverity.MEDIUM,
            rule_description=f"日次勤務時間が{rules['daily_work_hours_alert']}時間を超えています（実績: {work_hours:.1f}時間）",
        )
        db.add(issue)
        issues.append(issue)

    # R006: 深夜勤務
    if is_night_work(clock_in, clock_out, rules["night_start_hour"], rules["night_end_hour"]):
        issue = Issue(
            attendance_record_id=attendance.id,
            type=IssueType.NIGHT_WORK,
            severity=IssueSeverity.LOW,
            rule_description=f"深夜帯（{rules['night_start_hour']}時〜{rules['night_end_hour']}時）の勤務があります",
        )
        db.add(issue)
        issues.append(issue)

    # R007, R008: 不整合
    if clock_in is not None and clock_out is not None:
        dt_in = datetime.combine(_REF_DATE, clock_in)
        dt_out = datetime.combine(_REF_DATE, clock_out)
        if dt_out < dt_in and (dt_out.hour > 6):  # 日跨ぎでない場合
            issue = Issue(
                attendance_record_id=attendance.id,
                type=IssueType.INCONSISTENCY,
                severity=IssueSeverity.HIGH,
                rule_description="退勤時刻が出勤時刻より前です",
            )
            db.add(issue)
            issues.append(issue)

    if work_hours is not None and break_minutes > work_hours * 60:
        issue = Issue(
            attendance_record_id=attendance.id,
            type=IssueType.INCONSISTENCY,
            severity=IssueSeverity.HIGH,
            rule_description="休憩時間が勤務時間を超えています",
        )
        db.add(issue)
        issues.append(issue)

    return issues
