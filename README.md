# Numbers3, Numbers4 & Loto6 予測プロジェクト 🎰

ナンバーズ3・ナンバーズ4・ロト6の過去データをもとに、複数モデルによる予測・可視化・分析を行うPythonベースのアプリケーションです。

## Discoverability / 検索・海外向け

英語圏・中東などの検索エンジンや GitHub 探索で見つけやすくするためのキーワードです（コンテンツの本質は変えません）。

### English (for search engines & GitHub)

**Million Pocket Orchestra** — Open-source Python toolkit for **Japan Takarakuji** lottery analytics: **Numbers3**, **Numbers4**, and **Loto6** using historical draws, **ensemble machine learning** (e.g. LightGBM), SQLite workflows, optional **Streamlit** UI, and **GitHub Actions** for scheduled pipelines. For research and transparency; not gambling advice and not affiliated with any official operator.

**Suggested GitHub Topics** (set in repo Settings → General → Topics): `python`, `machine-learning`, `ensemble-learning`, `lightgbm`, `streamlit`, `github-actions`, `sqlite`, `takarakuji`, `numbers4`, `loto6`, `japan-lottery`, `lottery-analysis`, `data-science`.

## ✨ 主な機能

- 📊 過去の抽選データ・予測データの管理（SQLiteデータベース）
- 🤖 アンサンブル学習による最新予測の生成
- 📈 予測履歴の管理・統計分析
- 🔄 GitHub Actionsによる毎日自動予測
- 📱 LINE通知（オプション）

## 📁 ディレクトリ構成

```
million-pocket-orchestra/
├── numbers3/                    # ナンバーズ3予測ロジック
├── numbers4/                    # ナンバーズ4予測ロジック
├── loto6/                       # ロト6予測ロジック
├── tools/                       # ユーティリティツール
│   ├── utils.py                 # DB接続・共通関数
│   ├── run_numbers4_pipeline.py # Numbers4自動パイプライン
│   ├── run_loto6_pipeline.py    # Loto6自動パイプライン
│   ├── scrape_numbers4_rakuten.py # Numbers4データ取得
│   ├── scrape_loto6_rakuten.py  # Loto6データ取得
│   └── send_notification.py     # LINE通知
├── .github/workflows/           # GitHub Actions
├── lottery.db                   # SQLiteデータベース
├── schema.sql                   # DBスキーマ
├── requirements.txt             # Python依存関係
└── streamlit_app.py             # Streamlit Webアプリ
```

## 🚀 セットアップ

### 必要な環境

- Python 3.10 以上

### インストール

```bash
# リポジトリをクローン
git clone <your-repo-url>
cd million-pocket-orchestra

# Python仮想環境を作成（推奨）
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存パッケージをインストール
pip install -r requirements.txt

# データベースを初期化
python tools/utils.py
```

これだけ！Docker不要、Node.js不要！🎉

## 📈 予測の実行

### 自動パイプライン（推奨）

```bash
# ナンバーズ4の予測パイプライン
python tools/run_numbers4_pipeline.py

# ロト6の予測パイプライン
python tools/run_loto6_pipeline.py
```

パイプラインは以下を自動実行：
1. 楽天銀行から最新データをスクレイピング
2. モデルの学習更新
3. アンサンブル予測の実行
4. 結果をデータベースに保存

### 手動予測

```bash
# ナンバーズ4
python numbers4/predict_ensemble.py

# ロト6
python loto6/predict_ensemble.py
```

## 🔄 GitHub Actionsで毎日自動実行

`.github/workflows/daily-prediction.yml` により、毎日JST 17:00に自動で予測が実行されます。

### 設定方法

1. リポジトリをGitHubにプッシュ
2. Settings → Secrets and variables → Actions から必要なシークレットを設定
3. Actions タブで手動実行も可能

### LINE通知を有効にする場合

1. [LINE Notify](https://notify-bot.line.me/) でトークンを取得
2. GitHubシークレットに `LINE_NOTIFY_TOKEN` を設定
3. ワークフローファイルのLINE通知部分のコメントを解除

## 📊 予測履歴の管理

```bash
# 予測履歴を表示
python numbers4/manage_prediction_history.py list

# 特定の予測の詳細を表示
python numbers4/manage_prediction_history.py show <予測ID>

# 統計情報を表示
python numbers4/manage_prediction_history.py stats

# 予測結果を更新（当選番号が判明後）
python numbers4/manage_prediction_history.py update <予測ID> <実際の当選番号>
```

## 🖥️ Streamlit Webアプリ

```bash
python -m streamlit run streamlit_app.py
```

ブラウザで `http://localhost:8501` にアクセス

## 🏗️ アーキテクチャ

### データベース

SQLiteを使用（`lottery.db`）

- 外部サービス不要
- シンプルで高速
- リポジトリに含めて管理可能

### 予測モデル

各予測システムは複数のモデルを統合：
- 基本統計モデル
- 高度ヒューリスティックモデル
- 機械学習モデル（LightGBM）
- 探索的モデル

## 📝 完全サイクル例

```bash
# 1. 予測パイプラインを実行
python tools/run_numbers4_pipeline.py

# 2. 予測結果を確認
python numbers4/manage_prediction_history.py list

# 3. 当選番号が判明したら結果を更新
python numbers4/manage_prediction_history.py update <ID> <当選番号>

# 4. 統計を確認
python numbers4/manage_prediction_history.py stats
```

## ⚠️ 注意事項

- 宝くじの予測は参考情報です
- 購入は自己責任でお願いします
- SMBCでの自動購入APIは公開されていないため、購入は手動で行う必要があります

## 📄 ライセンス

MIT License
