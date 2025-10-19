# Million Pocket API Specification (TypeSpec)

TypeSpecでスケーラブルに分割構成されたMillion Pocket APIの仕様定義です。

## 📁 ディレクトリ構成

```
packages/api-spec/
├── tsp/                          # TypeSpec定義（分割構成）
│   ├── main.tsp                 # エントリーポイント
│   ├── common/                  # 共通型定義
│   │   ├── types.tsp           # LotteryType, Paginationなど
│   │   └── errors.tsp          # ErrorResponse, NotFoundErrorなど
│   ├── models/                  # データモデル
│   │   ├── user.tsp            # User, UserAnalysis
│   │   ├── draw.tsp            # Draw
│   │   ├── prediction.tsp      # Prediction, PredictionPost
│   │   └── social.tsp          # Like, Comment
│   └── routes/                  # エンドポイント定義
│       ├── auth.tsp            # 認証
│       ├── draws.tsp           # 抽選情報
│       ├── predictions.tsp     # 予測投稿
│       └── users.tsp           # ユーザー
├── tsp-output/                  # TypeSpecコンパイル結果
│   └── openapi.generated.yaml  # 生成されたOpenAPI仕様
├── orval.config.ts              # orval設定
├── tspconfig.yaml               # TypeSpec設定
└── package.json
```

## 🎯 設計の特徴

### スケーラビリティ
- **明確なファイル分割**: common, models, routesで責務を分離
- **namespace活用**: 各機能をnamespaceで整理
- **型の再利用**: 共通型をcommon/で一元管理

### 型安全性
- **厳密な型定義**: TypeSpecの型システムを最大限活用
- **union型対応**: `PredictionNumbers`は配列と文字列のunion
- **エラーハンドリング**: 統一されたErrorResponse型

### 保守性
- **ドキュメント埋め込み**: `@doc`デコレーターで説明を記載
- **タグ分類**: `@tag`でエンドポイントをグループ化
- **ステータスコード明示**: レスポンスのステータスコードを型で表現

## 🔧 開発ワークフロー

### 1. TypeSpec定義の編集

```bash
# VSCode拡張機能推奨
# TypeSpec for VS Code をインストール
```

### 2. OpenAPIの生成

```bash
cd packages/api-spec
pnpm run build
```

生成されたファイル: `tsp-output/openapi.generated.yaml`

### 3. クライアントコードの生成（customer-mobile向け）

```bash
pnpm run generate:mobile
```

生成されるファイル:
- `apps/customer-mobile/src/api/generated/endpoints.ts` - React Query hooks
- `apps/customer-mobile/src/api/generated/models/*` - 型定義

### 4. 自動watch（開発時）

```bash
pnpm run watch
```

TypeSpec定義を変更するたびに自動でOpenAPIを再生成します。

## 📱 customer-mobileでの使用方法

### 基本的な使用例

```typescript
// 抽選情報一覧の取得
import { useDrawsList } from '@/api/generated/endpoints';

function DrawsList() {
  const { data, isLoading } = useDrawsList({
    lotteryType: 'LOTO6',
    page: 1,
    limit: 20,
  });
  
  if (isLoading) return <div>Loading...</div>;
  
  return (
    <div>
      {data?.items.map((draw) => (
        <div key={draw.id}>{draw.drawNumber}回</div>
      ))}
    </div>
  );
}
```

### Mutation（予測投稿）

```typescript
import { usePredictionsCreate } from '@/api/generated/endpoints';

function PredictionForm() {
  const mutation = usePredictionsCreate();
  
  const handleSubmit = () => {
    mutation.mutate({
      data: {
        userId: 'user-id',
        drawId: 'draw-id',
        predictions: [
          { numbers: [1, 10, 22, 33, 40, 41] }, // LOTO6形式
        ],
      },
    });
  };
  
  return (
    <button onClick={handleSubmit} disabled={mutation.isPending}>
      {mutation.isPending ? '投稿中...' : '予測を投稿'}
    </button>
  );
}
```

### 型の利用

```typescript
// 生成された型をimport
import type { Draw, PredictionPost, User } from '@/api/generated/models';

const draw: Draw = {
  id: 'draw-1',
  lotteryType: 'LOTO6',
  drawNumber: 1850,
  drawDate: new Date().toISOString(),
};
```

## ✏️ TypeSpec定義の編集方法

### 新しいエンドポイントの追加

1. 該当するroutes/配下のファイルを編集
2. 必要に応じてmodels/に新しい型を追加
3. `pnpm run build`でOpenAPIを生成
4. `pnpm run generate:mobile`でクライアントを生成

### 例: 新しいエンドポイント追加

```typescript
// tsp/routes/draws.tsp に追加
@doc("特定ユーザーの予測履歴を含む抽選情報取得")
@get
@route("/{drawId}/with-predictions")
op getWithPredictions(
  @path drawId: string,
  @query userId?: string,
): {
  draw: Draw;
  predictions: PredictionPost[];
} | NotFoundError;
```

### 例: 新しいモデル追加

```typescript
// tsp/models/notification.tsp を新規作成
import "@typespec/http";

using TypeSpec.Http;

namespace MillionPocketAPI;

@doc("通知")
model Notification {
  @doc("通知ID")
  id: string;
  
  @doc("ユーザーID")
  userId: string;
  
  @doc("通知内容")
  message: string;
  
  @doc("既読フラグ")
  isRead: boolean;
  
  @doc("作成日時")
  createdAt: utcDateTime;
}
```

## 🔍 トラブルシューティング

### TypeSpecコンパイルエラー

```bash
# エラー詳細を確認
pnpm run build
```

よくあるエラー:
- `import-first`: importはnamespace宣言の前に置く
- `unknown-decorator`: デコレーターのtypoや未importチェック

### orval生成エラー

```bash
# OpenAPIファイルが存在するか確認
ls tsp-output/openapi.generated.yaml

# orval設定を確認
cat orval.config.ts
```

### クライアントコードが更新されない

```bash
# キャッシュをクリアして再生成
rm -rf apps/customer-mobile/src/api/generated
pnpm run generate:mobile
```

## 📚 参考リンク

- [TypeSpec公式ドキュメント](https://typespec.io/)
- [TypeSpec HTTP仕様](https://typespec.io/docs/libraries/http/)
- [orval公式ドキュメント](https://orval.dev/)
- [React Query](https://tanstack.com/query/latest)

## 🚀 次のステップ

1. **認証の実装**: Bearer JWT認証をTypeSpecで定義
2. **バリデーション強化**: より厳密な型制約の追加
3. **CI/CD統合**: 仕様変更時の自動テスト・生成
4. **モック生成**: `orval`のmock機能を有効化してテスト用データ生成
