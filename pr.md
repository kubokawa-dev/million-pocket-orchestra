# 概要
`apps/web` を Git のサブモジュール（gitlink）として扱うのをやめ、Next.js アプリ一式を親リポジトリの通常ディレクトリとして管理できるようにする。クローン・CI・コードレビューを単一リポジトリで完結させ、ツール連携の摩擦を減らすのが目的。

## 変更内容
- `apps/web` の gitlink（mode `160000`）を index から外し、ネストしていた `apps/web/.git` を削除して通常ツリーとして再登録した。
- Next.js 16 ベースの Web アプリ全体（約 55 ファイル）をリポジトリに含める。shadcn（Base UI 系）の Button / Card / Table / Badge などと Tailwind の共通スタイルを利用。
- サイト全体のシェル（sticky ヘッダー、`/` と `/numbers4` 系のアクティブなピルナビ）とホームの CTA を追加・整理した。
- ナンバーズ4: `/numbers4` に予測ダッシュボード（第6949回固定のデバッグ表示、データは Supabase → `predictions/daily` の JSON → 内蔵フォールバックの優先順）、`/numbers4/result` に当選番号一覧（nuqs + ページネーション）、`/numbers4/result/[draw_number]` に詳細、旧 URL 用のリダイレクトを配置した。
- Supabase 用のクライアント（server / browser）と、`numbers4_draws`・`numbers4_daily_prediction_documents` のマイグレーションを `apps/web/supabase` に含めた。
- `buttonVariants` を `button-variants.ts` に分離し、Server Component からもスタイルを参照できるようにした。
- レポート用の読み込みヘルパ（`lib/reports/load-numbers4-report.ts`）および Markdown 表示用コンポーネント（`numbers4-report-markdown.tsx`）を同梱した。

## 背景 / 目的
- サブモジュール運用をやめ、モノレポとして `apps/web` を他パッケージと同様に扱いたい。
- `.gitmodules` が無い不完全な gitlink 状態を解消し、`git submodule` まわりのエラーを防ぎたい。

## 動作確認 / テスト
- [ ] ローカルで動作確認（`cd apps/web && npm install && npm run dev` で `/`・`/numbers4`・`/numbers4/result` を開く）
- [ ] 自動テスト（Unit/E2E）: 未実施（本 PR では `npm run build` / `npm run lint` の実行は PR 作成フロー外。マージ前に `apps/web` で実行推奨）
- [ ] 手動テスト: 未実施（上記 URL の表示・Supabase 未設定時のフォールバック挙動を確認推奨）

## スクリーンショット / 動画（UI変更がある場合）
UI 変更あり（新規アプリ取り込み）。スクショは未添付。マージ前に主要画面のキャプチャ添付を推奨。

## 影響範囲
- リポジトリ利用者: `apps/web` が独立リポジトリではなくなるため、以前サブツリーで運用していた場合は clone / 更新手順が変わる。
- CI / デプロイ: ビルドルートが `apps/web` のままなら設定変更は不要なことが多いが、リモートの設定を一度確認した方がよい。
- 履歴: `apps/web` 単体リポジトリにしか無かったコミット履歴は、このクローンからは参照できなくなる（別リモートに残しているか要確認）。

## リスクと対策
- **巨大 diff**: レビュー負荷が高い。まず「サブモジュール解除 + ファイル追加」の機械的変更と、アプリ固有ロジックを分けて見る。
- **秘密情報**: `.env*` は `.gitignore` 対象。`.env.example` のみ追加。マージ前に本番キーが含まれていないか再確認する。
- **依存**: `package-lock.json` 同梱。lockfile の整合は `npm ci` で検証可能。

## ロールアウト / リリース手順（必要なら）
- [ ] 段階リリース
- [ ] フラグで切替
- [ ] リリース後の確認項目: 本番デプロイ後、トップ・Numbers4 各ページの 200 応答と Supabase 接続エラーがないか

## レビュー観点
- `apps/web` 以下に `node_modules` や `.env.local` が紛れ込んでいないか。
- マイグレーション SQL と RLS ポリシーが意図どおりか（anon の select 範囲など）。
- 旧 URL リダイレクト（`/numbers4` → `/numbers4/result` 廃止、`/numbers4/[draw_number]` → `/numbers4/result/...`）の挙動がプロダクト要件と合うか。

## チェックリスト
- [x] 目的に沿った最小変更になっている（サブモジュール解除が主目的で、そのためにツリー全体を取り込む形）
- [x] 不要なログ/デバッグコードを削除した（コミットメッセージの `Made-with: Cursor` はメタ情報のみ）
- [ ] 仕様/ドキュメントの更新が必要なら反映した（README / 開発手順は別 PR でも可）
- [ ] 破壊的変更がある場合、影響/移行手順を書いた（clone 手順の変更は上記「影響範囲」に記載）

---

## 自動情報（参考）

### diffstat
```
 apps/web                                           |    1 -
 apps/web/.env.example                              |   23 +
 apps/web/.gitignore                                |   42 +
 ... (略: 55 files changed, 5655 insertions(+), 1 deletion(-))
```

### changed files
```
apps/web
apps/web/.env.example
apps/web/.gitignore
apps/web/AGENTS.md
apps/web/CLAUDE.md
apps/web/README.md
apps/web/app/favicon.ico
apps/web/app/globals.css
apps/web/app/layout.tsx
apps/web/app/numbers4/[draw_number]/page.tsx
apps/web/app/numbers4/numbers4-predictions-hub.tsx
apps/web/app/numbers4/page.tsx
apps/web/app/numbers4/result/[draw_number]/numbers4-report-markdown.tsx
apps/web/app/numbers4/result/[draw_number]/page.tsx
apps/web/app/numbers4/result/numbers4-draws-table.tsx
apps/web/app/numbers4/result/numbers4-pagination.tsx
apps/web/app/numbers4/result/page.tsx
apps/web/app/page.tsx
apps/web/components.json
apps/web/components/site-header.tsx
apps/web/components/site-nav.tsx
apps/web/components/ui/badge.tsx
apps/web/components/ui/button-variants.ts
apps/web/components/ui/button.tsx
apps/web/components/ui/card.tsx
apps/web/components/ui/pagination.tsx
apps/web/components/ui/separator.tsx
apps/web/components/ui/table.tsx
apps/web/eslint.config.mjs
apps/web/lib/numbers4-predictions/fallback-6949.ts
apps/web/lib/numbers4-predictions/load-6949.ts
apps/web/lib/numbers4-predictions/summarize-method.ts
apps/web/lib/numbers4-predictions/types.ts
apps/web/lib/numbers4.ts
apps/web/lib/reports/load-numbers4-report.ts
apps/web/lib/supabase/admin.ts
apps/web/lib/supabase/client.ts
apps/web/lib/supabase/server.ts
apps/web/lib/supabase/session.ts
apps/web/lib/utils.ts
apps/web/next.config.ts
apps/web/package-lock.json
apps/web/package.json
apps/web/postcss.config.mjs
apps/web/proxy.ts
apps/web/public/file.svg
apps/web/public/globe.svg
apps/web/public/next.svg
apps/web/public/vercel.svg
apps/web/public/window.svg
apps/web/supabase/.gitignore
apps/web/supabase/config.toml
apps/web/supabase/migrations/20260329120000_numbers4_draws.sql
apps/web/supabase/migrations/20260330120000_numbers4_daily_prediction_documents.sql
apps/web/tsconfig.json
```

### commits (subject+body)
```
- be3ea7b chore: inline apps/web as normal tree (remove submodule gitlink)

Drop nested .git under apps/web and track all web app files in the parent repo.

Made-with: Cursor
```
