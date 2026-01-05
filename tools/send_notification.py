"""
予測サマリーを各種サービスに通知するスクリプト

使い方:
  # LINE Notifyで通知
  python tools/send_notification.py --line --summary predictions/numbers4_20260105.md
  
  # Discordで通知
  python tools/send_notification.py --discord --summary predictions/numbers4_20260105.md
  
  # Slackで通知
  python tools/send_notification.py --slack --summary predictions/numbers4_20260105.md

環境変数:
  - LINE_NOTIFY_TOKEN: LINE Notifyのアクセストークン
  - DISCORD_WEBHOOK_URL: DiscordのWebhook URL
  - SLACK_WEBHOOK_URL: SlackのIncoming Webhook URL
"""

import os
import sys
import argparse
import requests
import json
from pathlib import Path


def read_summary(file_path: str) -> str:
    """サマリーファイルを読み込む"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_top_predictions(markdown: str, top_n: int = 5) -> str:
    """Markdownから上位予測を抽出して通知用テキストを作成"""
    lines = markdown.split('\n')
    
    # タイトルを取得
    title = ""
    for line in lines:
        if line.startswith('# '):
            title = line.replace('# ', '')
            break
    
    # 予測情報を抽出
    info = []
    in_info_table = False
    for line in lines:
        if '| 項目 | 内容 |' in line:
            in_info_table = True
            continue
        if in_info_table and line.startswith('|') and '---' not in line:
            info.append(line)
        elif in_info_table and not line.startswith('|'):
            in_info_table = False
    
    # TOP予測を抽出
    top_predictions = []
    in_ranking = False
    for line in lines:
        if '安定上位予測' in line:
            in_ranking = True
            continue
        if in_ranking and line.startswith('| 🥇') or line.startswith('| 🥈') or line.startswith('| 🥉'):
            # テーブルから番号を抽出
            parts = line.split('|')
            if len(parts) >= 3:
                rank_part = parts[1].strip()
                number_part = parts[2].strip().replace('`', '').replace('**', '')
                rate_part = parts[3].strip() if len(parts) > 3 else ''
                top_predictions.append(f"{rank_part} {number_part} ({rate_part})")
        if in_ranking and len(top_predictions) >= top_n:
            break
    
    # 通知用テキストを組み立て
    message = f"🎰 {title}\n\n"
    
    # 予測情報
    message += "📋 予測情報\n"
    for line in info[:3]:
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) >= 2:
            message += f"  {parts[0]}: {parts[1]}\n"
    
    message += "\n🔥 安定上位予測 TOP5\n"
    for pred in top_predictions[:5]:
        message += f"  {pred}\n"
    
    return message


def send_line_notify(message: str, token: str) -> bool:
    """LINE Notifyで通知を送信"""
    url = 'https://notify-api.line.me/api/notify'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # メッセージが1000文字を超える場合は切り詰め
    if len(message) > 1000:
        message = message[:997] + '...'
    
    data = {'message': message}
    
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            print("✅ LINE通知を送信しました")
            return True
        else:
            print(f"❌ LINE通知に失敗: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ LINE通知エラー: {e}")
        return False


def send_discord_webhook(message: str, webhook_url: str) -> bool:
    """Discord Webhookで通知を送信"""
    # Discordの埋め込みメッセージを作成
    data = {
        "content": message[:2000],  # Discordの制限
        "username": "Numbers4 Bot",
        "avatar_url": "https://em-content.zobj.net/source/apple/354/slot-machine_1f3b0.png"
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code in [200, 204]:
            print("✅ Discord通知を送信しました")
            return True
        else:
            print(f"❌ Discord通知に失敗: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Discord通知エラー: {e}")
        return False


def send_slack_webhook(message: str, webhook_url: str) -> bool:
    """Slack Incoming Webhookで通知を送信"""
    data = {
        "text": message,
        "username": "Numbers4 Bot",
        "icon_emoji": ":slot_machine:"
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            print("✅ Slack通知を送信しました")
            return True
        else:
            print(f"❌ Slack通知に失敗: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Slack通知エラー: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='予測サマリーを通知')
    parser.add_argument('--summary', '-s', type=str, required=True,
                        help='サマリーファイルのパス')
    parser.add_argument('--line', action='store_true',
                        help='LINE Notifyで通知')
    parser.add_argument('--discord', action='store_true',
                        help='Discord Webhookで通知')
    parser.add_argument('--slack', action='store_true',
                        help='Slack Webhookで通知')
    parser.add_argument('--all', action='store_true',
                        help='設定された全サービスに通知')
    
    args = parser.parse_args()
    
    # サマリーファイルを読み込み
    if not os.path.exists(args.summary):
        print(f"❌ サマリーファイルが見つかりません: {args.summary}")
        sys.exit(1)
    
    markdown = read_summary(args.summary)
    message = extract_top_predictions(markdown)
    
    print("📨 通知メッセージ:")
    print("-" * 40)
    print(message)
    print("-" * 40)
    
    success = True
    
    # LINE Notify
    if args.line or args.all:
        token = os.environ.get('LINE_NOTIFY_TOKEN')
        if token:
            if not send_line_notify(message, token):
                success = False
        else:
            print("⚠️ LINE_NOTIFY_TOKEN が設定されていません")
    
    # Discord
    if args.discord or args.all:
        webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
        if webhook_url:
            if not send_discord_webhook(message, webhook_url):
                success = False
        else:
            print("⚠️ DISCORD_WEBHOOK_URL が設定されていません")
    
    # Slack
    if args.slack or args.all:
        webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
        if webhook_url:
            if not send_slack_webhook(message, webhook_url):
                success = False
        else:
            print("⚠️ SLACK_WEBHOOK_URL が設定されていません")
    
    if not (args.line or args.discord or args.slack or args.all):
        print("⚠️ 通知先を指定してください: --line, --discord, --slack, --all")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
