"""是正理由文生成サービス"""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.issue import Issue, CorrectionReason, ReasonTemplateType, CauseCategory, ActionType, PreventionType


# 原因カテゴリのラベル
CAUSE_LABELS = {
    "forgot_clock": "打刻忘れ",
    "device_issue": "端末不具合",
    "work_reason": "業務都合",
    "application_missing": "申請漏れ",
    "other": "その他",
}

# 対応のラベル
ACTION_LABELS = {
    "correction_request": "修正依頼",
    "employee_confirmation": "本人確認",
    "overtime_application": "残業申請",
    "warning": "注意喚起",
    "announcement": "周知",
}

# 再発防止のラベル
PREVENTION_LABELS = {
    "operation_notice": "運用周知の徹底",
    "device_placement": "打刻端末の配置見直し",
    "checklist": "確認チェックリストの導入",
    "double_check": "ダブルチェック体制の構築",
}

# 異常種別のラベル
ISSUE_TYPE_LABELS = {
    "missing_clock_in": "出勤打刻漏れ",
    "missing_clock_out": "退勤打刻漏れ",
    "insufficient_break": "休憩不足",
    "overtime": "長時間労働",
    "night_work": "深夜勤務",
    "inconsistency": "データ不整合",
}


def generate_internal_template(
    issue: Issue,
    cause_category: str,
    cause_detail: str | None,
    action_taken: str,
    prevention: str,
    handler_name: str,
) -> str:
    """社内記録用テンプレート（簡潔）"""
    employee = issue.attendance_record.employee
    date_str = str(issue.attendance_record.date)
    issue_type = ISSUE_TYPE_LABELS.get(issue.type.value, issue.type.value)

    text = f"""【勤怠異常対応記録】

対象: {employee.name}（{employee.employee_code}）
日付: {date_str}
異常: {issue_type}

原因: {CAUSE_LABELS.get(cause_category, cause_category)}
{f'詳細: {cause_detail}' if cause_detail else ''}

対応: {ACTION_LABELS.get(action_taken, action_taken)}
再発防止: {PREVENTION_LABELS.get(prevention, prevention)}

対応者: {handler_name}
対応日: {datetime.now().strftime('%Y-%m-%d')}
"""
    return text.strip()


def generate_employee_template(
    issue: Issue,
    cause_category: str,
    cause_detail: str | None,
    action_taken: str,
    prevention: str,
    handler_name: str,
) -> str:
    """本人確認用テンプレート（丁寧）"""
    employee = issue.attendance_record.employee
    date_str = str(issue.attendance_record.date)
    issue_type = ISSUE_TYPE_LABELS.get(issue.type.value, issue.type.value)

    text = f"""{employee.name} 様

お疲れ様です。勤怠管理担当の{handler_name}です。

{date_str}の勤怠データについて確認がございます。

【確認事項】
{issue_type}が検出されました。

【原因】
{CAUSE_LABELS.get(cause_category, cause_category)}によるものと確認いたしました。
{f'（{cause_detail}）' if cause_detail else ''}

【対応】
{ACTION_LABELS.get(action_taken, action_taken)}を実施いたします。

お手数ですが、上記内容に相違がないかご確認をお願いいたします。
ご不明な点がございましたら、お気軽にお問い合わせください。

以上、よろしくお願いいたします。

{handler_name}
{datetime.now().strftime('%Y年%m月%d日')}
"""
    return text.strip()


def generate_audit_template(
    issue: Issue,
    cause_category: str,
    cause_detail: str | None,
    action_taken: str,
    prevention: str,
    handler_name: str,
) -> str:
    """監査向けテンプレート（客観・事実ベース）"""
    employee = issue.attendance_record.employee
    date_str = str(issue.attendance_record.date)
    issue_type = ISSUE_TYPE_LABELS.get(issue.type.value, issue.type.value)

    text = f"""勤怠異常是正報告書

1. 事実
  対象日: {date_str}
  対象者: 従業員コード {employee.employee_code}
  検出内容: {issue_type}
  検出根拠: {issue.rule_description}

2. 原因
  分類: {CAUSE_LABELS.get(cause_category, cause_category)}
  {f'詳細: {cause_detail}' if cause_detail else ''}

3. 対応措置
  実施内容: {ACTION_LABELS.get(action_taken, action_taken)}
  対応日: {datetime.now().strftime('%Y-%m-%d')}
  対応者: {handler_name}

4. 再発防止策
  {PREVENTION_LABELS.get(prevention, prevention)}

※本報告書は勤怠管理システムにより自動生成されたものであり、
  最終的な判断および責任は管理者に帰属します。
"""
    return text.strip()


async def generate_reason_text(
    db: AsyncSession,
    issue: Issue,
    template_type: str,
    cause_category: str,
    cause_detail: str | None,
    action_taken: str,
    prevention: str,
    user: User,
) -> str:
    """是正理由文を生成"""

    handler_name = user.name

    if template_type == "internal":
        text = generate_internal_template(
            issue, cause_category, cause_detail, action_taken, prevention, handler_name
        )
    elif template_type == "employee":
        text = generate_employee_template(
            issue, cause_category, cause_detail, action_taken, prevention, handler_name
        )
    elif template_type == "audit":
        text = generate_audit_template(
            issue, cause_category, cause_detail, action_taken, prevention, handler_name
        )
    else:
        text = generate_internal_template(
            issue, cause_category, cause_detail, action_taken, prevention, handler_name
        )

    # 是正理由レコード保存
    correction_reason = CorrectionReason(
        issue_id=issue.id,
        template_type=ReasonTemplateType(template_type),
        cause_category=CauseCategory(cause_category),
        cause_detail=cause_detail,
        action_taken=ActionType(action_taken),
        prevention=PreventionType(prevention),
        generated_text=text,
        created_by=user.id,
    )
    db.add(correction_reason)

    return text
