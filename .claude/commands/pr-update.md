# /pr-update

`git` と `gh` だけで、**現在ブランチに紐づくPRの本文/タイトルを更新**します。コミットログ（subject+body）を読み、テンプレに沿って“文章で要約”した本文に更新します。

## 引数（任意）
- `base=<branch>`: ベースブランチ（既定: `main`）
- `title=<text>`: タイトルを固定（指定なしなら既存タイトル維持 or 差分から再提案）
- `labels=a,b,c`: ラベルを追加（`gh pr edit --add-label`）
- `rebuild`: 本文をテンプレ（`.cursor/PR_TEMPLATE.md`）から再生成して上書き（手書き部分も上書きされます）

## ゴール
- `gh pr view` で「このブランチのPR」を特定
- コミットログと差分を読み、テンプレの各セクションを**文章で更新**する
- 末尾に参考情報（diffstat / changed files / commits）を付ける

## 収集コマンド（まずこれで素材を集める）

```bash
set -euo pipefail

BASE="${BASE_BRANCH:-main}"
HEAD_BRANCH="$(git branch --show-current)"
if [ "$HEAD_BRANCH" = "main" ]; then
  echo "You are on main. Switch to a feature branch before updating a PR." >&2
  exit 1
fi

# PR番号（このブランチのPR）を取得
PR_NUMBER="$(gh pr view --json number -q .number 2>/dev/null || true)"
if [ -z "$PR_NUMBER" ]; then
  echo "No PR found for current branch. Run /pr-create first." >&2
  exit 1
fi

RANGE="origin/${BASE}...HEAD"
git rev-parse --verify "origin/${BASE}" >/dev/null 2>&1 || RANGE="${BASE}...HEAD"

echo "### current PR body (for reference)"
gh pr view "$PR_NUMBER" --json body -q .body
echo

echo "### commits (subject+body)"
git log --reverse "${RANGE}" --pretty=format:'- %h %s%n%n%b%n'
echo

echo "### diffstat"
git diff --stat "${RANGE}"
echo

echo "### changed files"
git diff --name-only "${RANGE}"
```

## 更新のルール（ここが“本気”ポイント）
- 既存PR本文の “いいところ” は尊重しつつ、**テンプレの各セクションを文章で更新**する。
- `rebuild` が指定されたら、既存本文は参考にせず、テンプレから作り直す（空欄は残さない。不明なら質問）。
- 末尾に `---` を入れて `## 自動情報（参考）` として diffstat / changed files / commits を付ける。

## PR更新（最終実行）
> 更新した本文を `pr.md` に保存してから実行してください。

```bash
PR_NUMBER="$(gh pr view --json number -q .number 2>/dev/null || true)"

TITLE_FLAG=""
if [ -n "${PR_TITLE:-}" ]; then
  TITLE_FLAG="--title ${PR_TITLE}"
fi

ADD_LABEL_FLAG=""
if [ -n "${PR_LABELS:-}" ]; then
  ADD_LABEL_FLAG="--add-label ${PR_LABELS}"
fi

gh pr edit "$PR_NUMBER" \
  --body-file pr.md \
  $TITLE_FLAG \
  $ADD_LABEL_FLAG
```

## 使い方（スラッシュコマンドでの指定）
- `base=develop` → `BASE_BRANCH=develop`
- `title=...` → `PR_TITLE=...`
- `labels=a,b` → `PR_LABELS=a,b`
- `rebuild` → `PR_REBUILD=true`


