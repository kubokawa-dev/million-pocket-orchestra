import os
import subprocess
import sys
import psycopg2
import json
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
    loto6/learn_from_predictions.py を呼び出します。
    """
    try:
        db_url = os.environ.get('DATABASE_URL')
        if db_url and '?schema' in db_url:
            db_url = db_url.split('?schema')[0]
        
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        # 最新の当選番号を取得 (numbers format: "01,02,03,04,05,06" or similar)
        cur.execute("SELECT numbers, bonus_number, draw_number FROM loto6_draws ORDER BY draw_date DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        
        if row:
            numbers_str = row[0]  # e.g., "01,02,03,04,05,06"
            bonus_num = row[1]
            draw_num = row[2]
            
            # カンマ区切りをスペースなしの文字列に変換 (e.g., "010203040506")
            # learn_from_predictions.py は "010203040506" 形式を受け取る
            numbers_normalized = numbers_str.replace(',', '').replace(' ', '')
            
            print(f"\n[Step 1.5] モデルの自己学習を実行中 (第{draw_num}回: {numbers_str})...")
            
            # 内部状態の学習 (loto6/learn_from_predictions.py)
            learn_py = os.path.join(ROOT, 'loto6', 'learn_from_predictions.py')
            if os.path.exists(learn_py):
                # args: actual_numbers [bonus_number] [draw_number]
                cmd = f'"{PY}" "{learn_py}" {numbers_normalized}'
                if bonus_num:
                    cmd += f" {bonus_num}"
                if draw_num:
                    cmd += f" {draw_num}"
                run(cmd)
            
        else:
            print("\n[warn] データベースに当選番号が見つかりません。学習をスキップします。")
            
    except Exception as e:
        print(f"\n[warn] モデル学習中にエラーが発生しました: {e}")
        # パイプラインを止めない


def main():
    print("="*60)
    print("🚀 Loto 6 自動予測パイプライン")
    print("="*60)

    # 1) 最新データの取得 (Scrape)
    print("\n[Step 1] 最新データの取得中...")
    scrape_py = os.path.join(ROOT, 'tools', 'scrape_loto6_rakuten.py')
    if os.path.exists(scrape_py):
        run(f'"{PY}" "{scrape_py}"')
    else:
        print('[warn] Loto6 scraper not found')

    # 1.5) モデルの自己学習 (Internal State Learning)
    update_learning_models()

    # 2) アンサンブル予測の実行 (Predict)
    print("\n[Step 2] アンサンブル予測の実行中...")
    ensemble_py = os.path.join(ROOT, 'loto6', 'ultimate_predict_ensemble.py')
    if os.path.exists(ensemble_py):
        run(f'"{PY}" "{ensemble_py}"')
    else:
        print('[error] ultimate ensemble predictor not found')

    print("\n✅ パイプライン完了")


if __name__ == '__main__':
    main()
