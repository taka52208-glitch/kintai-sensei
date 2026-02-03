# デプロイ手順書

## 現在のデプロイ状況

### フロントエンド (Vercel)
- **URL**: https://kintai-sensei.vercel.app
- **ステータス**: デプロイ完了
- **プロジェクト名**: kintai-sensei

### バックエンド
- **推奨**: Render.com または Railway.app (無料枠あり)
- **設定ファイル**: `backend/render.yaml` (Render用)、`backend/Dockerfile` (Docker対応プラットフォーム用)

---

## バックエンドデプロイ手順 (Render.com)

### 1. GitHubリポジトリを作成

```bash
cd /home/user/勤怠チェック＋是正理由作成システム
git init
git add .
git commit -m "Initial commit: Kintai Sensei System"
git remote add origin https://github.com/YOUR_USERNAME/kintai-sensei.git
git push -u origin main
```

### 2. Render.comでデプロイ

1. https://render.com にアクセス
2. GitHubアカウントで登録/ログイン
3. 「New +」→「Web Service」を選択
4. GitHubリポジトリを接続
5. 以下を設定:
   - **Name**: `kintai-sensei-api`
   - **Region**: Singapore (アジアに近い)
   - **Branch**: main
   - **Root Directory**: `backend`
   - **Runtime**: Docker
   - **Instance Type**: Free

### 3. 環境変数を設定

Renderダッシュボードで以下の環境変数を設定:

```
DATABASE_URL=postgresql://user:password@host/dbname
JWT_SECRET_KEY=your-secure-random-key-here
OPENAI_API_KEY=sk-your-openai-api-key
```

### 4. PostgreSQLを追加 (Render)

1. Renderダッシュボードで「New +」→「PostgreSQL」
2. **Name**: `kintai-sensei-db`
3. **Plan**: Free
4. 作成後、Internal Database URLをコピー
5. Web ServiceのDATABASE_URL環境変数に設定

---

## フロントエンド設定更新

バックエンドURLが決まったら、フロントエンドを更新:

### 1. vercel.jsonを更新

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://kintai-sensei-api.onrender.com/api/:path*"
    }
  ]
}
```

### 2. 再デプロイ

```bash
cd frontend
vercel --prod
```

---

## 代替デプロイオプション

### Railway.app

1. https://railway.app にアクセス
2. GitHubでログイン
3. 「New Project」→「Deploy from GitHub repo」
4. バックエンドフォルダを選択
5. 環境変数を設定

### Google Cloud Run (要Billing)

```bash
# プロジェクト設定
gcloud config set project YOUR_PROJECT_ID

# Cloud Run APIを有効化
gcloud services enable run.googleapis.com

# デプロイ
cd backend
gcloud run deploy kintai-sensei-api \
  --source . \
  --region asia-northeast1 \
  --allow-unauthenticated
```

---

## データベース設定

### Neon (PostgreSQL) - 推奨

1. https://neon.tech にアクセス
2. 無料アカウントを作成
3. 新しいプロジェクトを作成
4. 接続文字列をコピー:
   ```
   postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```
5. `DATABASE_URL`環境変数に設定

### Supabase (代替)

1. https://supabase.com にアクセス
2. 新しいプロジェクトを作成
3. Settings → Database → Connection string (URI)をコピー

---

## 動作確認

### ヘルスチェック
```bash
curl https://YOUR_BACKEND_URL/api/health
```

### ログインテスト
```bash
curl -X POST https://YOUR_BACKEND_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"KintaiDev2026!"}'
```

---

## トラブルシューティング

### CORS エラー
`backend/main.py`のCORS設定にフロントエンドURLを追加:
```python
allow_origins=[
    "https://kintai-sensei.vercel.app",
    "https://your-custom-domain.com",
]
```

### データベース接続エラー
- 環境変数`DATABASE_URL`が正しいか確認
- SSL設定(`?sslmode=require`)が含まれているか確認

### 500 Internal Server Error
- ログを確認: Renderダッシュボード → Logs
- 環境変数が正しく設定されているか確認

---

## コスト概算

| サービス | プラン | 月額コスト |
|---------|--------|-----------|
| Vercel (Frontend) | Free | $0 |
| Render (Backend) | Free | $0 |
| Neon (Database) | Free | $0 |
| OpenAI API | Pay-as-you-go | ~$3-5 |
| **合計** | | **~$3-5/月** |

---

*最終更新: 2026-02-04*
