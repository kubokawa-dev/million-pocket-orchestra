"""
CSVファイルからSQLiteデータベースにナンバーズ4の履歴データをロードするスクリプト

GitHub Actions上で毎回DBを再構築するために使用します。
numbers4/*.csv から全履歴を読み込み、当選番号に加え4等級分の口数・払戻金額も投入します。
"""
import os
import re
import csv
import sys
import glob

# プロジェクトルートをパスに追加
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from tools.utils import (
    get_db_connection,
    ensure_numbers4_draws_columns,
    parse_numbers4_int_cell,
)

CSV_DIR = os.path.join(ROOT, "numbers4")

# 月次ファイル名: 201503.csv → 年 2015
_MONTH_CSV_NAME_RE = re.compile(r"^(\d{4})(\d{2})\.csv$")

INSERT_SQL = """
INSERT OR REPLACE INTO numbers4_draws (
    draw_number, draw_date, numbers,
    tier1_winners, tier1_payout_yen,
    tier2_winners, tier2_payout_yen,
    tier3_winners, tier3_payout_yen,
    tier4_winners, tier4_payout_yen
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def ensure_table(conn):
    """テーブルが存在しない場合は作成（既存3列DBは後続で ALTER）"""
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS numbers4_draws (
            draw_number INTEGER PRIMARY KEY,
            draw_date TEXT NOT NULL,
            numbers TEXT NOT NULL
        )
        """
    )
    conn.commit()
    ensure_numbers4_draws_columns(conn)


def parse_csv_row(row: list[str]):
    """
    CSVの1行をパースして DB 投入用タプルを返す（不足列は None）

    CSVフォーマット例:
    第6890回,2026/01/05,7526,23,"1,042,200円",374,"43,400円",...
    tier1..4 = ストレート / ボックス / セットストレート / セットボックス
    """
    if len(row) < 3:
        return None

    kai_str = row[0]
    kai_match = re.search(r"(\d+)", kai_str)
    if not kai_match:
        return None
    draw_number = int(kai_match.group(1))

    draw_date = row[1].strip()
    numbers = row[2].strip()
    if not re.fullmatch(r"\d{4}", numbers):
        return None

    t1w = parse_numbers4_int_cell(row[3]) if len(row) > 3 else None
    t1y = parse_numbers4_int_cell(row[4]) if len(row) > 4 else None
    t2w = parse_numbers4_int_cell(row[5]) if len(row) > 5 else None
    t2y = parse_numbers4_int_cell(row[6]) if len(row) > 6 else None
    t3w = parse_numbers4_int_cell(row[7]) if len(row) > 7 else None
    t3y = parse_numbers4_int_cell(row[8]) if len(row) > 8 else None
    t4w = parse_numbers4_int_cell(row[9]) if len(row) > 9 else None
    t4y = parse_numbers4_int_cell(row[10]) if len(row) > 10 else None

    return (
        draw_number,
        draw_date,
        numbers,
        t1w,
        t1y,
        t2w,
        t2y,
        t3w,
        t3y,
        t4w,
        t4y,
    )


def load_all_csv_files():
    """numbers4/*.csv から全データを読み込む"""
    csv_files = sorted(glob.glob(os.path.join(CSV_DIR, "*.csv")))
    skip_names = {"draws_normalized.csv"}

    all_rows = []
    for csv_path in csv_files:
        base = os.path.basename(csv_path)
        if base in skip_names:
            continue
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
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


def load_csv_files_for_year_range(min_year: int, max_year: int) -> list:
    """
    numbers4/YYYYMM.csv のファイル名から年を解釈し、min_year〜max_year の月次だけ読む。
    """
    if min_year > max_year:
        raise ValueError("min_year must be <= max_year")

    csv_files = sorted(glob.glob(os.path.join(CSV_DIR, "*.csv")))
    skip_names = {"draws_normalized.csv"}

    all_rows: list = []
    used_files: list[str] = []
    for csv_path in csv_files:
        base = os.path.basename(csv_path)
        if base in skip_names:
            continue
        m = _MONTH_CSV_NAME_RE.match(base)
        if not m:
            continue
        year = int(m.group(1))
        if year < min_year or year > max_year:
            continue
        used_files.append(base)
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
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

    print(
        f"📅 年範囲 {min_year}–{max_year}: "
        f"{len(used_files)} 個の月次CSVから {len(all_rows)} 行を読み込み"
    )
    return all_rows


def load_csv_to_db():
    """CSVファイルからDBにデータをロード"""
    print("=" * 60)
    print("📂 CSVからデータベースを構築中...")
    print("=" * 60)

    all_rows = load_all_csv_files()
    print(f"📊 CSVから {len(all_rows)} 件のデータを読み込みました")

    if not all_rows:
        print("⚠️  CSVファイルにデータがありません")
        return 0

    conn = get_db_connection()
    ensure_table(conn)
    cur = conn.cursor()

    inserted = 0
    for row in all_rows:
        cur.execute(INSERT_SQL, row)
        inserted += 1

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM numbers4_draws")
    total = cur.fetchone()[0]

    cur.execute("SELECT MIN(draw_number), MAX(draw_number) FROM numbers4_draws")
    min_draw, max_draw = cur.fetchone()

    cur.execute(
        "SELECT COUNT(*) FROM numbers4_draws WHERE tier1_winners IS NOT NULL"
    )
    with_prizes = cur.fetchone()[0]

    conn.close()

    print(f"✅ DBに {inserted} 件を反映（INSERT OR REPLACE）")
    print(f"📊 DB総件数: {total} 件（第{min_draw}回〜第{max_draw}回）")
    print(f"📊 払戻列あり: {with_prizes} 件")
    return inserted


if __name__ == "__main__":
    load_csv_to_db()
