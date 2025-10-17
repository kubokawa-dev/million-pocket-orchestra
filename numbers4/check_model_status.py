"""
ナンバーズ4予測システムの状態を診断するスクリプト

データベースの最新データとモデルの更新状況を確認します。
"""

import os
import sys
import json
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(project_root, 'numbers4', 'model_state.json')


def get_db_connection():
    """データベース接続を取得"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL が設定されていません。")
        sys.exit(1)
    if '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    return psycopg2.connect(db_url)


def check_database():
    """データベースの状態を確認"""
    print("\n" + "="*60)
    print("📊 データベース状態")
    print("="*60)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 総レコード数
        cur.execute("SELECT COUNT(*) FROM numbers4_draws")
        total_count = cur.fetchone()[0]
        print(f"総抽選回数: {total_count}件")
        
        # 最新の抽選結果
        cur.execute("""
            SELECT draw_number, draw_date, numbers 
            FROM numbers4_draws 
            ORDER BY draw_date DESC, draw_number DESC 
            LIMIT 5
        """)
        latest_draws = cur.fetchall()
        
        print("\n最新5件の抽選結果:")
        for draw_number, draw_date, numbers in latest_draws:
            print(f"  第{draw_number}回 ({draw_date}) = {numbers}")
        
        # 最古の抽選結果
        cur.execute("""
            SELECT draw_number, draw_date, numbers 
            FROM numbers4_draws 
            ORDER BY draw_date ASC, draw_number ASC 
            LIMIT 1
        """)
        oldest = cur.fetchone()
        if oldest:
            print(f"\n最古の抽選結果: 第{oldest[0]}回 ({oldest[1]}) = {oldest[2]}")
        
        conn.close()
        return latest_draws[0] if latest_draws else None
        
    except Exception as e:
        print(f"❌ データベースエラー: {e}")
        return None


def check_model():
    """モデルの状態を確認"""
    print("\n" + "="*60)
    print("🤖 モデル状態")
    print("="*60)
    
    if not os.path.exists(MODEL_PATH):
        print(f"❌ モデルファイルが見つかりません: {MODEL_PATH}")
        print("💡 learn_from_predictions.py を実行してモデルを初期化してください。")
        return None
    
    try:
        with open(MODEL_PATH, 'r', encoding='utf-8') as f:
            model_state = json.load(f)
        
        version = model_state.get('version', 'unknown')
        updated_at = model_state.get('updated_at', 'unknown')
        events = model_state.get('events', 0)
        
        print(f"モデルバージョン: {version}")
        print(f"最終更新日時: {updated_at}")
        print(f"学習イベント数: {events}回")
        
        # 更新からの経過時間を計算
        if updated_at and updated_at != 'unknown':
            try:
                updated_dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                age = now - updated_dt
                age_hours = age.total_seconds() / 3600
                age_days = age.days
                
                print(f"更新からの経過時間: {age_days}日 {age_hours % 24:.1f}時間")
                
                # 警告判定
                if age_hours > 48:
                    print("⚠️  警告: モデルが2日以上更新されていません。")
                    print("   最新データでモデルを更新することを推奨します。")
                elif age_hours > 24:
                    print("⚠️  注意: モデルが1日以上更新されていません。")
                else:
                    print("✅ モデルは最新です。")
                
                if events < 20:
                    print(f"⚠️  警告: 学習イベント数が少ない（{events}回）。")
                    print("   より多くのデータで学習することを推奨します。")
                
            except Exception as e:
                print(f"⚠️  日時解析エラー: {e}")
        
        # 各桁の確率分布の概要を表示
        pos_probs = model_state.get('pos_probs', [])
        if pos_probs and len(pos_probs) == 4:
            print("\n各桁の確率分布（上位3つ）:")
            for i, probs in enumerate(pos_probs):
                if len(probs) == 10:
                    sorted_probs = sorted(enumerate(probs), key=lambda x: x[1], reverse=True)[:3]
                    top_digits = ', '.join([f"{digit}({prob*100:.1f}%)" for digit, prob in sorted_probs])
                    print(f"  {i+1}桁目: {top_digits}")
        
        return model_state
        
    except Exception as e:
        print(f"❌ モデル読み込みエラー: {e}")
        return None


def check_sync(latest_draw, model_state):
    """データベースとモデルの同期状態を確認"""
    print("\n" + "="*60)
    print("🔄 同期状態")
    print("="*60)
    
    if not latest_draw or not model_state:
        print("⚠️  同期状態を確認できません。")
        return
    
    draw_number, draw_date, numbers = latest_draw
    model_updated = model_state.get('updated_at', '')
    
    print(f"DB最新抽選: 第{draw_number}回 ({draw_date}) = {numbers}")
    print(f"モデル更新: {model_updated}")
    
    # 簡易的な同期チェック
    if model_updated:
        try:
            model_dt = datetime.fromisoformat(model_updated.replace('Z', '+00:00'))
            # draw_dateが文字列の場合、日付部分のみを比較
            draw_date_str = str(draw_date)
            if draw_date_str > model_updated[:10]:
                print("\n⚠️  警告: DBの最新抽選がモデル更新後に追加されています。")
                print(f"   最新の当選番号 {numbers} でモデルを更新してください。")
                print(f"   実行: python numbers4/update_model.py {numbers}")
            else:
                print("\n✅ モデルは最新の抽選データを反映しています。")
        except Exception as e:
            print(f"⚠️  同期チェックエラー: {e}")


def main():
    print("\n" + "="*60)
    print("🔍 ナンバーズ4予測システム 診断ツール")
    print("="*60)
    
    # データベース確認
    latest_draw = check_database()
    
    # モデル確認
    model_state = check_model()
    
    # 同期状態確認
    check_sync(latest_draw, model_state)
    
    # 推奨アクション
    print("\n" + "="*60)
    print("💡 推奨アクション")
    print("="*60)
    
    if latest_draw and model_state:
        model_updated = model_state.get('updated_at', '')
        if model_updated:
            try:
                model_dt = datetime.fromisoformat(model_updated.replace('Z', '+00:00'))
                age_hours = (datetime.now(timezone.utc) - model_dt).total_seconds() / 3600
                
                if age_hours > 24:
                    print("1. モデルを最新データで更新:")
                    print(f"   python numbers4/update_model.py --auto")
                    print("\n2. 予測を実行:")
                    print(f"   python numbers4/predict_ensemble.py")
                else:
                    print("✅ システムは正常です。予測を実行できます:")
                    print(f"   python numbers4/predict_ensemble.py")
            except:
                pass
    
    print("\n" + "="*60)


if __name__ == '__main__':
    main()
