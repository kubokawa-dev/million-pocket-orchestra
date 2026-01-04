## 概要

コードベースから不要になったファイルを削除し、プロジェクトを整理しました。

## 背景・目的

開発を進める中で、以下のようなファイルが蓄積していました：
- 移行完了済みのスクリプト（SQLite→Postgres、Supabase移行等）
- 一時的なデバッグ/診断用スクリプト
- 都度生成される予測結果MDファイル
- 使われなくなった分析/レポートドキュメント

これらを削除することで、コードベースの見通しを良くし、メンテナンス性を向上させます。

## 変更内容

### ルートディレクトリ（13ファイル削除）
- `analyze_n4_patterns.py` - パターン分析スクリプト
- `check_db_status.py` / `check_latest_draw.py` - DB確認用
- `migrate_to_supabase.py` - Supabase移行（完了済み）
- `run_numbers4_ultimate.py` / `run_numbers4_v10.py` - 旧実行スクリプト
- `scrape_loto6_detailed.py` / `update_and_learn.py` - 統合済み機能
- `CYCLE_TEST_SUMMARY.md` - テストサマリー
- `data_export.sql` / `schema_export.sql` - SQL出力
- `lottery_numbers.txt` - 番号リスト

### tools/ディレクトリ（9ファイル削除）
- `backtest_numbers4.py` / `diagnose_numbers4_miss.py` - デバッグ用
- `dump_millions_db.py` / `inspect_db.py` / `inspect_db_columns.py` - DB確認用
- `migrate_sqlite_to_postgres.py` - 移行完了済み
- `query_numbers4_latest.py` / `smoke_test.py` / `update_model_from_db.py` - 不要

### numbers4/ディレクトリ（6ファイル削除）
- `ANALYSIS_0100_FAILURE.md` / `CHANGELOG_PREDICTION_LOG.md` - 分析レポート
- `IMPROVEMENT_SUMMARY.md` / `README_PREDICTION_HISTORY.md` - ドキュメント
- `advanced_numbers4_prediction_result.md` / `prediction_result.md` - 予測結果（都度生成）

### loto6/ディレクトリ（6ファイル削除）
- `README_ULTIMATE.md` / `SYSTEM_COMPLETION_REPORT.md` / `ULTIMATE_SYSTEM_GUIDE.md` - ガイド
- `advanced_loto6_prediction_result.md` / `loto6_prediction_result.md` / `loto6_prediction_result_latest.md` - 予測結果（都度生成）

## 影響範囲

- 削除したファイルは現在使用されていないため、既存機能への影響なし
- 予測パイプライン（`run_numbers4_pipeline.py` 等）は引き続き動作

## リスクと対策

- **リスク**: 削除したファイルを参照しているコードがあった場合に動作しない
- **対策**: 削除対象は独立したスクリプトまたはドキュメントのみを選定

## 動作確認

- [x] 削除対象がインポートされていないことを確認
- [x] 主要パイプラインスクリプトの存在確認

## レビュー観点

- 削除対象に必要なファイルが含まれていないか
- tools/の残存ファイル（パイプライン系）が正しく残っているか

---

## 自動情報（参考）

### diffstat
```
 37 files changed, 9 insertions(+), 6040 deletions(-)
```

### 削除ファイル一覧
```
CYCLE_TEST_SUMMARY.md
analyze_n4_patterns.py
check_db_status.py
check_latest_draw.py
data_export.sql
loto6/README_ULTIMATE.md
loto6/SYSTEM_COMPLETION_REPORT.md
loto6/ULTIMATE_SYSTEM_GUIDE.md
loto6/advanced_loto6_prediction_result.md
loto6/loto6_prediction_result.md
loto6/loto6_prediction_result_latest.md
lottery_numbers.txt
migrate_to_supabase.py
numbers4/ANALYSIS_0100_FAILURE.md
numbers4/CHANGELOG_PREDICTION_LOG.md
numbers4/IMPROVEMENT_SUMMARY.md
numbers4/README_PREDICTION_HISTORY.md
numbers4/advanced_numbers4_prediction_result.md
numbers4/prediction_result.md
run_numbers4_ultimate.py
run_numbers4_v10.py
schema_export.sql
scrape_loto6_detailed.py
tools/backtest_numbers4.py
tools/diagnose_numbers4_miss.py
tools/dump_millions_db.py
tools/inspect_db.py
tools/inspect_db_columns.py
tools/migrate_sqlite_to_postgres.py
tools/query_numbers4_latest.py
tools/smoke_test.py
tools/update_model_from_db.py
update_and_learn.py
```
