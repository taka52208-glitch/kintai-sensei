# 勤怠チェック＋是正理由作成システム 進捗管理表

## フェーズ進捗

- [x] Phase 1: 要件定義
- [ ] Phase 2: Git管理（スキップ）
- [x] Phase 3: フロントエンド基盤
- [x] Phase 4: バックエンド基盤
- [ ] Phase 5: 機能実装
- [ ] Phase 6: テスト・デプロイ

---

## ページ管理表

| ID | ページ名 | ルート | 権限 | 着手 | 完了 |
|----|---------|-------|------|------|------|
| P-001 | ログイン | /login | 全員 | [x] | [x] |
| P-002 | 取り込み＆異常一覧 | /dashboard | 店舗管理者以上 | [x] | [x] |
| P-003 | 異常詳細＆是正対応 | /issues/:id | 店舗管理者以上 | [x] | [x] |
| P-004 | レポート出力 | /reports | 店舗管理者以上 | [x] | [x] |
| P-005 | 設定 | /settings | 管理者 | [x] | [x] |
| A-001 | ユーザー管理 | /admin/users | 管理者 | [x] | [x] |
| A-002 | 店舗管理 | /admin/stores | 管理者 | [x] | [x] |

---

## バックエンドAPI管理表

| エンドポイント | メソッド | 説明 | 着手 | 完了 |
|---------------|----------|------|------|------|
| /api/health | GET | ヘルスチェック | [x] | [x] |
| /api/auth/login | POST | ログイン | [x] | [x] |
| /api/auth/refresh | POST | トークンリフレッシュ | [x] | [x] |
| /api/auth/logout | POST | ログアウト | [x] | [x] |
| /api/users | GET/POST | ユーザー一覧/作成 | [x] | [x] |
| /api/users/{id} | GET/PUT/DELETE | ユーザー詳細 | [x] | [x] |
| /api/users/invite | POST | 招待リンク発行 | [x] | [x] |
| /api/stores | GET/POST | 店舗一覧/作成 | [x] | [x] |
| /api/stores/{id} | GET/PUT/DELETE | 店舗詳細 | [x] | [x] |
| /api/attendance/upload | POST | CSV取り込み | [x] | [x] |
| /api/attendance/preview | POST | CSVプレビュー | [x] | [x] |
| /api/issues | GET | 異常一覧 | [x] | [x] |
| /api/issues/{id} | GET/PUT | 異常詳細/更新 | [x] | [x] |
| /api/issues/{id}/logs | GET/POST | 対応ログ | [x] | [x] |
| /api/issues/{id}/reason | POST | 是正理由文生成 | [x] | [x] |
| /api/reports | POST | レポート生成 | [x] | [ ] |
| /api/settings/rules | GET/PUT | 検知ルール設定 | [x] | [x] |
| /api/settings/templates | GET/PUT | テンプレート設定 | [x] | [ ] |
| /api/settings/dictionary | GET/PUT | 語彙辞書設定 | [x] | [ ] |

---

## マイルストーン

| マイルストーン | 目標 | 状態 |
|---------------|------|------|
| 要件定義完了 | Phase 1 | 完了 |
| 基盤構築完了 | Phase 3-4 | 完了 |
| コア機能完了 | CSV取込+検知+理由文生成 | 完了 |
| MVP完成 | 全7ページ動作 | 完了 |
| リリース | 本番デプロイ | 未着手 |

---

## コスト最適化方針

- AI API: テンプレ＋スロット方式で呼び出し最小化（LLMは整形のみ）
- DB: Neon無料枠（0.5GB）で開始
- ホスティング: Vercel/Cloud Run無料枠活用
- 初期月額目標: $10以下

---

## 起動方法

### フロントエンド
```bash
cd frontend
npm install
npm run dev  # http://localhost:3847
```

### バックエンド
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8634
```

---

*最終更新: 2026-02-03*
