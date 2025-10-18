import os
import re
from urllib.request import urlopen, Request

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

def parse_loto6_detailed(html: str):
    """Parse Rakuten Loto6 page with detailed prize information."""
    
    # Remove all HTML tags but keep the text structure
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    
    # Find all draw sections by looking for draw number patterns
    # Pattern: 第XXXX回 followed by date YYYY/MM/DD
    draw_pattern = r'第(\d+)回[^0-9]*(\d{4}/\d{2}/\d{2})'
    draws = list(re.finditer(draw_pattern, text))
    
    rows = []
    
    for i, match in enumerate(draws):
        draw_num = match.group(1)
        draw_date = match.group(2)
        
        # Extract the section for this draw (from current match to next match or end)
        start_pos = match.end()
        end_pos = draws[i + 1].start() if i + 1 < len(draws) else len(text)
        section = text[start_pos:end_pos]
        
        # Extract main numbers (looking for 6 numbers between 1-43)
        # They usually appear in sequence after "本数字" or in a specific pattern
        number_candidates = []
        
        # Look for number patterns in the section
        # Remove HTML tags from section first
        clean_section = re.sub(r'<[^>]+>', ' ', section)
        
        # Find all 1-2 digit numbers that could be lottery numbers
        all_nums = re.findall(r'\b(\d{1,2})\b', clean_section)
        
        # Filter to valid lottery numbers (1-43)
        valid_nums = [n for n in all_nums if n.isdigit() and 1 <= int(n) <= 43]
        
        # Take first 7 unique numbers (6 main + 1 bonus)
        seen = set()
        unique_nums = []
        for n in valid_nums:
            if n not in seen:
                unique_nums.append(n)
                seen.add(n)
            if len(unique_nums) >= 7:
                break
        
        if len(unique_nums) < 6:
            print(f"Warning: Could not find 6 numbers for draw {draw_num}")
            continue
        
        main_numbers = unique_nums[:6]
        bonus_number = unique_nums[6] if len(unique_nums) > 6 else None
        
        # Extract prize information
        # Look for patterns like "X口" followed by "XX,XXX円"
        prize_pattern = r'(該当なし|[\d,]+口)[^0-9円]*(該当なし|[\d,]+円)'
        prizes = re.findall(prize_pattern, clean_section)
        
        # Build CSV line
        csv_line = [f'第{draw_num}回', draw_date]
        csv_line.extend(main_numbers)
        csv_line.append(f'({bonus_number})' if bonus_number else '')
        
        # Add prize information (expecting 5 ranks: 1st to 5th)
        for j in range(5):
            if j < len(prizes):
                csv_line.append(prizes[j][0])  # winners
                csv_line.append(f'"{prizes[j][1]}"')  # amount
            else:
                csv_line.append('該当なし')
                csv_line.append('該当なし')
        
        # Add carryover (look for キャリーオーバー)
        carryover_match = re.search(r'キャリーオーバー[^0-9]*([\d,]+円)', clean_section)
        if carryover_match:
            csv_line.append(f'"{carryover_match.group(1)}"')
        else:
            csv_line.append('"0円"')
        
        rows.append(csv_line)
    
    return rows

def main():
    url = 'https://takarakuji.rakuten.co.jp/backnumber/loto6/202510/'
    print(f'Fetching: {url}')
    
    html = fetch_html(url)
    rows = parse_loto6_detailed(html)
    
    if not rows:
        print('No data found!')
        return
    
    # Write to CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'loto6', '202510.csv')
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        for row in rows:
            f.write(','.join(str(x) for x in row) + '\n')
    
    print(f'\nSuccessfully wrote {len(rows)} rows to {csv_path}')
    print('\nParsed data:')
    for row in rows:
        print(','.join(str(x) for x in row))

if __name__ == '__main__':
    main()
