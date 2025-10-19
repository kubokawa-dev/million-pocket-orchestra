# Million Pocket API Client

このディレクトリには、Million Pocket APIとの通信に必要な型定義とクライアントコードが含まれています。

## 📁 ファイル構成

```
src/api/
├── types.gen.ts          # 自動生成された型定義（編集不可）
├── client.ts             # APIクライアントのラッパー（手動作成）
└── README.md             # このファイル
```

## 🔄 型定義の更新

API仕様が変更された場合、以下のコマンドで型定義を再生成してください：

```bash
cd packages/api-spec
pnpm run generate:mobile
```

## 💡 使用例

### 基本的な使用方法

```typescript
import type { components, paths } from './api/types.gen';

// スキーマの型を取得
type User = components['schemas']['User'];
type Draw = components['schemas']['Draw'];
type PredictionPost = components['schemas']['PredictionPost'];

// エンドポイントのレスポンス型を取得
type GetDrawsResponse = 
  paths['/draws']['get']['responses']['200']['content']['application/json'];

type CreatePredictionRequest =
  paths['/predictions']['post']['requestBody']['content']['application/json'];
```

### Fetch APIでの使用例

```typescript
import type { components } from './api/types.gen';

type Draw = components['schemas']['Draw'];
type PredictionPost = components['schemas']['PredictionPost'];

const API_BASE_URL = 'http://localhost:8787';

// 抽選情報一覧を取得
async function getDraws(lotteryType?: string): Promise<Draw[]> {
  const params = new URLSearchParams();
  if (lotteryType) params.append('lotteryType', lotteryType);
  
  const response = await fetch(`${API_BASE_URL}/draws?${params}`);
  const data = await response.json();
  return data.items;
}

// 予測を投稿
async function createPrediction(
  userId: string,
  drawId: string,
  numbers: number[]
): Promise<PredictionPost> {
  const response = await fetch(`${API_BASE_URL}/predictions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      userId,
      drawId,
      predictions: [{ numbers }],
    }),
  });
  return response.json();
}
```

### Axios + React Queryでの使用例（推奨）

まず、Axiosインスタンスを作成：

```typescript
// src/api/axios-instance.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: 'http://localhost:8787',
});

// 認証トークンを自動で付与
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

React Queryのカスタムフックを作成：

```typescript
// src/api/hooks/useDraws.ts
import { useQuery } from '@tanstack/react-query';
import type { components } from '../types.gen';
import { apiClient } from '../axios-instance';

type Draw = components['schemas']['Draw'];
type PaginationResponse<T> = {
  items: T[];
  total: number;
  page: number;
  limit: number;
};

export function useDraws(lotteryType?: string) {
  return useQuery({
    queryKey: ['draws', lotteryType],
    queryFn: async (): Promise<PaginationResponse<Draw>> => {
      const { data } = await apiClient.get('/draws', {
        params: { lotteryType, page: 1, limit: 20 },
      });
      return data;
    },
  });
}

// src/api/hooks/usePredictions.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { components } from '../types.gen';
import { apiClient } from '../axios-instance';

type PredictionPost = components['schemas']['PredictionPost'];

interface CreatePredictionParams {
  userId: string;
  drawId: string;
  predictions: Array<{ numbers: number[] | string }>;
}

export function useCreatePrediction() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (params: CreatePredictionParams): Promise<PredictionPost> => {
      const { data } = await apiClient.post('/predictions', params);
      return data;
    },
    onSuccess: () => {
      // キャッシュを無効化して再取得
      queryClient.invalidateQueries({ queryKey: ['predictions'] });
    },
  });
}
```

コンポーネントでの使用：

```typescript
// src/components/DrawsList.tsx
import { useDraws } from '../api/hooks/useDraws';

export function DrawsList() {
  const { data, isLoading, error } = useDraws('LOTO6');
  
  if (isLoading) return <div>読み込み中...</div>;
  if (error) return <div>エラーが発生しました</div>;
  
  return (
    <div>
      <h2>抽選一覧（全{data?.total}件）</h2>
      {data?.items.map((draw) => (
        <div key={draw.id}>
          <p>第{draw.drawNumber}回</p>
          <p>{draw.lotteryType}</p>
          <p>{new Date(draw.drawDate).toLocaleDateString()}</p>
        </div>
      ))}
    </div>
  );
}

// src/components/PredictionForm.tsx
import { useState } from 'react';
import { useCreatePrediction } from '../api/hooks/usePredictions';

export function PredictionForm({ userId, drawId }: { userId: string; drawId: string }) {
  const [numbers, setNumbers] = useState<number[]>([]);
  const mutation = useCreatePrediction();
  
  const handleSubmit = () => {
    mutation.mutate({
      userId,
      drawId,
      predictions: [{ numbers }],
    });
  };
  
  return (
    <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
      {/* 数字入力UI */}
      <button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? '投稿中...' : '予測を投稿'}
      </button>
      {mutation.isSuccess && <p>投稿しました！</p>}
      {mutation.isError && <p>エラーが発生しました</p>}
    </form>
  );
}
```

## 🔧 orvalでの完全自動生成（オプション）

より高度な自動生成が必要な場合は、orvalを使用してfetcherも含めて自動生成できます。

### 1. orval設定ファイルを作成

`apps/customer-mobile/orval.config.ts`:

```typescript
import { defineConfig } from 'orval';

export default defineConfig({
  millionPocket: {
    input: '../../packages/api-spec/openapi.yaml',
    output: {
      mode: 'tags-split',
      target: 'src/api/generated',
      client: 'react-query',
      override: {
        mutator: {
          path: './src/api/axios-instance.ts',
          name: 'apiClient',
        },
      },
    },
  },
});
```

### 2. 生成実行

```bash
cd apps/customer-mobile
pnpm dlx orval --config orval.config.ts
```

これにより、`src/api/generated/`に完全な型定義とReact Queryフックが生成されます。

## 📚 参考リンク

- [openapi-typescript](https://github.com/drwpow/openapi-typescript)
- [orval](https://orval.dev/)
- [React Query](https://tanstack.com/query/latest)
- [Axios](https://axios-http.com/)
