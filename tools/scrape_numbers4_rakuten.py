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
CSV_DIR = os.path.join(ROOT, 'numbers4')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127 Safari/537.36'
}

# CSV columns (no header):
# kai, date, number, s_kuchi, s_kingaku, b_kuchi, b_kingaku, set_s_kuchi, set_s_kingaku, set_b_kuchi, set_b_kingaku


def fetch_text(url: str) -> str:
    req = Request(url, headers=HEADERS)
    with urlopen(req) as resp:
        html = resp.read()
    # Try utf-8 first
    try:
        return html.decode('utf-8')
    except UnicodeDecodeError:
        return html.decode('cp932', errors='ignore')


def parse_month(text: str):
    """Parse Rakuten Numbers4 monthly page text.
    Strategy: remove HTML tags -> compact spaces -> split by date anchors ->
    for each block, take first 4-digit as number and first 4 prize pairs.
    """
    # Header range: （第6825回～第6833回）
    rng = re.search(r'（第(\d+)回～第(\d+)回）', text)
    start = end = None
    if rng:
        start = int(rng.group(1))
        end = int(rng.group(2))

    # Strip tags to get plain text stream
    plain = re.sub(r'<[^>]+>', ' ', text)
    # Normalize pipes and whitespace
    plain = plain.replace('|', ' ')
    plain = re.sub(r'[\u3000\s]+', ' ', plain)

    # Find all date positions
    dates = [m for m in re.finditer(r'(\d{4}/\d{2}/\d{2})', plain)]
    rows = []
    for idx, dm in enumerate(dates):
        date = dm.group(1)
        start_i = dm.end()
        end_i = dates[idx + 1].start() if idx + 1 < len(dates) else len(plain)
        block = plain[start_i:end_i]

        # number: first 4-digit standalone token
        nm = re.search(r'\b(\d{4})\b', block)
        if not nm:
            continue
        num = nm.group(1)

        # prize pairs: 4 pairs like "NN口 ... MMM円"
        pairs = re.findall(r'(\d+)口\s*([0-9,]+)円', block)
        if len(pairs) < 4:
            # Some pages might interleave; try to widen search window a bit
            ext_end = min(len(plain), end_i + 400)
            ext_block = plain[start_i:ext_end]
            pairs = re.findall(r'(\d+)口\s*([0-9,]+)円', ext_block)
        if len(pairs) < 4:
            continue

        s_kuchi, s_yen = pairs[0]
        b_kuchi, b_yen = pairs[1]
        ss_kuchi, ss_yen = pairs[2]
        sb_kuchi, sb_yen = pairs[3]

        rows.append({
            'date': date,
            'number': num,
            's_kuchi': s_kuchi,
            's_kingaku': f'"{s_yen}円"',
            'b_kuchi': b_kuchi,
            'b_kingaku': f'"{b_yen}円"',
            'set_s_kuchi': ss_kuchi,
            'set_s_kingaku': f'"{ss_yen}円"',
            'set_b_kuchi': sb_kuchi,
            'set_b_kingaku': f'"{sb_yen}円"',
        })

    # sort by date asc to map draw numbers
    try:
        rows.sort(key=lambda r: datetime.strptime(r['date'], '%Y/%m/%d'))
    except Exception:
        pass

    # assign draw numbers by header range if available; otherwise leave None
    if start is not None and len(rows) > 0:
        for i, r in enumerate(rows):
            r['kai'] = start + i
    else:
        for r in rows:
            r['kai'] = None

    return start, end, rows


def upsert_csv(month: str, rows):
    # month is YYYYMM
    csv_path = os.path.join(CSV_DIR, f'{month}.csv')
    os.makedirs(CSV_DIR, exist_ok=True)

    existing = {}
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for cols in reader:
                if not cols:
                    continue
                # Expect: 第XXXX回,YYYY/MM/DD,NNNN,...
                try:
                    kai_str = cols[0]
                    kai = int(re.sub(r'[^0-9]', '', kai_str))
                    existing[kai] = cols
                except Exception:
                    continue

    # Build new lines and merge only missing draw numbers
    appended = 0
    with open(csv_path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for r in rows:
            kai = r['kai']
            if kai is None:
                # cannot map draw number; skip CSV append
                continue
            if kai in existing:
                continue
            line = [
                f'第{kai}回',
                r['date'],
                r['number'],
                r['s_kuchi'], r['s_kingaku'],
                r['b_kuchi'], r['b_kingaku'],
                r['set_s_kuchi'], r['set_s_kingaku'],
                r['set_b_kuchi'], r['set_b_kingaku'],
            ]
            writer.writerow(line)
            appended += 1
    return appended, csv_path


def ensure_db(conn):
    cur = conn.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS numbers4_draws (
            draw_number INTEGER PRIMARY KEY,
            draw_date TEXT NOT NULL,
            numbers TEXT NOT NULL
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
        cur.execute('SELECT 1 FROM numbers4_draws WHERE draw_number = %s', (kai,))
        if cur.fetchone():
            continue
        cur.execute(
            'INSERT INTO numbers4_draws(draw_number, draw_date, numbers) VALUES (%s,%s,%s)',
            (kai, r['date'], r['number'])
        )
        inserted += 1
    conn.commit()
    conn.close()
    return inserted


def run(url: str):
    print('[scrape] Fetching:', url)
    text = fetch_text(url)
    start, end, rows = parse_month(text)
    if not rows:
        print('[scrape] No rows parsed. Check page structure.')
        return
    # Determine month string from first date
    mstr = None
    for r in rows:
        if r['date']:
            mstr = r['date'].replace('/', '')[:6]
            break
    if not mstr:
        print('[scrape] Could not determine month string.')
        return

    appended, csv_path = upsert_csv(mstr, rows)
    inserted = upsert_postgres(rows)

    print(f"[scrape] Parsed range: 第{start}回～第{end}回 | Rows: {len(rows)}")
    print(f"[scrape] CSV updated: +{appended} rows -> {csv_path}")
    print(f"[scrape] PostgreSQL updated: +{inserted} rows")


if __name__ == '__main__':
    # CLI usage:
    #   python tools/scrape_numbers4_rakuten.py            -> fetch current and previous month
    #   python tools/scrape_numbers4_rakuten.py 202510     -> fetch specified month
    #   python tools/scrape_numbers4_rakuten.py 202509 202510 -> fetch two months

    def ym_str(dt: date) -> str:
        return f"{dt.year}{dt.month:02d}"

    args = [a for a in sys.argv[1:] if re.fullmatch(r"\d{6}", a)]
    months = []
    if args:
        months = args
    else:
        today = date.today()
        # current month
        cur = ym_str(today)
        # previous month
        prev_month = today.month - 1 or 12
        prev_year = today.year - 1 if today.month == 1 else today.year
        prev = f"{prev_year}{prev_month:02d}"
        months = [prev, cur]

    # Deduplicate while preserving order
    seen = set()
    uniq_months = []
    for m in months:
        if m not in seen:
            uniq_months.append(m)
            seen.add(m)

    for m in uniq_months:
        url = f'https://takarakuji.rakuten.co.jp/backnumber/numbers4/{m}'
        run(url)
