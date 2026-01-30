# 概要
手法別予測の導入と早朝ローテ実行に加えて、ボックスタイプ分布の調整と保存候補の拡張を行い、予測の多様性と保存品質を強化しました。

## 変更内容
- 手法別予測JSONの保存と実行スクリプトを追加し、手法単位で出力できるように整備
- 日次サマリーに手法別の共通候補・TOP3・実行回数を追加して可視化を強化
- 予測ワークフローを早朝30分おきローテに変更し、手法の最低3回実行を担保
- 過去データ由来のボックスタイプ分布でスコア補正し、順列展開で保存候補を拡張
- 保存上限を150件に拡大し、元番号も含めたモデル寄与判定に対応

## 背景 / 目的
- 手法特化の予測結果を比較・集計できるようにしたい
- 予測ローテの早朝化と実行回数の担保を行いたい
- ボックスタイプ分布を実績に寄せて候補品質を高めたい

## 動作確認 / テスト
- [ ] ローカルで動作確認（未実施：次回 `workflow_dispatch` で生成物確認予定）
- [ ] 自動テスト（Unit/E2E）: 未実施
- [ ] 手動テスト: 未実施

## スクリーンショット / 動画（UI変更がある場合）
なし

## 影響範囲
- `.github/workflows/daily-numbers4-prediction.yml` / `.github/workflows/daily-numbers4-summary.yml`
- `numbers4/predict_ensemble.py` / `numbers4/save_prediction_history.py`
- 手法別JSON出力: `predictions/daily/methods/`

## リスクと対策
- Actions実行回数増加でキュー遅延の可能性 → 実行ログと生成結果の確認を推奨
- ボックス分布補正/順列展開で保存件数が増える → DB保存上限を明示し監視

## ロールアウト / リリース手順（必要なら）
- [ ] 段階リリース
- [ ] フラグで切替
- [ ] リリース後の確認項目: 予測JSON生成、手法別サマリー、DB保存件数

## レビュー観点
- 手法別JSONとサマリー集計の整合性
- 早朝ローテのスロット割り当てと最低3回の実行担保
- ボックス分布補正と順列展開のスコア影響

## チェックリスト
- [x] 目的に沿った最小変更になっている
- [x] 不要なログ/デバッグコードを削除した
- [x] 仕様/ドキュメントの更新が必要なら反映した
- [ ] 破壊的変更がある場合、影響/移行手順を書いた

---
## 自動情報（参考）
### diffstat
 .github/workflows/daily-numbers4-prediction.yml | 118 ++++++++++++-
 .github/workflows/daily-numbers4-summary.yml    |   9 +-
 numbers4/predict_ensemble.py                    | 158 +++++++++++++++--
 numbers4/save_method_prediction_json.py         |  88 ++++++++++
 numbers4/save_prediction_history.py             |  12 +-
 numbers4/summarize_from_json.py                 | 216 +++++++++++++++++++++++-
 tools/run_numbers4_method_predictions.py        | 216 ++++++++++++++++++++++++
 7 files changed, 793 insertions(+), 24 deletions(-)

### changed files
.github/workflows/daily-numbers4-prediction.yml
.github/workflows/daily-numbers4-summary.yml
numbers4/predict_ensemble.py
numbers4/save_method_prediction_json.py
numbers4/save_prediction_history.py
numbers4/summarize_from_json.py
tools/run_numbers4_method_predictions.py

### commits (subject+body)
- 4d8416c feat(numbers4): 手法別予測と早朝ローテを追加

手法別の予測JSON保存と専用実行スクリプトを追加し、手法単位の出力を整備した。
日次サマリーに手法別の共通候補・TOP3・実行回数の集計を統合して可視化を強化した。
予測ワークフローを早朝30分おきのローテに変更し、手法スロット選択と実行回数の担保を行った。
手法別予測JSONのコミット対象を追加し、サマリー生成時に手法別ディレクトリを参照するよう調整した。
動作確認は未実施のため、次回のworkflow_dispatch実行で生成物の確認を推奨する。

- 18005b6 feat(numbers4): ボックス分布調整と保存拡張

過去実績に基づくボックスタイプ分布の算出とスコア補正を追加し、予測の分布バランスを調整した。
ストレート当て向けにボックスの順列展開を導入し、保存用の候補数を拡張できるようにした。
予測候補の保存上限を150件に拡大し、モデル寄与判定に元番号も考慮するよう改善した。
動作確認は未実施のため、次回の予測実行で保存件数と出力の確認を推奨する。
