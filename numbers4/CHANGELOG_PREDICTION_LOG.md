# Numbers4PredictionLog テーブルの改善

## 変更内容

### 問題点
`numbers4_predictions_log` テーブルに**どの回号の予測かわからない**という問題がありました。

### 解決策
**`target_draw_number`** カラムを追加し、予測対象の抽選回を記録できるようにしました。

## 📊 変更されたスキーマ

### Before（変更前）
```prisma
model Numbers4PredictionLog {
  id         Int     @id @default(autoincrement())
  created_at String
  source     String
  label      String?
  number     String

  @@map("numbers4_predictions_log")
}
```

### After（変更後）
```prisma
model Numbers4PredictionLog {
  id                 Int     @id @default(autoincrement())
  created_at         String
  source             String
  label              String?
  number             String
  target_draw_number Int?    // 予測対象の抽選回 ← 新規追加

  @@map("numbers4_predictions_log")
  @@index([target_draw_number])  // インデックスも追加
}
```

## 🔄 マイグレーション

### 実行方法

```bash
# すべてのマイグレーションを実行
python scripts/run_all_migrations.py
```

または個別に実行：

```bash
# このマイグレーションのみ実行
python scripts/run_migration.py
# → prisma/migrations/add_target_draw_to_prediction_log/migration.sql
```

### マイグレーション内容

1. **カラム追加**: `target_draw_number` (INTEGER, NULL可)
2. **インデックス作成**: `target_draw_number` に対するインデックス
3. **既存データ更新**: 既存レコードに対して、作成日時から推定した抽選回を設定

```sql
-- カラム追加
ALTER TABLE "numbers4_predictions_log" 
ADD COLUMN IF NOT EXISTS "target_draw_number" INTEGER;

-- インデックス作成
CREATE INDEX IF NOT EXISTS "numbers4_predictions_log_target_draw_number_idx" 
ON "numbers4_predictions_log"("target_draw_number");

-- 既存データ更新
UPDATE "numbers4_predictions_log" 
SET target_draw_number = (
    SELECT MAX(draw_number) + 1 
    FROM numbers4_draws 
    WHERE draw_date <= numbers4_predictions_log.created_at
)
WHERE target_draw_number IS NULL;
```

## 🔧 コード変更

### 1. `learn_from_predictions.py`

**変更点:**
- `learn()` 関数に `actual_draw_number` パラメータを追加
- 予測ログ保存時に `target_draw_number` を記録

```python
# Before
def learn(actual_number: str):
    # ...
    cur.execute(
        'INSERT INTO numbers4_predictions_log(created_at, source, label, number) VALUES (%s, %s, %s, %s)',
        (ts, s, l, n)
    )

# After
def learn(actual_number: str, actual_draw_number: int = None):
    # ...
    # 抽選回番号を自動取得（指定されていない場合）
    if actual_draw_number is None:
        cur.execute("SELECT MAX(draw_number) FROM numbers4_draws")
        row = cur.fetchone()
        actual_draw_number = row[0] if row and row[0] else None
    
    cur.execute(
        'INSERT INTO numbers4_predictions_log(created_at, source, label, number, target_draw_number) VALUES (%s, %s, %s, %s, %s)',
        (ts, s, l, n, actual_draw_number)
    )
```

### 2. `update_model.py`

**変更点:**
- `get_latest_number_from_db()` が抽選回番号も返すように変更
- `learn()` 関数呼び出し時に抽選回番号を渡す

```python
# Before
def get_latest_number_from_db():
    # ...
    return numbers  # 当選番号のみ

# After
def get_latest_number_from_db():
    # ...
    return (draw_number, numbers)  # (抽選回, 当選番号) のタプル
```

## 📋 使用例

### 1. モデル更新（自動取得）

```bash
python numbers4/update_model.py --auto
```

**出力例:**
```
📊 最新の抽選結果: 第6837回 (2025-10-16) = 1234

🔄 モデル更新を開始します... (1件)
============================================================

📝 学習中: 第6837回 = 1234
✅ 完了: 1234
```

### 2. モデル更新（手動指定）

```bash
python numbers4/update_model.py 1234
```

この場合、`target_draw_number` は自動的にDBから推定されます。

### 3. データベースクエリ

```sql
-- 特定の抽選回の予測を確認
SELECT * FROM numbers4_predictions_log
WHERE target_draw_number = 6838
ORDER BY created_at DESC;

-- 抽選回ごとの予測数を集計
SELECT target_draw_number, COUNT(*) as prediction_count
FROM numbers4_predictions_log
GROUP BY target_draw_number
ORDER BY target_draw_number DESC
LIMIT 10;

-- 予測と実際の結果を比較
SELECT 
    p.target_draw_number,
    p.number as predicted,
    d.numbers as actual,
    p.source,
    p.label
FROM numbers4_predictions_log p
LEFT JOIN numbers4_draws d ON d.draw_number = p.target_draw_number
WHERE p.target_draw_number IS NOT NULL
ORDER BY p.target_draw_number DESC, p.created_at DESC;
```

## 🎯 メリット

### 1. **予測の追跡が容易**
- どの回号の予測かが明確
- 抽選回ごとに予測をグループ化可能

### 2. **的中率の分析が可能**
- 予測と実際の結果を簡単に比較
- 抽選回ごとの精度を分析

### 3. **データの整合性向上**
- 予測と抽選結果の関連付けが明確
- 履歴管理が容易

## 🔍 既存データへの影響

### マイグレーション実行後
- 既存のレコードには、作成日時から推定した `target_draw_number` が自動設定されます
- 推定できない場合は `NULL` のまま（問題なし）

### 今後の動作
- `update_model.py --auto` を使用すると、自動的に正しい抽選回番号が記録されます
- 手動で番号を指定した場合は、DBから最新の抽選回+1が推定されます

## ✅ 確認方法

### マイグレーション後の確認

```bash
# テーブル構造を確認
python -c "
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get('DATABASE_URL').split('?schema')[0]
conn = psycopg2.connect(db_url)
cur = conn.cursor()

cur.execute('''
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name = 'numbers4_predictions_log'
    ORDER BY ordinal_position
''')

print('numbers4_predictions_log のカラム:')
for col in cur.fetchall():
    print(f'  - {col[0]} ({col[1]}) NULL可: {col[2]}')

conn.close()
"
```

### データの確認

```bash
# 最新10件の予測ログを確認
python -c "
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get('DATABASE_URL').split('?schema')[0]
conn = psycopg2.connect(db_url)
cur = conn.cursor()

cur.execute('''
    SELECT id, target_draw_number, number, source, label, created_at
    FROM numbers4_predictions_log
    ORDER BY created_at DESC
    LIMIT 10
''')

print('最新10件の予測ログ:')
for row in cur.fetchall():
    print(f'  ID:{row[0]} 第{row[1]}回 {row[2]} ({row[3]}/{row[4]}) {row[5]}')

conn.close()
"
```

## 📝 まとめ

- ✅ `target_draw_number` カラムを追加
- ✅ インデックスを作成してクエリ性能を向上
- ✅ 既存データに対しても推定値を自動設定
- ✅ `learn_from_predictions.py` と `update_model.py` を更新
- ✅ マイグレーションスクリプトを作成

これにより、**どの回号の予測か**が明確になり、予測履歴の管理と分析が大幅に改善されました！
