# 勤怠チェック＋是正理由作成システム 進捗管理表

## フェーズ進捗

- [x] Phase 1: 要件定義
- [x] Phase 2: Git管理
- [x] Phase 3: フロントエンド基盤
- [x] Phase 4: バックエンド基盤
- [x] Phase 5: 機能実装
- [x] Phase 6: 本番デプロイ
- [x] Phase 7: 販売準備（法務・LP・決済・KPI）

---

## 本番環境

| サービス | URL | ステータス |
|---------|-----|-----------|
| フロントエンド | https://kintai-sensei.vercel.app | 稼働中 |
| バックエンドAPI | https://kintai-sensei-api.onrender.com | 稼働中 |
| GitHubリポジトリ | https://github.com/taka52208-glitch/kintai-sensei | 公開中 |

### テストアカウント
| ロール | Email | Password |
|--------|-------|----------|
| 管理者 | admin@example.com | KintaiDev2026! |
| 店長 | store@example.com | KintaiDev2026! |

---

## ページ管理表

| ID | ページ名 | ルート | 権限 | 完了 |
|----|---------|-------|------|------|
| P-000 | ランディングページ | /landing | 全員 | [x] |
| P-001 | ログイン | /login | 全員 | [x] |
| P-001b | 新規登録 | /signup | 全員 | [x] |
| P-002 | 取り込み＆異常一覧 | /dashboard | 店舗管理者以上 | [x] |
| P-003 | 異常詳細＆是正対応 | /issues/:id | 店舗管理者以上 | [x] |
| P-004 | レポート出力 | /reports | 店舗管理者以上 | [x] |
| P-005 | 設定（検知ルール＋課金） | /settings | 管理者 | [x] |
| A-001 | ユーザー管理 | /admin/users | 管理者 | [x] |
| A-002 | 店舗管理 | /admin/stores | 管理者 | [x] |

---

## バックエンドAPI管理表

| エンドポイント | メソッド | 説明 | 完了 |
|---------------|----------|------|------|
| /api/health | GET | ヘルスチェック | [x] |
| /api/auth/login | POST | ログイン | [x] |
| /api/auth/signup | POST | セルフサインアップ | [x] |
| /api/auth/refresh | POST | トークンリフレッシュ | [x] |
| /api/auth/logout | POST | ログアウト | [x] |
| /api/users | GET | ユーザー一覧 | [x] |
| /api/users/{id} | GET/PUT/DELETE | ユーザー詳細 | [x] |
| /api/users/invite | POST | ユーザー招待 | [x] |
| /api/stores | GET/POST | 店舗一覧/作成 | [x] |
| /api/stores/{id} | GET/PUT/DELETE | 店舗詳細 | [x] |
| /api/attendance/upload | POST | CSV取り込み＋プラン制限チェック | [x] |
| /api/attendance/preview | POST | CSVプレビュー | [x] |
| /api/issues | GET | 異常一覧 | [x] |
| /api/issues/{id} | GET/PUT | 異常詳細/更新 | [x] |
| /api/issues/{id}/logs | POST | 対応ログ追加 | [x] |
| /api/issues/{id}/reason | POST | 是正理由文生成 | [x] |
| /api/reports | POST | レポート生成（PDF/CSV） | [x] |
| /api/settings/rules | GET/PUT | 検知ルール設定 | [x] |
| /api/settings/templates | GET/PUT | テンプレート設定 | [x] |
| /api/settings/dictionary | GET/PUT | 語彙辞書設定 | [x] |
| /api/billing/plan | GET | プラン情報取得 | [x] |
| /api/billing/checkout | POST | Stripeチェックアウト | [x] |
| /api/billing/portal | POST | Stripeポータル | [x] |
| /api/billing/webhook | POST | Stripe Webhook | [x] |

---

## 販売準備チェックリスト

| タスク | 状態 |
|--------|------|
| 利用規約（docs/legal/terms-of-service.md） | 完了 |
| プライバシーポリシー（docs/legal/privacy-policy.md） | 完了 |
| 特定商取引法に基づく表記（docs/legal/tokushoho.md） | 完了 |
| ランディングページ（/landing） | 完了 |
| セルフサインアップ（/signup） | 完了 |
| Renderコールドスタート対策 | 完了 |
| Stripe決済基盤 | 完了（APIキー設定で有効化） |
| フリーミアム制限（従業員数上限） | 完了 |
| デモデータ生成スクリプト | 完了 |
| KPI計測（GA4） | 完了（VITE_GA_ID設定で有効化） |
| PDF レポート出力（reportlab） | 完了 |
| テンプレート/語彙辞書API | 完了 |
| 販売計画書（docs/SALES_PLAN.md） | 完了 |
| X(Twitter)・noteアカウント開設 | 完了 |
| note記事1本目（是正勧告対応ガイド） | 完了 |
| 競合分析（ジョブカン・KING OF TIME） | 完了 |

---

## コンテンツ成果物

| ファイル | 内容 | 状態 |
|---------|------|------|
| docs/content/note-article-01-zesei-kankoku.md | note記事「是正勧告の対応方法を5ステップで解説」 | 完了（noteへ投稿待ち） |
| docs/content/competitive-analysis.md | 競合分析レポート（ジョブカン・KING OF TIME・市場動向） | 完了 |

---

## マイルストーン

| マイルストーン | 状態 |
|---------------|------|
| 要件定義完了 | 完了 |
| 基盤構築完了 | 完了 |
| 本番デプロイ | 完了 |
| ログイン機能 | 完了 |
| コア機能完了（CSV+検知+理由文生成） | 完了 |
| MVP全ページ動作 | 完了 |
| 販売基盤準備（法務+決済+LP） | 完了 |
| コンテンツマーケ開始（note記事・競合分析） | 完了 |

---

## 月額コスト

| サービス | プラン | 月額 |
|---------|--------|------|
| Vercel | Free | $0 |
| Render | Free | $0 |
| SQLite | 内蔵 | $0 |
| **合計** | | **$0** |

---

## デプロイ前の環境変数設定

| 変数 | 設定先 | 用途 |
|------|--------|------|
| STRIPE_SECRET_KEY | Render | Stripe決済 |
| STRIPE_WEBHOOK_SECRET | Render | Stripe Webhook検証 |
| STRIPE_PRICE_STANDARD | Render | Standard プランPrice ID |
| STRIPE_PRICE_PRO | Render | Pro プランPrice ID |
| VITE_GA_ID | Vercel | Google Analytics 4 計測ID |

---

## 起動方法

### 本番環境
https://kintai-sensei.vercel.app にアクセス

### ローカル開発

#### フロントエンド
```bash
cd frontend
npm install
npm run dev  # http://localhost:3847
```

#### バックエンド
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. alembic upgrade head
PYTHONPATH=. python scripts/init_data.py
PYTHONPATH=. python scripts/seed_demo_data.py  # デモデータ（任意）
PYTHONPATH=. uvicorn main:app --reload --port 8634
```

---

*最終更新: 2026-02-07*
