"""デモ用サンプルデータ生成スクリプト

init_data.py 実行後に使用。
リアルな飲食店勤怠データ（異常含む）を生成します。

Usage:
    cd backend && source venv/bin/activate
    PYTHONPATH=. python scripts/seed_demo_data.py
"""

import asyncio
import uuid
from datetime import datetime, date, time, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.config import settings
from src.models.store import Organization, Store
from src.models.employee import Employee
from src.models.attendance import AttendanceRecord
from src.models.issue import Issue, IssueType, IssueSeverity, IssueStatus

# デモ従業員（飲食店らしい名前）
DEMO_EMPLOYEES = [
    {"code": "EMP001", "name": "田中 太郎"},
    {"code": "EMP002", "name": "鈴木 花子"},
    {"code": "EMP003", "name": "佐藤 健一"},
    {"code": "EMP004", "name": "山田 美咲"},
    {"code": "EMP005", "name": "高橋 翔太"},
    {"code": "EMP006", "name": "渡辺 あかり"},
    {"code": "EMP007", "name": "伊藤 大輔"},
    {"code": "EMP008", "name": "中村 さくら"},
]

# 2026年1月の勤怠パターン
NORMAL_SHIFTS = [
    # ランチ帯
    {"clock_in": time(9, 0), "clock_out": time(15, 0), "break": 45},
    {"clock_in": time(10, 0), "clock_out": time(16, 0), "break": 45},
    # 通し
    {"clock_in": time(10, 0), "clock_out": time(21, 0), "break": 60},
    {"clock_in": time(9, 0), "clock_out": time(18, 0), "break": 60},
    # ディナー帯
    {"clock_in": time(16, 0), "clock_out": time(23, 0), "break": 45},
    {"clock_in": time(17, 0), "clock_out": time(23, 30), "break": 45},
]

# 異常パターン（デモ用）
ANOMALIES = [
    # 打刻漏れ（出勤）
    {
        "employee_idx": 0, "date": date(2026, 1, 8),
        "clock_in": None, "clock_out": time(21, 0), "break": 60,
        "issue_type": IssueType.MISSING_CLOCK_IN.value,
        "severity": IssueSeverity.HIGH.value,
        "rule": "出勤打刻がありません（退勤: 21:00）",
    },
    # 打刻漏れ（退勤）
    {
        "employee_idx": 2, "date": date(2026, 1, 10),
        "clock_in": time(10, 0), "clock_out": None, "break": 0,
        "issue_type": IssueType.MISSING_CLOCK_OUT.value,
        "severity": IssueSeverity.HIGH.value,
        "rule": "退勤打刻がありません（出勤: 10:00）",
    },
    # 休憩不足（6時間超）
    {
        "employee_idx": 1, "date": date(2026, 1, 12),
        "clock_in": time(10, 0), "clock_out": time(17, 30), "break": 30,
        "issue_type": IssueType.INSUFFICIENT_BREAK.value,
        "severity": IssueSeverity.MEDIUM.value,
        "rule": "7.5時間勤務に対し休憩30分（法定45分以上必要）",
    },
    # 休憩不足（8時間超）
    {
        "employee_idx": 3, "date": date(2026, 1, 14),
        "clock_in": time(9, 0), "clock_out": time(19, 0), "break": 45,
        "issue_type": IssueType.INSUFFICIENT_BREAK.value,
        "severity": IssueSeverity.HIGH.value,
        "rule": "10時間勤務に対し休憩45分（法定60分以上必要）",
    },
    # 長時間労働
    {
        "employee_idx": 4, "date": date(2026, 1, 15),
        "clock_in": time(9, 0), "clock_out": time(23, 30), "break": 60,
        "issue_type": IssueType.OVERTIME.value,
        "severity": IssueSeverity.HIGH.value,
        "rule": "日次勤務時間13.5時間（アラート閾値10時間超過）",
    },
    # 深夜勤務
    {
        "employee_idx": 5, "date": date(2026, 1, 17),
        "clock_in": time(18, 0), "clock_out": time(2, 0), "break": 45,
        "issue_type": IssueType.NIGHT_WORK.value,
        "severity": IssueSeverity.MEDIUM.value,
        "rule": "深夜時間帯（22:00〜翌5:00）の勤務あり",
    },
    # 打刻漏れ（出勤）2件目
    {
        "employee_idx": 6, "date": date(2026, 1, 20),
        "clock_in": None, "clock_out": time(22, 0), "break": 60,
        "issue_type": IssueType.MISSING_CLOCK_IN.value,
        "severity": IssueSeverity.HIGH.value,
        "rule": "出勤打刻がありません（退勤: 22:00）",
    },
    # 長時間＋深夜
    {
        "employee_idx": 0, "date": date(2026, 1, 22),
        "clock_in": time(10, 0), "clock_out": time(1, 0), "break": 60,
        "issue_type": IssueType.OVERTIME.value,
        "severity": IssueSeverity.HIGH.value,
        "rule": "日次勤務時間14時間（アラート閾値10時間超過）＋深夜勤務",
    },
    # 休憩不足3件目
    {
        "employee_idx": 7, "date": date(2026, 1, 24),
        "clock_in": time(11, 0), "clock_out": time(20, 0), "break": 30,
        "issue_type": IssueType.INSUFFICIENT_BREAK.value,
        "severity": IssueSeverity.HIGH.value,
        "rule": "9時間勤務に対し休憩30分（法定60分以上必要）",
    },
    # 退勤漏れ2件目
    {
        "employee_idx": 4, "date": date(2026, 1, 27),
        "clock_in": time(16, 0), "clock_out": None, "break": 0,
        "issue_type": IssueType.MISSING_CLOCK_OUT.value,
        "severity": IssueSeverity.HIGH.value,
        "rule": "退勤打刻がありません（出勤: 16:00）",
    },
]


async def seed_demo_data():
    """デモデータを生成"""
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 既存の組織・店舗を取得
        org_result = await session.execute(select(Organization).limit(1))
        org = org_result.scalar_one_or_none()
        if not org:
            print("組織が見つかりません。先に init_data.py を実行してください。")
            return

        store_result = await session.execute(
            select(Store).where(Store.organization_id == org.id).limit(1)
        )
        store = store_result.scalar_one_or_none()
        if not store:
            print("店舗が見つかりません。")
            return

        # 既存の従業員チェック
        emp_result = await session.execute(
            select(Employee).where(Employee.organization_id == org.id)
        )
        if emp_result.scalars().first():
            print("デモ従業員が既に存在します。スキップします。")
            return

        # 従業員作成
        employees = []
        for emp_data in DEMO_EMPLOYEES:
            emp = Employee(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                store_id=store.id,
                employee_code=emp_data["code"],
                name=emp_data["name"],
            )
            session.add(emp)
            employees.append(emp)
        await session.flush()

        # 正常な勤怠データ（2026年1月）
        record_count = 0
        start_date = date(2026, 1, 5)  # 月曜始まり

        for emp_idx, emp in enumerate(employees):
            for day_offset in range(25):  # 25日分
                d = start_date + timedelta(days=day_offset)
                # 土日はスキップ（飲食だが、デモ用にシンプルに）
                if d.weekday() >= 6:  # 日曜のみ休み
                    continue

                # 異常パターンか確認
                anomaly = next(
                    (a for a in ANOMALIES if a["employee_idx"] == emp_idx and a["date"] == d),
                    None,
                )

                if anomaly:
                    record = AttendanceRecord(
                        id=str(uuid.uuid4()),
                        employee_id=emp.id,
                        date=d,
                        clock_in=anomaly["clock_in"],
                        clock_out=anomaly["clock_out"],
                        break_minutes=anomaly["break"],
                    )
                    session.add(record)
                    await session.flush()

                    issue = Issue(
                        id=str(uuid.uuid4()),
                        attendance_record_id=record.id,
                        type=anomaly["issue_type"],
                        severity=anomaly["severity"],
                        status=IssueStatus.PENDING.value,
                        rule_description=anomaly["rule"],
                    )
                    session.add(issue)
                else:
                    # 正常シフト（従業員ごとにパターンを変える）
                    shift = NORMAL_SHIFTS[(emp_idx + day_offset) % len(NORMAL_SHIFTS)]
                    record = AttendanceRecord(
                        id=str(uuid.uuid4()),
                        employee_id=emp.id,
                        date=d,
                        clock_in=shift["clock_in"],
                        clock_out=shift["clock_out"],
                        break_minutes=shift["break"],
                    )
                    session.add(record)

                record_count += 1

        await session.commit()

        print("=" * 50)
        print("デモデータを生成しました")
        print("=" * 50)
        print(f"  従業員数: {len(employees)}名")
        print(f"  勤怠レコード: {record_count}件")
        print(f"  異常データ: {len(ANOMALIES)}件")
        print()
        print("異常の内訳:")
        print(f"  打刻漏れ(出勤): 2件")
        print(f"  打刻漏れ(退勤): 2件")
        print(f"  休憩不足: 3件")
        print(f"  長時間労働: 2件")
        print(f"  深夜勤務: 1件")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
