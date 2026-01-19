"""
Numbers4 自動予測パイプライン（SQLite版）
"""
import os
import subprocess
import sys

# プロジェクトルートをパスに追加
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from tools.utils import get_db_connection

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
        conn = get_db_connection()
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

    # 3) 保存された予測結果の確認
    print("\n[Step 3] 保存された予測結果を確認中...")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 最新の予測結果を取得
        cur.execute("""
            SELECT id, target_draw_number, created_at, predictions_count
            FROM numbers4_ensemble_predictions 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        row = cur.fetchone()
        conn.close()
        
        if row:
            pred_id, target_draw, created_at, pred_count = row
            print(f"✅ 予測結果をDBに保存しました:")
            print(f"   - 予測ID: {pred_id}")
            print(f"   - 対象抽選回: 第{target_draw}回" if target_draw else "   - 対象抽選回: 未設定")
            print(f"   - 保存日時: {created_at}")
            print(f"   - 予測候補数: {pred_count}件")
        else:
            print("⚠️  予測結果が見つかりませんでした。保存に失敗した可能性があります。")
    except Exception as e:
        print(f"⚠️  予測結果の確認中にエラーが発生しました: {e}")

    # 4) 組み合わせ（ボックス）統計分析
    print("\n[Step 4] 組み合わせ統計分析を実行中...")
    analyze_py = os.path.join(ROOT, 'numbers4', 'analyze_box_stats.py')
    if os.path.exists(analyze_py):
        try:
            run(f'"{PY}" "{analyze_py}"')
        except SystemExit:
            print("[warn] 統計分析でエラーが発生しましたが、パイプラインを続行します")
    else:
        print('[warn] analyze_box_stats.py not found, skipping analysis step')

    print("\n✅ パイプライン完了")


if __name__ == '__main__':
    main()
