# Numbers4 & Loto6 Prediction Project

このプロジェクトは、ナンバーズ4・ロト6の過去データをもとに、複数モデルによる予測・可視化・分析を行うPythonベースのアプリケーションです。

## 主な機能

- 過去の抽選データ・予測データの管理（SQLiteデータベース）
- アンサンブル学習による最新予測の生成
- StreamlitによるリッチなWeb可視化
    - 予測ボタンで最新の当選番号予測を即時表示
    - 過去の予測と実際の当選番号の比較・分析
    - 的中数やモデルごとのパフォーマンス指標

## ディレクトリ構成

```
lottery_numbers.txt
loto6/
    ...
numbers4/
    predict_ensemble.py  # 予測ロジック本体
    ...
streamlit_app.py         # Streamlit Webアプリ
```

## 必要な環境

- Python 3.10 以上
- 必要パッケージ: pandas, numpy, streamlit, tqdm など

### インストール

```bash
pip install -r requirements.txt
```

## Streamlitアプリの起動方法

1. 必要なパッケージをインストール
2. 環境変数 `DATABASE_URL` に PostgreSQL 接続文字列を設定（例: `postgresql://user:pass@host:5432/dbname`）
3. 以下のコマンドでWebアプリを起動

```bash
python -m streamlit run streamlit_app.py
```

- ブラウザで `http://localhost:8501` にアクセス
- 画面上部の「予測を実行」ボタンで最新予測を表示
- 下部で過去の予測と当選番号の比較・分析が可能

## 予測ロジックについて

- `numbers4/predict_ensemble.py` にて、
    - 基本統計モデル
    - 高度ヒューリスティックモデル
    - 機械学習モデル
    - 探索的モデル
  など複数モデルの予測を統合
- Streamlit UIから直接呼び出し可能

## よくあるトラブル

- 予測ボタンでエラーが出る場合は、
    - Pythonバージョンや依存パッケージを確認
    - データベースファイルの有無・整合性を確認
    - エラーメッセージをもとに `numbers4/predict_ensemble.py` のカラム名や返り値を調整

## ライセンス

MIT License

---

ご質問・機能追加要望はIssueまたはチャットでご連絡ください。
