# 🚀 Million Pocket クイックスタート

## 最速で動かす（5分）

### 1. 依存関係のインストール

```bash
pnpm install
```

### 2. 環境変数の設定（最小限）

ルートディレクトリの `.env` を作成：

```env
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/millions?schema=public"

# Supabaseは後で設定可能
NEXT_PUBLIC_SUPABASE_URL="http://localhost:54321"
NEXT_PUBLIC_SUPABASE_ANON_KEY="dummy-key"
SUPABASE_SERVICE_ROLE_KEY="dummy-key"

NEXT_PUBLIC_API_URL="http://localhost:3001/api"
```

### 3. データベース起動

```bash
docker-compose up -d
```

### 4. データベースセットアップ

```bash
pnpm db:generate
pnpm db:push
```

### 5. 起動

```bash
pnpm dev
```

✅ 完了！

- 管理画面: http://localhost:3001
- モバイルアプリ: ターミナルに表示されるQRコード

## 次にやること

### Supabase Authを設定する

1. [Supabase](https://supabase.com) でプロジェクト作成
2. `.env` に正しい認証情報を設定
3. アプリを再起動

### 既存のPythonデータをインポート

```bash
source .venv/bin/activate
python import_lottery_data.py
```

### API定義を確認・変更

```bash
# TypeSpec定義を編集
code packages/api-spec/main.tsp

# 再生成
pnpm api:generate
```

### 管理画面にアクセス

1. http://localhost:3001 を開く
2. `/predictions` で投稿一覧
3. `/draws` で抽選結果登録

### モバイルアプリで確認

1. Expo Goアプリをインストール（iOS/Android）
2. QRコードをスキャン
3. ホーム画面で予測一覧を確認

## 既存機能も引き続き動作

```bash
# Python予測スクリプト
python numbers4/predict_ensemble.py

# Streamlitダッシュボード
streamlit run streamlit_app.py
```

## よくある質問

### Q: pnpmがない

```bash
npm install -g pnpm@9
```

### Q: Dockerが使えない

ローカルPostgreSQLを使用し、DATABASE_URLを設定してください。

### Q: TypeScriptエラーが出る

```bash
pnpm db:generate  # Prismaクライアント再生成
pnpm api:generate # APIクライアント再生成
```

### Q: Expoが起動しない

```bash
cd apps/mobile
npx expo start --clear  # キャッシュクリア
```

## トラブルシューティング

問題が起きたら：

1. `pnpm clean` で全キャッシュをクリア
2. `pnpm install` で再インストール
3. `SETUP.md` の詳細手順を確認

## ディレクトリ構成

```
apps/
  admin-web/     # Next.js管理画面 (ポート3001)
  mobile/        # Expo React Native

packages/
  database/      # Prisma (共有)
  api-spec/      # TypeSpec API定義
  api-client/    # 生成されたクライアント

numbers3/        # Python予測ロジック (既存)
numbers4/        # Python予測ロジック (既存)
loto6/           # Python予測ロジック (既存)
```

## さらに詳しく

- `README_NEW.md` - プロジェクト全体の説明
- `SETUP.md` - 詳細なセットアップガイド

---

質問や問題があれば、issueを立ててください！
