# 独自ドメイン取得 → Resendメール営業セットアップガイド

> Phase 1（初期顧客獲得）メール営業基盤の構築手順
> 最終更新: 2026-02-10

---

## 概要

メール営業を始めるために必要な手順:
1. 独自ドメイン取得
2. Resendにドメイン登録 & DNS設定（SPF/DKIM）
3. 送信元アドレス設定
4. テスト送信で動作確認
5. 営業メール一括送信

---

## 1. 独自ドメイン取得

### レジストラ比較

| レジストラ | .com費用 | 特徴 | おすすめ度 |
|-----------|---------|------|----------|
| **Cloudflare Registrar** | 約1,200円/年 | 最安・原価提供・更新料も同額 | ★★★ |
| Google Domains (Squarespace) | 約1,400円/年 | 管理しやすい・DNS設定が直感的 | ★★☆ |
| お名前.com | 約1,500円/年 | 日本語サポート・営業メール多い | ★☆☆ |

**推奨: Cloudflare Registrar**
- 原価提供のため最安（マークアップなし）
- 更新料の値上げがない
- Cloudflare DNSと統合済みで設定が楽
- WHOIS代行が無料

### ドメイン候補

| ドメイン | 用途 | 備考 |
|---------|------|------|
| `kintai-sensei.com` | メイン | 国際的に使える・最安 |
| `kintai-sensei.jp` | 日本市場向け | 信頼感あり・やや高い（約3,000円/年） |

**推奨: `kintai-sensei.com`**（コスト重視 + 現在のVercel URLと一致）

### Cloudflare Registrarでの取得手順

1. [Cloudflare](https://dash.cloudflare.com/sign-up) にアカウント作成
2. ダッシュボード → 「ドメインの登録」 → 希望ドメインを検索
3. カートに追加 → 支払い（クレジットカード/PayPal）
4. 登録完了（通常数分でアクティブに）

> Cloudflareで取得すると、DNSもCloudflareで管理するため、
> 次のステップのDNS設定がそのまま同じ画面でできる。

---

## 2. ResendにDNS設定（SPF/DKIM）

### Resend無料枠

| 項目 | 制限 |
|------|------|
| 月間送信数 | 3,000通 |
| 日次送信数 | 100通 |
| ドメイン数 | 1 |
| API呼び出し | 無制限 |

> Phase 1の営業規模（5社×数通）には十分。

### 手順

#### 2-1. Resendにドメイン追加

1. [Resend Dashboard](https://resend.com/domains) にログイン
2. 「Domains」→「Add Domain」
3. ドメイン名を入力: `kintai-sensei.com`
4. リージョン: **US East** または **EU West**（どちらでもOK）
5. 「Add」をクリック

#### 2-2. DNS レコード設定

Resendがドメイン追加後に表示するDNSレコードを、Cloudflare DNSに追加する。

表示されるレコード（例）:

| タイプ | ホスト | 値 | 優先度 |
|--------|--------|-----|--------|
| **MX** | `send._domainkey` | `feedback-smtp.us-east-1.amazonses.com` | 10 |
| **TXT** | `send._domainkey` | `v=DKIM1; k=rsa; p=MIGf...`（Resendが提示） | - |
| **TXT** | `@` | `v=spf1 include:amazonses.com ~all` | - |

> 実際の値はResendダッシュボードに表示されるものを**そのままコピー**すること。

#### 2-3. Cloudflare DNSへの追加手順

1. Cloudflareダッシュボード → 対象ドメイン → 「DNS」→「レコード」
2. Resendが指示する各レコードを1つずつ追加
3. **プロキシ（オレンジの雲）はOFF**にする（DNS onlyに設定）

#### 2-4. ドメイン検証

1. Resendダッシュボード → 「Domains」
2. 追加したドメインの「Verify」をクリック
3. ステータスが **Verified** になれば完了（通常数分〜最大48時間）

> DNS伝播に時間がかかる場合がある。1時間経っても未検証の場合は
> DNSレコードの値を再確認。

---

## 3. 送信元アドレスの設定

### 推奨する送信元アドレス

| 用途 | アドレス | 表示名 |
|------|---------|--------|
| 営業メール | `info@kintai-sensei.com` | 勤怠先生 |
| サポート | `support@kintai-sensei.com` | 勤怠先生 サポート |
| 自動通知 | `noreply@kintai-sensei.com` | 勤怠先生 |

> ドメイン検証が完了していれば、任意のアドレスで送信可能。
> 個別のメールボックス作成は不要（Resendは送信専用サービス）。

### 返信の受信

Resendは送信専用のため、返信を受け取るには別途対応が必要:

**方法A: 転送サービス（推奨）**
- [Cloudflare Email Routing](https://developers.cloudflare.com/email-routing/)（無料）
- `info@kintai-sensei.com` → `taka52208@gmail.com` に転送設定

**Cloudflare Email Routingの設定:**
1. Cloudflareダッシュボード → 「メール」→「Email Routing」
2. 「ルーティングルール」→「アドレスの作成」
3. カスタムアドレス: `info`
4. 転送先: `taka52208@gmail.com`
5. 「保存」

---

## 4. テスト送信スクリプト

### 事前準備

```bash
pip install resend
```

### テスト送信スクリプト

ファイル: `scripts/test_email.py`

```python
"""Resend テスト送信スクリプト"""
import resend
import sys

# --- 設定 ---
RESEND_API_KEY = "re_4KHgS6FR_F9yQuTmXU5T5n8WunAs9gHiB"
FROM_ADDRESS = "info@kintai-sensei.com"
FROM_NAME = "勤怠先生"
TEST_TO = "taka52208@gmail.com"

resend.api_key = RESEND_API_KEY


def send_test_email(to_address: str = TEST_TO) -> None:
    """テストメールを送信"""
    params: resend.Emails.SendParams = {
        "from": f"{FROM_NAME} <{FROM_ADDRESS}>",
        "to": [to_address],
        "subject": "【テスト】勤怠先生 メール送信テスト",
        "html": """
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1976d2;">勤怠先生 メール送信テスト</h2>
            <p>このメールは Resend API のテスト送信です。</p>
            <p>正常に受信できていれば、メール営業基盤のセットアップは完了です。</p>
            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 24px 0;">
            <p style="color: #666; font-size: 12px;">
                勤怠先生 - 飲食業界特化の勤怠チェックシステム<br>
                https://kintai-sensei.vercel.app
            </p>
        </div>
        """,
    }
    email = resend.Emails.send(params)
    print(f"送信成功! Email ID: {email['id']}")


if __name__ == "__main__":
    to = sys.argv[1] if len(sys.argv) > 1 else TEST_TO
    print(f"テストメール送信先: {to}")
    send_test_email(to)
```

### 実行方法

```bash
# デフォルト（taka52208@gmail.com宛て）
python scripts/test_email.py

# 任意のアドレス宛て
python scripts/test_email.py someone@example.com
```

---

## 5. 営業メール一括送信スクリプト

ファイル: `scripts/send_outreach.py`

```python
"""
営業メール一括送信スクリプト
monitor-recruitment.md のテンプレートAを使用
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
```

### CSVファイルのフォーマット

ファイル: `scripts/recipients.csv`（例）

```csv
name,email,company
山田太郎,yamada@example.com,渋谷食堂
佐藤花子,sato@example.com,新宿ダイニング
```

### 実行方法

```bash
# Step 1: ドライラン（送信せずに確認）
python scripts/send_outreach.py scripts/recipients.csv

# Step 2: 実際に送信
python scripts/send_outreach.py scripts/recipients.csv --send
```

### 送信ログ

送信ごとに `scripts/send_log_YYYYMMDD_HHMMSS.csv` が自動生成される。

| カラム | 内容 |
|--------|------|
| timestamp | 送信日時 |
| name | 送信先名 |
| email | メールアドレス |
| company | 企業/店舗名 |
| status | dry_run / sent / failed |
| email_id | Resendの送信ID |

---

## セットアップ完了チェックリスト

- [ ] ドメイン取得完了（Cloudflare Registrar）
- [ ] Resendにドメイン追加
- [ ] DNS レコード設定（SPF/DKIM/MX）
- [ ] Resendでドメイン検証完了（Verified）
- [ ] Cloudflare Email Routing設定（返信転送）
- [ ] テスト送信成功（`test_email.py`）
- [ ] 送信先CSVファイル作成（`recipients.csv`）
- [ ] ドライランで確認（`send_outreach.py`）
- [ ] 営業メール送信開始

---

## トラブルシューティング

### ドメイン検証が通らない

1. Cloudflare DNS でプロキシ（オレンジの雲）がOFFになっているか確認
2. TXTレコードの値を再確認（コピペミスに注意）
3. 最大48時間待つ（通常は数分〜数時間）

### メールが迷惑メールに入る

1. SPF/DKIMの設定が正しいか確認
2. 初期は少量（1日10通以下）から始めてドメインの信頼度を上げる
3. HTML内に過度なリンクや画像を避ける

### Resend APIエラー

| エラー | 原因 | 対処 |
|--------|------|------|
| `validation_error` | パラメータ不正 | from/to/subjectを確認 |
| `not_found` | ドメイン未登録 | Resendでドメイン検証を確認 |
| `rate_limit_exceeded` | 送信上限超過 | 翌日まで待つ（日次100通） |
| `missing_api_key` | APIキー未設定 | RESEND_API_KEYを確認 |

---

## コスト

| 項目 | 費用 | 備考 |
|------|------|------|
| ドメイン（.com） | 約1,200円/年 | Cloudflare Registrar |
| Resend | 無料 | 月3,000通まで |
| Cloudflare Email Routing | 無料 | メール転送 |
| **合計** | **約1,200円/年** | **月100円程度** |

---

*最終更新: 2026-02-10*
