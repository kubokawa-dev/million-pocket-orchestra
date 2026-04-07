# 宝くじAI プロジェクト構造

## 📦 モノレポ構成

```
million-pocket/
├── 📱 apps/                          # アプリケーション
│   ├── admin-web/                    # Next.js 管理画面
│   │   ├── src/
│   │   │   ├── app/                  # App Router
│   │   │   │   ├── api/              # RESTful API エンドポイント
│   │   │   │   │   ├── predictions/      # 予測CRUD
│   │   │   │   │   │   ├── route.ts      # GET, POST
│   │   │   │   │   │   └── [id]/
│   │   │   │   │   │       ├── route.ts  # GET, PATCH, DELETE
│   │   │   │   │   │       ├── like/     # いいね
│   │   │   │   │   │       └── comments/ # コメント
│   │   │   │   │   └── admin/            # 管理者専用API
│   │   │   │   │       ├── predictions/  # 非表示切替、結果登録
│   │   │   │   │       └── draws/        # 抽選結果登録
│   │   │   │   ├── page.tsx         # ホーム
│   │   │   │   ├── layout.tsx       # ルートレイアウト
│   │   │   │   └── globals.css      # Tailwind CSS
│   │   │   └── lib/
│   │   │       ├── supabase.ts       # Supabase クライアント
│   │   │       └── auth.ts           # 認証ヘルパー
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── next.config.js
│   │   └── tailwind.config.js
│   │
│   └── mobile/                       # Expo React Native ユーザーアプリ
│       ├── app/                      # Expo Router
│       │   ├── _layout.tsx           # ルートレイアウト
│       │   └── (tabs)/               # タブナビゲーション
│       │       ├── _layout.tsx
│       │       ├── index.tsx         # ホーム（予測一覧）
│       │       ├── create.tsx        # 予測投稿
│       │       └── profile.tsx       # プロフィール
│       ├── package.json
│       ├── app.json                  # Expo設定
│       ├── tsconfig.json
│       ├── tailwind.config.js
│       ├── metro.config.js
│       └── global.css                # NativeWind
│
├── 📚 packages/                      # 共有パッケージ
│   ├── database/                     # Prisma Database Package
│   │   ├── prisma/
│   │   │   └── schema.prisma         # 統合スキーマ
│   │   ├── src/
│   │   │   └── index.ts              # Prisma Client エクスポート
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── api-spec/                     # TypeSpec API定義
│   │   ├── main.tsp                  # API仕様 (TypeSpec)
│   │   ├── tspconfig.yaml
│   │   └── package.json
│   │
│   ├── api-client/                   # 生成されたAPIクライアント
│   │   ├── src/
│   │   │   ├── generated/            # Orvalが生成 (Git無視)
│   │   │   ├── axios-instance.ts     # Axiosカスタムインスタンス
│   │   │   └── index.ts
│   │   ├── orval.config.ts           # Orval設定
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── typescript-config/            # 共有TypeScript設定
│       ├── base.json                 # ベース設定
│       ├── nextjs.json               # Next.js用
│       ├── react-native.json         # React Native用
│       └── package.json
│
├── 🐍 Python予測エンジン (既存コード - 保持)
│   ├── numbers3/
│   │   ├── predict_ensemble.py       # Numbers3予測
│   │   ├── manage_prediction_history.py
│   │   └── ...
│   ├── numbers4/
│   │   ├── predict_ensemble.py       # Numbers4予測
│   │   ├── manage_prediction_history.py
│   │   └── ...
│   ├── loto6/
│   │   ├── predict_ensemble.py       # Loto6予測
│   │   ├── manage_prediction_history.py
│   │   └── ...
│   ├── tools/                        # ユーティリティ
│   ├── scripts/                      # マイグレーション等
│   └── streamlit_app.py              # Streamlit UI
│
├── ⚙️ 設定ファイル
│   ├── turbo.json                    # Turborepo設定
│   ├── pnpm-workspace.yaml           # pnpm workspaces
│   ├── package.json                  # ルートpackage.json
│   ├── .npmrc                        # pnpm設定
│   ├── docker-compose.yml            # PostgreSQL
│   ├── .gitignore
│   ├── .env.example
│   └── mise.toml                     # 開発環境管理
│
└── 📖 ドキュメント
    ├── README_NEW.md                 # 新プロジェクトREADME
    ├── README.md                     # 既存Python README (保持)
    ├── SETUP.md                      # 詳細セットアップガイド
    ├── QUICKSTART.md                 # クイックスタート
    └── PROJECT_STRUCTURE.md          # このファイル
```

## 🔧 技術スタック

### フロントエンド

| 領域 | 技術 |
|------|------|
| モバイルアプリ | Expo, React Native, Expo Router |
| スタイリング | NativeWind (Tailwind CSS for RN) |
| 管理画面 | Next.js 15 (App Router) |
| スタイリング | TailwindCSS |
| アイコン | Lucide React / Lucide React Native |

### バックエンド

| 領域 | 技術 |
|------|------|
| API | Next.js API Routes (REST) |
| データベース | PostgreSQL (Supabase) |
| ORM | Prisma |
| 認証 | Supabase Auth |
| セキュリティ | Row Level Security (RLS) |

### API開発

| 領域 | 技術 |
|------|------|
| API定義 | TypeSpec |
| OpenAPI生成 | @typespec/openapi3 |
| クライアント生成 | Orval |
| 状態管理 | TanStack Query (React Query) |
| HTTP クライアント | Axios |

### Python予測エンジン

| 領域 | 技術 |
|------|------|
| 機械学習 | scikit-learn |
| データ処理 | pandas, numpy |
| 可視化 | Streamlit |
| スクレイピング | requests, BeautifulSoup |

### 開発ツール

| 領域 | 技術 |
|------|------|
| モノレポ管理 | Turborepo |
| パッケージマネージャー | pnpm (workspaces) |
| 型チェック | TypeScript 5.6 |
| Linter | ESLint |
| コンテナ | Docker, Docker Compose |

## 🔄 開発フロー

### API変更フロー

1. `packages/api-spec/main.tsp` を編集
2. `pnpm api:generate` で生成
3. 型安全なクライアントコードが自動生成
4. Next.js API Routes で実装
5. モバイル/Webアプリで使用

### データベース変更フロー

1. `packages/database/prisma/schema.prisma` を編集
2. `pnpm db:generate` でクライアント生成
3. `pnpm db:push` でスキーマをプッシュ
   または `pnpm db:migrate` でマイグレーション作成

### Python予測との連携

- Python → DB: 既存スクリプトがPostgreSQLに直接書き込み
- API → DB: Prisma経由でアクセス
- 同じデータベースを共有

## 📊 データフロー

```
┌─────────────────┐
│  Mobile App     │
│  (Expo)         │
└────────┬────────┘
         │ REST API
         │ (TanStack Query)
         ▼
┌─────────────────┐      ┌──────────────┐
│  Admin Web      │      │  Supabase    │
│  (Next.js)      │◄────►│  Auth        │
└────────┬────────┘      └──────────────┘
         │
         │ API Routes
         ▼
┌─────────────────┐
│  Prisma ORM     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  PostgreSQL     │◄────►│  Python      │
│  (Supabase)     │      │  Scripts     │
└─────────────────┘      └──────────────┘
```

## 🚀 デプロイ構成

### 推奨デプロイ先

- **管理画面**: Vercel
- **モバイルアプリ**: Expo EAS (App Store / Google Play)
- **データベース**: Supabase (PostgreSQL + Auth + Storage)
- **API**: Next.js API Routes → 将来的に Supabase Edge Functions

### 環境変数

各環境で設定が必要：

- `DATABASE_URL`: PostgreSQL接続文字列
- `NEXT_PUBLIC_SUPABASE_URL`: Supabaseプロジェクト URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: 匿名キー
- `SUPABASE_SERVICE_ROLE_KEY`: サービスロールキー
- `NEXT_PUBLIC_API_URL`: APIベースURL

## 📝 主要機能

### ユーザー機能 (Mobile)

- ✅ 予測一覧表示（フィルタリング）
- ✅ 予測投稿（Numbers3/4, Loto6）
- ✅ いいね機能
- ✅ コメント機能
- ✅ プロフィール表示

### 管理機能 (Admin Web)

- ✅ 全投稿一覧
- ✅ 投稿の非表示/再表示
- ✅ フラグ管理
- ✅ 抽選結果の手動登録
- ✅ 予測結果の更新

### Python予測機能（既存）

- ✅ Numbers3/4/Loto6 予測生成
- ✅ アンサンブル学習
- ✅ 予測履歴管理
- ✅ Streamlit可視化

## 🔐 セキュリティ

- Supabase Auth による認証
- Row Level Security (RLS) でデータ保護
- API エンドポイントで認証チェック
- 管理者ロールによる権限管理（TODO）

## 📦 パッケージ間の依存関係

```
apps/admin-web
  ├─ @million-pocket/database
  ├─ @million-pocket/api-client
  └─ @million-pocket/typescript-config

apps/mobile
  ├─ @million-pocket/api-client
  └─ @million-pocket/typescript-config

packages/api-client
  └─ packages/api-spec (ビルド時)

packages/database
  └─ prisma schema
```

## 🎯 Next Steps

1. **認証実装**: Supabase Auth UIの統合
2. **RLS設定**: Supabaseダッシュボードでポリシー設定
3. **画像アップロード**: アバター、予測画像
4. **プッシュ通知**: 抽選結果、いいね通知
5. **テスト**: E2E、Unit tests
6. **CI/CD**: GitHub Actions

## 📚 参考資料

- [Turborepo Docs](https://turbo.build/repo)
- [Prisma Docs](https://prisma.io/docs)
- [TypeSpec Docs](https://typespec.io/)
- [Supabase Docs](https://supabase.com/docs)
- [Expo Docs](https://docs.expo.dev/)
- [Next.js Docs](https://nextjs.org/docs)
