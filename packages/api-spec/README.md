# Million Pocket API Specification

Million Pocket宝くじ予測アプリのOpenAPI 3.1仕様です。

## 📁 ディレクトリ構成

```
packages/api-spec/
├── openapi.yaml              # ルート仕様ファイル
├── components/
│   └── schemas/             # 再利用可能なスキーマ定義
│       ├── User.yaml
│       ├── Draw.yaml
│       ├── PredictionPost.yaml
│       └── ...
└── paths/                   # エンドポイント定義（リソース別に分割）
    ├── auth/
    │   ├── signup.yaml
    │   └── login.yaml
    ├── draws/
    │   ├── index.yaml
    │   ├── upcoming.yaml
    │   └── detail.yaml
    ├── predictions/
    │   ├── index.yaml
    │   ├── detail.yaml
    │   ├── likes.yaml
    │   └── comments.yaml
    └── users/
        ├── profile.yaml
        ├── predictions.yaml
        └── analysis.yaml
```

## 🎯 設計ポイント

### スケーラビリティ
- **ファイル分割**: リソース単位でpathsを分割し、保守性を向上
- **スキーマ共通化**: `components/schemas/`で型定義を再利用
- **共通パラメータ**: ページネーション等をrootで定義し参照

### 柔軟な型定義
- **`Prediction.numbers`**: LOTO6（配列）とNUMBERS3/4（文字列）両対応の`oneOf`
- **`LotteryType` enum**: 宝くじ種類を集中管理
- **`Pagination`**: 標準的なページネーション形式

## 🔧 開発ツール

### Lint & Bundle

```bash
# 仕様の検証
pnpm dlx @redocly/cli lint packages/api-spec/openapi.yaml

# 1ファイルにバンドル
pnpm dlx @redocly/cli bundle packages/api-spec/openapi.yaml -o packages/api-spec/bundle.yaml
```

### プレビュー

```bash
# ブラウザでドキュメントをプレビュー
pnpm dlx @redocly/cli preview-docs packages/api-spec/openapi.yaml
```

## 📱 クライアント生成（customer-mobile向け）

### 方法1: openapi-typescript（型定義のみ・軽量）

TypeScriptの型定義のみを生成します。軽量で導入が容易です。

```bash
# 型定義を生成
pnpm dlx openapi-typescript packages/api-spec/openapi.yaml \
  -o apps/customer-mobile/src/api/types.gen.ts
```

#### 使用例

```typescript
// apps/customer-mobile/src/api/types.gen.ts が生成される
import type { components, paths } from './api/types.gen';

type User = components['schemas']['User'];
type GetDrawsResponse = paths['/draws']['get']['responses']['200']['content']['application/json'];
```

### 方法2: orval（型定義 + fetcher生成・DX重視）

型定義に加えて、React Query対応のfetcherコードも自動生成します。

#### 1. 設定ファイル作成

`apps/customer-mobile/orval.config.ts`:

```typescript
import { defineConfig } from 'orval';

export default defineConfig({
  millionPocket: {
    input: '../../packages/api-spec/openapi.yaml',
    output: {
      mode: 'tags-split',
      target: 'src/api/client.ts',
      schemas: 'src/api/model',
      client: 'react-query',
      mock: false,
      override: {
        mutator: {
          path: './src/api/axios-instance.ts',
          name: 'customInstance',
        },
      },
    },
  },
});
```

#### 2. カスタムAxiosインスタンス作成

`apps/customer-mobile/src/api/axios-instance.ts`:

```typescript
import Axios, { AxiosRequestConfig } from 'axios';

export const AXIOS_INSTANCE = Axios.create({
  baseURL: 'http://localhost:8787',
});

// 認証トークンをヘッダーに自動付与する例
AXIOS_INSTANCE.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const customInstance = <T>(config: AxiosRequestConfig): Promise<T> => {
  return AXIOS_INSTANCE(config).then(({ data }) => data);
};
```

#### 3. クライアント生成

```bash
# orvalでコード生成
pnpm dlx orval --config apps/customer-mobile/orval.config.ts
```

#### 4. 使用例（React Query）

```typescript
import { useGetDraws, useCreatePredictionPost } from './api/client';

function DrawsList() {
  const { data, isLoading } = useGetDraws({ lotteryType: 'LOTO6', page: 1, limit: 20 });
  
  if (isLoading) return <div>Loading...</div>;
  
  return (
    <div>
      {data?.items.map((draw) => (
        <div key={draw.id}>{draw.drawNumber}回</div>
      ))}
    </div>
  );
}

function PredictionForm() {
  const mutation = useCreatePredictionPost();
  
  const handleSubmit = () => {
    mutation.mutate({
      userId: 'user-id',
      drawId: 'draw-id',
      predictions: [{ numbers: [1, 10, 22, 33, 40, 41] }],
    });
  };
  
  return <button onClick={handleSubmit}>予測投稿</button>;
}
```

## 🔐 認証について

現在の実装では`userId`をリクエストボディで受け取っていますが、将来的には以下の対応を推奨します：

1. **Bearer JWT認証**: `Authorization: Bearer <token>`ヘッダーでトークンを送信
2. **サーバー側でトークン検証**: `userId`をトークンから抽出
3. **仕様の更新**: 各エンドポイントに`security: [{ bearerAuth: [] }]`を追加

## 📊 エンドポイント概要

### 認証 (`/auth`)
- `POST /auth/signup` - 新規ユーザー登録
- `POST /auth/login` - ログイン

### 抽選情報 (`/draws`)
- `GET /draws` - 一覧取得（ページネーション）
- `GET /draws/upcoming` - 開催予定取得
- `GET /draws/{drawId}` - 詳細取得

### 予測投稿 (`/predictions`)
- `GET /predictions` - 一覧取得（フィルタ・ページネーション）
- `POST /predictions` - 新規投稿
- `GET /predictions/{postId}` - 詳細取得
- `POST /predictions/{postId}/likes` - いいね
- `DELETE /predictions/{postId}/likes` - いいね取り消し
- `POST /predictions/{postId}/comments` - コメント投稿

### ユーザー (`/users`)
- `GET /users/{userId}` - プロフィール取得
- `GET /users/{userId}/predictions` - 予測投稿履歴
- `GET /users/{userId}/analysis` - 予測成績分析

## 🚀 次のステップ

1. **型生成の実行**: 上記コマンドでクライアントコードを生成
2. **API実装との同期**: サーバー側の実装変更時に仕様を更新
3. **認証の実装**: Bearer JWT認証への移行
4. **バリデーション強化**: より厳密な型制約の追加
5. **CI/CD統合**: 仕様変更時の自動テスト・クライアント再生成

## 📝 メンテナンス

仕様を更新した場合は、必ずlintを実行し、クライアントコードを再生成してください：

```bash
# 1. 仕様を検証
pnpm dlx @redocly/cli lint packages/api-spec/openapi.yaml

# 2. クライアントを再生成
pnpm dlx orval --config apps/customer-mobile/orval.config.ts
```
