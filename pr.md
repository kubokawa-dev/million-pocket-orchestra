# 概要

リポジトリルートに **pnpm ワークスペース** と **Turborepo** を導入し、`build` / `dev` / `lint` をルートから `turbo run` で回せる基盤を追加する。あわせて `packages/config` にプレースホルダパッケージを置き、Turbo のタスク定義（成果物なしビルドの扱い）を検証できるようにした。

なお、現在の `origin/main`（`f4c347c`）より手前のコミット（`37cf57b`）から分岐しているため、**本 PR の差分には `predictions/daily/methods/**/numbers4_6947.json` の更新差分も含まれる**（メイン側にのみ入っている直近の予測コミットとのツリー差分）。意図する変更はモノレポ基盤まわりなので、マージ前に **`main` を取り込むか rebase して予測 JSON のノイズを消す**ことを強く推奨する。

## 変更内容

- ルートに `package.json` を追加し、`private`・`packageManager`（pnpm 固定）・`turbo` を devDependency として宣言。スクリプトは `turbo run build|dev|lint` に集約した。
- `pnpm-workspace.yaml` で `apps/*` と `packages/*` をワークスペース化し、`pnpm-lock.yaml` で依存解決を固定した（ロックには Next.js / React / Tailwind / ESLint / shadcn / `@base-ui/react` などが `apps/web` 向けに記録されている）。
- `turbo.json` で `build`（上位 `build` 依存、`dist` / `.next` 出力想定）、`lint`、`dev`（キャッシュ無効・永続）を定義した。
- `packages/config` に no-op の `build` / `lint` スクリプトを持つパッケージを追加し、同梱の `turbo.json` で `build` の `outputs` を空にして Turbo の警告を避けた。
- `apps/web` を **git サブモジュール（gitlink）** として登録している。単一リポジトリ内に Next アプリのソースを置く運用なら、サブモジュールが意図と一致するか要確認。
- （上記分岐の結果として）`predictions/daily/methods/**/numbers4_6947.json` が `main` とのツリー差分として表示される。

## 背景 / 目的

ブランチ名（`feature/add-turborepo-with-web-app`）およびコミット本文から、**Python 中心の既存リポジトリにフロントエンド用のモノレポ基盤を足し、以降 `apps/web` で Web を育てる**ことが目的と読み取れる。Turborepo によりタスクのキャッシュ・依存関係（`^build`）を明示し、パッケージが増えた後のビルドや CI 運用をしやすくする。

## 動作確認 / テスト

- [ ] ローカルで動作確認（**未実施**: コミット本文でも merge 前の `pnpm install` / `pnpm build` / `pnpm lint` 再実行が推奨とされていたため、マージ前に実施予定）
- [ ] 自動テスト（Unit/E2E）: 対象なし（本変更は主に Node ツールチェーン追加）
- [ ] 手動テスト: サブモジュールとしての `apps/web` が clone 後に意図どおり取得できるか、`pnpm install` 後にルートから `pnpm build` が通るかを確認する

## スクリーンショット / 動画（UI変更がある場合）

UI の見た目の変更はない（ツールチェーン・リポジトリ構成の変更）。

## 影響範囲

- **開発者**: ルートで `pnpm` / `turbo` を使う前提が増える。既存の Python ワークフローとは独立だが、CI や README に追記が必要になる可能性がある。
- **`apps/web`**: サブモジュール参照のため、clone 時に `--recurse-submodules` 等が必要になる場合がある。
- **`pnpm-lock.yaml`**: 大きな追加があり、レビューは差分より「何がロックされたか」の要約で十分なことが多い。
- **予測 JSON**: 上記のとおり `main` との分岐により差分に含まれる。実質的な意図した変更ではない可能性が高い。

## リスクと対策

- **サブモジュール運用のミスマッチ**: 単一リポジトリで管理したい場合、gitlink のままだと期待と異なる。対策: 方針に合わせて通常ディレクトリに差し替えるか、サブモジュール運用をドキュメント化する。
- **`main` との分岐によるノイズ差分**: レビュー負荷と誤マージリスク。対策: **`main` を取り込み（merge または rebase）**してから PR を更新する。
- **ロックファイルの肥大化**: 依存の追加・更新時にコンフリクトしやすい。対策: コンフリクト時は `pnpm install` で再生成を基本とする。

## ロールアウト / リリース手順（必要なら）

- [ ] 段階リリース
- [ ] フラグで切替
- [ ] リリース後の確認項目: 本 PR はライブラリ配布ではなくリポジトリ構成変更のため、デプロイ対象があれば `apps/web` 側のパイプラインで `pnpm build` が通ることを確認する

## レビュー観点

- `apps/web` をサブモジュールにした意図がプロジェクト方針と一致するか。
- `turbo.json` の `outputs` / `dev` の `persistent` 設定が、今後追加するアプリ（Next 等）と整合するか。
- `origin/main` との分岐による `predictions/**` の差分を、**意図した変更として扱うか、rebase して除去するか**の判断。
- ルート `.gitignore` と Node 成果物（`node_modules` / `.turbo` 等）の扱いが既に十分か（既存設定を踏襲している想定）。

## チェックリスト

- [x] 目的に沿った最小変更になっている（意図はモノレポ基盤。分岐による JSON 差分は別途整理推奨）
- [x] 不要なログ/デバッグコードを削除した（該当なし）
- [ ] 仕様/ドキュメントの更新が必要なら反映した（README への `pnpm install` 手順追記は未対応の可能性 — 必要なら別コミット）
- [ ] 破壊的変更がある場合、影響/移行手順を書いた（サブモジュール化はクローン手順に影響しうるため、チーム合意とドキュメント化を推奨）

---

## 自動情報（参考）

### diffstat（`origin/main..HEAD`）

```
 apps/web                                           |    1 +
 package.json                                       |   13 +
 packages/config/package.json                       |    9 +
 packages/config/turbo.json                         |   8 +
 pnpm-lock.yaml                                     | 6174 ++++++++++++++++++++
 pnpm-workspace.yaml                                |    3 +
 .../daily/methods/box_pattern/numbers4_6947.json   |  115 +-
 .../daily/methods/cold_revival/numbers4_6947.json  |  115 +-
 .../daily/methods/hot_pair/numbers4_6947.json      |  115 +-
 .../methods/sequential_pattern/numbers4_6947.json  |  115 +-
 turbo.json                                         |   14 +
 11 files changed, 6230 insertions(+), 452 deletions(-)
```

### changed files（`origin/main..HEAD`）

```
apps/web
package.json
packages/config/package.json
packages/config/turbo.json
pnpm-lock.yaml
pnpm-workspace.yaml
predictions/daily/methods/box_pattern/numbers4_6947.json
predictions/daily/methods/cold_revival/numbers4_6947.json
predictions/daily/methods/hot_pair/numbers4_6947.json
predictions/daily/methods/sequential_pattern/numbers4_6947.json
turbo.json
```

### commits（subject+body, `origin/main..HEAD`, `--reverse`）

- aab0f36 build: ルートにpnpmワークスペースとTurborepoを導入する

ブランチ名からチケット形式のIDは抽出できなかったため、タイトルにはIDを付けていない。

リポジトリルートに package.json を追加し、private かつ packageManager に pnpm を固定したうえで、build・dev・lint を turbo run 経由で実行できるようにした。開発用依存として Turborepo（turbo）を宣言し、モノレポ全体のタスク実行の入口をルートに集約している。

pnpm-workspace.yaml で apps/* と packages/* をワークスペース対象にし、pnpm-lock.yaml で依存関係を確定させた。ロックファイル上は apps/web 向けに Next.js・React・Tailwind・ESLint、shadcn 関連、@base-ui/react などが解決済みとして記録されており、フロントエンドアプリをワークスペースの一員として扱う前提が読み取れる。

turbo.json では build に上位パッケージの build への依存と、dist や .next を想定した outputs を定義し、lint・dev もパイプライン対象に含めた。dev はキャッシュを無効化しつつ永続プロセスとして扱う設定にしている。packages/config にはビルド・lint が実質 no-op のプレースホルダパッケージを置き、同ディレクトリの turbo.json で build の outputs を空にして、成果物のないタスクでも Turbo 側の警告が出にくいようにしている。

apps/web はディレクトリツリーとしての一括追加ではなく、gitlink（サブモジュール）として特定コミットを指す形でステージされている。意図が「単一リポジトリ内に Next アプリのソースを置く」ことであれば、サブモジュール登録が本当に望ましいかを確認した方がよい。

動作確認としては、ここではステージ済み差分のコミットのみ実施し、merge 前にルートで pnpm install および pnpm build / pnpm lint を改めて流すことを推奨する。

Made-with: Cursor
