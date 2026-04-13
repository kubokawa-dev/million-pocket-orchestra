# 概要

ナンバーズ3ゾーンで、ナンバーズ4と同様に **日次の ensemble / method / budget_plan を読み込み、回ごとに当せんと照合して表示する** Web 機能を追加する。これまで当せん一覧・簡易詳細に留まっていた導線を、予測データの有無に応じたハブ表示・公式フォールバック・SEO 付きの結果ページまで一貫させる。

## 変更内容

- **データ取得層**: `numbers3_daily_prediction_documents` と `predictions/daily` の `numbers3_*.json` / `methods/*` を、DB 優先・無ければリポジトリ JSON で読む `load-numbers3` 一式を追加した。
- **3桁向けロジック**: 正規化・ストレート／ボックス照合、手法 JSON の要約、寄与モデル集計を numbers3 用に切り出した。`buildMethodConsensus` に桁数引数を追加し、3桁・4桁の双方で使えるようにした。
- **UI**: `Numbers3PredictionsHub` を新設し、アンサンブル・手法別・予算プラン系カード、直近5回の当せん×method 照合などをナンバーズ4のハブに近い構成で表示する。予測が無い回は `Numbers3OfficialDrawDetail` にフォールバックする。
- **結果ページ**: `/numbers3/result/[回]` を、公式リンク・前後回・同月回・共有ツールバー・JSON-LD を含むレイアウトに差し替え、ハブを埋め込んだ。
- **ハブ `/numbers3`**: 当せんの最新取り込み回と、試算データの最新対象回を分けて案内し、試算ページへの導線を明示した。
- **共有部品**: `Numbers4RecentModelHits` に結果 URL と「何桁の当選か」を渡せるオプションを追加し、ナンバーズ3から再利用できるようにした。

## 背景 / 目的

ナンバーズ4では既にマルチモデルの試算と当せんの照合が一画面で見られる一方、ナンバーズ3は当せんのみで **試算 JSON や Supabase の予測ドキュメントと UI が結びついていなかった**。利用者の期待（「4と同じように見たい」）に応え、保守しやすいよう numbers4 のパターン（読み込み層・型・ハブの責務分離）に寄せた。

## 動作確認 / テスト

- [x] ローカルで動作確認（コードレビュー相当: 型・ルート構成の整合）
- [x] 自動テスト: リポジトリルートで `pnpm test:python` → 30 件すべて成功
- [ ] 手動テスト: `/numbers3`・`/numbers3/result/<回>` での実ブラウザ確認は **未実施**（デプロイ後またはローカル `pnpm dev` での確認を推奨）

## スクリーンショット / 動画（UI変更がある場合）

未添付。マージ前にナンバーズ3の結果ページ（試算あり／当せんのみ）のスクショを1枚ずつあるとレビューが楽になる。

## 影響範囲

- **利用者**: ナンバーズ3の `/numbers3`・`/numbers3/result/[回]` の表示・導線が変わる（当せんのみだった詳細ページが予測ハブ中心になる）。
- **開発者**: `apps/web/lib/numbers3-predictions/*` と `numbers3-predictions-hub.tsx` が新規の主要拠点。`numbers4-predictions/consensus.ts` のシグネチャ変更に注意（第3引数は省略時 4 桁のまま）。
- **インフラ**: Supabase の `numbers3_daily_prediction_documents` が無い環境でも、同梱 JSON があれば表示可能。

## リスクと対策

- **大きな TSX 追加**: ハブファイルが肥大化しているため、将来の共通化・分割時に差分が読みにくくなりうる。必要になった段階で numbers4 と共通のサブコンポーネント抽出を検討する。
- **既存 URL の意味変更**: `/numbers3/result/[回]` が「当せん表のみ」から「試算＋照合」に変わる。ブックマーク利用者向けにリリースノートや FAQ 更新があると安心。
- **Lint 警告**: コミット時点で `numbers4-predictions-hub` や API ルートに既存の unused 警告が残る可能性がある（本 PR では numbers3 側の新規警告は抑止済み）。

## ロールアウト / リリース手順（必要なら）

- [ ] 段階リリース
- [ ] フラグで切替
- [x] リリース後の確認項目: 本番 Supabase に numbers3 の予測ドキュメントが入っている環境で、対象回の試算が表示されるか／当せんのみ回でフォールバックになるかを spot で確認する

## レビュー観点

- **3桁照合**: `normalizeNumbers3` / `classifyHit` / 寄与モデル集計が、ストレート・ボックスの解釈として妥当か。
- **フォールバック順**: DB → FS → 内蔵デモの優先順位と、404 になる条件（予測も当せんも無い回）が意図どおりか。
- **Numbers4 への副作用**: `consensus.ts` の第3引数デフォルトと、`Numbers4RecentModelHits` のデフォルト挙動が従来と変わっていないか。

## チェックリスト

- [x] 目的に沿った最小変更になっている
- [x] 不要なログ/デバッグコードを削除した
- [ ] 仕様/ドキュメントの更新が必要なら反映した（README のナンバーズ3説明は未更新の可能性あり）
- [x] 破壊的変更がある場合、影響/移行手順を書いた（URL 同一・表示内容変更を上記に記載）

---

## 自動情報（参考）

### diffstat（origin/main...HEAD）

```
 .../web/app/numbers3/ensemble-contributor-cell.tsx |  123 ++
 .../app/numbers3/numbers3-official-draw-detail.tsx |  128 ++
 apps/web/app/numbers3/numbers3-predictions-hub.tsx | 2027 ++++++++++++++++++++
 apps/web/app/numbers3/page.tsx                     |  111 +-
 .../web/app/numbers3/result/[draw_number]/page.tsx |  237 +--
 .../numbers4/result/numbers4-recent-model-hits.tsx |   58 +-
 apps/web/components/numbers3-draw-page-chrome.tsx  |  144 ++
 apps/web/lib/numbers3-draw-neighbors.ts            |   78 +
 apps/web/lib/numbers3-draw-page-seo.ts             |   33 +
 apps/web/lib/numbers3-official-sources.ts          |   15 +
 .../numbers3-predictions/ensemble-contributors.ts  |   48 +
 .../lib/numbers3-predictions/fallback-numbers3.ts  |   44 +
 apps/web/lib/numbers3-predictions/load-numbers3.ts |  412 ++++
 .../numbers3-predictions/prediction-hit-utils.ts   |   49 +
 .../lib/numbers3-predictions/summarize-method.ts   |   50 +
 apps/web/lib/numbers4-predictions/consensus.ts     |    3 +-
 16 files changed, 3415 insertions(+), 145 deletions(-)
```

### changed files

- apps/web/app/numbers3/ensemble-contributor-cell.tsx
- apps/web/app/numbers3/numbers3-official-draw-detail.tsx
- apps/web/app/numbers3/numbers3-predictions-hub.tsx
- apps/web/app/numbers3/page.tsx
- apps/web/app/numbers3/result/[draw_number]/page.tsx
- apps/web/app/numbers4/result/numbers4-recent-model-hits.tsx
- apps/web/components/numbers3-draw-page-chrome.tsx
- apps/web/lib/numbers3-draw-neighbors.ts
- apps/web/lib/numbers3-draw-page-seo.ts
- apps/web/lib/numbers3-official-sources.ts
- apps/web/lib/numbers3-predictions/ensemble-contributors.ts
- apps/web/lib/numbers3-predictions/fallback-numbers3.ts
- apps/web/lib/numbers3-predictions/load-numbers3.ts
- apps/web/lib/numbers3-predictions/prediction-hit-utils.ts
- apps/web/lib/numbers3-predictions/summarize-method.ts
- apps/web/lib/numbers4-predictions/consensus.ts

### commits (subject+body)

- 103a661 feat(web): ナンバーズ3にナンバーズ4相当のモデル試算・当選照合UIを追加

（本文はコミットメッセージと同一のため省略）
