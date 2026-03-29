# 概要

ナンバーズ4 予測ハブのアンサンブル表で、「寄与モデル」列を `<details>` 展開から Base UI のツールチップ表示に切り替えた。行の高さがクリックで変わってテーブルが崩れる問題を解消しつつ、一致／ボックスのモデル内訳はホバーやキーボードフォーカスで確認できるようにする。

## 変更内容

- アンサンブル表の寄与モデル表示から `<details>` を廃止し、セルは常に1行（「一致 N」「ボックス N」）に固定した。
- 「一致」「ボックス」それぞれをツールチップのトリガーとし、モデル名一覧と説明をポップアップ（Portal）で表示する。一覧が長い場合はツールチップ内のみスクロールする。
- `EnsembleContributorCell` を `apps/web/app/numbers4/ensemble-contributor-cell.tsx` に切り出し、クライアントコンポーネントとして Base UI `Tooltip` と連携させた。
- 共通の `HelpTooltip` / `HelpTooltipProvider` を `apps/web/components/ui/help-tooltip.tsx` に追加した（`closeDelay` など一覧閲覧向けの調整を含む）。
- 予測ハブの注釈テキストおよび「寄与モデル」列見出しの `title` を、ツールチップ操作に合わせて更新した。

## 背景 / 目的

寄与モデル列で内訳を開くと行高が伸び、アンサンブル表のレイアウトが崩れるという利用上の課題があった。詳細は見せつつ表の見た目を安定させるため、インライン展開ではなくオーバーレイ型のツールチップに変更する。

## 動作確認 / テスト

- [x] ローカルで動作確認（コミット時点で `pnpm run build` 成功を確認済み）
- [ ] 自動テスト（Unit/E2E）: 本変更では未実行。CI の `lint` / `build` に任せる。
- [ ] 手動テスト: 予測ハブのアンサンブル表で「一致」「ボックス」にカーソルを載せ／Tab でフォーカスし、ツールチップとキーボード操作を確認することを推奨。

## スクリーンショット / 動画（UI変更がある場合）

未添付。マージ前に Before（展開で行が伸びる）/ After（1行＋ツールチップ）のキャプチャを足すとレビューがしやすい。

## 影響範囲

- `apps/web` のナンバーズ4 予測ハブ（`numbers4-predictions-hub.tsx`）のアンサンブル表のみ。
- 新規 UI プリミティブ `help-tooltip.tsx` は他画面からも import 可能だが、本 PR では当該寄与列のみで使用。

## リスクと対策

- **タッチデバイス**: ホバーが使えない環境ではフォーカス操作が必要になる。必要なら将来ポップオーバー化やタップ対応を検討する。
- **Base UI / Portal**: z-index は `z-50` を指定。極端に重なり順の高いモーダルと干渉する場合は調整が必要。
- **クライアント境界**: 寄与セル周りのバンドルがわずかに増えるが、表示箇所は限定的。

## ロールアウト / リリース手順（必要なら）

- [ ] 段階リリース
- [ ] フラグで切替
- [x] リリース後の確認項目: Web デプロイ後、予測ハブのアンサンブル表で寄与列のツールチップが期待どおり開くかを確認。

## レビュー観点

- ツールチップの開閉・`closeDelay` が長い一覧でも読みやすいか。
- アクセシビリティ（フォーカスリング、意味のある `title`）が十分か。
- `help-tooltip.tsx` の API（`contentClassName` 等）が今後の再利用に耐えるか。

## チェックリスト

- [x] 目的に沿った最小変更になっている
- [x] 不要なログ/デバッグコードを削除した
- [x] 仕様/ドキュメントの更新が必要なら反映した（画面上の注釈を更新）
- [x] 破壊的変更がある場合、影響/移行手順を書いた（利用者向け操作が「展開」から「ホバー／フォーカス」に変わる旨を本文に記載）

---

## 自動情報（参考）

### diffstat（origin/main...HEAD）

```
 .../web/app/numbers4/ensemble-contributor-cell.tsx | 123 +++++++++++++++++++++
 apps/web/app/numbers4/numbers4-predictions-hub.tsx |  80 ++------------
 apps/web/components/ui/help-tooltip.tsx            |  80 ++++++++++++++
 3 files changed, 211 insertions(+), 72 deletions(-)
```

### changed files

- `apps/web/app/numbers4/ensemble-contributor-cell.tsx`
- `apps/web/app/numbers4/numbers4-predictions-hub.tsx`
- `apps/web/components/ui/help-tooltip.tsx`

### commits（subject + body）

- `4a052cc` feat(web): ナンバーズ4アンサンブル表の寄与モデル列をツールチップ化してレイアウト崩れを解消

アンサンブル表の「寄与モデル」列では、これまで `<details>` で「一致」「ボックス」の内訳を展開しており、クリックで行の高さが変わってテーブルレイアウトが崩れる問題があった。利用者からも同様の指摘があったため、行の高さを一定に保ちつつ詳細を見られる UI に切り替えた。

`EnsembleContributorCell` をクライアントコンポーネントとして `apps/web/app/numbers4/ensemble-contributor-cell.tsx` に切り出し、「一致 N」「ボックス N」をそれぞれ Base UI の `Tooltip` トリガーにした。説明文とモデル一覧はポータル経由のポップアップに表示し、長い場合はツールチップ内だけスクロールする。ホバーに加え、キーボードフォーカスでも開くよう `focus-visible` のリングを付与している。

再利用のため `@/components/ui/help-tooltip.tsx` を新設し、`HelpTooltip` と複数ツールチップ向けの `HelpTooltipProvider` を定義した。予測ハブ側では列見出しの `title` と注釈テキストを、ツールチップ操作に合わせて更新した。

影響範囲はナンバーズ4予測ハブのアンサンブル表および新規 UI コンポーネントに限定される。`pnpm run build` でビルドが通ることを確認済み。

Made-with: Cursor
