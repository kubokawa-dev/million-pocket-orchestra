# Cursor カスタムスラッシュコマンド

このディレクトリには、宝くじAIプロジェクトで使用できるカスタムスラッシュコマンドが含まれています。

## 使い方

1. Cursorのチャット入力欄で `/` を入力
2. 表示されるコマンドリストから実行したいコマンドを選択
3. または、コマンド名を直接入力（例: `/predict-numbers4`）

## 利用可能なコマンド

### 予測系コマンド

- **`/predict-numbers4`** - ナンバーズ4の予測パイプラインを実行し、結果をDBに保存
  - 最新データの取得 → モデル学習 → 予測実行 → DB保存
  - 実行時間: 約1-2分

- **`/predict-numbers3`** - ナンバーズ3の予測パイプラインを実行し、結果をDBに保存

### 予測管理系コマンド ✨NEW✨

- **`/prediction-list`** - 予測履歴をテーブル形式で一覧表示（最新20件）
  - 予測した番号と実際の結果を比較
  - 更新可能な予測を自動検出

- **`/prediction-stats`** - 予測統計を表示
  - 的中率、平均一致桁数、完全一致した番号など

- **`/prediction-show prediction_id=<ID>`** - 特定の予測の詳細を表示
  - 例: `/prediction-show prediction_id=180`

- **`/prediction-update prediction_id=<ID> actual_numbers=<番号>`** - 予測結果を更新
  - 当選番号が判明したら実行
  - 例: `/prediction-update prediction_id=180 actual_numbers=1234`

- **`/prediction-auto-update`** - 更新可能な予測を一括自動更新 🆕
  - DBに当選番号がある予測を自動検出して一括更新
  - 統計も自動表示

### スクレイピング系コマンド

- **`/scrape-numbers4`** - ナンバーズ4の最新データをスクレイピングしてDBに保存
  - 楽天銀行サイトから最新の抽選結果を取得

- **`/scrape-loto6`** - ロト6の最新データをスクレイピングしてDBに保存

### 確認系コマンド

- **`/check-db`** - データベースの状態を確認
  - 各テーブルのレコード数を表示

- **`/check-latest`** - 最新の抽選結果を確認
  - 直近の当選番号と予測履歴を表示

### アプリケーション

- **`/run-streamlit`** - Streamlitアプリを起動
  - ブラウザでUIを使って予測結果を確認

## 推奨ワークフロー

1. **定期的な予測実行** (週3回: 月・水・金)
   ```
   /predict-numbers4
   ```

2. **結果確認**
   ```
   /check-latest
   ```

3. **データ分析** (必要に応じて)
   ```
   /run-streamlit
   ```

## トラブルシューティング

### コマンドが表示されない場合

1. Cursorを再起動
2. `.cursor/commands` ディレクトリが存在することを確認
3. コマンドファイルに実行権限があることを確認
   ```bash
   ls -la .cursor/commands/
   ```

### コマンド実行時にエラーが発生する場合

1. Python環境が正しくセットアップされているか確認
2. `.env` ファイルにDATABASE_URLが設定されているか確認
3. 必要なパッケージがインストールされているか確認
   ```bash
   pip install -r requirements.txt
   ```

## カスタムコマンドの追加

新しいコマンドを追加する場合:

1. `.cursor/commands/` ディレクトリに新しい `.md` ファイルを作成
2. 以下の形式で記述:

```markdown
---
description: コマンドの説明
---

\`\`\`bash
実行するコマンド
\`\`\`
```

3. 実行権限を付与:
```bash
chmod +x .cursor/commands/your-command.md
```

4. Cursorを再起動（必要な場合）

## 参考

- [Cursor公式ドキュメント - カスタムコマンド](https://docs.cursor.com/ja/agent/chat/commands)

