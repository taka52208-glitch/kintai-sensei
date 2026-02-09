# Renderコールドスタート対策 - 外部監視サービス設定ガイド

## 問題

Render.com無料枠では、15分間リクエストがないとサービスがスリープし、次のリクエスト時に30秒〜1分のコールドスタートが発生する。

## 対策（2段構え）

### 対策1: フロントエンドからのウォームアップ（実装済み）

LandingPage、LoginPageのマウント時に `/api/health` へpingを送信。
ユーザーがページを開いた瞬間にバックエンドを起こすことで、ログインやCSVアップロード時の待ち時間を軽減。

### 対策2: 外部監視サービスによる定期ping

14分間隔でヘルスチェックを送信し、スリープを防止する。

## 推奨サービス: UptimeRobot（無料）

### 設定手順

1. https://uptimerobot.com/ でアカウント作成（無料）
2. 「Add New Monitor」をクリック
3. 以下の設定を入力:

| 項目 | 設定値 |
|------|--------|
| Monitor Type | HTTP(s) |
| Friendly Name | 勤怠先生 API |
| URL | `https://kintai-sensei-api.onrender.com/api/health` |
| Monitoring Interval | 5 minutes |

4. 「Create Monitor」をクリック

### 無料プランの制限
- モニター数: 50件まで
- 最短間隔: 5分
- ログ保持: 2ヶ月

## 代替サービス

### cron-job.org（無料）

1. https://cron-job.org/ でアカウント作成
2. 「Create cronjob」で以下を設定:
   - URL: `https://kintai-sensei-api.onrender.com/api/health`
   - Schedule: Every 14 minutes
3. 保存して有効化

### Freshping（無料）

1. https://www.freshworks.com/website-monitoring/ でアカウント作成
2. 同様にURLとチェック間隔を設定

## 注意事項

- Renderの無料枠は月750時間の稼働時間制限がある（1サービスなら24時間x31日=744時間で収まる）
- 定期pingでスリープを防止しても、月間稼働時間の制限には影響しない
- 将来的にユーザー数が増えた場合、Render有料プラン($7/月)への移行を検討
