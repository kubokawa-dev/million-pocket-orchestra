"""
楽天銀行ロト6スクレイパー（月次 CSV + 任意で SQLite）

月次ページは numbers3 と同様の tblType02 表ブロックのため、旧プレーンテキストパーサーは使わない。
CSV は既存 loto6/*.csv と同一20列（train_and_predict / advanced_predict の COLS 互換）。
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import time
from datetime import date
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tools.utils import get_db_connection

CSV_DIR = os.path.join(ROOT, "loto6")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/127 Safari/537.36"
    )
}


def fetch_text(url: str) -> str:
    req = Request(url, headers=HEADERS)
    try:
        with urlopen(req) as resp:
            html = resp.read()
    except HTTPError as e:
        if e.code == 404:
            print(f"[scrape-loto6] Page not found (404): {url}")
            return ""
        raise
    for enc in ("utf-8", "cp932"):
        try:
            return html.decode(enc)
        except UnicodeDecodeError:
            continue
    return html.decode("utf-8", errors="ignore")


def _strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


def _tier_pair(table_html: str, label: str) -> tuple[str, str]:
    m = re.search(
        rf"<th>{re.escape(label)}</th>\s*"
        r'<td class="txtRight" colspan="3">(.*?)</td>\s*'
        r'<td class="txtRight" colspan="3">(.*?)</td>',
        table_html,
        re.DOTALL,
    )
    if not m:
        return "該当なし", "該当なし"
    return _strip_tags(m.group(1)), _strip_tags(m.group(2))


def parse_draw_table(table_html: str) -> dict | None:
    m_kai = re.search(r'<th colspan="6">\s*第(\d+)回\s*</th>', table_html)
    m_date = re.search(
        r'<th>抽せん日</th>\s*<td[^>]*colspan="6">(\d{4}/\d{2}/\d{2})</td>',
        table_html,
    )
    main_m = re.search(r"<th>本数字</th>(.*?)</tr>", table_html, re.DOTALL)
    if not (m_kai and m_date and main_m):
        return None
    nums = [int(x) for x in re.findall(r"loto-font-large\">(\d+)</span>", main_m.group(1))]
    if len(nums) != 6:
        return None

    bm = re.search(r"loto-highlight[^>]*>\((\d+)\)</span>", table_html)
    bonus = int(bm.group(1)) if bm else None

    t1w, t1y = _tier_pair(table_html, "1等")
    t2w, t2y = _tier_pair(table_html, "2等")
    t3w, t3y = _tier_pair(table_html, "3等")
    t4w, t4y = _tier_pair(table_html, "4等")
    t5w, t5y = _tier_pair(table_html, "5等")

    cm = re.search(
        r"<th>キャリーオーバー</th>\s*<td[^>]*colspan=\"6\">(.*?)</td>",
        table_html,
        re.DOTALL,
    )
    carry = _strip_tags(cm.group(1)) if cm else "0円"

    return {
        "kai": int(m_kai.group(1)),
        "date": m_date.group(1),
        "nums": nums,
        "bonus": bonus,
        "t1w": t1w,
        "t1y": t1y,
        "t2w": t2w,
        "t2y": t2y,
        "t3w": t3w,
        "t3y": t3y,
        "t4w": t4w,
        "t4y": t4y,
        "t5w": t5w,
        "t5y": t5y,
        "carry": carry,
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
    rows.sort(key=lambda r: r["kai"])
    return rows


def row_to_csv_line(r: dict) -> list:
    n1, n2, n3, n4, n5, n6 = r["nums"]
    bonus_cell = f"({r['bonus']})" if r["bonus"] is not None else ""
    return [
        f"第{r['kai']}回",
        r["date"],
        n1,
        n2,
        n3,
        n4,
        n5,
        n6,
        bonus_cell,
        r["t1w"],
        r["t1y"],
        r["t2w"],
        r["t2y"],
        r["t3w"],
        r["t3y"],
        r["t4w"],
        r["t4y"],
        r["t5w"],
        r["t5y"],
        r["carry"],
    ]


def write_month_csv(month: str, rows: list[dict], overwrite: bool) -> tuple[int, str]:
    csv_path = os.path.join(CSV_DIR, f"{month}.csv")
    os.makedirs(CSV_DIR, exist_ok=True)

    merged: dict[int, list] = {}
    if not overwrite and os.path.isfile(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            for cols in csv.reader(f):
                if not cols:
                    continue
                try:
                    kai = int(re.sub(r"[^0-9]", "", cols[0]))
                    merged[kai] = cols
                except Exception:
                    continue

    for r in rows:
        merged[r["kai"]] = row_to_csv_line(r)

    ordered = [merged[k] for k in sorted(merged)]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(ordered)
    return len(rows), csv_path


def ensure_db(conn):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS loto6_draws (
            draw_number INTEGER PRIMARY KEY,
            draw_date TEXT NOT NULL,
            numbers TEXT NOT NULL,
            bonus_number INTEGER
        );
        """
    )
    conn.commit()


def upsert_sqlite(rows: list[dict]) -> int:
    conn = get_db_connection()
    ensure_db(conn)
    cur = conn.cursor()
    inserted = 0
    for r in rows:
        kai = r["kai"]
        cur.execute("SELECT 1 FROM loto6_draws WHERE draw_number = ?", (kai,))
        if cur.fetchone():
            continue
        numbers_str = ",".join(str(x) for x in r["nums"])
        bonus = int(r["bonus"]) if r["bonus"] is not None else None
        cur.execute(
            "INSERT INTO loto6_draws(draw_number, draw_date, numbers, bonus_number) VALUES (?,?,?,?)",
            (kai, r["date"], numbers_str, bonus),
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
    url = f"https://takarakuji.rakuten.co.jp/backnumber/loto6/{month}"
    print("[scrape-loto6] Fetching:", url)
    text = fetch_text(url)
    if not text:
        return
    rows = parse_month_html(text)
    if not rows:
        print(f"[scrape-loto6] No rows parsed for {month}.")
        return
    n, csv_path = write_month_csv(month, rows, overwrite=overwrite)
    ins = upsert_sqlite(rows) if sqlite else 0
    print(f"[scrape-loto6] {month}: {len(rows)} draws -> {csv_path}")
    if sqlite:
        print(f"[scrape-loto6] SQLite +{ins} rows")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="楽天ロト6 月次バックナンバー → loto6/YYYYMM.csv")
    p.add_argument("months", nargs="*", help="YYYYMM（省略時は前月と当月）")
    p.add_argument(
        "--from",
        dest="from_month",
        metavar="YYYYMM",
        help="--to と併用で範囲一括（端含む）",
    )
    p.add_argument("--to", dest="to_month", metavar="YYYYMM")
    p.add_argument("--sleep", type=float, default=0.25)
    p.add_argument(
        "--no-overwrite",
        action="store_true",
        help="既存 CSV と回号マージ（欠損のみ）。既定は月ごとに表の内容で全置換",
    )
    p.add_argument(
        "--sqlite",
        action="store_true",
        help="lottery.db の loto6_draws にも未存在分を投入",
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
