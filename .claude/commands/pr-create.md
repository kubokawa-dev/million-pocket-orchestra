# /pr-create

`git` と `gh` だけで、**現在ブランチの“全コミットログ（subject+body）”と差分を読み、PRテンプレに沿って“文章で要約”した本文とタイトルを作って PR を作成**します。

## 引数（任意）
- `base=<branch>`: ベースブランチ（既定: `main`）
  - 例: `/pr-create base=develop`
- `draft`: Draft で作成
  - 例: `/pr-create draft`
- `title=<text>`: タイトルを固定
- `labels=a,b,c`
- `reviewers=a,b,c`

## ゴール
- PR テンプレ（`.cursor/PR_TEMPLATE.md`）に沿って、**ブランチの全コミット**を読み「文章で要約」して本文を埋め、`gh pr create` で PR を作成する
- タイトルは「変更の主語 + 何をしたか」が分かる形で適切に作る（必要なら `title=` で上書き）

## 進め方（エージェント手順）
1. 現在ブランチを確認（`git branch --show-current`）。`main` なら止めて確認する（PR作成は通常しないため）。
2. ベースブランチを決定（引数 `base=` がなければ `main`）。
3. `git fetch` して `origin/<base>` を最新化（可能なら）。
4. 差分範囲を決定（`origin/<base>...HEAD` を優先。無理なら `<base>...HEAD`）。
5. **コミットログ（range内）を全件取得**（subject+body）して「何を・なぜ・どう変えたか」を把握する。
6. 差分の概要（diffstat、変更ファイル、重要そうな差分）を確認して「影響範囲/リスク/テスト観点」を立てる。
7. `PR_TEMPLATE.md` の各セクションを、コミットログを根拠に**文章で埋める**（空欄は残さない。不明なら質問する）。
8. タイトル案を作る:
   - `title=` 指定があればそれを使用
   - それ以外は、コミット全体から最も代表的な変更を1行に圧縮して作る（例: `chore(cursor): add PR create/update commands`）
9. `gh pr create` を実行し、作成した PR URL を返す。

## 収集コマンド（まずこれを実行して素材を集める）
> ※ ここでいう `<range>` は `origin/<base>...HEAD`（fallback: `<base>...HEAD`）

```bash
git fetch origin --prune || true

BASE="${BASE_BRANCH:-main}"
RANGE="origin/${BASE}...HEAD"
git rev-parse --verify "origin/${BASE}" >/dev/null 2>&1 || RANGE="${BASE}...HEAD"

echo "### commits (subject+body)"
git log --reverse "${RANGE}" --pretty=format:'- %h %s%n%n%b%n'
echo

echo "### diffstat"
git diff --stat "${RANGE}"
echo

echo "### changed files"
git diff --name-only "${RANGE}"
```

## 要約のルール（ここが“本気”ポイント）
- **コミットsubjectの羅列は禁止**（参考として末尾に付けるのはOK）。テンプレの `## 変更内容` は必ず“文章として整理した変更点”を書く。
- **テンプレの全セクションを埋める**。不明な項目は「推測で書く」のではなく、**ユーザーに質問**してからPRを作る。
- **変更内容の書き方**: 3〜8個の箇条書きにまとめ、同じテーマのコミットは統合する（例: 設定追加/リファクタ/テスト追加 など）。
- **背景/目的**: コミットbodyやブランチ名から読み取れる「なぜ」を1〜3行で。
- **影響範囲/リスクと対策/レビュー観点**: 差分（変更ファイルやdiffstat）を根拠に、最低でも1〜3項目を具体的に。
- **動作確認**: コミットログから分かる範囲で埋め、未実施なら「未実施（理由/次のアクション）」を明記。

## PR本文の構成（必ずこの順序）
1. `.cursor/PR_TEMPLATE.md` をベースに本文を作る（見出しは同一）
2. 末尾に `---` を入れて、参考として以下を付ける:
   - `## 自動情報（参考）`
   - diffstat / changed files / commits (subject+body)

## PR作成（最終実行）
> 生成した本文を `pr.md` に保存してから実行してください。

```bash
BASE="${BASE_BRANCH:-main}"
HEAD_BRANCH="$(git branch --show-current)"

DRAFT_FLAG=""
[ "${PR_DRAFT:-false}" = "true" ] && DRAFT_FLAG="--draft"

LABELS_FLAG=""
[ -n "${PR_LABELS:-}" ] && LABELS_FLAG="--label ${PR_LABELS}"

REVIEWERS_FLAG=""
[ -n "${PR_REVIEWERS:-}" ] && REVIEWERS_FLAG="--reviewer ${PR_REVIEWERS}"

gh pr create \
  --base "$BASE" \
  --head "$HEAD_BRANCH" \
  --title "${PR_TITLE:?set PR_TITLE or pass title=...}" \
  --body-file pr.md \
  $DRAFT_FLAG \
  $LABELS_FLAG \
  $REVIEWERS_FLAG
```

## 使い方（スラッシュコマンドでの指定）
スラッシュコマンドの後ろに書いた文字列を解釈して、上の bash で環境変数へ流し込みます:
- `base=develop` → `BASE_BRANCH=develop`
- `draft` → `PR_DRAFT=true`
- `labels=a,b` → `PR_LABELS=a,b`
- `reviewers=foo,bar` → `PR_REVIEWERS=foo,bar`
- `title=...` → `PR_TITLE=...`


