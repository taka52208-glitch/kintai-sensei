"""
営業メール一括送信スクリプト
monitor-recruitment.md のテンプレートAを使用

使い方:
    python scripts/send_outreach.py recipients.csv          # ドライラン（確認のみ）
    python scripts/send_outreach.py recipients.csv --send   # 実際に送信

CSVフォーマット:
    name,email,company
    山田太郎,yamada@example.com,渋谷食堂
"""
import csv
import resend
import time
import sys
from datetime import datetime
from pathlib import Path

# --- 設定 ---
RESEND_API_KEY = "re_4KHgS6FR_F9yQuTmXU5T5n8WunAs9gHiB"
FROM_ADDRESS = "info@kintai-sensei.com"
FROM_NAME = "勤怠先生"
SENDER_NAME = "（あなたの名前）"  # ← 送信前に変更

# Resend無料枠の制限
DAILY_LIMIT = 100
DELAY_SECONDS = 2  # 送信間隔（秒）

resend.api_key = RESEND_API_KEY

SUBJECT = "【ご協力のお願い】飲食店向け勤怠チェックツール「勤怠先生」無料モニター募集"

EMAIL_TEMPLATE = """\
<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; line-height: 1.8;">

<p>{recipient_name}様</p>

<p>お世話になっております。{sender_name}です。</p>

<p>突然のご連絡失礼いたします。<br>
現在、飲食店向けの勤怠チェックシステム「<strong>勤怠先生</strong>」を開発・運営しており、<br>
正式リリースに先立ち、<strong>無料モニター</strong>にご協力いただける飲食店様を探しております。</p>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">
  勤怠先生とは
</h3>

<p>既存の勤怠管理システム（ジョブカン、Airシフト等）から出力したCSVを取り込むだけで、<br>
以下を<strong>自動で</strong>行うクラウドサービスです。</p>

<ul>
  <li>長時間労働・休憩不足・打刻漏れなど <strong>8種類の異常を自動検知</strong></li>
  <li>労基署対応に使える <strong>是正理由文をAIが自動生成</strong></li>
  <li>検知結果を <strong>PDF/CSVレポートとして出力</strong>（監査対応用）</li>
</ul>

<p>「検知して終わり」ではなく「<strong>対応まで完結</strong>」する点が最大の特徴です。</p>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">
  無料モニター特典
</h3>

<table style="border-collapse: collapse; width: 100%;">
  <tr style="background: #f5f5f5;">
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>利用料</strong></td>
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>3ヶ月間 完全無料</strong>（スタンダードプラン相当）</td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>従業員数制限</strong></td>
    <td style="border: 1px solid #ddd; padding: 8px;">なし（モニター期間中）</td>
  </tr>
  <tr style="background: #f5f5f5;">
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>全機能利用</strong></td>
    <td style="border: 1px solid #ddd; padding: 8px;">異常検知・是正理由文生成・レポート出力すべて利用可</td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>優先サポート</strong></td>
    <td style="border: 1px solid #ddd; padding: 8px;">導入・操作方法を直接サポートいたします</td>
  </tr>
  <tr style="background: #f5f5f5;">
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>モニター終了後</strong></td>
    <td style="border: 1px solid #ddd; padding: 8px;">フリープラン（10名以下無料）への自動移行</td>
  </tr>
</table>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">
  お願いしたいこと
</h3>

<ul>
  <li>月1〜2回の勤怠データ（CSV）のアップロード</li>
  <li>簡単なアンケートへのご回答（5〜10分程度、計2回）</li>
  <li>気づいた点・ご要望のフィードバック</li>
</ul>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">
  モニター期間
</h3>

<p>2026年2月〜4月（3ヶ月間）</p>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">
  お申し込み方法
</h3>

<p>ご興味をお持ちいただけましたら、本メールにご返信いただくか、<br>
以下のURLからサインアップをお願いいたします。</p>

<p style="text-align: center; margin: 24px 0;">
  <a href="https://kintai-sensei.vercel.app/signup"
     style="background: #1976d2; color: white; padding: 12px 32px;
            text-decoration: none; border-radius: 4px; font-weight: bold;">
    無料でサインアップ
  </a>
</p>

<p>もし{recipient_name}様のお知り合いで、飲食店を経営されている方がいらっしゃいましたら、<br>
ご紹介いただけますと大変ありがたく存じます。</p>

<p>ご不明な点がございましたら、お気軽にお問い合わせください。<br>
何卒よろしくお願いいたします。</p>

<p>{sender_name}</p>

<hr style="border: none; border-top: 1px solid #e0e0e0; margin: 24px 0;">

<p style="color: #999; font-size: 11px;">
  勤怠先生 - 飲食業界特化の勤怠チェックシステム<br>
  https://kintai-sensei.vercel.app<br>
  ※このメールに心当たりがない場合は、お手数ですがそのまま破棄してください。
</p>

</div>
"""


def load_recipients(csv_path: str) -> list[dict]:
    """CSVから送信先リストを読み込み

    CSVフォーマット:
      name,email,company
      山田太郎,yamada@example.com,渋谷食堂
    """
    recipients = []
    path = Path(csv_path)
    if not path.exists():
        print(f"エラー: {csv_path} が見つかりません")
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("email"):
                recipients.append({
                    "name": row.get("name", "ご担当者"),
                    "email": row["email"].strip(),
                    "company": row.get("company", ""),
                })
    return recipients


def send_outreach(recipients: list[dict], dry_run: bool = True) -> None:
    """営業メールを一括送信

    Args:
        recipients: 送信先リスト
        dry_run: Trueの場合、実際には送信しない（確認用）
    """
    total = len(recipients)
    if total > DAILY_LIMIT:
        print(f"警告: 送信先が{total}件あります（日次上限: {DAILY_LIMIT}件）")
        print(f"最初の{DAILY_LIMIT}件のみ送信します。残りは翌日に送信してください。")
        recipients = recipients[:DAILY_LIMIT]
        total = DAILY_LIMIT

    print(f"\n{'='*50}")
    print(f"営業メール {'ドライラン' if dry_run else '送信'}")
    print(f"送信件数: {total}")
    print(f"送信元: {FROM_NAME} <{FROM_ADDRESS}>")
    print(f"{'='*50}\n")

    log_file = Path(f"scripts/send_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(log_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "name", "email", "company", "status", "email_id"])

        for i, r in enumerate(recipients, 1):
            html = EMAIL_TEMPLATE.format(
                recipient_name=r["name"],
                sender_name=SENDER_NAME,
            )

            print(f"[{i}/{total}] {r['name']} <{r['email']}> ({r['company']})...", end=" ")

            if dry_run:
                print("(ドライラン - 送信スキップ)")
                writer.writerow([
                    datetime.now().isoformat(), r["name"], r["email"],
                    r["company"], "dry_run", "",
                ])
                continue

            try:
                params: resend.Emails.SendParams = {
                    "from": f"{FROM_NAME} <{FROM_ADDRESS}>",
                    "to": [r["email"]],
                    "subject": SUBJECT,
                    "html": html,
                }
                result = resend.Emails.send(params)
                email_id = result["id"]
                print(f"送信成功 (ID: {email_id})")
                writer.writerow([
                    datetime.now().isoformat(), r["name"], r["email"],
                    r["company"], "sent", email_id,
                ])
            except Exception as e:
                print(f"送信失敗: {e}")
                writer.writerow([
                    datetime.now().isoformat(), r["name"], r["email"],
                    r["company"], "failed", str(e),
                ])

            if i < total:
                time.sleep(DELAY_SECONDS)

    print(f"\n送信ログ: {log_file}")


def main():
    if len(sys.argv) < 2:
        print("使い方:")
        print("  python scripts/send_outreach.py recipients.csv          # ドライラン（確認のみ）")
        print("  python scripts/send_outreach.py recipients.csv --send   # 実際に送信")
        print("")
        print("CSVフォーマット:")
        print("  name,email,company")
        print("  山田太郎,yamada@example.com,渋谷食堂")
        sys.exit(0)

    csv_path = sys.argv[1]
    dry_run = "--send" not in sys.argv

    recipients = load_recipients(csv_path)
    if not recipients:
        print("エラー: 送信先が0件です。CSVファイルを確認してください。")
        sys.exit(1)

    print(f"送信先: {len(recipients)}件読み込み")

    if not dry_run:
        confirm = input("本当に送信しますか？ (yes/no): ")
        if confirm.lower() != "yes":
            print("キャンセルしました。")
            sys.exit(0)

    send_outreach(recipients, dry_run=dry_run)


if __name__ == "__main__":
    main()
