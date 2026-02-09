"""
営業メール一括送信スクリプト
送信先のtypeに応じて文面を自動切替

使い方:
    python scripts/send_outreach.py recipients.csv          # ドライラン（確認のみ）
    python scripts/send_outreach.py recipients.csv --send   # 実際に送信

CSVフォーマット:
    name,email,company,type
    川崎潤一,kawasaki@leaf-sr.jp,リーフレイバー,sharoushi
    ご担当者,info@shokudanren.jp,食団連,association

type: sharoushi（社労士）/ association（業界団体）/ media（メディア）/ monitor（モニター募集）
"""
import csv
import resend
import time
import sys
from datetime import datetime
from pathlib import Path

# --- 設定 ---
RESEND_API_KEY = "re_4KHgS6FR_F9yQuTmXU5T5n8WunAs9gHiB"
FROM_ADDRESS = "onboarding@resend.dev"  # Resend無料テストドメイン（独自ドメイン不要）
FROM_NAME = "勤怠先生"
SENDER_NAME = "勤怠先生 開発チーム"
REPLY_TO = "taka52208@gmail.com"

# Resend無料枠の制限
DAILY_LIMIT = 100
DELAY_SECONDS = 2  # 送信間隔（秒）

resend.api_key = RESEND_API_KEY

# --- 件名 ---
SUBJECTS = {
    "sharoushi": "【ご連携のご相談】飲食店向け勤怠チェックツール「勤怠先生」のご紹介",
    "association": "【ご紹介】飲食業界向け勤怠チェックシステム「勤怠先生」について",
    "media": "【掲載・連携のご相談】飲食業界特化の勤怠チェックシステム「勤怠先生」",
    "monitor": "【ご協力のお願い】飲食店向け勤怠チェックツール「勤怠先生」無料モニター募集",
}

# --- 共通フッター ---
FOOTER = """\
<hr style="border: none; border-top: 1px solid #e0e0e0; margin: 24px 0;">
<p style="color: #999; font-size: 11px;">
  勤怠先生 - 飲食業界特化の勤怠チェックシステム<br>
  https://kintai-sensei.vercel.app<br>
  ※返信は {reply_to} まで直接お送りください。<br>
  ※このメールに心当たりがない場合は、お手数ですがそのまま破棄してください。
</p>
</div>
"""

# --- 社労士向けテンプレート ---
TEMPLATE_SHAROUSHI = """\
<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; line-height: 1.8;">

<p>{recipient_name}様</p>

<p>突然のご連絡失礼いたします。飲食業界特化の勤怠チェックシステム「<strong>勤怠先生</strong>」を開発・運営しております、{sender_name}と申します。</p>

<p>貴事務所が飲食業の労務管理に精通されていることを拝見し、<strong>顧問先様へのご紹介</strong>という形での連携をご相談したく、ご連絡いたしました。</p>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">勤怠先生でできること</h3>

<p>既存の勤怠システム（ジョブカン、Airシフト等）のCSVを取り込むだけで、以下を自動で行います。</p>

<ul>
  <li>長時間労働・休憩不足・打刻漏れなど <strong>8種類の異常を自動検知</strong></li>
  <li>労基署対応に使える <strong>是正理由文をAIが自動生成</strong></li>
  <li><strong>PDF/CSVレポート出力</strong>（監査対応用）</li>
</ul>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">連携メリット</h3>

<ul>
  <li>顧問先の労務リスクを事前に可視化し、是正勧告を未然に防止</li>
  <li>是正理由文の下書きをAI生成 → 先生方の業務効率化</li>
  <li>顧問先への付加価値提案として差別化に</li>
</ul>

<p><strong>10名以下の店舗は永久無料</strong>で、サイトからすぐにお試しいただけます。導入に手間はかかりません。</p>

<p style="text-align: center; margin: 24px 0;">
  <a href="https://kintai-sensei.vercel.app/signup"
     style="background: #1976d2; color: white; padding: 12px 32px;
            text-decoration: none; border-radius: 4px; font-weight: bold;">
    無料で試してみる
  </a>
</p>

<p>ご不明な点があれば <strong>{reply_to}</strong> までお気軽にどうぞ。</p>

<p>よろしくお願いいたします。</p>

<p>{sender_name}</p>
"""

# --- 業界団体向けテンプレート ---
TEMPLATE_ASSOCIATION = """\
<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; line-height: 1.8;">

<p>{recipient_name}様</p>

<p>突然のご連絡失礼いたします。飲食業界特化の勤怠チェックシステム「<strong>勤怠先生</strong>」を開発・運営しております、{sender_name}と申します。</p>

<p>貴団体が飲食業界の発展に取り組まれていることを拝見し、<strong>会員様への情報提供</strong>という形でお力添えできないかと思い、ご連絡いたしました。</p>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">勤怠先生でできること</h3>

<p>既存の勤怠システム（ジョブカン、Airシフト等）のCSVを取り込むだけで、以下を自動で行います。</p>

<ul>
  <li>長時間労働・休憩不足・打刻漏れなど <strong>8種類の異常を自動検知</strong></li>
  <li>労基署対応に使える <strong>是正理由文をAIが自動生成</strong></li>
  <li><strong>PDF/CSVレポート出力</strong>（監査対応用）</li>
</ul>

<p>飲食業界は労基署の重点調査対象業種であり、中小飲食店にとって法令遵守は大きな課題です。<strong>10名以下の店舗は永久無料</strong>で、サイトからすぐにお試しいただけます。</p>

<p style="text-align: center; margin: 24px 0;">
  <a href="https://kintai-sensei.vercel.app/signup"
     style="background: #1976d2; color: white; padding: 12px 32px;
            text-decoration: none; border-radius: 4px; font-weight: bold;">
    無料で試してみる
  </a>
</p>

<p>会員様への情報提供の一環としてご紹介いただけましたら幸いです。ご不明な点があれば <strong>{reply_to}</strong> までお気軽にどうぞ。</p>

<p>よろしくお願いいたします。</p>

<p>{sender_name}</p>
"""

# --- メディア向けテンプレート ---
TEMPLATE_MEDIA = """\
<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; line-height: 1.8;">

<p>{recipient_name}様</p>

<p>突然のご連絡失礼いたします。飲食業界特化の勤怠チェックシステム「<strong>勤怠先生</strong>」を開発・運営しております、{sender_name}と申します。</p>

<p>貴メディアが飲食店経営者向けの情報発信をされていることを拝見し、<strong>記事掲載・サービス紹介</strong>のご相談をしたく、ご連絡いたしました。</p>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">勤怠先生でできること</h3>

<p>既存の勤怠システム（ジョブカン、Airシフト等）のCSVを取り込むだけで、以下を自動で行います。</p>

<ul>
  <li>長時間労働・休憩不足・打刻漏れなど <strong>8種類の異常を自動検知</strong></li>
  <li>労基署対応に使える <strong>是正理由文をAIが自動生成</strong>（市場唯一の機能）</li>
  <li><strong>PDF/CSVレポート出力</strong>（監査対応用）</li>
</ul>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">ご提案</h3>

<ul>
  <li>サービス紹介記事の掲載（取材対応可）</li>
  <li>飲食店の勤怠管理に関する寄稿・監修</li>
  <li>読者向けの無料利用枠のご提供</li>
</ul>

<p><strong>10名以下の店舗は永久無料</strong>で、サイトからすぐにお試しいただけます。</p>

<p style="text-align: center; margin: 24px 0;">
  <a href="https://kintai-sensei.vercel.app/signup"
     style="background: #1976d2; color: white; padding: 12px 32px;
            text-decoration: none; border-radius: 4px; font-weight: bold;">
    無料で試してみる
  </a>
</p>

<p>ご不明な点があれば <strong>{reply_to}</strong> までお気軽にどうぞ。</p>

<p>よろしくお願いいたします。</p>

<p>{sender_name}</p>
"""

# --- モニター募集テンプレート（飲食店オーナー向け） ---
TEMPLATE_MONITOR = """\
<div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; line-height: 1.8;">

<p>{recipient_name}様</p>

<p>突然のご連絡失礼いたします。飲食店向けの勤怠チェックシステム「<strong>勤怠先生</strong>」を開発・運営しております、{sender_name}と申します。</p>

<p>正式リリースに先立ち、<strong>3ヶ月間無料のモニター</strong>にご協力いただける飲食店様を探しております。</p>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">勤怠先生でできること</h3>

<p>既存の勤怠システム（ジョブカン、Airシフト等）のCSVを取り込むだけで、以下を自動で行います。</p>

<ul>
  <li>長時間労働・休憩不足・打刻漏れなど <strong>8種類の異常を自動検知</strong></li>
  <li>労基署対応に使える <strong>是正理由文をAIが自動生成</strong></li>
  <li><strong>PDF/CSVレポート出力</strong>（監査対応用）</li>
</ul>

<h3 style="color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 4px;">無料モニター特典</h3>

<table style="border-collapse: collapse; width: 100%;">
  <tr style="background: #f5f5f5;">
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>利用料</strong></td>
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>3ヶ月間 完全無料</strong></td>
  </tr>
  <tr>
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>全機能利用</strong></td>
    <td style="border: 1px solid #ddd; padding: 8px;">異常検知・是正理由文生成・レポート出力</td>
  </tr>
  <tr style="background: #f5f5f5;">
    <td style="border: 1px solid #ddd; padding: 8px;"><strong>終了後</strong></td>
    <td style="border: 1px solid #ddd; padding: 8px;">フリープラン（10名以下無料）へ自動移行</td>
  </tr>
</table>

<p style="text-align: center; margin: 24px 0;">
  <a href="https://kintai-sensei.vercel.app/signup"
     style="background: #1976d2; color: white; padding: 12px 32px;
            text-decoration: none; border-radius: 4px; font-weight: bold;">
    無料でサインアップ
  </a>
</p>

<p>ご興味をお持ちいただけましたら <strong>{reply_to}</strong> までご連絡ください。</p>

<p>よろしくお願いいたします。</p>

<p>{sender_name}</p>
"""

TEMPLATES = {
    "sharoushi": TEMPLATE_SHAROUSHI,
    "association": TEMPLATE_ASSOCIATION,
    "media": TEMPLATE_MEDIA,
    "monitor": TEMPLATE_MONITOR,
}


def load_recipients(csv_path: str) -> list[dict]:
    """CSVから送信先リストを読み込み"""
    recipients = []
    path = Path(csv_path)
    if not path.exists():
        print(f"エラー: {csv_path} が見つかりません")
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("email"):
                rtype = row.get("type", "monitor").strip()
                if rtype not in TEMPLATES:
                    print(f"警告: 不明なtype '{rtype}' → monitorとして処理")
                    rtype = "monitor"
                recipients.append({
                    "name": row.get("name", "ご担当者"),
                    "email": row["email"].strip(),
                    "company": row.get("company", ""),
                    "type": rtype,
                })
    return recipients


def send_outreach(recipients: list[dict], dry_run: bool = True) -> None:
    """営業メールを一括送信"""
    total = len(recipients)
    if total > DAILY_LIMIT:
        print(f"警告: 送信先が{total}件あります（日次上限: {DAILY_LIMIT}件）")
        print(f"最初の{DAILY_LIMIT}件のみ送信します。")
        recipients = recipients[:DAILY_LIMIT]
        total = DAILY_LIMIT

    print(f"\n{'='*60}")
    print(f"営業メール {'ドライラン' if dry_run else '送信'}")
    print(f"送信件数: {total}")
    print(f"送信元: {FROM_NAME} <{FROM_ADDRESS}>")
    print(f"返信先: {REPLY_TO}")
    print(f"{'='*60}\n")

    log_file = Path(f"scripts/send_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(log_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "name", "email", "company", "type", "status", "email_id"])

        for i, r in enumerate(recipients, 1):
            template = TEMPLATES[r["type"]]
            subject = SUBJECTS[r["type"]]
            html = template.format(
                recipient_name=r["name"],
                sender_name=SENDER_NAME,
                reply_to=REPLY_TO,
            ) + FOOTER.format(reply_to=REPLY_TO)

            type_label = {"sharoushi": "社労士", "association": "団体", "media": "メディア", "monitor": "モニター"}
            print(f"[{i}/{total}] [{type_label.get(r['type'], r['type'])}] {r['name']} <{r['email']}>", end=" ")

            if dry_run:
                print("(ドライラン)")
                writer.writerow([
                    datetime.now().isoformat(), r["name"], r["email"],
                    r["company"], r["type"], "dry_run", "",
                ])
                continue

            try:
                params: resend.Emails.SendParams = {
                    "from": f"{FROM_NAME} <{FROM_ADDRESS}>",
                    "to": [r["email"]],
                    "reply_to": REPLY_TO,
                    "subject": subject,
                    "html": html,
                }
                result = resend.Emails.send(params)
                email_id = result["id"]
                print(f"送信成功 (ID: {email_id})")
                writer.writerow([
                    datetime.now().isoformat(), r["name"], r["email"],
                    r["company"], r["type"], "sent", email_id,
                ])
            except Exception as e:
                print(f"送信失敗: {e}")
                writer.writerow([
                    datetime.now().isoformat(), r["name"], r["email"],
                    r["company"], r["type"], "failed", str(e),
                ])

            if i < total:
                time.sleep(DELAY_SECONDS)

    print(f"\n送信ログ: {log_file}")


def main():
    if len(sys.argv) < 2:
        print("使い方:")
        print("  python scripts/send_outreach.py recipients.csv          # ドライラン")
        print("  python scripts/send_outreach.py recipients.csv --send   # 実際に送信")
        print("")
        print("CSVフォーマット:")
        print("  name,email,company,type")
        print("  川崎潤一,kawasaki@leaf-sr.jp,リーフレイバー,sharoushi")
        print("")
        print("type: sharoushi / association / media / monitor")
        sys.exit(0)

    csv_path = sys.argv[1]
    dry_run = "--send" not in sys.argv

    recipients = load_recipients(csv_path)
    if not recipients:
        print("エラー: 送信先が0件です。")
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
