import os
import re
import csv
from urllib.request import urlopen, Request

# Define headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.1 Safari/537.36'
}

def fetch_html(url: str) -> str:
    """Fetches HTML content from a URL."""
    req = Request(url, headers=HEADERS)
    try:
        with urlopen(req) as resp:
            html_bytes = resp.read()
            # Try decoding with utf-8 first, then cp932 as a fallback
            try:
                return html_bytes.decode('utf-8')
            except UnicodeDecodeError:
                return html_bytes.decode('cp932', errors='ignore')
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return ""

def parse_and_format(html: str) -> list:
    """Parses the HTML to extract Loto6 draw data."""
    # Use BeautifulSoup to parse the HTML
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    all_rows = []
    # Find all sections, each containing one draw's data
    draw_sections = soup.select('section.p-backnumber__section')

    for section in draw_sections:
        # Extract draw number and date from the title
        title_text = section.select_one('h3.p-backnumber__title').get_text(strip=True)
        draw_match = re.search(r'第(\d+)回', title_text)
        date_match = re.search(r'(\d{4}/\d{2}/\d{2})', title_text)
        if not (draw_match and date_match):
            continue

        draw_number = draw_match.group(1)
        draw_date = date_match.group(1)

        # Extract winning numbers
        numbers = [num.get_text(strip=True) for num in section.select('ul.p-backnumber__number-list li:not(.p-backnumber__bonus) .p-backnumber__number-item')]
        bonus_number = section.select_one('.p-backnumber__bonus .p-backnumber__number-item').get_text(strip=True)

        # Extract prize details
        prize_data = []
        prize_rows = section.select('table.p-backnumber__table tr')
        # 1等 to 5等
        for i in range(1, 6):
            # The first row is a header, so we skip it (i)
            if i < len(prize_rows):
                cells = prize_rows[i].select('td')
                if len(cells) == 3:
                    winners = cells[1].get_text(strip=True)
                    amount = cells[2].get_text(strip=True)
                    prize_data.extend([winners, amount])
                else:
                    prize_data.extend(['該当なし', '該当なし'])
            else:
                 prize_data.extend(['該当なし', '該当なし'])

        # Extract carryover
        carryover_text = section.select_one('.p-backnumber__carryover').get_text(strip=True)
        carryover_match = re.search(r'([0-9,]+円)', carryover_text)
        carryover = carryover_match.group(1) if carryover_match else '0円'

        # Assemble the row for the CSV
        csv_row = [
            f'第{draw_number}回',
            draw_date,
            *numbers,
            f'({bonus_number})',
            *prize_data,
            f'"{carryover}"'
        ]
        all_rows.append(csv_row)

    return all_rows

def main():
    """Main function to scrape and write data."""
    url = 'https://takarakuji.rakuten.co.jp/backnumber/loto6/202510/'
    print(f"Fetching data from {url}...")
    html = fetch_html(url)
    if not html:
        print("Failed to fetch HTML. Aborting.")
        return

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("BeautifulSoup is not installed. Please install it using: pip install beautifulsoup4")
        return

    print("Parsing data...")
    loto6_data = parse_and_format(html)

    if not loto6_data:
        print("No data was parsed. The website structure might have changed.")
        return

    # Sort data by draw number descending
    loto6_data.sort(key=lambda x: int(re.search(r'(\d+)', x[0]).group(1)), reverse=True)

    # Define the output file path
    output_file = os.path.join('loto6', '202510.csv')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print(f"Writing data to {output_file}...")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONE, escapechar='\\')
        for row in loto6_data:
            # Manually handle quoting for prize money to match your format
            formatted_row = []
            for item in row:
                if '円' in str(item) and ',' in str(item):
                    formatted_row.append(f'"{item}"')
                else:
                    formatted_row.append(item)
            writer.writerow(formatted_row)

    print("\n--- Scraped Data ---")
    for row in loto6_data:
        print(','.join(map(str,row)))
    print(f"\nSuccessfully updated {output_file} with {len(loto6_data)} records.")

if __name__ == '__main__':
    main()
