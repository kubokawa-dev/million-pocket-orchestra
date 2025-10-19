# Million Pocket API Client

このディレクトリには、Million Pocket APIとの通信に必要なクライアントコードが含まれています。

## 📁 ファイル構成

```
api/
├── axios-instance.ts     # Axiosインスタンス（手動管理）
├── generated/            # orvalで自動生成（編集不可）
│   ├── endpoints.ts     # React Query hooks（tag別に分割）
│   └── models/          # TypeScript型定義
├── README.md            # このファイル
```

## ⚠️ 重要

- **`generated/`配下のファイルは自動生成されます。直接編集しないでください。**
- **`axios-instance.ts`は手動管理ファイルです。**

## 🔄 再生成方法

API仕様（TypeSpec）が変更された場合：

```bash
# 1. packages/api-specでTypeSpecをコンパイル
cd packages/api-spec
pnpm run build

# 2. orvalでクライアントコードを再生成
pnpm run generate:mobile
```

これにより、`api/generated/`配下のファイルが最新のAPI仕様に基づいて再生成されます。

## 💡 使用例

### Query（データ取得）

```typescript
import { useDrawsList, useDrawsGet } from '@/api/generated/endpoints';

function DrawsList() {
  const { data, isLoading, error } = useDrawsList({
    lotteryType: 'LOTO6',
    page: 1,
    limit: 20,
  });
  
  if (isLoading) return <Text>Loading...</Text>;
  if (error) return <Text>Error: {error.message}</Text>;
  
  return (
    <FlatList
      data={data?.items}
      renderItem={({ item }) => (
        <Text>第{item.drawNumber}回 - {item.lotteryType}</Text>
      )}
    />
  );
}
```

### Mutation（データ更新）

```typescript
import { usePredictionsCreate } from '@/api/generated/endpoints';
import { useQueryClient } from '@tanstack/react-query';

function PredictionForm() {
  const queryClient = useQueryClient();
  const mutation = usePredictionsCreate();
  
  const handleSubmit = async (numbers: number[]) => {
    try {
      await mutation.mutateAsync({
        data: {
          userId: 'user-id', // 将来は認証トークンから取得
          drawId: 'draw-id',
          predictions: [{ numbers }],
        },
      });
      
      // 成功時にキャッシュを無効化
      queryClient.invalidateQueries({ queryKey: ['/predictions'] });
      
      alert('予測を投稿しました！');
    } catch (error) {
      console.error('投稿エラー:', error);
    }
  };
  
  return (
    <Button
      onPress={() => handleSubmit([1, 10, 22, 33, 40, 41])}
      disabled={mutation.isPending}
    >
      {mutation.isPending ? '投稿中...' : '予測を投稿'}
    </Button>
  );
}
```

### 型の活用

```typescript
import type { 
  Draw, 
  PredictionPost, 
  User,
  LotteryType 
} from '@/api/generated/models';

// 型安全な関数
function formatDraw(draw: Draw): string {
  return `第${draw.drawNumber}回 ${draw.lotteryType}`;
}

// 列挙型の使用
const lotteryTypes: LotteryType[] = ['LOTO6', 'NUMBERS3', 'NUMBERS4'];
```

## 🔐 認証トークンの設定

`axios-instance.ts`でリクエストインターセプターを設定し、認証トークンを自動付与できます：

```typescript
// axios-instance.ts に追加
AXIOS_INSTANCE.interceptors.request.use((config) => {
  // AsyncStorageや状態管理から取得
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

## 📊 利用可能なエンドポイント

### 認証
- `useAuthSignup` - 新規登録
- `useAuthLogin` - ログイン

### 抽選情報
- `useDrawsList` - 一覧取得
- `useDrawsUpcoming` - 開催予定取得
- `useDrawsGet` - 詳細取得

### 予測投稿
- `usePredictionsList` - 一覧取得
- `usePredictionsCreate` - 新規投稿
- `usePredictionsGet` - 詳細取得
- `usePredictionsLike` - いいね
- `usePredictionsUnlike` - いいね取り消し
- `usePredictionsCreateComment` - コメント投稿

### ユーザー
- `useUsersGetProfile` - プロフィール取得
- `useUsersGetPredictions` - 投稿履歴取得
- `useUsersGetAnalysis` - 成績分析取得

## 🛠️ カスタマイズ

### ベースURLの変更

環境変数でAPIのURLを切り替え可能です：

```typescript
// axios-instance.ts
const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';
```

### タイムアウトの設定

```typescript
// axios-instance.ts
export const AXIOS_INSTANCE = Axios.create({ 
  baseURL: API_URL,
  timeout: 10000, // 10秒
});
```

### エラーハンドリング

```typescript
// axios-instance.ts
AXIOS_INSTANCE.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 認証エラー時の処理
      // 例: ログアウトして認証画面にリダイレクト
    }
    return Promise.reject(error);
  }
);
```

## 📚 参考リンク

- [orval公式ドキュメント](https://orval.dev/)
- [React Query公式ドキュメント](https://tanstack.com/query/latest)
- [Axios公式ドキュメント](https://axios-http.com/)
- [TypeSpec（API定義）](../../packages/api-spec/README.TypeSpec.md)
