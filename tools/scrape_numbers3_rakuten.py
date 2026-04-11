"""
楽天銀行ナンバーズ3スクレイパー（月次 CSV / 任意で SQLite）

月次ページは表ブロック単位の HTML のため、numbers4 用スクレイパーとはパース経路が異なる。
等級は numbers4 月次 CSV と同じ 4 列（ストレート / ボックス / セットストレート / セットボックス）に揃える。
ページ上の「ミニ」等級は DB スキーマ上の tier 列と対応しないため CSV には含めない。
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sqlite3
import sys
import time
from datetime import date
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.utils import (
    ensure_numbers3_draws_columns,
    get_db_connection,
    parse_numbers4_int_cell,
)

CSV_DIR = os.path.join(ROOT, "numbers3")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/127 Safari/537.36"
    )
}

TIER_LABELS = ("ストレート", "ボックス", "セット（ストレート）", "セット（ボックス）")


def fetch_text(url: str) -> str:
    req = Request(url, headers=HEADERS)
    try:
        with urlopen(req) as resp:
            html = resp.read()
    except HTTPError as e:
        if e.code == 404:
            print(f"[scrape] Page not found (404): {url}")
            return ""
        raise
    try:
        return html.decode("utf-8")
    except UnicodeDecodeError:
        return html.decode("cp932", errors="ignore")


def _parse_prize_pair(table_html: str, label: str) -> tuple[str, str] | None:
    esc = re.escape(label)
    m = re.search(
        rf"<th>{esc}</th>\s*<td class=\"num\">(.*?)</td>\s*"
        r'<td class="price">(.*?)</td>',
        table_html,
        re.DOTALL,
    )
    if not m:
        return None
    raw_kuchi, raw_price = m.group(1).strip(), m.group(2).strip()
    if "該当なし" in raw_kuchi or "該当なし" in raw_price:
        return "0", "0"
    km = re.fullmatch(r"([0-9,]+)口", raw_kuchi)
    pm = re.fullmatch(r"([0-9,]+)円", raw_price)
    if not km or not pm:
        return None
    return km.group(1), pm.group(1)


def parse_draw_table(table_html: str) -> dict | None:
    m_kai = re.search(r'<th colspan="2">\s*第(\d+)回\s*</th>', table_html)
    m_date = re.search(
        r"<th>抽せん日</th>\s*<td[^>]*>(\d{4}/\d{2}/\d{2})</td>", table_html
    )
    m_num = re.search(
        r"<th>当せん番号</th>\s*<td[^>]*>\s*(\d{1,3})\s*</td>", table_html
    )
    if not (m_kai and m_date and m_num):
        return None
    raw = m_num.group(1).strip()
    if not raw.isdigit():
        return None
    num = raw.zfill(3)
    if len(num) != 3:
        return None

    pairs: list[tuple[str, str]] = []
    for lab in TIER_LABELS:
        p = _parse_prize_pair(table_html, lab)
        if not p:
            return None
        pairs.append(p)

    s_kuchi, s_yen = pairs[0]
    b_kuchi, b_yen = pairs[1]
    ss_kuchi, ss_yen = pairs[2]
    sb_kuchi, sb_yen = pairs[3]

    return {
        "kai": int(m_kai.group(1)),
        "date": m_date.group(1),
        "number": num,
        "s_kuchi": s_kuchi,
        "s_kingaku": f'"{s_yen}円"',
        "b_kuchi": b_kuchi,
        "b_kingaku": f'"{b_yen}円"',
        "set_s_kuchi": ss_kuchi,
        "set_s_kingaku": f'"{ss_yen}円"',
        "set_b_kuchi": sb_kuchi,
        "set_b_kingaku": f'"{sb_yen}円"',
    }


def parse_month_html(text: str) -> list[dict]:
    parts = re.split(
        r'<table class="tblType02 tblNumberGuid">', text, flags=re.IGNORECASE
    )
    rows: list[dict] = []
    for chunk in parts[1:]:
        end = chunk.find("</table>")
        block = chunk[:end] if end != -1 else chunk
        row = parse_draw_table(block)
        if row:
            rows.append(row)
    try:
        rows.sort(key=lambda r: r["kai"])
    except Exception:
        pass
    return rows


def write_month_csv(month: str, rows: list[dict], overwrite: bool) -> tuple[int, str]:
    csv_path = os.path.join(CSV_DIR, f"{month}.csv")
    os.makedirs(CSV_DIR, exist_ok=True)

    to_write: dict[int, list] = {}
    if not overwrite and os.path.isfile(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            for cols in csv.reader(f):
                if not cols:
                    continue
                try:
                    kai = int(re.sub(r"[^0-9]", "", cols[0]))
                    to_write[kai] = cols
                except Exception:
                    continue

    for r in rows:
        kai = r["kai"]
        to_write[kai] = [
            f"第{kai}回",
            r["date"],
            r["number"],
            r["s_kuchi"],
            r["s_kingaku"],
            r["b_kuchi"],
            r["b_kingaku"],
            r["set_s_kuchi"],
            r["set_s_kingaku"],
            r["set_b_kuchi"],
            r["set_b_kingaku"],
        ]

    ordered = [to_write[k] for k in sorted(to_write)]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for line in ordered:
            writer.writerow(line)
    return len(rows), csv_path


def ensure_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS numbers3_draws (
            draw_number INTEGER PRIMARY KEY,
            draw_date TEXT NOT NULL,
            numbers TEXT NOT NULL
        );
        """
    )
    conn.commit()
    ensure_numbers3_draws_columns(conn)


def upsert_sqlite(rows: list[dict]) -> int:
    conn = get_db_connection()
    ensure_db(conn)
    cur = conn.cursor()
    inserted = 0
    for r in rows:
        kai = r["kai"]
        cur.execute("SELECT 1 FROM numbers3_draws WHERE draw_number = ?", (kai,))
        if cur.fetchone():
            continue
        cur.execute(
            """
            INSERT INTO numbers3_draws(
                draw_number, draw_date, numbers,
                tier1_winners, tier1_payout_yen,
                tier2_winners, tier2_payout_yen,
                tier3_winners, tier3_payout_yen,
                tier4_winners, tier4_payout_yen
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                kai,
                r["date"],
                r["number"],
                parse_numbers4_int_cell(r["s_kuchi"]),
                parse_numbers4_int_cell(r["s_kingaku"]),
                parse_numbers4_int_cell(r["b_kuchi"]),
                parse_numbers4_int_cell(r["b_kingaku"]),
                parse_numbers4_int_cell(r["set_s_kuchi"]),
                parse_numbers4_int_cell(r["set_s_kingaku"]),
                parse_numbers4_int_cell(r["set_b_kuchi"]),
                parse_numbers4_int_cell(r["set_b_kingaku"]),
            ),
        )
        inserted += 1
    conn.commit()
    conn.close()
    return inserted


def iter_yyyymm(start: str, end: str) -> list[str]:
    sy, sm = int(start[:4]), int(start[4:6])
    ey, em = int(end[:4]), int(end[4:6])
    out: list[str] = []
    y, m = sy, sm
    while (y, m) <= (ey, em):
        out.append(f"{y}{m:02d}")
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


def run_month(
    month: str,
    *,
    overwrite: bool,
    sqlite: bool,
) -> None:
    url = f"https://takarakuji.rakuten.co.jp/backnumber/numbers3/{month}"
    print("[scrape] Fetching:", url)
    text = fetch_text(url)
    if not text:
        return
    rows = parse_month_html(text)
    if not rows:
        print(f"[scrape] No rows parsed for {month}.")
        return
    n, csv_path = write_month_csv(month, rows, overwrite=overwrite)
    ins = upsert_sqlite(rows) if sqlite else 0
    print(f"[scrape] {month}: parsed {len(rows)} draws -> {csv_path} (merged/wrote {n} from page)")
    if sqlite:
        print(f"[scrape] SQLite +{ins} rows")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="楽天ナンバーズ3 月次バックナンバー → numbers3/YYYYMM.csv")
    p.add_argument(
        "months",
        nargs="*",
        help="YYYYMM（省略時は前月と当月）",
    )
    p.add_argument(
        "--from",
        dest="from_month",
        metavar="YYYYMM",
        help="--to と併用で範囲一括（含端）",
    )
    p.add_argument("--to", dest="to_month", metavar="YYYYMM")
    p.add_argument(
        "--sleep",
        type=float,
        default=0.25,
        help="リクエスト間の秒数（既定 0.25）",
    )
    p.add_argument(
        "--no-overwrite",
        action="store_true",
        help="既存 CSV と回号マージ（欠損のみ追記）。既定は月ごとに全行を書き直し",
    )
    p.add_argument(
        "--sqlite",
        action="store_true",
        help="lottery.db の numbers3_draws にも未存在分を投入",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    overwrite = not args.no_overwrite

    months: list[str] = []
    if args.from_month and args.to_month:
        months = iter_yyyymm(args.from_month, args.to_month)
    elif args.from_month or args.to_month:
        print("❌ --from と --to は両方指定してください")
        sys.exit(1)
    elif args.months:
        for m in args.months:
            if not re.fullmatch(r"\d{6}", m):
                print(f"❌ 無効な月: {m}")
                sys.exit(1)
            months.append(m)
    else:
        today = date.today()
        cur = f"{today.year}{today.month:02d}"
        prev_month = today.month - 1 or 12
        prev_year = today.year - 1 if today.month == 1 else today.year
        prev = f"{prev_year}{prev_month:02d}"
        months = [prev, cur]

    seen: set[str] = set()
    uniq: list[str] = []
    for m in months:
        if m not in seen:
            uniq.append(m)
            seen.add(m)

    for i, m in enumerate(uniq):
        run_month(m, overwrite=overwrite, sqlite=args.sqlite)
        if args.sleep > 0 and i + 1 < len(uniq):
            time.sleep(args.sleep)


if __name__ == "__main__":
    main()
