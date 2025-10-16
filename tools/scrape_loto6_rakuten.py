import os
import re
import csv
import psycopg2
import sys
from datetime import datetime, date
from urllib.request import urlopen, Request
from dotenv import load_dotenv

load_dotenv()

ROOT = os.path.dirname(os.path.dirname(__file__))
CSV_DIR = os.path.join(ROOT, 'loto6')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127 Safari/537.36'
}

# Target table: loto6_draws(draw_number INTEGER PK, draw_date TEXT, numbers TEXT, bonus_number INTEGER)


def fetch_text(url: str) -> str:
    req = Request(url, headers=HEADERS)
    with urlopen(req) as resp:
        html = resp.read()
    for enc in ('utf-8', 'cp932'):
        try:
            return html.decode(enc)
        except UnicodeDecodeError:
            continue
    return html.decode('utf-8', errors='ignore')


def parse_month(text: str):
    """Parse Rakuten Loto6 monthly page text into rows.
    Extract draw range header, then split by dates, find 6 main numbers and a bonus in each block.
    """
    # Header example: （第2039回～第2041回）
    rng = re.search(r'（第(\d+)回～第(\d+)回）', text)
    start = end = None
    if rng:
        start = int(rng.group(1))
        end = int(rng.group(2))

    # Strip tags to get a plain text stream
    plain = re.sub(r'<[^>]+>', ' ', text)
    plain = plain.replace('|', ' ')
    plain = re.sub(r'[\u3000\s]+', ' ', plain)

    # Find all date positions
    dates = [m for m in re.finditer(r'(\d{4}/\d{2}/\d{2})', plain)]
    rows = []
    for idx, dm in enumerate(dates):
        date_str = dm.group(1)
        start_i = dm.end()
        end_i = dates[idx + 1].start() if idx + 1 < len(dates) else len(plain)
        block = plain[start_i:end_i]

        # Bonus number often shown in parentheses
        bonus = None
        bm = re.search(r'\((\d{1,2})\)', block)
        if bm:
            try:
                b = int(bm.group(1))
                if 1 <= b <= 43:
                    bonus = b
            except Exception:
                pass

        # Extract candidate numbers 1..43 from the block
        nums = [int(x) for x in re.findall(r'\b(\d{1,2})\b', block)
                if x.isdigit() and 1 <= int(x) <= 43]
        # Remove the bonus occurrence from nums (if present once)
        if bonus is not None:
            # remove only one instance
            removed = False
            tmp = []
            for v in nums:
                if (v == bonus) and (not removed):
                    removed = True
                    continue
                tmp.append(v)
            nums = tmp

        # Deduplicate while preserving order
        seen = set()
        uniq = []
        for n in nums:
            if n not in seen:
                uniq.append(n)
                seen.add(n)

        if len(uniq) < 6:
            # Widen the window just in case
            ext_end = min(len(plain), end_i + 300)
            ext_block = plain[start_i:ext_end]
            nums_ext = [int(x) for x in re.findall(r'\b(\d{1,2})\b', ext_block)
                        if x.isdigit() and 1 <= int(x) <= 43]
            if bonus is not None and (bonus in nums_ext):
                # remove first occurrence of bonus
                ridx = nums_ext.index(bonus)
                nums_ext.pop(ridx)
            uniq = []
            seen = set()
            for n in nums_ext:
                if n not in seen:
                    uniq.append(n)
                    seen.add(n)

        if len(uniq) < 6:
            continue

        main6 = uniq[:6]
        main6.sort()

        rows.append({
            'date': date_str,
            'nums': main6,
            'bonus': bonus,
        })

    # Sort by date asc to map draw numbers
    try:
        rows.sort(key=lambda r: datetime.strptime(r['date'], '%Y/%m/%d'))
    except Exception:
        pass

    # assign draw numbers by header range if available
    if start is not None and len(rows) > 0:
        for i, r in enumerate(rows):
            r['kai'] = start + i
    else:
        for r in rows:
            r['kai'] = None

    return start, end, rows


def upsert_csv(month: str, rows):
    csv_path = os.path.join(CSV_DIR, f'{month}.csv')
    os.makedirs(CSV_DIR, exist_ok=True)

    existing = set()
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for cols in reader:
                if not cols:
                    continue
                try:
                    kai = int(re.sub(r'[^0-9]', '', cols[0]))
                    existing.add(kai)
                except Exception:
                    continue

    appended = 0
    with open(csv_path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for r in rows:
            kai = r['kai']
            if kai is None or kai in existing:
                continue
            n1, n2, n3, n4, n5, n6 = r['nums']
            bonus_token = f'({r["bonus"]})' if r['bonus'] is not None else ''
            line = [
                f'第{kai}回',
                r['date'],
                n1, n2, n3, n4, n5, n6,
                bonus_token,
            ]
            writer.writerow(line)
            appended += 1
    return appended, csv_path


def ensure_db(conn):
    cur = conn.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS loto6_draws (
            draw_number INTEGER PRIMARY KEY,
            draw_date TEXT NOT NULL,
            numbers TEXT NOT NULL,
            bonus_number INTEGER
        );
        '''
    )
    conn.commit()


def upsert_postgres(rows):
    db_url = os.environ.get('DATABASE_URL')
    if db_url and '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    conn = psycopg2.connect(db_url)
    ensure_db(conn)
    cur = conn.cursor()
    inserted = 0
    for r in rows:
        kai = r['kai']
        if kai is None:
            continue
        cur.execute('SELECT 1 FROM loto6_draws WHERE draw_number = %s', (kai,))
        if cur.fetchone():
            continue
        numbers_str = ','.join(str(x) for x in r['nums'])
        bonus = int(r['bonus']) if r['bonus'] is not None else None
        cur.execute(
            'INSERT INTO loto6_draws(draw_number, draw_date, numbers, bonus_number) VALUES (%s,%s,%s,%s)',
            (kai, r['date'], numbers_str, bonus)
        )
        inserted += 1
    conn.commit()
    conn.close()
    return inserted


def run(url: str):
    print('[scrape-loto6] Fetching:', url)
    text = fetch_text(url)
    start, end, rows = parse_month(text)
    if not rows:
        print('[scrape-loto6] No rows parsed. Check page structure.')
        return
    # Determine month string from first date
    mstr = None
    for r in rows:
        if r['date']:
            mstr = r['date'].replace('/', '')[:6]
            break
    if not mstr:
        print('[scrape-loto6] Could not determine month string.')
        return

    appended, csv_path = upsert_csv(mstr, rows)
    inserted = upsert_postgres(rows)

    print(f"[scrape-loto6] Parsed range: 第{start}回～第{end}回 | Rows: {len(rows)}")
    print(f"[scrape-loto6] CSV updated: +{appended} rows -> {csv_path}")
    print(f"[scrape-loto6] PostgreSQL updated: +{inserted} rows")


if __name__ == '__main__':
    # CLI usage:
    #   python tools/scrape_loto6_rakuten.py            -> fetch current and previous month
    #   python tools/scrape_loto6_rakuten.py 202510     -> fetch specified month
    #   python tools/scrape_loto6_rakuten.py 202509 202510 -> fetch two months

    def ym_str(dt: date) -> str:
        return f"{dt.year}{dt.month:02d}"

    args = [a for a in sys.argv[1:] if re.fullmatch(r"\d{6}", a)]
    months = []
    if args:
        months = args
    else:
        today = date.today()
        cur = ym_str(today)
        prev_month = today.month - 1 or 12
        prev_year = today.year - 1 if today.month == 1 else today.year
        prev = f"{prev_year}{prev_month:02d}"
        months = [prev, cur]

    seen = set()
    uniq_months = []
    for m in months:
        if m not in seen:
            uniq_months.append(m)
            seen.add(m)

    for m in uniq_months:
        url = f'https://takarakuji.rakuten.co.jp/backnumber/loto6/{m}'
        run(url)
