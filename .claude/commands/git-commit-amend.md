# /git:commit-amend

staged 差分（直前コミットからの追加差分）を踏まえ、過去の良いコミットメッセージの雰囲気に合わせて **日本語コミットメッセージ**を再生成し、`git commit --amend` で更新してください。

## 引数（任意）
- `no-edit`: メッセージは変えずに `git commit --amend --no-edit`（内容だけ更新）
- `dry-run`: 実行せず案だけ出す
- `no-verify`: `--no-verify`

## ゴール
- amend は **stagedのみ** を取り込む（unstagedは含めない）
- `no-edit` 以外は、直前コミットの本文も参照して「より良い要約」に更新する

## 進め方（必須手順）
1. staged が空なら中断:
   - `git diff --cached --name-only` が空 → 「先に stage してね」で終了
2. 直前コミットのメッセージを取得（参考にする）:
   - `git log -1 --format=%B`
3. staged 情報を収集（根拠はstaged）:
   - `git diff --cached --name-status`
   - `git diff --cached --stat`
   - `git diff --cached`
4. 過去コミットの「雰囲気」を抽出:
   - `git log -n 200 --format=%s`
5. `no-edit` の場合:
   - `git commit --amend --no-edit` を実行（`no-verify` 指定なら付与）
6. `no-edit` でない場合:
   - `git:commit` と同じルールでタイトル/本文を再生成（日本語・本文詳しめ）
   - `dry-run` なら提示して終了
   - そうでなければ `git commit --amend -F <tmpfile>` を実行

## 実行コマンド
```bash
git diff --cached --name-only
git diff --cached --name-status
git diff --cached --stat
git diff --cached
git log -1 --format=%B
git log -n 200 --format=%s
```


