"""
LINE通知送信スクリプト

使用方法:
1. LINE Notify でトークンを取得: https://notify-bot.line.me/
2. 環境変数 LINE_NOTIFY_TOKEN を設定
3. python tools/send_notification.py

環境変数:
  LINE_NOTIFY_TOKEN: LINE Notifyのアクセストークン
"""

import os
import sys
import json
from urllib.request import urlopen, Request
from urllib.error import HTTPError

# プロジェクトルートをパスに追加
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from tools.utils import get_db_connection

LINE_NOTIFY_URL = 'https://notify-api.line.me/api/notify'


def get_latest_predictions():
    """最新の予測結果を取得"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    results = {}
    
    # Numbers4の最新予測
    try:
        cur.execute("""
            SELECT target_draw_number, top_predictions, created_at
            FROM numbers4_ensemble_predictions 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        row = cur.fetchone()
        if row:
            top_preds = json.loads(row[1]) if row[1] else []
            results['numbers4'] = {
                'target_draw': row[0],
                'predictions': [p['number'] for p in top_preds[:5]],
                'created_at': row[2]
            }
    except Exception as e:
        print(f"[warn] Numbers4予測取得エラー: {e}")
    
    # Loto6の最新予測
    try:
        cur.execute("""
            SELECT target_draw_number, top_predictions, created_at
            FROM loto6_ensemble_predictions 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        row = cur.fetchone()
        if row:
            top_preds = json.loads(row[1]) if row[1] else []
            results['loto6'] = {
                'target_draw': row[0],
                'predictions': [p['number'] for p in top_preds[:5]],
                'created_at': row[2]
            }
    except Exception as e:
        print(f"[warn] Loto6予測取得エラー: {e}")
    
    conn.close()
    return results


def format_message(predictions):
    """通知メッセージを整形"""
    lines = [
        "🎰 宝くじ予測通知 🎰",
        "━━━━━━━━━━━━━━━━"
    ]
    
    # Numbers4
    if 'numbers4' in predictions:
        n4 = predictions['numbers4']
        lines.append("")
        lines.append(f"📊 ナンバーズ4 第{n4['target_draw']}回")
        lines.append("🔮 予測番号:")
        for i, num in enumerate(n4['predictions'], 1):
            lines.append(f"  {i}位: {num}")
    
    # Loto6
    if 'loto6' in predictions:
        l6 = predictions['loto6']
        lines.append("")
        lines.append(f"📊 ロト6 第{l6['target_draw']}回")
        lines.append("🔮 予測番号:")
        for i, num in enumerate(l6['predictions'], 1):
            lines.append(f"  {i}位: {num}")
    
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("💡 購入はお早めに！")
    
    return "\n".join(lines)


def send_line_notify(message, token=None):
    """LINE Notifyでメッセージを送信"""
    token = token or os.environ.get('LINE_NOTIFY_TOKEN')
    
    if not token:
        print("❌ LINE_NOTIFY_TOKEN が設定されていません")
        print("   LINE Notify: https://notify-bot.line.me/")
        return False
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = f'message={message}'.encode('utf-8')
    
    try:
        req = Request(LINE_NOTIFY_URL, data=data, headers=headers, method='POST')
        with urlopen(req) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result.get('status') == 200:
                print("✅ LINE通知を送信しました")
                return True
            else:
                print(f"❌ LINE通知エラー: {result}")
                return False
    except HTTPError as e:
        print(f"❌ LINE通知HTTPエラー: {e.code} {e.reason}")
        return False
    except Exception as e:
        print(f"❌ LINE通知エラー: {e}")
        return False


def main():
    print("="*60)
    print("📱 LINE通知送信")
    print("="*60)
    
    # 予測結果を取得
    print("\n[Step 1] 最新予測を取得中...")
    predictions = get_latest_predictions()
    
    if not predictions:
        print("⚠️ 予測結果がありません。先に予測を実行してください。")
        return
    
    # メッセージを整形
    print("\n[Step 2] メッセージを作成中...")
    message = format_message(predictions)
    print(message)
    
    # LINE通知を送信
    print("\n[Step 3] LINE通知を送信中...")
    success = send_line_notify(message)
    
    if success:
        print("\n✅ 通知完了！")
    else:
        print("\n⚠️ 通知に失敗しました。")


if __name__ == '__main__':
    main()

