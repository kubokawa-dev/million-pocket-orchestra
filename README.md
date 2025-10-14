# million-pocket

ナンバーズ4/ロト6の予測・学習・データ管理用ミニツール群です。

## セットアップ

1. Python 3.9+ を用意
2. 依存パッケージのインストール

```pwsh
python -m pip install -r requirements.txt
```

## 1コマンド・パイプライン（ナンバーズ4）

次を実行すると、スクレイプ→DB更新→未学習なら学習→予測出力 まで一気に実行されます。

```pwsh
python tools/run_numbers4_pipeline.py
```

内部で呼ばれる主なスクリプト:
- `tools/scrape_numbers4_rakuten.py` … 楽天バックナンバーから当選データを抽出し、`numbers4/YYYYMM.csv` と `millions.sqlite` を差分更新
- `tools/update_model_from_sqlite.py` … `numbers4_draws` の最新当選が未学習なら `numbers4/learn_from_predictions.py` を実行して学習
- `numbers4/advanced_predict_numbers4.py` … 高度予測（多視点スコア）
- `numbers4/predict_numbers_with_model.py` … 学習済み位置分布モデルからTop-K
- `numbers4/predict_numbers.py` … 基本的な傾向分析＋学習事前分布の軽ブレンド

## 単体での使い方

- 最新10件のDB確認:
```pwsh
python tools/query_numbers4_latest.py
```

- 学習（最新の予想レポートと実当選で更新）:
```pwsh
python numbers4/learn_from_predictions.py
```

- 予測出力（モデルベースTop-K）:
```pwsh
python numbers4/predict_numbers_with_model.py
```

## メモ

- SQLite DB: `millions.sqlite`
  - `numbers4_draws(draw_number, draw_date, numbers)` を主に使用
  - 学習ログ: `numbers4_model_events`, 予想ログ: `numbers4_predictions_log`
- 事前分布: `numbers4/model_state.json`（`learn_from_predictions.py` で更新）
- スクレイプ対象のHTML構造が変わった場合は `tools/scrape_numbers4_rakuten.py` の正規表現調整が必要です。

## 免責

本ツールの予測は統計的・経験則に基づくものであり、当選を保証するものではありません。利用は自己責任でお願いします。

## PrismaでDBを閲覧（任意）

Prisma Studioから `millions.sqlite` をブラウズできます。

1) ルートに `.env` を作成済み（本リポジトリでは同梱）

```
DATABASE_URL="file:./millions.sqlite"
```

2) Prismaスキーマ `prisma/schema.prisma` を用意済み。Node.js と Prisma CLI が必要です。

```pwsh
# Prisma Clientの生成（初回）
npx prisma generate

# Prisma Studioの起動
npx prisma studio
```

Studio上で以下のテーブルを閲覧／編集できます。
- Numbers4Draw (`numbers4_draws`)
- Loto6Draw (`loto6_draws`)
- Numbers4ModelEvent (`numbers4_model_events`)
- Numbers4PredictionLog (`numbers4_predictions_log`)
