"""
CSVファイルからSQLiteデータベースにナンバーズ4の履歴データをロードするスクリプト

GitHub Actions上で毎回DBを再構築するために使用します。
numbers4/*.csv から全履歴を読み込んでlottery.dbに投入します。
"""
import os
import re
import csv
import sys
import glob

# プロジェクトルートをパスに追加
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from tools.utils import get_db_connection

CSV_DIR = os.path.join(ROOT, 'numbers4')


def ensure_table(conn):
    """テーブルが存在しない場合は作成"""
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS numbers4_draws (
            draw_number INTEGER PRIMARY KEY,
            draw_date TEXT NOT NULL,
            numbers TEXT NOT NULL
        )
    ''')
    conn.commit()


def parse_csv_row(row):
    """
    CSVの1行をパースして (draw_number, draw_date, numbers) を返す
    
    CSVフォーマット例:
    第6890回,2026/01/05,7526,23,"1,042,200円",374,"43,400円",...
    """
    if len(row) < 3:
        return None
    
    # 回号を抽出 (第XXXX回 → XXXX)
    kai_str = row[0]
    kai_match = re.search(r'(\d+)', kai_str)
    if not kai_match:
        return None
    draw_number = int(kai_match.group(1))
    
    # 日付 (YYYY/MM/DD)
    draw_date = row[1]
    
    # 当選番号 (4桁)
    numbers = row[2]
    if not re.fullmatch(r'\d{4}', numbers):
        return None
    
    return (draw_number, draw_date, numbers)


def load_all_csv_files():
    """
    numbers4/*.csv から全データを読み込む
    """
    csv_files = sorted(glob.glob(os.path.join(CSV_DIR, '*.csv')))
    
    all_rows = []
    for csv_path in csv_files:
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row:
                        continue
                    parsed = parse_csv_row(row)
                    if parsed:
                        all_rows.append(parsed)
        except Exception as e:
            print(f"[warn] Error reading {csv_path}: {e}")
            continue
    
    return all_rows


def load_csv_to_db():
    """
    CSVファイルからDBにデータをロード
    """
    print("="*60)
    print("📂 CSVからデータベースを構築中...")
    print("="*60)
    
    # 全CSVファイルを読み込み
    all_rows = load_all_csv_files()
    print(f"📊 CSVから {len(all_rows)} 件のデータを読み込みました")
    
    if not all_rows:
        print("⚠️  CSVファイルにデータがありません")
        return 0
    
    # DBに投入
    conn = get_db_connection()
    ensure_table(conn)
    cur = conn.cursor()
    
    inserted = 0
    skipped = 0
    
    for draw_number, draw_date, numbers in all_rows:
        # 既に存在するかチェック
        cur.execute('SELECT 1 FROM numbers4_draws WHERE draw_number = ?', (draw_number,))
        if cur.fetchone():
            skipped += 1
            continue
        
        cur.execute(
            'INSERT INTO numbers4_draws (draw_number, draw_date, numbers) VALUES (?, ?, ?)',
            (draw_number, draw_date, numbers)
        )
        inserted += 1
    
    conn.commit()
    
    # 結果を確認
    cur.execute('SELECT COUNT(*) FROM numbers4_draws')
    total = cur.fetchone()[0]
    
    cur.execute('SELECT MIN(draw_number), MAX(draw_number) FROM numbers4_draws')
    min_draw, max_draw = cur.fetchone()
    
    conn.close()
    
    print(f"✅ DBに {inserted} 件を新規追加（{skipped} 件はスキップ）")
    print(f"📊 DB総件数: {total} 件（第{min_draw}回〜第{max_draw}回）")
    
    return inserted


if __name__ == '__main__':
    load_csv_to_db()
