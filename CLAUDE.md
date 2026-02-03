# 勤怠チェック＋是正理由作成システム

## プロジェクト概要
飲食業界特化の勤怠異常検知＋是正理由文生成システム

## 技術スタック

### フロントエンド
- React 18 + TypeScript 5 + MUI v6
- Vite 5 + React Router v6
- Zustand + React Query (TanStack Query)

### バックエンド
- Python 3.12 + FastAPI
- SQLAlchemy 2.0 + Pydantic v2
- python-jose (JWT認証)

### データベース
- SQLite（ローカル開発）
- PostgreSQL (Neon) - 本番環境（無料枠使用）

### インフラ（コスト最小構成）
- フロントエンド: Vercel（無料枠）
- バックエンド: Google Cloud Run（無料枠）
- ストレージ: Cloud Storage（最小利用）

## ポート設定
```
frontend: 3847
backend: 8634
```
※複数プロジェクト並行開発のため、一般的でないポートを使用

## テスト認証情報
```
管理者アカウント:
  email: admin@example.com
  password: KintaiDev2026!

店舗管理者アカウント:
  email: store@example.com
  password: KintaiDev2026!

デモ店舗:
  コード: STORE001
  名前: 渋谷店
```

## 環境変数
```
設定ファイル: .env.local（ルートのみ）
設定モジュール:
  - frontend: src/config/index.ts
  - backend: src/config.py
ハードコード禁止: 環境変数はconfig経由のみ
```

## 命名規則
```
ファイル:
  - PascalCase.tsx（コンポーネント）
  - camelCase.ts（その他）
  - snake_case.py（Python）

変数/関数:
  - camelCase (TypeScript)
  - snake_case (Python)

定数: UPPER_SNAKE_CASE
型: PascalCase
```

## 型定義
```
frontend: src/types/index.ts
backend: src/schemas/（Pydanticモデル）
# 両ファイルは常に同期
```

## コード品質
```
関数行数: 100行以下
ファイル行数: 700行以下
複雑度: 10以下
行長: 120文字
```

## ディレクトリ構造
```
/
├── frontend/
│   ├── src/
│   │   ├── components/    # 共通コンポーネント
│   │   ├── pages/         # ページコンポーネント
│   │   ├── hooks/         # カスタムフック
│   │   ├── stores/        # Zustand ストア
│   │   ├── services/      # API呼び出し
│   │   ├── types/         # 型定義
│   │   ├── utils/         # ユーティリティ
│   │   └── config/        # 設定
│   └── package.json
├── backend/
│   ├── src/
│   │   ├── api/           # APIエンドポイント
│   │   ├── models/        # SQLAlchemyモデル
│   │   ├── schemas/       # Pydanticスキーマ
│   │   ├── services/      # ビジネスロジック
│   │   ├── core/          # 認証・設定等
│   │   └── utils/         # ユーティリティ
│   ├── requirements.txt
│   └── main.py
├── docs/
│   ├── requirements.md    # 要件定義書
│   └── SCOPE_PROGRESS.md  # 進捗管理
├── CLAUDE.md              # このファイル
└── .env.local             # 環境変数（git管理外）
```

## 主要コマンド
```bash
# フロントエンド開発サーバー
cd frontend && npm run dev

# バックエンド開発サーバー
cd backend && source venv/bin/activate && PYTHONPATH=. uvicorn main:app --reload --port 8634

# データベースマイグレーション
cd backend && source venv/bin/activate && PYTHONPATH=. alembic upgrade head

# 初期データ投入
cd backend && source venv/bin/activate && PYTHONPATH=. python scripts/init_data.py

# 型チェック
cd frontend && npx tsc --noEmit
cd backend && mypy src

# リント
cd frontend && npm run lint
cd backend && ruff check src

# テスト
cd frontend && npm run test
cd backend && pytest
```

## コスト最適化方針

### AI API（是正理由文生成）
- **方式**: テンプレ＋スロット方式（LLMは整形のみ）
- **モデル**: OpenAI GPT-4o-mini（最安）
- **呼び出し最小化**: 定型部分はテンプレで処理、LLMは自然な日本語化のみ
- **概算**: 月6,000件で$3〜5程度

### インフラ
- Vercel: 無料枠（月100GB帯域）
- Cloud Run: 無料枠（月200万リクエスト）
- Neon: 無料枠（0.5GB、月190時間）

### 月額コスト目標
- **初期**: $10以下
- **成長期**: $30〜50

## 重要な注意点

### 法令責任の免責
- 本システムは法令判定を代替しない
- 「要確認」「アラート」「疑い」の文言を使用
- 出力文に免責注記を含める

### セキュリティ
- 全入力にサニタイゼーション適用
- JWTトークン有効期限: 1時間
- リフレッシュトークン有効期限: 7日
- ブルートフォース対策: 5回失敗で15分ロック

## 最新技術情報（知識カットオフ対応）

### MUI v6の変更点
- @mui/material/styles からの直接インポート推奨
- ThemeProviderの設定方法は従来通り

### FastAPI + SQLAlchemy 2.0
- async sessionの使用推奨
- `select()` 構文を使用（旧`query()`は非推奨）

### React Query v5 (TanStack Query)
- `useQuery`のオプション構文が変更
- `queryKey`は配列形式必須

## デプロイ情報

### フロントエンド
- **URL**: https://kintai-sensei.vercel.app
- **プラットフォーム**: Vercel (無料枠)
- **ステータス**: デプロイ完了

### バックエンド
- **推奨プラットフォーム**: Render.com
- **設定ファイル**: `backend/render.yaml`
- **詳細手順**: `docs/DEPLOYMENT.md`

---

*最終更新: 2026-02-04*
*Phase 1: 要件定義 完了*
*Phase 2: 基盤構築 完了（DB初期化・認証API動作確認済み）*
*Phase 3: フロントエンドデプロイ完了*
