# Changelog - Million Pocket API Spec

## 2025-10-19

### ドキュメント充実化

- ✅ **TypeSpec全体に詳細な`@doc`ドキュメントを追加**
  - すべてのモデル（User, Draw, Prediction, Like, Commentなど）
  - すべてのプロパティに詳細な説明
  - エンドポイントにレスポンスコード説明を追加
  - 列挙型（LotteryType）に各値の説明を追加

### ドキュメント化された内容

#### モデル
- **User**: ユーザー情報、Supabase認証との連携説明
- **Draw**: 抽選情報、回号・当選番号の形式説明
- **PredictionPost**: 予測投稿、最大5つの予測を含む仕様
- **Prediction**: 個別予測、宝くじ種類による数字形式の違い
- **Like**: いいね機能、1ユーザー1投稿1回の制約
- **Comment**: コメント機能、文字数制限（1〜500文字）
- **UserAnalysis**: 予測成績分析、的中率計算方法
- **LotteryType**: 6種類の宝くじ、それぞれの数字形式

#### エンドポイント
- **POST /auth/signup**: 新規登録、レスポンスコード説明（201, 400）
- **POST /auth/login**: ログイン、認証エラー説明（200, 401）
- **GET /draws**: 抽選一覧、ページネーションパラメータ説明
- **GET /predictions**: 予測一覧、フィルタパラメータ詳細
- **POST /predictions**: 予測投稿、数字形式のバリデーション
- **POST /predictions/{postId}/likes**: いいね、重複防止
- **GET /users/{userId}/analysis**: 成績分析、計算ロジック説明

### 生成物の更新

- **OpenAPI 3.1**: `tsp-output/openapi.generated.yaml` に詳細な説明が反映
- **クライアントコード**: `apps/customer-mobile/api/generated/` に型定義とReact Query hooksが再生成

### ドキュメント形式

TypeSpecの三重引用符（`"""`）を使用した複数行ドキュメントにより、
以下の情報を記載：

- 概要説明
- 使用例
- 制約事項
- 関連情報
- 注意事項

### RedocやSwagger UIでの表示

生成されたOpenAPIファイルをRedocやSwagger UIで表示すると、
すべてのドキュメントが適切にレンダリングされます。

```bash
# ブラウザでプレビュー
pnpm run preview
```

これにより、開発者がAPIを理解しやすくなり、
クライアント実装時の参考資料として活用できます。
