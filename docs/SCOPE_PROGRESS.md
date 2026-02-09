# 勤怠先生 進捗管理表

## フェーズ進捗

- [x] Phase 1: 要件定義
- [x] Phase 2: Git管理
- [x] Phase 3: フロントエンド基盤
- [x] Phase 4: バックエンド基盤
- [x] Phase 5: 機能実装
- [x] Phase 6: 本番デプロイ
- [x] Phase 7: 販売準備（法務・LP・決済・KPI）
- [x] Phase 8: 販売開始（ローンチ）
- [x] Phase 9: 品質監査＋セキュリティ強化（19件修正）
- [x] Phase 10: 本番DB移行（Neon PostgreSQL＋日次バックアップ）
- [ ] Phase 11: 初期顧客獲得（目標10社）→ トラッカー: docs/PHASE1_TRACKER.md

---

## 本番環境

| サービス | URL | ステータス |
|---------|-----|-----------|
| フロントエンド | https://kintai-sensei.vercel.app | 稼働中 |
| バックエンドAPI | https://kintai-sensei-api.onrender.com | 稼働中 |
| データベース | Neon PostgreSQL (us-east-1) | 稼働中 |
| DBバックアップ | GitHub Actions (毎日JST 4:00) | 稼働中 |
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
| /api/auth/logout | POST | ログアウト（トークン無効化） | [x] |
| /api/auth/password | PUT | パスワード変更 | [x] |
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
| note記事2本目（8つの法令違反） | 完了 |
| 無料モニター募集テンプレート | 完了 |
| 社労士ヒアリングシート | 完了 |
| X(Twitter)ローンチ投稿テンプレート | 完了 |

---

## 品質監査＆セキュリティ強化（2026-02-10実施）

### Phase A: CRITICAL修正（7件）
| # | 修正内容 | 状態 |
|---|---------|------|
| C1 | JWT秘密鍵デフォルト値拒否 | 完了 |
| C2 | クロステナントアクセス防止（issues API） | 完了 |
| C3 | CSV store_id所有権検証 | 完了 |
| C4 | リフレッシュトークン実装 | 完了 |
| C5 | 法的文書プレースホルダー置換 | 完了 |
| C6 | パスワード変更機能 | 完了 |
| C7 | トークンブラックリスト（ログアウト無効化） | 完了 |

### Phase B: HIGH修正（5件）
| # | 修正内容 | 状態 |
|---|---------|------|
| H1 | CSV重複アップロード防止 | 完了 |
| H2 | ページネーションUI | 完了 |
| H3 | CSV取込先店舗選択UI | 完了 |
| H4 | Error Boundary（白画面防止） | 完了 |
| H7 | グローバル例外ハンドラ（トレースバック漏洩防止） | 完了 |

### Phase C: MEDIUM修正（7件）
| # | 修正内容 | 状態 |
|---|---------|------|
| M1 | DBインデックス追加 | 完了 |
| M3 | datetime.utcnow()→timezone-aware化 | 完了 |
| M4 | ユーザー一覧page_size上限追加 | 完了 |
| M7 | フリーテキスト長さ制限追加 | 完了 |
| M9 | アプリ名統一（勤怠先生） | 完了 |
| M11 | ログインエラー詳細漏洩修正 | 完了 |
| M12 | CSP/Referrer-Policy/Permissions-Policyヘッダー | 完了 |

### 本番DB移行
| タスク | 状態 |
|--------|------|
| Neon PostgreSQLプロジェクト作成 | 完了 |
| マイグレーション実行 | 完了 |
| 初期データ投入 | 完了 |
| Render環境変数設定（DATABASE_URL） | 完了 |
| GitHub Actions日次バックアップ | 完了（90日保持） |
| DateTime(timezone=True)互換修正 | 完了 |

---

## コンテンツ成果物

| ファイル | 内容 | 状態 |
|---------|------|------|
| docs/content/note-article-01-zesei-kankoku.md | note記事「是正勧告の対応方法を5ステップで解説」 | 完了（noteへ投稿待ち） |
| docs/content/note-article-02-8violations.md | note記事「飲食店の勤怠管理で見逃しがちな8つの法令違反」 | 完了（noteへ投稿待ち） |
| docs/content/competitive-analysis.md | 競合分析レポート（ジョブカン・KING OF TIME・市場動向） | 完了 |
| docs/content/monitor-recruitment.md | 無料モニター募集テンプレート（メール/DM/SNS用） | 完了 |
| docs/content/sharoushi-hearing-sheet.md | 社労士パートナー候補ヒアリングシート | 完了 |
| docs/content/launch-posts.md | X(Twitter)ローンチ投稿テンプレート（6本） | 完了 |

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
| 販売開始（営業資料・ローンチ投稿準備） | 完了 |
| 品質監査＋セキュリティ強化（19件） | 完了 |
| 本番DB移行（SQLite→Neon PostgreSQL） | 完了 |
| 日次DBバックアップ（GitHub Actions） | 完了 |
| Vercel/Render本番デプロイ最新化 | 完了 |
| Phase 1 初期顧客獲得（10社目標） | 進行中 |

---

## 月額コスト

| サービス | プラン | 月額 |
|---------|--------|------|
| Vercel | Free | $0 |
| Render | Free | $0 |
| Neon PostgreSQL | Free (0.5GB) | $0 |
| GitHub Actions | Free (2,000分/月) | $0 |
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
| DATABASE_URL | Render | Neon PostgreSQL接続文字列 |
| JWT_SECRET_KEY | Render | JWT署名用秘密鍵 |
| DATABASE_URL | GitHub Secret | DBバックアップ用 |

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

*最終更新: 2026-02-10*
