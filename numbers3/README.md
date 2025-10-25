# ナンバーズ3 予測・学習システム

ナンバーズ3（3桁）の当選番号を予測し、結果から学習するシステムです。

## 📂 ファイル構成

```
numbers3/
├── predict_ensemble.py          # アンサンブル予測の実行
├── prediction_logic.py          # 予測ロジック（基本統計/高度/探索的モデル）
├── learn_from_predictions.py   # 予測結果からの学習
├── manage_prediction_history.py # 予測履歴の管理
├── save_prediction_history.py  # 予測履歴の保存ユーティリティ
├── model_state.json            # 学習済みモデルの状態
└── README.md                   # このファイル
```

---

## 🔄 完全な予測・学習サイクル

### 1. 予測を実行

次回の当選番号を予測します。

```bash
python numbers3/predict_ensemble.py
```

**出力例:**
```
🎯 ナンバーズ3 アンサンブル予測システム
予測結果を保存しました。予測ID: 2

👑 次回ナンバーズ3 最終予測 👑
使用した重み: {'basic_stats': 1.2, 'advanced_heuristics': 1.5, 'exploratory': 1.0}

--- 最終予測 (上位20件) ---
   1位: 272 (スコア: 1.5)
   2位: 636 (スコア: 1.5)
   3位: 727 (スコア: 1.5)
   ...
```

### 2. 実際の当選番号で予測結果を更新

当選番号が判明したら、予測結果を更新します。

```bash
python numbers3/manage_prediction_history.py update <予測ID> <当選番号>

# 例: 予測ID 2、当選番号 729
python numbers3/manage_prediction_history.py update 2 729
```

**出力例:**
```
🔄 予測ID 2 の結果を更新中...
実際の番号: 729
予測結果を更新しました。的中: 2/3桁
✅ 更新完了！
```

### 3. 予測結果から学習

実際の結果を使ってモデルを更新します。

```bash
python numbers3/learn_from_predictions.py <当選番号> [抽選回号]

# 例: 当選番号 729
python numbers3/learn_from_predictions.py 729
```

**出力例:**
```
[learn] Loaded 10 predictions from database (ID: 2, Draw: 6838)
[learn] ✅ Updated model_state.json and logged training event.
[learn] Actual: 729 | Predictions: 10 | Max position hits: 2 (top: 727)
[learn] Model events: 2 | Updated: 2025-10-19T23:44:05.391584+00:00
```

### 4. 統計情報を確認

予測の精度を確認します。

```bash
python numbers3/manage_prediction_history.py stats
```

**出力例:**
```
📈 ナンバーズ3 予測統計
総予測数: 2件
評価済み: 2件
完全一致: 0件
部分一致: 2件
完全一致率: 0.0%
部分一致率: 100.0%

🎯 的中桁数分布:
   2桁: 2件
```

### 5. 次の予測サイクルへ

学習が完了したら、また1に戻って次の予測を実行します。

---

## 📊 予測履歴の管理

### 履歴を一覧表示

```bash
python numbers3/manage_prediction_history.py list [件数]

# 例: 最新10件を表示
python numbers3/manage_prediction_history.py list 10
```

### 特定の予測の詳細を表示

```bash
python numbers3/manage_prediction_history.py show <予測ID>

# 例: 予測ID 2の詳細
python numbers3/manage_prediction_history.py show 2
```

---

## 🤖 予測モデル

### 1. 基本統計モデル
- 時系列重み付け: 最近のデータほど重視
- 各桁の出現頻度を確率的にサンプリング
- **重み: 1.2**

### 2. 高度ヒューリスティックモデル
- 合計値のトレンド分析
- 偶数・奇数のバランス
- ペアの出現頻度
- **重み: 1.5（最も信頼性が高い）**

### 3. 探索的モデル
- 統計的な「穴」を狙う
- 極端な合計値（低/高）
- 長期間出現していない数字（コールドナンバー）
- **重み: 1.0**

---

## 🗃️ データベース構造

### numbers3_ensemble_predictions
アンサンブル予測の結果を保存

### numbers3_prediction_candidates
各予測の候補（上位20件）

### numbers3_predictions_log
すべての予測ログ

### numbers3_model_events
モデルの学習イベント

### numbers3_draws
過去の抽選結果

---

## 💡 ヒント

### 学習の頻度
- 毎回の抽選後に学習することで精度が向上します
- `model_state.json`には学習回数（events）が記録されます

### 予測の評価
- 完全一致: 3桁すべて的中
- 部分一致: 1桁以上的中
- hit_count: 位置も含めて的中した桁数

### モデルの改善
- `prediction_logic.py`で各モデルのロジックをカスタマイズ可能
- `predict_ensemble.py`でモデルの重みを調整可能

---

## 🔧 トラブルシューティング

### 予測が実行できない
```bash
# データベース接続を確認
echo $DATABASE_URL  # Linux/Mac
echo %DATABASE_URL%  # Windows

# 抽選データが存在するか確認
python -c "from tools.utils import get_db_connection; conn = get_db_connection(); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM numbers3_draws'); print(cur.fetchone())"
```

### 学習が失敗する
- 予測を先に実行してください（`predict_ensemble.py`）
- 予測結果を更新してください（`manage_prediction_history.py update`）

---

## 📈 今後の改善案

- [ ] 機械学習モデル（ニューラルネットワーク）の追加
- [ ] 季節性の考慮
- [ ] より高度なパターン認識
- [ ] A/Bテストによるモデル評価

---

## 📝 関連ドキュメント

- [Numbers4のREADME](../numbers4/README_PREDICTION_HISTORY.md)
- [メインREADME](../README.md)
