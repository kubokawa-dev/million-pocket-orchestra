# /git:commit

staged に上がっている差分 **だけ** を対象に、過去の「しっかりしたコミットメッセージ」の雰囲気を抽出して、Conventional Commits 形式の **日本語コミットメッセージ（本文は詳しめ）** を作り、`git commit` まで実行してください。

## 引数（任意）
- `type=<feat|fix|chore|refactor|test|docs|style|perf|build|ci>`: typeを固定
- `scope=<text>`: scopeを固定（例: `frontend-admin`）
- `title=<text>`: タイトル要約（日本語）を固定（type/scope/IDは自動付与）
- `dry-run`: コミットはせず、メッセージ案だけ出す
- `no-verify`: `git commit --no-verify`

## ゴール
- **staged差分のみ**でコミットする（unstagedは絶対に含めない）
- タイトルは `type(scope): ID 要約` を基本形にする
  - scopeが不要なら `type: ID 要約`
  - IDが無ければ `type(scope): 要約`
- コミット本文は、作業内容を**文章で整理**して詳しく記載（subjectの羅列は禁止）
- 日本語でシンプルで分かりやすい表現にする

## 進め方（必須手順）
1. 現在ブランチ名を取得: `git branch --show-current`
2. staged が空なら中断:
   - `git diff --cached --name-only` が空 → 「先に stage してね」で終了
3. staged 情報を収集（**これだけ**を根拠にする）:
   - `git diff --cached --name-status`
   - `git diff --cached --stat`
   - `git diff --cached`（長い場合は要点抽出して良いが、判断根拠はstaged）
4. 過去コミットの「雰囲気」を抽出:
   - `git log -n 200 --format=%s`
   - `^(feat|fix|chore|refactor|test|docs|style|perf|build|ci)(\\([^)]*\\))?: ` に一致するものを優先して20件程度ピックアップ
   - よく使われる type/scope の傾向、日本語/英語、ID付与の仕方を把握する
5. ブランチ名からID抽出:
   - 正規表現 `\\b[A-Z]{2,10}-\\d+\\b` を使い、見つかったら `ID` として採用（複数あれば先頭）
6. scope 推定（`scope=` 未指定のとき）:
   - stagedファイルのパスに `apps/<name>/...` が多い → scope=`<name>`
   - `packages/<name>/...` が多い → scope=`<name>`
   - `apps/` と `packages/` が混在する場合は scope無しでもOK（無理に付けない）
7. type 推定（`type=` 未指定のとき）:
   - テスト中心→`test`
   - リファクタ中心→`refactor`
   - 設定/雑務→`chore` / `build` / `ci`
   - バグ修正→`fix`
   - 機能追加→`feat`
8. コミットメッセージを作る（テンプレ）
   - **タイトル（1行）**:
     - 例: `feat(frontend-admin): ABA-441 教育動画まわりの処理を整理して保守性を改善`
   - **本文（複数行）**: 変更を統合して3〜8個で書く
     - 例:
       - 変更点（何をどう変えたか）
       - 背景/目的（なぜ）
       - 影響範囲（どこに影響）
       - 動作確認（やったこと / 未実施なら理由と次アクション）
9. `dry-run` ならメッセージ案を提示して終了。
10. `dry-run` でなければ、一時ファイルに本文を書き `git commit -F` で実行（`no-verify` 指定なら `--no-verify`）。

## 実行コマンド（この順で使う）
```bash
git branch --show-current
git diff --cached --name-only
git diff --cached --name-status
git diff --cached --stat
git diff --cached
git log -n 200 --format=%s
```


