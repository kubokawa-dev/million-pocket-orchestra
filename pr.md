## 概要

PostgreSQL + Prisma + Docker構成から、Pythonのみで完結するSQLite構成へ完全移行しました。
これにより、シークレットなアプリケーションとして単一ファイルDBで運用可能になり、
GitHub Actionsでの自動予測パイプライン実行にも対応しました。

## 変更内容

### 新規追加
- **SQLiteスキーマ定義** (`schema.sql`): PostgreSQLと同等のテーブル構造をSQLite向けに定義
- **データ移行スクリプト** (`tools/migrate_to_sqlite.py`): PostgreSQLからSQLiteへのデータ移行ツール
- **LINE通知スクリプト** (`tools/send_notification.py`): 予測結果をLINE Notifyで通知する機能
- **GitHub Actionsワークフロー** (`.github/workflows/daily-prediction.yml`): 毎日自動で予測パイプラインを実行

### 変更
- `tools/utils.py`: DB接続を `psycopg2` (PostgreSQL) から `sqlite3` へ変更
- 全PythonファイルでSQLプレースホルダを `%s` から `?` へ変更
- `RETURNING id` を `cur.lastrowid` に変更（SQLite互換）
- `requirements.txt`: `psycopg2-binary` を削除、`requests` を追加

### 削除（計約16,000行）
- `docker-compose.yml`: PostgreSQLコンテナ定義
- `packages/` ディレクトリ全体: Prismaスキーマ、マイグレーション、TypeScript設定
- Node.js関連: `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `turbo.json`

## 背景・目的

1. **シークレットなアプリケーション**: 単一ファイルDBで完結させ、外部DB依存を排除
2. **シンプル化**: Docker/Node.js依存を排除し、Pythonのみで運用可能に
3. **自動化対応**: GitHub Actionsで毎日の予測パイプラインを自動実行できるように

## 影響範囲

| 影響範囲 | 詳細 |
|----------|------|
| データベース | PostgreSQL → SQLite（既存データは移行スクリプトで移行済み） |
| Numbers4予測パイプライン | 動作確認済み（予測ID: 231まで正常動作） |
| Loto6予測パイプライン | SQLite対応完了 |
| Node.js/TypeScript | 完全削除（使用していなかった部分） |

## リスクと対策

| リスク | 対策 |
|--------|------|
| SQLite同時書き込み制限 | 単一プロセスでの実行を想定しており問題なし |
| データ移行漏れ | 移行スクリプトで9,473件のレコード移行を確認済み |
| GitHub Actions実行時のDB永続化 | ワークフロー内でSQLite DBをGitコミットするオプションを用意 |

## 動作確認

- [x] PostgreSQL → SQLiteデータ移行（9,473件移行完了）
- [x] Numbers4予測パイプライン実行テスト（予測ID: 231まで正常動作）
- [x] スクレイピング動作確認（404エラーハンドリング追加済み）
- [ ] GitHub Actions自動実行（マージ後に確認予定）
- [ ] LINE通知テスト（LINE_NOTIFY_TOKEN設定後に確認予定）

## レビュー観点

1. **SQLite互換性**: `?` プレースホルダ、`cur.lastrowid` の使用が正しいか
2. **移行スクリプト**: データ型変換（datetime→TEXT、BOOLEAN→INTEGER）が適切か
3. **GitHub Actionsワークフロー**: cron設定、シークレット利用が適切か

---

## 自動情報（参考）

### diffstat
```
 50 files changed, 1120 insertions(+), 16018 deletions(-)
```

### changed files
- `.github/workflows/daily-prediction.yml` (新規)
- `README.md` (更新)
- `docker-compose.yml` (削除)
- `loto6/*.py` (SQLite対応)
- `numbers4/*.py` (SQLite対応)
- `tools/*.py` (SQLite対応、新規スクリプト追加)
- `packages/` (全削除)
- `package.json`, `pnpm-lock.yaml`, `turbo.json` (削除)
- `schema.sql` (新規)

### commits
- `8e91a33` refactor: PostgreSQL/PrismaからSQLiteへの移行とNode.js関連ファイルの削除
