## 概要

Numbers4の予測ワークフローを強化し、平日に10回の予測を実行して結果をサマリーとしてまとめる機能を追加しました。

## 背景・目的

- 1日1回の予測だと、その時点でのモデル状態に依存しすぎてしまう
- 複数回予測を実行し、安定して上位に来る番号を特定することで、より信頼性の高い予測を提供したい
- 予測結果を見やすいMarkdown形式でまとめ、外部サービスへの通知も可能にしたい

## 変更内容

- **ワークフローのリネームと最適化**
  - `daily-loto6-prediction.yml` → `daily-numbers4-prediction.yml` にリネーム
  - Numbers4専用のワークフローとして整理し、Loto6予測とLINE通知を削除
  - 実行スケジュールを平日6:00〜15:00の毎時10回に変更

- **サマリー生成ワークフローの新規作成**
  - `daily-numbers4-summary.yml` を新規作成
  - 平日16:00に実行され、1日の予測結果をMarkdownでまとめる
  - LINE/Discord/Slack/Email/GitHub Issueへの通知に対応（コメントアウト状態）

- **予測サマリースクリプトの実装**
  - `summarize_daily_predictions.py` を新規作成
  - 同一回号の複数予測を集計し、安定上位予測をランキング
  - 出現率・平均スコア・最高順位・安定度などを可視化

- **通知スクリプトの改修**
  - `send_notification.py` を複数通知サービス（LINE/Discord/Slack/Email/GitHub Issue）対応に改修
  - サマリーからTOP5予測を抽出して通知メッセージを生成

## 影響範囲

- GitHub Actionsのワークフロー実行スケジュール
- `predictions/` ディレクトリへのMarkdownファイル出力
- 通知機能（設定後に有効化）

## リスクと対策

- **GitHub Actionsの無料枠消費**: 平日10回×月22日=220回/月の実行となるが、無料枠内に収まる見込み
- **cron実行の遅延**: GitHub Actionsのcronは混雑時に5〜15分遅れる可能性あり（許容範囲）

## レビュー観点

- [ ] cronスケジュールのUTC/JST変換が正しいか
- [ ] サマリー生成スクリプトのMarkdown出力が適切か
- [ ] 通知スクリプトの各サービス対応が正しいか

## 動作確認

- [x] ローカルでのサマリー生成スクリプト動作確認
- [ ] GitHub Actions での実行確認（マージ後）

---

## 自動情報（参考）

### diffstat
```diff
 .github/workflows/daily-numbers4-prediction.yml |  20 +-
 .github/workflows/daily-numbers4-summary.yml    | 104 ++++++
 numbers4/model_state.json                       |  84 ++---
 numbers4/summarize_daily_predictions.py         | 370 +++++++++++++++++++++
 pr.md                                           | 134 ++++----
 tools/send_notification.py                      | 348 +++++++++++--------
 6 files changed, 783 insertions(+), 277 deletions(-)
```

### changed files
- .github/workflows/daily-numbers4-prediction.yml
- .github/workflows/daily-numbers4-summary.yml
- numbers4/model_state.json
- numbers4/summarize_daily_predictions.py
- tools/send_notification.py

### commits
- 303b12c feat(numbers4): 平日10回予測とサマリー通知ワークフローの追加
