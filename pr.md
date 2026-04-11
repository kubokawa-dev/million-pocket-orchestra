# 概要

ナンバーズ4の利用者向け文言と詳細ページ体験を改善しつつ、ナンバーズ3をナンバーズ4とほぼ同じ運用レベル（Web導線・API・予測パイプライン・GitHub Actions・DB取り込み）まで横展開したPRです。  
Numbers3/Numbers4 の日次運用を対称化し、今後の機能追加や保守時のワークフロー差分を最小化することを目的としています。

## 変更内容
- ナンバーズ4側で、利用者向け文言から実装寄りの語（DB/Supabaseなど）を外し、画面・API説明の可読性を改善しました。
- ナンバーズ4詳細ページに「モデル横断 BOX組み合わせランキング」を追加し、複数モデルで重なるBOX候補の可視化を可能にしました（正規化・同率時安定ソート込み）。
- `apps/web` にナンバーズ3のページ群（ハブ、結果一覧、詳細、旧URLリダイレクト）と `api/numbers3/latest` を追加しました。
- OpenAPI・サイトナビ・サイトマップを numbers3 対応し、検索導線と機械可読導線を揃えました。
- Supabase migration と Python ツール群を追加し、numbers3 の CSV投入・daily JSON upsert・target check・pipeline 実行を可能にしました。
- GitHub Actions を numbers3 向けに新設し、prediction / summary / analysis / target check / weekly box stats の運用フローを numbers4 と同等にしました。
- `numbers3` パッケージ（core, ensemble, method predictions, JSON保存, 履歴保存, summary, budget plan）を追加し、最低限の end-to-end 実行が通る実装を導入しました。

## 背景 / 目的
- 既存の運用は numbers4 中心で、numbers3 側に同等の実行導線・自動化・公開導線が不足していました。
- lottery種別ごとに運用フローが分かれると、CI運用や障害対応時の認知コストが上がる課題がありました。
- そのため、numbers4 で成立している構成をベースに numbers3 を対称化し、将来拡張時の差分を抑えることを目的にしています。

## 動作確認 / テスト
- [x] ローカルで動作確認
- [x] 自動テスト（Unit/E2E）: `pnpm --filter web lint`、`pnpm --filter web exec tsc --noEmit`
- [x] 手動テスト: `python tools/run_numbers3_pipeline.py`、`python tools/run_numbers3_method_predictions.py --limit 50 --top 10`、`python tools/check_numbers3_target_number.py --number 123 --methods box_model,cold_revival`

## スクリーンショット / 動画（UI変更がある場合）
未添付。必要に応じて、`/numbers3`・`/numbers3/result`・`/numbers4/result/[draw_number]` の画面キャプチャを追記します。

## 影響範囲
- `apps/web` の公開導線（ナビ、sitemap、OpenAPI、numbers3 ページ群、numbers4 詳細ページ文言/ランキング）に影響します。
- `tools`・`numbers3` 配下の運用スクリプトと GitHub Actions に影響し、CI運用面の動作範囲が増えます。
- Supabase の `numbers3_draws` / `numbers3_daily_prediction_documents` 新規テーブル追加が必要です。

## リスクと対策
- **新規運用フローの初期不安定**: numbers3 の予測ロジックは初期実装のため、運用初期はログ監視を厚めに行う前提です。
- **numbers3/4 budget_plan ファイル名衝突**: numbers3 は `budget_plan_numbers3_<draw>.json` を採用し、共通収集ロジックも lottery別判定に分離済みです。
- **差分規模の増大**: 48 files と広範囲のため、レビュー観点を「Web導線」「CI」「DB」「Python実行」に分けて確認できるよう本文に整理しました。

## ロールアウト / リリース手順（必要なら）
- [ ] 段階リリース
- [ ] フラグで切替
- [x] リリース後の確認項目: numbers3 workflows の初回成功、`/numbers3`・`/numbers3/result` の表示、`/api/numbers3/latest` の応答、Supabase migration 適用後の upsert 成功を確認

## レビュー観点
- numbers3 の新規導線（ページ・API・sitemap・nav）が壊れず接続されているか。
- numbers3 用 workflows と tools の組み合わせが、想定運用（prediction/summary/analysis/check）を満たしているか。
- `tools/daily_predictions_json_common.py` の lottery別判定で、numbers3/4 の budget plan 取り込みが正しく分離されているか。
- numbers4 側の文言変更と BOXランキング追加が既存機能を壊していないか。

## チェックリスト
- [x] 目的に沿った最小変更になっている
- [x] 不要なログ/デバッグコードを削除した
- [x] 仕様/ドキュメントの更新が必要なら反映した
- [x] 破壊的変更がある場合、影響/移行手順を書いた

---

## 自動情報（参考）

### diffstat（origin/main...HEAD）

```
 .github/workflows/daily-numbers3-analysis.yml      |  76 ++++++
 .github/workflows/daily-numbers3-prediction.yml    |  75 ++++++
 .github/workflows/daily-numbers3-summary.yml       |  79 ++++++
 .github/workflows/numbers3-target-number-check.yml |  50 ++++
 .../weekly-numbers3-box-stats-analysis.yml         |  45 ++++
 apps/web/app/api/numbers3/latest/route.ts          |  69 +++++
 apps/web/app/api/numbers4/latest/route.ts          |   2 +-
 apps/web/app/api/openapi.json/route.ts             |  22 +-
 apps/web/app/data-sources/page.tsx                 |   4 +-
 apps/web/app/llms-full.txt/route.ts                |   2 +-
 apps/web/app/llms.txt/route.ts                     |   2 +-
 apps/web/app/numbers3/[draw_number]/page.tsx       |  10 +
 apps/web/app/numbers3/page.tsx                     | 107 ++++++++
 .../web/app/numbers3/result/[draw_number]/page.tsx |  75 ++++++
 .../app/numbers3/result/numbers3-draws-table.tsx   |  91 +++++++
 .../app/numbers3/result/numbers3-pagination.tsx    |  80 ++++++
 apps/web/app/numbers3/result/page.tsx              | 102 ++++++++
 .../app/numbers4/numbers4-official-draw-detail.tsx |   2 +-
 apps/web/app/numbers4/numbers4-predictions-hub.tsx | 162 ++++++++++--
 apps/web/app/numbers4/page.tsx                     |   9 +-
 .../numbers4/result/numbers4-recent-model-hits.tsx |   4 +-
 apps/web/app/numbers4/stats/page.tsx               |  12 +-
 apps/web/app/sitemap.ts                            |  22 ++
 apps/web/components/site-nav.tsx                   |   1 +
 apps/web/lib/blog/posts-en.ts                      |   4 +-
 apps/web/lib/blog/posts.ts                         |   4 +-
 apps/web/lib/faq-content.ts                        |   2 +-
 apps/web/lib/home-landing-copy.ts                  |   4 +-
 apps/web/lib/numbers3.ts                           |  25 ++
 .../migrations/20260410120000_numbers3_draws.sql   |  18 ++
 ...0121000_numbers3_daily_prediction_documents.sql |  36 +++
 numbers3/__init__.py                               |   1 +
 numbers3/core.py                                   | 211 +++++++++++++++
 numbers3/generate_budget_plan.py                   |  70 +++++
 numbers3/predict_ensemble.py                       |  74 ++++++
 numbers3/prediction_utils.py                       |  41 +++
 numbers3/run_method_predictions.py                 |  47 ++++
 numbers3/save_method_prediction_json.py            |  71 +++++
 numbers3/save_prediction_history.py                | 120 +++++++++
 numbers3/save_prediction_json.py                   |  59 +++++
 numbers3/summarize_from_json.py                    |  72 +++++
 tools/check_numbers3_target_number.py              | 205 +++++++++++++++
 tools/daily_predictions_json_common.py             |  43 ++-
 tools/ddl_numbers3_draws_postgres.sql              |  10 +
 tools/load_numbers3_csv_to_postgres.py             | 290 +++++++++++++++++++++
 tools/load_numbers3_daily_json_to_postgres.py      | 158 +++++++++++
 tools/run_numbers3_method_predictions.py           |  41 +++
 tools/run_numbers3_pipeline.py                     |  52 ++++
 48 files changed, 2692 insertions(+), 69 deletions(-)
```

### changed files

- `.github/workflows/daily-numbers3-analysis.yml`
- `.github/workflows/daily-numbers3-prediction.yml`
- `.github/workflows/daily-numbers3-summary.yml`
- `.github/workflows/numbers3-target-number-check.yml`
- `.github/workflows/weekly-numbers3-box-stats-analysis.yml`
- `apps/web/app/api/numbers3/latest/route.ts`
- `apps/web/app/api/numbers4/latest/route.ts`
- `apps/web/app/api/openapi.json/route.ts`
- `apps/web/app/data-sources/page.tsx`
- `apps/web/app/llms-full.txt/route.ts`
- `apps/web/app/llms.txt/route.ts`
- `apps/web/app/numbers3/[draw_number]/page.tsx`
- `apps/web/app/numbers3/page.tsx`
- `apps/web/app/numbers3/result/[draw_number]/page.tsx`
- `apps/web/app/numbers3/result/numbers3-draws-table.tsx`
- `apps/web/app/numbers3/result/numbers3-pagination.tsx`
- `apps/web/app/numbers3/result/page.tsx`
- `apps/web/app/numbers4/numbers4-official-draw-detail.tsx`
- `apps/web/app/numbers4/numbers4-predictions-hub.tsx`
- `apps/web/app/numbers4/page.tsx`
- `apps/web/app/numbers4/result/numbers4-recent-model-hits.tsx`
- `apps/web/app/numbers4/stats/page.tsx`
- `apps/web/app/sitemap.ts`
- `apps/web/components/site-nav.tsx`
- `apps/web/lib/blog/posts-en.ts`
- `apps/web/lib/blog/posts.ts`
- `apps/web/lib/faq-content.ts`
- `apps/web/lib/home-landing-copy.ts`
- `apps/web/lib/numbers3.ts`
- `apps/web/supabase/migrations/20260410120000_numbers3_draws.sql`
- `apps/web/supabase/migrations/20260410121000_numbers3_daily_prediction_documents.sql`
- `numbers3/__init__.py`
- `numbers3/core.py`
- `numbers3/generate_budget_plan.py`
- `numbers3/predict_ensemble.py`
- `numbers3/prediction_utils.py`
- `numbers3/run_method_predictions.py`
- `numbers3/save_method_prediction_json.py`
- `numbers3/save_prediction_history.py`
- `numbers3/save_prediction_json.py`
- `numbers3/summarize_from_json.py`
- `tools/check_numbers3_target_number.py`
- `tools/daily_predictions_json_common.py`
- `tools/ddl_numbers3_draws_postgres.sql`
- `tools/load_numbers3_csv_to_postgres.py`
- `tools/load_numbers3_daily_json_to_postgres.py`
- `tools/run_numbers3_method_predictions.py`
- `tools/run_numbers3_pipeline.py`

### commits（subject + body）

- `00fb12a` chore(web): ユーザー向け文言からDB・Supabase等の技術表記を除き平易な表現に統一

利用者向けの説明文・ヘルプ・API の人が読む説明から、Supabase やテーブル名、
「DB」「データベース」「リポジトリ」など実装詳細に寄った語を外し、
「サイトへの取り込み」「オンラインの最新データ」「サイト同梱の日次 JSON」など、
サービスとして理解しやすい言い回しに揃えた。

対象はランディングコピー、FAQ、データ出所ページ、ナンバーズ4 の入口・予測ハブ・統計・
直近照合コンポーネント、公式当選のみページ、日英ブログ本文、llms.txt / llms-full.txt の
スタック説明、OpenAPI のエンドポイント説明、および numbers4/latest API の 503 時エラー
メッセージである。画面の機能やデータ取得ロジック自体は変えず、表示テキストと
ドキュメント用の文言のみを更新している。

apps/web 配下に限定した変更であり、Supabase へのクエリや環境変数名などコード内部の
識別子は触っていない。動作確認としては `npm run lint` および `npx tsc --noEmit` を
実行し、エラーがないことを確認済みである。

Made-with: Cursor

- `6d120f3` feat(web): モデル横断のBOX組み合わせランキング表を追加

ナンバーズ4の各回詳細ページに、method予測を横断して確認できる
「BOX組み合わせランキング」カードを新設しました。各モデルの候補番号を
順不同のBOXキーへ正規化して集計し、出現回数が多い順に可視化しています。

今回の変更では、予測番号を4桁正規化したうえでBOXキー化する集計関数を追加し、
出現回数・出現モデル数・モデル一覧を同時に保持するようにしました。
同率時はモデル数とキーで並び順を安定化し、表示順のぶれを抑えています。

画面側では既存のテーブルデザインに合わせてカードを追加し、
BOX集計の定義（例: 1234 と 4321 は同一扱い）が伝わる説明文を明示しました。
これにより、アンサンブル順位だけでなく、モデル群で重なって出やすい
組み合わせを回ごとに把握しやすくしています。

動作確認としては lint を実行し、追加変更によるエラーが出ないことを確認済みです。
既存の未解消 warning は別箇所のもののみで、本変更による新規エラーはありません。

Made-with: Cursor

- `43fc52d` feat(web): ナンバーズ4詳細ページの文言整理とBOX組み合わせランキング追加 (#28)

`00fb12a` と `6d120f3` を統合したマージコミット。文言整理と BOX ランキング追加を
一本化し、numbers4 詳細ページ体験を改善。

- `c2dbcf8` feat(numbers3): add numbers3 web and automation pipeline

Numbers3 can now run through the same daily prediction, summary, analysis, and target-check flow as Numbers4, with matching API and web entry points for results and detail pages. This keeps rollout and operations symmetric across both lottery products while avoiding workflow drift.

Made-with: Cursor
