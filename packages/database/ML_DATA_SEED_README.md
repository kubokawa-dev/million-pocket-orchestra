# ML Model Data Seeding Guide

機械学習モデルの予測データと学習履歴をデータベースに投入する方法です。

## 📊 投入されるデータ

### Numbers4 ML Data
- `numbers4_model_events`: 1件
- `numbers4_predictions_log`: 10件  
- `numbers4_ensemble_predictions`: 2件
- `numbers4_prediction_candidates`: 34件

### Numbers3 ML Data
- `numbers3_model_events`: 1件
- `numbers3_predictions_log`: 10件
- `numbers3_ensemble_predictions`: 1件
- `numbers3_prediction_candidates`: 10件

### Loto6 ML Data
- `loto6_model_events`: 2件
- `loto6_predictions_log`: 20件
- `loto6_ensemble_predictions`: 2件
- `loto6_prediction_candidates`: 20件

---

## 🚀 方法1: TypeScriptシードスクリプト（推奨）

### 実行方法

```bash
cd packages/database
npm run db:seed-ml
```

### メリット
- ✅ Prisma Clientを使用するため型安全
- ✅ `upsert`を使用するため、既存データがあっても安全
- ✅ エラーハンドリングが充実
- ✅ 実行結果がわかりやすい

### ファイル
- `prisma/seed-ml.ts`

---

## ⚡ 方法2: SQLファイル直接実行（高速）

### 実行方法

#### PostgreSQL CLIを使用する場合

```bash
# DATABASE_URLから接続情報を取得して実行
psql $DATABASE_URL -f packages/database/seed-ml-data.sql
```

#### または、Supabase CLIを使用する場合

```bash
cd packages/database
supabase db execute --file seed-ml-data.sql
```

### メリット
- ✅ 実行が速い
- ✅ 大量データの投入に適している
- ✅ SQLで直接データを確認できる

### 注意点
- ❌ 既存のデータがある場合は`ON CONFLICT`句で制御
- ❌ 型チェックがない

### ファイル
- `seed-ml-data.sql`

---

## 🔍 データ確認方法

### Prisma Studioで確認

```bash
cd packages/database
npm run db:studio
```

ブラウザで http://localhost:5555 が開きます。

### SQLで直接確認

```sql
-- Model Eventsを確認
SELECT * FROM numbers4_model_events;
SELECT * FROM numbers3_model_events;
SELECT * FROM loto6_model_events;

-- Ensemble Predictionsを確認  
SELECT * FROM numbers4_ensemble_predictions;
SELECT * FROM numbers3_ensemble_predictions;
SELECT * FROM loto6_ensemble_predictions;

-- Prediction Logsを確認
SELECT * FROM numbers4_predictions_log;
SELECT * FROM numbers3_predictions_log;
SELECT * FROM loto6_predictions_log;
```

---

## 🔄 通常のシードとMLシードの組み合わせ

### 1. 最初からすべて投入する場合

```bash
# スキーマをリセット＆適用
npm run db:push -- --force-reset

# 通常のデータ（Draws）を投入
npm run db:seed

# MLデータを投入  
npm run db:seed-ml
```

### 2. MLデータのみ追加する場合

```bash
# 既存データはそのままで、MLデータだけ追加
npm run db:seed-ml
```

---

## ❓ トラブルシューティング

### エラー: `relation "numbers4_model_events" does not exist`

スキーマがデータベースに反映されていません。

```bash
npm run db:push
```

### エラー: `Unique constraint failed`

既にデータが存在しています。TypeScriptシードスクリプトは`upsert`を使用しているため問題ありません。SQLファイルを使用する場合は、既存データを削除してから実行してください。

```sql
-- 既存のMLデータを削除
DELETE FROM numbers4_model_events;
DELETE FROM numbers3_model_events;
DELETE FROM loto6_model_events;
-- 関連テーブルも必要に応じて削除
```

---

## 📝 元データの場所

すべてのMLデータは`data_export.sql`から抽出されました。

完全なデータが必要な場合は、ルートディレクトリの`data_export.sql`を確認してください。
