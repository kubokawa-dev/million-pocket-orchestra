# 宝くじAI セットアップガイド

## 初回セットアップ手順

### 1. pnpmのインストール（まだの場合）

```bash
npm install -g pnpm@9
```

### 2. 依存関係のインストール

```bash
# プロジェクトルートで実行
pnpm install
```

これにより、すべてのワークスペース（apps/*, packages/*）の依存関係が一括インストールされます。

### 3. 環境変数の設定

#### 3.1 ルートディレクトリ

```bash
cp .env.example .env
```

`.env` を編集：

```env
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/millions?schema=public"

NEXT_PUBLIC_SUPABASE_URL="https://your-project.supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="your-anon-key"
SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"

NEXT_PUBLIC_API_URL="http://localhost:3001/api"
```

#### 3.2 管理画面

```bash
cp apps/admin-web/.env.example apps/admin-web/.env.local
```

`.env.local` に同じSupabase設定を記入

#### 3.3 モバイルアプリ

```bash
cp apps/mobile/.env.example apps/mobile/.env
```

`.env` に設定を記入（`EXPO_PUBLIC_` プレフィックスに注意）

### 4. Supabaseプロジェクトの作成

1. [Supabase](https://supabase.com) にアクセス
2. 新規プロジェクトを作成
3. Settings → API から以下を取得：
   - Project URL → `NEXT_PUBLIC_SUPABASE_URL`
   - anon/public key → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - service_role key → `SUPABASE_SERVICE_ROLE_KEY`

### 5. PostgreSQLの起動

#### Dockerを使用する場合（推奨）

```bash
docker-compose up -d
```

#### SQLiteを最新化（PostgreSQL → SQLite）

```bash
bash scripts/update_sqlite_from_docker.sh
```

#### Numbers4当選結果CSVの取り込み（任意）

```bash
bash scripts/import_numbers4_draws_csv.sh /path/to/numbers4_draws.csv
```

#### ローカルPostgreSQLを使用する場合

DATABASE_URLを適切に設定してください。

### 6. Prismaのセットアップ

```bash
# Prismaクライアントを生成
pnpm db:generate

# データベースにスキーマをプッシュ
pnpm db:push
```

### 7. TypeSpec → OpenAPI → Orval の生成

```bash
# API定義からクライアントコードを生成
pnpm api:generate
```

このコマンドは以下を実行します：
1. TypeSpec (`packages/api-spec/main.tsp`) → OpenAPI YAML
2. OpenAPI YAML → TanStack Query + Axios クライアント (`packages/api-client/src/generated`)

### 8. 開発サーバーの起動

```bash
# すべてのアプリを並行起動
pnpm dev
```

または個別に起動：

```bash
# 管理画面のみ
cd apps/admin-web
pnpm dev

# モバイルアプリのみ
cd apps/mobile
pnpm dev
```

### 9. アクセス確認

- **管理画面**: http://localhost:3001
- **モバイルアプリ**: Expoアプリで表示されるQRコードをスキャン

## トラブルシューティング

### エラー: `Cannot find module '@million-pocket/database'`

```bash
# Prismaクライアントを再生成
pnpm db:generate
```

### エラー: `tsp: command not found`

```bash
# TypeSpec CLIをインストール
cd packages/api-spec
pnpm install
```

### エラー: `Failed to connect to database`

- PostgreSQLが起動しているか確認
- DATABASE_URLが正しいか確認
- `docker-compose ps` でコンテナの状態を確認

### エラー: `Expo Metro bundler error`

```bash
# キャッシュをクリア
cd apps/mobile
npx expo start --clear
```

### Turboキャッシュをクリア

```bash
pnpm turbo clean
```

## 既存のPython環境との共存

Python仮想環境は既存のまま使用できます：

```bash
# Python環境をアクティベート
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 既存の予測スクリプトを実行
python numbers4/predict_ensemble.py
```

データベースは共有されているため、PythonスクリプトとNode.jsアプリは同じデータにアクセスします。

## データベースのマイグレーション

既存の `prisma/schema.prisma` から新しい `packages/database/prisma/schema.prisma` に移行する場合：

```bash
# 既存のスキーマを確認
cat prisma/schema.prisma

# 新しいスキーマをプッシュ（既存データを保持）
cd packages/database
pnpm db:push

# または、マイグレーションを作成
pnpm db:migrate
```

## Next Steps

1. Supabase AuthでユーザーUIを実装
2. 管理画面でSupabase RLSポリシーを設定
3. モバイルアプリで実際のAPI連携を実装
4. 既存のPython予測データと新規投稿データの連携

## ディレクトリ構造の確認

```bash
# ツリー表示（Windowsの場合）
tree /F /A

# または
ls -R
```

期待される構造：

```
million-pocket/
├── apps/
│   ├── admin-web/
│   └── mobile/
├── packages/
│   ├── database/
│   ├── api-spec/
│   ├── api-client/
│   └── typescript-config/
├── numbers3/          # 既存Python
├── numbers4/          # 既存Python
├── loto6/             # 既存Python
└── ...
```

## 参考リンク

- [Turborepo Documentation](https://turbo.build/repo/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [Expo Documentation](https://docs.expo.dev/)
- [Prisma Documentation](https://www.prisma.io/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [TypeSpec Documentation](https://typespec.io/)
- [TanStack Query Documentation](https://tanstack.com/query)
