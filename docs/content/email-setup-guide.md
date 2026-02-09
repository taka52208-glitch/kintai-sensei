# Resendメール営業セットアップガイド（無料版）

> Phase 1（初期顧客獲得）メール営業基盤
> Resend無料テストドメイン使用 - 独自ドメイン不要・コスト0円
> 最終更新: 2026-02-10

---

## 概要

Resendの無料テストドメイン `onboarding@resend.dev` を使って、
独自ドメインなし・コスト0円でメール営業を行う。

Phase 1は知人ネットワーク（5社程度）への営業のため、これで十分。

### Resend無料枠

| 項目 | 制限 |
|------|------|
| 月間送信数 | 3,000通 |
| 日次送信数 | 100通 |
| テストドメイン | `onboarding@resend.dev` |
| 費用 | **0円** |

---

## セットアップ済み

| 項目 | ステータス |
|------|----------|
| Resendアカウント | 作成済み |
| APIキー | 取得済み・動作確認済み |
| テスト送信スクリプト | `scripts/test_email.py` |
| 一括送信スクリプト | `scripts/send_outreach.py` |
| テスト送信 | 成功確認済み（`taka52208@gmail.com` 宛て） |

---

## 使い方

### 1. テスト送信

```bash
cd backend && source venv/bin/activate
python ../scripts/test_email.py
```

### 2. 送信先CSVを作成

`scripts/recipients.csv` を作成:

```csv
name,email,company
山田太郎,yamada@example.com,渋谷食堂
佐藤花子,sato@example.com,新宿ダイニング
```

### 3. ドライラン（確認のみ）

```bash
python ../scripts/send_outreach.py ../scripts/recipients.csv
```

### 4. 実際に送信

```bash
python ../scripts/send_outreach.py ../scripts/recipients.csv --send
```

送信ログは `scripts/send_log_YYYYMMDD_HHMMSS.csv` に自動保存される。

---

## 注意事項

### テストドメインの制限
- 送信元は `onboarding@resend.dev` 固定（変更不可）
- 受信者の迷惑メールフォルダに入る可能性あり
- 知人への営業では「メールが届いていなければ迷惑メールフォルダを確認してください」と一言添える

### 返信の受け取り
- `onboarding@resend.dev` への返信は受け取れない
- メール本文に「本メールにご返信いただくか」の記載あり → 返信先としてGmailを案内する運用

### 将来の独自ドメイン移行
独自ドメインが必要になった場合:
1. Cloudflare Registrarで `kintai-sensei.com` 取得（約1,200円/年）
2. ResendにDNS設定（SPF/DKIM）
3. スクリプトの `FROM_ADDRESS` を `info@kintai-sensei.com` に変更

---

## コスト

| 項目 | 費用 |
|------|------|
| Resend | 無料（月3,000通） |
| 独自ドメイン | 不要 |
| **合計** | **0円** |

---

*最終更新: 2026-02-10*
