# Numbers3, Numbers4 & Loto6 Prediction Project

このプロジェクトは、ナンバーズ3・ナンバーズ4・ロト6の過去データをもとに、複数モデルによる予測・可視化・分析を行うPythonベースのアプリケーションです。

## 主な機能

- 過去の抽選データ・予測データの管理（PostgreSQLデータベース）
- アンサンブル学習による最新予測の生成
- 予測履歴の管理・統計分析
- StreamlitによるリッチなWeb可視化
    - 予測ボタンで最新の当選番号予測を即時表示
    - 過去の予測と実際の当選番号の比較・分析
    - 的中数やモデルごとのパフォーマンス指標

## ディレクトリ構成

```
numbers3/
    predict_ensemble.py      # ナンバーズ3予測ロジック本体
    manage_prediction_history.py  # 予測履歴管理
    save_prediction_history.py    # 予測結果保存
    ...
numbers4/
    predict_ensemble.py      # ナンバーズ4予測ロジック本体
    manage_prediction_history.py  # 予測履歴管理
    save_prediction_history.py    # 予測結果保存
    ...
loto6/
    predict_ensemble.py      # ロト6予測ロジック本体
    manage_prediction_history.py  # 予測履歴管理
    save_prediction_history.py    # 予測結果保存
    ...
streamlit_app.py            # Streamlit Webアプリ
prisma/
    schema.prisma           # データベーススキーマ
    seed.ts                 # シードデータ
```

## 必要な環境

- Python 3.10 以上
- Node.js 18 以上
- PostgreSQL（Docker推奨）
- 必要パッケージ: pandas, numpy, streamlit, tqdm, psycopg2 など

### インストール

```bash
# Pythonパッケージのインストール
pip install -r requirements.txt

# Node.jsパッケージのインストール
npm install

# データベースの起動（Docker）
docker-compose up -d

# データベースマイグレーション
npx prisma migrate dev

# シードデータの投入
npx prisma db seed
```

## Streamlitアプリの起動方法

1. 必要なパッケージをインストール
2. 環境変数 `DATABASE_URL` に PostgreSQL 接続文字列を設定（例: `postgresql://user:pass@host:5432/dbname`）
3. 以下のコマンドでWebアプリを起動

```bash
python -m streamlit run streamlit_app.py
```

- ブラウザで `http://localhost:8501` にアクセス
- 画面上部の「予測を実行」ボタンで最新予測を表示
- 下部で過去の予測と当選番号の比較・分析が可能

## 予測・学習サイクル

### ナンバーズ3の完全サイクル

```bash
# 1. 次回当選番号を予測
python numbers3/predict_ensemble.py
# → 予測ID: 2, 予測番号: 272, 636, 727...

# 2. 実際の当選番号が判明（例：729）
python numbers3/manage_prediction_history.py update 2 729

# 3. 予測結果から学習（モデルを更新）
python numbers3/learn_from_predictions.py 729

# 4. 統計確認
python numbers3/manage_prediction_history.py stats

# 5. 次の予測サイクルへ
python numbers3/predict_ensemble.py
```

### ナンバーズ4の完全サイクル

```bash
# 1. 次回当選番号を予測
python numbers4/predict_ensemble.py
# → 予測ID: 5, 予測番号: 2025, 3456, 7890...

# 2. 実際の当選番号が判明（例：2025）
python numbers4/manage_prediction_history.py update 5 2025

# 3. 予測結果から学習
python numbers4/learn_from_predictions.py

# 4. 統計確認
python numbers4/manage_prediction_history.py stats

# 5. 次の予測サイクルへ
python numbers4/predict_ensemble.py
```

### ロト6の完全サイクル

```bash
# 1. 次回当選番号を予測
python loto6/predict_ensemble.py
# → 予測ID: 1, 予測番号: 06 13 17 21 35 36, 06 13 17 20 35 36...

# 2. 実際の当選番号が判明（例：06,13,17,21,35,36、ボーナス数字：7）
python loto6/manage_prediction_history.py update 1 06,13,17,21,35,36 7

# 3. 予測結果から学習（モデルを更新）
python loto6/learn_from_predictions.py 06,13,17,21,35,36 7

# 4. 統計確認
python loto6/manage_prediction_history.py stats

# 5. 次の予測サイクルへ
python loto6/predict_ensemble.py
```

## 予測ロジックについて

各予測システム（`predict_ensemble.py`）にて：
- 基本統計モデル
- 高度ヒューリスティックモデル
- 機械学習モデル
- 探索的モデル
など複数モデルの予測を統合
- Streamlit UIから直接呼び出し可能

## 予測履歴管理コマンド

### 予測履歴の確認
```bash
# 予測履歴一覧表示
python numbers3/manage_prediction_history.py list
python numbers4/manage_prediction_history.py list
python loto6/manage_prediction_history.py list

# 特定の予測の詳細表示
python numbers4/manage_prediction_history.py show <予測ID>

# 統計情報表示
python numbers4/manage_prediction_history.py stats
```

### 予測結果の更新
```bash
# ナンバーズ3/4の場合
python numbers4/manage_prediction_history.py update <予測ID> <実際の当選番号>

# ロト6の場合（ボーナス数字も含む）
python loto6/manage_prediction_history.py update <予測ID> <実際の当選番号> <ボーナス数字>
```

## よくあるトラブル

- 予測ボタンでエラーが出る場合は、
    - Pythonバージョンや依存パッケージを確認
    - データベース接続を確認（PostgreSQLが起動しているか）
    - 環境変数 `DATABASE_URL` が正しく設定されているか確認
    - エラーメッセージをもとに各 `predict_ensemble.py` のカラム名や返り値を調整

## ライセンス

MIT License

---

ご質問・機能追加要望はIssueまたはチャットでご連絡ください。
