# ナンバーズ4 予測履歴管理システム

予測結果をデータベースに保存し、的中率の分析や履歴管理を行うシステムです。

## 📊 機能概要

### 1. **予測履歴の自動保存**
- アンサンブル予測を実行すると、自動的にデータベースに保存
- 予測番号、スコア、使用したモデル、重み設定などを記録

### 2. **結果の追跡**
- 当選番号が判明したら、予測結果を更新
- 的中状況（完全一致/部分一致/外れ）を自動判定

### 3. **統計分析**
- 予測精度の推移を確認
- モデル別の的中率を分析
- 最も的中率の高い番号パターンを特定

## 🗄️ データベース構造

### `numbers4_ensemble_predictions` テーブル
アンサンブル予測の実行履歴を保存

| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | INT | 主キー |
| created_at | TIMESTAMP | 予測実行日時 |
| target_draw_number | INT | 予測対象の抽選回 |
| model_updated_at | TEXT | 使用したモデルの更新日時 |
| model_events_count | INT | モデルの学習イベント数 |
| ensemble_weights | TEXT (JSON) | アンサンブルの重み設定 |
| predictions_count | INT | 生成した予測候補の総数 |
| top_predictions | TEXT (JSON) | 上位予測結果 |
| model_predictions | TEXT (JSON) | モデル別の予測結果 |
| actual_draw_number | INT | 実際の抽選回（結果判明後） |
| actual_numbers | TEXT | 実際の当選番号（結果判明後） |
| hit_status | TEXT | 的中状況（exact/partial/miss） |
| hit_count | INT | 的中した桁数（0-4） |
| notes | TEXT | メモ・備考 |

### `numbers4_prediction_candidates` テーブル
個別の予測候補の詳細

| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | INT | 主キー |
| ensemble_prediction_id | INT | 親のアンサンブル予測ID |
| rank | INT | 順位（1から始まる） |
| number | TEXT | 予測番号（4桁） |
| score | FLOAT | アンサンブルスコア |
| contributing_models | TEXT (JSON) | この番号を予測したモデルのリスト |
| created_at | TIMESTAMP | 作成日時 |

## 🚀 セットアップ

### 1. マイグレーション実行

```bash
# データベースに予測履歴テーブルを作成
python scripts/run_migration.py
```

### 2. 予測実行（自動的に履歴が保存されます）

```bash
# アンサンブル予測を実行
python numbers4/predict_ensemble.py
```

予測実行時に自動的に以下が保存されます：
- 予測番号とスコア（上位50件）
- 使用したモデルと重み設定
- モデルの学習状態

## 📋 使い方

### 予測履歴の確認

```bash
# 最新20件の予測履歴を表示
python numbers4/manage_prediction_history.py list

# 最新50件を表示
python numbers4/manage_prediction_history.py list --limit 50
```

**出力例:**
```
[ID: 5] 2025-10-17 23:30
  対象: 第6838回
  上位5予測: 4325, 7890, 1234, 5678, 9012
  結果: ⏳ 未判明

[ID: 4] 2025-10-16 22:15
  対象: 第6837回
  上位5予測: 1234, 5678, 9012, 3456, 7890
  結果: 🎲 1235 (partial, 3桁一致)
```

### 予測の詳細表示

```bash
# 特定の予測IDの詳細を表示
python numbers4/manage_prediction_history.py show 5
```

**出力例:**
```
📊 予測詳細 [ID: 5]
================================================================================

作成日時: 2025-10-17 23:30:45
対象抽選回: 第6838回
予測候補数: 30件

【モデル情報】
  モデル更新日時: 2025-10-17T14:20:00
  学習イベント数: 15回

【アンサンブル重み】
  basic_stats: 1.2
  advanced_heuristics: 1.5
  ml_model_new: 1.0
  exploratory: 0.9

【上位10予測】
   1位: 4325 (スコア: 5.80)
   2位: 7890 (スコア: 4.50)
   3位: 1234 (スコア: 4.20)
   ...

【モデル別予測】
  basic_stats: 5件
    上位: 4325, 1234, 5678, 9012, 3456
  advanced_heuristics: 5件
    上位: 7890, 4325, 2345, 6789, 0123
  ...

【結果】
  ⏳ 未判明
```

### 予測結果の更新

当選番号が判明したら、結果を更新します。

```bash
# 予測ID 5 の結果を更新（当選番号: 4325）
python numbers4/manage_prediction_history.py update 5 4325
```

**出力例:**
```
✅ 予測結果を更新しました (ID: 5)
   実際の当選番号: 4325
   的中状況: exact (4桁一致)
```

### 統計情報の表示

```bash
# 予測精度の統計を表示
python numbers4/manage_prediction_history.py stats
```

**出力例:**
```
📈 予測統計
================================================================================

総予測回数: 25回

【的中統計】
  exact: 2回 (平均4.00桁一致)
  partial: 15回 (平均2.53桁一致)
  miss: 8回 (平均0.00桁一致)

【最近10回の結果】
  第6837回: 1235 🎲 (3桁) - 予測: 1234, 5678, 9012
  第6836回: 7890 🎯 (4桁) - 予測: 7890, 1234, 5678
  第6835回: 3456 ❌ (0桁) - 予測: 1234, 5678, 9012
  ...

【完全一致した予測番号】
  7890: 1回
  1234: 1回
```

## 🔄 ワークフロー例

### 1. 定期的な予測と履歴保存

```bash
# ステップ1: モデルを最新データで更新
python numbers4/update_model.py --auto

# ステップ2: 予測を実行（自動的に履歴が保存される）
python numbers4/predict_ensemble.py

# ステップ3: 履歴を確認
python numbers4/manage_prediction_history.py list
```

### 2. 当選番号判明後の結果更新

```bash
# ステップ1: 最新の予測IDを確認
python numbers4/manage_prediction_history.py list

# ステップ2: 結果を更新
python numbers4/manage_prediction_history.py update <予測ID> <当選番号>

# ステップ3: 統計を確認
python numbers4/manage_prediction_history.py stats
```

## 📊 データ活用例

### Pythonスクリプトでの利用

```python
from numbers4.save_prediction_history import get_prediction_history

# 最新10件の予測履歴を取得
history = get_prediction_history(10)

for h in history:
    print(f"ID: {h['id']}, 対象: 第{h['target_draw_number']}回")
    if h['actual_numbers']:
        print(f"  結果: {h['actual_numbers']} ({h['hit_status']})")
```

### SQLでの直接クエリ

```sql
-- 的中率の高い予測を抽出
SELECT 
    id, target_draw_number, actual_numbers, hit_status, hit_count,
    top_predictions::json->0->>'number' as top_prediction
FROM numbers4_ensemble_predictions
WHERE hit_status = 'exact'
ORDER BY created_at DESC;

-- モデル別の予測精度を分析
SELECT 
    ensemble_weights::json->>'basic_stats' as basic_weight,
    ensemble_weights::json->>'advanced_heuristics' as advanced_weight,
    AVG(hit_count) as avg_hit_count
FROM numbers4_ensemble_predictions
WHERE actual_numbers IS NOT NULL
GROUP BY ensemble_weights;
```

## 🎯 改善ポイント

### 予測精度の向上
1. **統計分析**: `stats` コマンドで的中率を確認
2. **モデル調整**: 的中率の低いモデルの重みを調整
3. **学習データ更新**: 定期的に `update_model.py` を実行

### データの活用
1. **トレンド分析**: 時系列での的中率の推移を確認
2. **パターン発見**: 的中した番号の共通パターンを分析
3. **モデル比較**: モデル別の予測精度を比較

## 🔧 トラブルシューティング

### マイグレーションエラー

```bash
# テーブルが既に存在する場合
# migration.sqlの CREATE TABLE を CREATE TABLE IF NOT EXISTS に変更済み
python scripts/run_migration.py
```

### 履歴保存エラー

予測実行時に履歴保存に失敗しても、予測結果は表示されます。
エラーメッセージを確認してデータベース接続を確認してください。

```bash
# データベース接続を確認
python numbers4/check_model_status.py
```

## 📝 注意事項

- 予測履歴は自動的に保存されますが、結果の更新は手動で行う必要があります
- データベースの容量に注意してください（予測1回あたり約50レコード）
- 古い履歴は定期的にアーカイブすることを推奨します

## 🎉 まとめ

このシステムにより、以下が可能になります：

✅ **予測の追跡**: すべての予測を履歴として保存  
✅ **精度の分析**: 的中率やパターンを統計的に分析  
✅ **モデルの改善**: データに基づいたモデルの調整  
✅ **透明性の向上**: 予測プロセスの可視化

予測精度の向上と、データドリブンな意思決定にご活用ください！
