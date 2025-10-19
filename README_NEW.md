# Million Pocket - 予測投稿アプリ

宝くじ（Numbers3/4, Loto6）の予測を投稿・共有するモバイルアプリと管理画面のモノレポプロジェクト。

## 🎯 プロジェクト概要

- **ユーザー向けアプリ (Expo/React Native)**: 予測投稿、一覧表示、いいね、コメント機能
- **管理画面 (Next.js)**: 投稿一覧、フラグ確認、非表示切替、抽選結果の登録
- **Python予測エンジン**: 機械学習モデルによる番号予測（既存コード保持）

## 📁 プロジェクト構造

```
million-pocket/
├── apps/
│   ├── admin-web/          # Next.js管理画面
│   │   ├── src/
│   │   │   ├── app/        # App Router
│   │   │   │   ├── api/    # REST API エンドポイント
│   │   │   │   ├── page.tsx
│   │   │   │   └── layout.tsx
│   │   │   └── lib/        # Supabase設定
│   │   ├── package.json
│   │   └── next.config.js
│   └── mobile/             # Expo React Nativeアプリ
│       ├── app/            # Expo Router
│       │   ├── (tabs)/     # タブナビゲーション
│       │   └── _layout.tsx
│       ├── package.json
│       └── app.json
├── packages/
│   ├── database/           # Prisma共有パッケージ
│   │   ├── prisma/
│   │   │   └── schema.prisma
│   │   └── src/index.ts
│   ├── api-spec/           # TypeSpec API定義
│   │   ├── main.tsp
│   │   └── tspconfig.yaml
│   ├── api-client/         # Orval生成クライアント
│   │   ├── src/
│   │   └── orval.config.ts
│   └── typescript-config/  # 共有TypeScript設定
├── numbers3/               # Python予測ロジック（既存）
├── numbers4/               # Python予測ロジック（既存）
├── loto6/                  # Python予測ロジック（既存）
├── prisma/                 # 既存Prismaスキーマ（移行予定）
├── turbo.json
├── pnpm-workspace.yaml
└── package.json
```

## 🚀 セットアップ

### 前提条件

- Node.js 20以上
- pnpm 9以上
- Python 3.10以上
- PostgreSQL（Dockerまたはローカル）
- Supabase プロジェクト

### 1. 依存関係のインストール

```bash
# pnpmを使用（推奨）
pnpm install

# または npm
npm install
```

### 2. 環境変数の設定

```bash
# ルートディレクトリ
cp .env.example .env

# 管理画面
cp apps/admin-web/.env.example apps/admin-web/.env.local

# モバイルアプリ
cp apps/mobile/.env.example apps/mobile/.env
```

各ファイルに以下を設定：

- `DATABASE_URL`: PostgreSQL接続文字列
- `NEXT_PUBLIC_SUPABASE_URL`: SupabaseプロジェクトURL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Supabase Anon Key
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase Service Role Key

### 3. データベースのセットアップ

```bash
# PostgreSQLを起動（Docker）
docker-compose up -d

# Prisma クライアント生成
pnpm db:generate

# データベースにスキーマをプッシュ
pnpm db:push
```

### 4. TypeSpec → OpenAPI → Orval の生成

```bash
# API定義からクライアントコードを生成
pnpm api:generate
```

## 🏃 開発サーバーの起動

### すべてのアプリを起動

```bash
pnpm dev
```

### 個別に起動

```bash
# 管理画面（ポート3001）
cd apps/admin-web
pnpm dev

# モバイルアプリ
cd apps/mobile
pnpm dev
```

### Python予測スクリプト（既存機能）

```bash
# Python環境をアクティベート
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Numbers4予測を実行
python numbers4/predict_ensemble.py
```

## 📱 アプリケーション

### ユーザーアプリ (Mobile)

- **ホーム画面**: 予測一覧（フィルタリング可）
- **予測投稿**: 番号入力、理由・根拠の記載
- **予測詳細**: いいね、コメント機能
- **プロフィール**: 自分の予測履歴、統計

### 管理画面 (Admin Web)

- **投稿一覧**: すべての予測を表示
- **フラグ確認**: 報告された投稿の管理
- **非表示切替**: 不適切な投稿を非表示
- **抽選結果登録**: Numbers3/4、Loto6の結果を手動登録

## 🛠️ 技術スタック

### フロントエンド

- **モバイル**: Expo (React Native), Expo Router, NativeWind (Tailwind CSS)
- **管理画面**: Next.js 15 (App Router), TailwindCSS, Lucide Icons

### バックエンド

- **API**: Next.js API Routes（将来 Supabase Edge Functions に移行可能）
- **データベース**: PostgreSQL (Supabase)
- **ORM**: Prisma
- **認証**: Supabase Auth (RLS対応)

### API開発

- **定義**: TypeSpec
- **生成**: OpenAPI 3.0 → Orval
- **クライアント**: TanStack Query (React Query) + Axios

### Python予測エンジン

- **機械学習**: scikit-learn, pandas, numpy
- **可視化**: Streamlit（既存）

### モノレポ管理

- **ビルドツール**: Turborepo
- **パッケージマネージャー**: pnpm (workspaces)

## 🔐 認証とセキュリティ

- Supabase Authによるユーザー認証
- Row Level Security (RLS) でデータアクセス制御
- APIエンドポイントで認証チェック
- 管理者ロールによる権限分離（TODO実装予定）

## 🗄️ データベーススキーマ

主要なテーブル：

- `users`: ユーザー情報（Supabase Auth連携）
- `predictions`: 予測投稿
- `likes`: いいね
- `comments`: コメント
- `numbers3_draws`, `numbers4_draws`, `loto6_draws`: 抽選結果（Python連携）

既存のML関連テーブルも保持：
- `*_model_events`, `*_predictions_log`, `*_ensemble_predictions` など

## 📊 API エンドポイント

### ユーザー向け

- `GET /api/predictions` - 予測一覧取得
- `POST /api/predictions` - 予測投稿
- `GET /api/predictions/:id` - 予測詳細
- `POST /api/predictions/:id/like` - いいね
- `GET /api/predictions/:id/comments` - コメント一覧
- `POST /api/predictions/:id/comments` - コメント投稿

### 管理者向け

- `GET /api/admin/predictions` - 全投稿一覧
- `PATCH /api/admin/predictions/:id/hide` - 投稿を非表示
- `PATCH /api/admin/predictions/:id/unhide` - 投稿を再表示
- `PATCH /api/admin/predictions/:id/result` - 結果を更新
- `POST /api/admin/draws/numbers3` - Numbers3結果登録
- `POST /api/admin/draws/numbers4` - Numbers4結果登録
- `POST /api/admin/draws/loto6` - Loto6結果登録

## 🔧 開発コマンド

```bash
# すべてのアプリを開発モードで起動
pnpm dev

# ビルド
pnpm build

# 型チェック
pnpm type-check

# Linter実行
pnpm lint

# Prismaスタジオ起動
pnpm db:studio

# API定義から再生成
pnpm api:generate
```

## 🐍 Python予測エンジンの使用

既存のPython予測ロジックは完全に保持されています：

```bash
# Numbers4の予測を実行
python numbers4/predict_ensemble.py

# 予測履歴の管理
python numbers4/manage_prediction_history.py list
python numbers4/manage_prediction_history.py update <ID> <当選番号>

# Streamlitダッシュボード起動
streamlit run streamlit_app.py
```

## 🚢 デプロイ

### Vercel（推奨）

```bash
# 管理画面をデプロイ
cd apps/admin-web
vercel
```

### モバイルアプリ

```bash
# Expo EASでビルド
cd apps/mobile
eas build --platform android
eas build --platform ios
```

## 🤝 コントリビューション

1. 機能追加は新しいブランチで作業
2. コミット前に `pnpm type-check` と `pnpm lint` を実行
3. API変更時は TypeSpec を更新し `pnpm api:generate` を実行

## 📝 TODO

- [ ] Supabase RLS ポリシーの設定
- [ ] 管理者ロール判定の実装
- [ ] 画像アップロード機能（アバター、予測画像）
- [ ] プッシュ通知（抽選結果、いいね、コメント）
- [ ] Supabase Edge Functions への移行検討
- [ ] E2Eテスト（Playwright, Detox）
- [ ] CI/CD パイプライン（GitHub Actions）

## 📄 ライセンス

MIT License

---

**既存のPython予測機能について**: 
このプロジェクトは既存のPython機械学習モデルと予測ロジックを完全に保持しています。
`numbers3/`, `numbers4/`, `loto6/` ディレクトリ内のすべてのPythonコードは引き続き使用可能です。
