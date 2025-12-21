# Million Pocket - Cursorスラッシュコマンド

## 🚀 クイックスタート

Cursorのチャット入力欄で `/` を入力すると、以下のカスタムコマンドが利用できます。

## 📋 利用可能なコマンド一覧

### 🎯 予測実行

| コマンド | 説明 | 実行時間 |
|---------|------|---------|
| `/predict-numbers4` | ナンバーズ4の予測パイプラインを実行してDBに保存 | 約1-2分 |
| `/predict-numbers3` | ナンバーズ3の予測パイプラインを実行してDBに保存 | 約1-2分 |

**実行内容:**
1. 最新データのスクレイピング
2. モデルの学習・更新
3. アンサンブル予測の実行
4. 予測結果をデータベースに保存

### 📊 予測管理・分析 ✨NEW✨

| コマンド | 説明 | 実行時間 |
|---------|------|---------|
| `/prediction-list` | 予測履歴を一覧表示（最新20件） | 即座 |
| `/prediction-stats` | 予測統計（的中率・精度）を表示 | 即座 |
| `/prediction-show` | 特定の予測IDの詳細を表示 | 即座 |
| `/prediction-update` | 予測結果を実際の当選番号で更新 | 即座 |

**使い方:**
- `/prediction-list` - そのまま実行
- `/prediction-stats` - そのまま実行
- `/prediction-show prediction_id=180` - 予測IDを指定
- `/prediction-update prediction_id=180 actual_numbers=1234` - IDと当選番号を指定

### 📥 データ取得

| コマンド | 説明 | 実行時間 |
|---------|------|---------|
| `/scrape-numbers4` | ナンバーズ4の最新データをスクレイピング | 約10秒 |
| `/scrape-loto6` | ロト6の最新データをスクレイピング | 約10秒 |

### 🔍 確認・分析

| コマンド | 説明 | 実行時間 |
|---------|------|---------|
| `/check-db` | データベースの状態を確認 | 即座 |
| `/check-latest` | 最新の抽選結果を確認 | 即座 |
| `/run-streamlit` | StreamlitアプリをブラウザでUIとして起動 | 約5秒 |

## 💡 推奨ワークフロー

### 週次ルーティン（月・水・金）

```
1. /predict-numbers4     # 予測を実行・保存
2. /check-latest         # 結果を確認
3. /prediction-list      # 予測履歴を確認
```

### 当選番号が出たら

```
1. /prediction-update prediction_id=180 actual_numbers=1234  # 結果を更新
2. /prediction-stats                                          # 統計を確認
```

### 詳しく分析したい時

```
1. /prediction-show prediction_id=180  # 特定の予測の詳細
2. /prediction-stats                    # 全体の統計
3. /run-streamlit                       # ブラウザで可視化
```

### データ更新のみ

```
/scrape-numbers4         # 最新データだけ取得
```

### 詳細分析

```
/run-streamlit           # ブラウザで可視化・分析
```

## 🎯 使用例

### 例1: ナンバーズ4の予測を実行

Cursorチャットで:
```
/predict-numbers4
```

実行結果:
```
🚀 Numbers 4 自動予測パイプライン
============================================================

[Step 1] 最新データの取得中...
[Step 1.5] モデルの自己学習を実行中...
[Step 2] アンサンブル予測の実行中...
✅ 予測履歴をデータベースに保存しました
   📝 予測ID: 123
   🎯 対象抽選回: 第6881回
   📊 予測候補数: 1500件
   💾 保存した候補: 50件

[Step 3] 保存された予測結果を確認中...
✅ 予測結果をDBに保存しました:
   - 予測ID: 123
   - 対象抽選回: 第6881回
   - 保存日時: 2025-12-20 11:15:30
   - 予測候補数: 1500件

✅ パイプライン完了
```

### 例2: データベースの状態確認

```
/check-db
```

実行結果:
```
📊 データベース状態
- numbers4_draws: 6,880件
- numbers4_ensemble_predictions: 15件
- numbers4_prediction_candidates: 750件
```

### 例3: 予測統計の確認 ✨NEW✨

```
/prediction-stats
```

実行結果:
```
📈 予測統計
============================================================

総予測回数: 150回

【的中統計】
  exact: 2回 (平均4.00桁一致) 🎯
  partial: 15回 (平均1.80桁一致) 🎲
  miss: 8回 (平均0.00桁一致) ❌

【最近10回の結果】
  第6881回: 5879 🎲 (1桁) - 予測: 2220, 2221, 2223
  第6880回: 0497 ❌ (0桁) - 予測: 2322, 2323, 2220

【完全一致した予測番号】
  2220: 1回
  3133: 1回
```

### 例4: 予測結果の更新 ✨NEW✨

```
/prediction-update prediction_id=180 actual_numbers=2220
```

実行結果:
```
✅ 予測結果を更新しました (ID: 180)
   実際の当選番号: 2220
   的中状況: exact (4桁一致) 🎯
```

## 🔧 トラブルシューティング

### コマンドが表示されない

1. **Cursorを再起動**
   - 完全に終了してから再度開く

2. **ファイルの確認**
   ```bash
   ls -la .cursor/commands/
   ```
   - 実行権限（`x`）が付いているか確認

### コマンド実行でエラー

1. **Python環境の確認**
   ```bash
   python --version  # Python 3.8以上
   ```

2. **環境変数の確認**
   ```bash
   cat .env | grep DATABASE_URL
   ```

3. **パッケージのインストール**
   ```bash
   pip install -r requirements.txt
   ```

## 📚 詳細情報

詳しい使い方やカスタムコマンドの追加方法は以下を参照:

- [`.cursor/commands/README.md`](.cursor/commands/README.md) - コマンド詳細
- [Cursor公式ドキュメント](https://docs.cursor.com/ja/agent/chat/commands) - カスタムコマンド

## ⚙️ カスタムコマンドの追加

新しいコマンドを追加する場合:

1. `.cursor/commands/` に新しい `.md` ファイルを作成
2. 以下の形式で記述:

```markdown
---
description: コマンドの説明
---

\`\`\`bash
python your_script.py
\`\`\`
```

3. 実行権限を付与:
```bash
chmod +x .cursor/commands/your-command.md
```

## 🎉 便利な使い方

### コマンドの組み合わせ

Cursorチャットで複数のタスクを一度に依頼:

```
/predict-numbers4 を実行して、結果をMarkdownでまとめてください
```

### 定期実行の自動化

cronで定期実行する場合:
```bash
# 毎週月・水・金の9時に実行
0 9 * * 1,3,5 cd /path/to/million-pocket && python tools/run_numbers4_pipeline.py
```

---

**Million Pocket** - 宝くじ予測システム  
より良い予測のために 🎯

