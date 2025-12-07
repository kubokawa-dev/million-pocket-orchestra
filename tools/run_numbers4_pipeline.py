import os
import subprocess
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

ROOT = os.path.dirname(os.path.dirname(__file__))
PY = sys.executable or 'python'


def run(cmd, cwd=None):
    print(f"[run] {cmd}")
    res = subprocess.run(cmd, cwd=cwd or ROOT, shell=True)
    if res.returncode != 0:
        raise SystemExit(res.returncode)


def update_learning_models():
    """
    データベースの最新の当選番号を使用して、モデルの学習（内部状態更新）を実行します。
    numbers4/learn_from_predictions.py を呼び出します。
    """
    try:
        db_url = os.environ.get('DATABASE_URL')
        if db_url and '?schema' in db_url:
            db_url = db_url.split('?schema')[0]
        
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        # 最新の当選番号を取得
        cur.execute("SELECT numbers FROM numbers4_draws ORDER BY draw_date DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        
        if row:
            latest_number = row[0]
            print(f"\n[Step 1.5] モデルの自己学習を実行中 (最新当選番号: {latest_number})...")
            
            # 内部状態の学習 (numbers4/learn_from_predictions.py)
            learn_py = os.path.join(ROOT, 'numbers4', 'learn_from_predictions.py')
            if os.path.exists(learn_py):
                run(f'"{PY}" "{learn_py}" {latest_number}')
            
            # 重みの学習はスクレイピング時(Step 1)に numbers4/add_recent_draws.py または tools/scrape_numbers4_rakuten.py 内で行われます
            # ここでは明示的に呼び出す必要はありませんが、念のため確認します
            
        else:
            print("\n[warn] データベースに当選番号が見つかりません。学習をスキップします。")
            
    except Exception as e:
        print(f"\n[warn] モデル学習中にエラーが発生しました: {e}")
        # パイプラインを止めない


def main():
    print("="*60)
    print("🚀 Numbers 4 自動予測パイプライン")
    print("="*60)

    # 1) 最新データの取得 (Scrape)
    #    ※ このステップで numbers4/online_learning.py (重み調整) も実行される場合があります
    print("\n[Step 1] 最新データの取得中...")
    scrape_py = os.path.join(ROOT, 'tools', 'scrape_numbers4_rakuten.py')
    if os.path.exists(scrape_py):
        run(f'"{PY}" "{scrape_py}"')
    else:
        print('[warn] scraper not found, skipping scrape step')

    # 1.5) モデルの自己学習 (Internal State Learning)
    update_learning_models()

    # 2) アンサンブル予測の実行 (Predict)
    print("\n[Step 2] アンサンブル予測の実行中...")
    ensemble_py = os.path.join(ROOT, 'numbers4', 'predict_ensemble.py')
    if os.path.exists(ensemble_py):
        run(f'"{PY}" "{ensemble_py}"')
    else:
        print('[error] ensemble predictor not found')

    print("\n✅ パイプライン完了")


if __name__ == '__main__':
    main()
