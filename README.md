# Numbers3, Numbers4 & Loto6 予測プロジェクト 🎰

ナンバーズ3・ナンバーズ4・ロト6の過去データをもとに、複数モデルによる予測・可視化・分析を行う **Python** と **Next.js（Web）** を組み合わせたプロジェクトです。

## Discoverability / 検索・海外向け

英語圏・中東などの検索エンジンや GitHub 探索で見つけやすくするためのキーワードです（コンテンツの本質は変えません）。

### English (for search engines & GitHub)

**Million Pocket Orchestra** — Open-source toolkit for **Japan Takarakuji** lottery analytics: **Numbers3**, **Numbers4**, and **Loto6** using historical draws, **ensemble machine learning** (e.g. LightGBM), SQLite workflows, optional **Streamlit** UI, **Next.js** site with **Supabase**, **Turborepo** / **pnpm**, and **GitHub Actions** for scheduled pipelines. For research and transparency; not gambling advice and not affiliated with any official operator.

**Suggested GitHub Topics** (set in repo Settings → General → Topics): `python`, `machine-learning`, `ensemble-learning`, `lightgbm`, `streamlit`, `nextjs`, `supabase`, `turborepo`, `pnpm`, `github-actions`, `sqlite`, `takarakuji`, `numbers3`, `numbers4`, `loto6`, `japan-lottery`, `lottery-analysis`, `data-science`.

## ✨ 主な機能

- 📊 過去の抽選データ・予測データの管理（SQLiteデータベース）
- 🤖 アンサンブル学習による最新予測の生成
- 📈 予測履歴の管理・統計分析
- 🔄 GitHub Actions による定期パイプライン（予測・分析・Supabase 同期など）
- 🌐 Next.js Web アプリ（`apps/web`、オプションで Supabase 連携）
- 📱 LINE通知（オプション）

## 📁 ディレクトリ構成

```
million-pocket-orchestra/
├── apps/web/                    # Next.js（公開サイト・Supabase）
├── packages/config/             # Turborepo 用の共有設定パッケージ
├── numbers3/                    # ナンバーズ3予測ロジック・CSV
├── numbers4/                    # ナンバーズ4予測ロジック
├── loto6/                       # ロト6予測ロジック
├── tools/                       # ユーティリティ・パイプライン
├── tests/                       # pytest（クリティカルなパース等）
├── predictions/                 # 日次予測 JSON（Actions がコミット）
├── schema.sql                   # SQLite スキーマ
├── requirements.txt             # Python 本番・パイプライン用依存
├── requirements-dev.txt         # 開発用（pytest など）
├── streamlit_app.py             # Streamlit Webアプリ
├── turbo.json                   # Turborepo タスク定義
├── pnpm-workspace.yaml
└── package.json                 # モノレポルート（pnpm）
```

## 🚀 セットアップ

### 必要な環境

- **Python 3.11**（GitHub Actions の各ワークフローと揃えています。3.10+ でも動く可能性はあります）
- **Web を触る場合**: Node.js **20.x**、**pnpm 9**（`package.json` の `packageManager` に合わせる）

### Python（予測・ツール）

```bash
git clone <your-repo-url>
cd million-pocket-orchestra

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt

# テスト用（任意）
pip install -r requirements-dev.txt
python -m pytest
```

`lottery.db` は **`schema.sql` からローカル生成**します（ファイル名は `tools/utils.py` の `DB_PATH`）。リポジトリの `.gitignore` で `*.db` を無視しているため、**データベースファイル自体は Git に含まれません**。チームで共有する場合は別途配布するか、各自 `python tools/utils.py` で初期化してください。

```bash
python tools/utils.py
```

### Web（Next.js）

```bash
pnpm install

# apps/web に .env.local を置き、Supabase の URL / anon / service_role を設定
pnpm --filter web dev
```

本番ビルド例（環境変数は実プロジェクトの Supabase に合わせる）:

```bash
pnpm exec turbo run lint build --filter=web
```

Docker は必須ではありません。

## 📈 予測の実行

### 自動パイプライン（推奨）

```bash
# ナンバーズ3
python tools/run_numbers3_pipeline.py

# ナンバーズ4
python tools/run_numbers4_pipeline.py

# ロト6
python tools/run_loto6_pipeline.py
```

パイプラインは概ね以下を自動実行します（スクリプトにより異なります）:

1. データ取得（スクレイピング等）
2. モデルの学習更新
3. アンサンブル予測の実行
4. 結果を SQLite や JSON に保存

### 手動予測

```bash
# ナンバーズ4
python numbers4/predict_ensemble.py

# ロト6
python loto6/predict_ensemble.py
```

## 🔄 GitHub Actions

定期実行・手動実行のワークフローは `.github/workflows/` にあります。主なもの:

| ワークフロー | 用途 |
|--------------|------|
| `ci.yml` | PR / main 向け **lint・ビルド（web）** と **pytest** |
| `daily-numbers3-prediction.yml` | Numbers3 日次予測・JSON コミット・Supabase |
| `daily-numbers3-analysis.yml` | Numbers3 分析 |
| `daily-numbers3-summary.yml` | Numbers3 サマリー |
| `daily-numbers4-prediction.yml` | Numbers4 日次予測 等 |
| `daily-numbers4-analysis.yml` | Numbers4 分析 |
| `daily-numbers4-summary.yml` | Numbers4 サマリー |
| `daily-loto6-prediction.yml` | ロト6 日次予測 |
| `numbers3-target-number-check.yml` / `numbers4-target-number-check.yml` | 当選番号チェック |
| `manual-numbers3-supabase-sync.yml` | Supabase 手動同期 |
| `weekly-numbers3-box-stats-analysis.yml` / `weekly-numbers4-box-stats-analysis.yml` | 週次ボックス統計 |

### 設定方法

1. リポジトリを GitHub にプッシュする
2. Settings → Secrets and variables → Actions から必要なシークレットを設定する（Supabase 連携ワークフローでは `NEXT_PUBLIC_SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` 等）
3. Actions タブから手動実行（`workflow_dispatch`）も可能

### LINE通知を有効にする場合

1. [LINE Notify](https://notify-bot.line.me/) でトークンを取得する
2. GitHub シークレットに `LINE_NOTIFY_TOKEN` を設定する
3. 該当ワークフロー内の LINE 通知ステップのコメントを解除する

### 依存関係の更新

`.github/dependabot.yml` により **npm（pnpm ロックファイル）** と **GitHub Actions** の更新 PR が週次で作成されます。

## 🛡️ 公開 API（レート制限）

Next.js 16 の **`apps/web/proxy.ts`**（旧ミドルウェア相当）で `/api/*` に対し **IP ごとのベストエフォートなレート制限**（メモリ内カウンタ）をかけています。サーバレスやマルチリージョンではプロセス間で共有されないため、厳密な上限にはなりません。高トラフィックや分散環境では **Upstash Redis** 等の専用ストアを検討してください。

## 📊 予測履歴の管理

```bash
python numbers4/manage_prediction_history.py list
python numbers4/manage_prediction_history.py show <予測ID>
python numbers4/manage_prediction_history.py stats
python numbers4/manage_prediction_history.py update <予測ID> <実際の当選番号>
```

## 🖥️ Streamlit Webアプリ

```bash
python -m streamlit run streamlit_app.py
```

ブラウザで `http://localhost:8501` にアクセスします。

## 🏗️ アーキテクチャ

### データベース

- ローカル解析・パイプライン: **SQLite**（`lottery.db`、`.gitignore` 対象）
- 公開サイト: **Supabase（PostgreSQL）**（`apps/web` のマイグレーション参照）

### 予測モデル

各予測システムは複数モデルを統合しています:

- 基本統計モデル
- 高度ヒューリスティックモデル
- 機械学習モデル（LightGBM）
- 探索的モデル

## 📝 完全サイクル例

```bash
python tools/run_numbers4_pipeline.py
python numbers4/manage_prediction_history.py list
python numbers4/manage_prediction_history.py update <ID> <当選番号>
python numbers4/manage_prediction_history.py stats
```

## ⚠️ 注意事項

- 宝くじの予測は参考情報です
- 購入は自己責任でお願いします
- SMBCでの自動購入APIは公開されていないため、購入は手動で行う必要があります

## 📄 ライセンス

MIT License
