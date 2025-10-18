import os
import re
import csv
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127 Safari/537.36'
}

def fetch_html(url: str) -> str:
    req = Request(url, headers=HEADERS)
    with urlopen(req) as resp:
        html = resp.read()
    for enc in ('utf-8', 'cp932'):
        try:
            return html.decode(enc)
        except UnicodeDecodeError:
            continue
    return html.decode('utf-8', errors='ignore')

def parse_loto6_page(html: str):
    """Parse Rakuten Loto6 page and extract all draw information including prizes."""
    soup = BeautifulSoup(html, 'html.parser')
    rows = []
    
    # Find all draw sections
    draw_sections = soup.find_all('section', class_='p-backnumber__section')
    
    for section in draw_sections:
        try:
            # Extract draw number and date
            title = section.find('h3', class_='p-backnumber__title')
            if not title:
                continue
            
            title_text = title.get_text(strip=True)
            draw_match = re.search(r'第(\d+)回', title_text)
            date_match = re.search(r'(\d{4}/\d{2}/\d{2})', title_text)
            
            if not draw_match or not date_match:
                continue
            
            draw_num = draw_match.group(1)
            draw_date = date_match.group(1)
            
            # Extract numbers
            number_items = section.find_all('li', class_='p-backnumber__number-item')
            main_numbers = []
            bonus_number = None
            
            for item in number_items:
                num_text = item.get_text(strip=True)
                if 'ボーナス数字' in item.get('class', []) or item.find_parent(class_='p-backnumber__bonus'):
                    bonus_number = num_text
                else:
                    main_numbers.append(num_text)
            
            # Extract prize information
            prize_table = section.find('table', class_='p-backnumber__table')
            prizes = {}
            
            if prize_table:
                prize_rows = prize_table.find_all('tr')
                for row in prize_rows[1:]:  # Skip header
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        rank = cells[0].get_text(strip=True)
                        winners = cells[1].get_text(strip=True)
                        amount = cells[2].get_text(strip=True)
                        prizes[rank] = {'winners': winners, 'amount': amount}
            
            # Format the CSV line according to the provided format
            # 第2030回,2025/09/01,3,7,28,29,32,36,(13),該当なし,該当なし,4口,"18,228,100円",264口,"298,200円","12,618口","6,500円","198,695口","1,000円","324,569,514円"
            
            csv_line = [f'第{draw_num}回', draw_date]
            
            # Add main numbers
            if len(main_numbers) >= 6:
                csv_line.extend(main_numbers[:6])
            else:
                csv_line.extend(main_numbers)
                csv_line.extend([''] * (6 - len(main_numbers)))
            
            # Add bonus number
            csv_line.append(f'({bonus_number})' if bonus_number else '')
            
            # Add prize information (1st to 5th place + carryover)
            # Format: winners, amount for each rank
            for rank_num in range(1, 6):
                rank_key = f'{rank_num}等'
                if rank_key in prizes:
                    winners = prizes[rank_key]['winners']
                    amount = prizes[rank_key]['amount']
                    csv_line.append(winners)
                    csv_line.append(amount)
                else:
                    csv_line.append('該当なし')
                    csv_line.append('該当なし')
            
            # Add carryover amount (last column)
            carryover = section.find(text=re.compile(r'キャリーオーバー'))
            if carryover:
                carryover_parent = carryover.find_parent()
                carryover_amount = re.search(r'[\d,]+円', carryover_parent.get_text())
                csv_line.append(carryover_amount.group(0) if carryover_amount else '0円')
            else:
                csv_line.append('0円')
            
            rows.append(csv_line)
            
        except Exception as e:
            print(f"Error parsing section: {e}")
            continue
    
    return rows

def main():
    url = 'https://takarakuji.rakuten.co.jp/backnumber/loto6/202510/'
    print(f'Fetching: {url}')
    
    html = fetch_html(url)
    rows = parse_loto6_page(html)
    
    if not rows:
        print('No data found!')
        return
    
    # Write to CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'loto6', '202510.csv')
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)
    
    print(f'Successfully wrote {len(rows)} rows to {csv_path}')
    for row in rows:
        print(','.join(str(x) for x in row))

if __name__ == '__main__':
    main()
