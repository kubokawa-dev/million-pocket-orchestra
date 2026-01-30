"""
numbers4/ 配下の月次CSV（例: 202601.csv）から
draw_number, draw_date, numbers を抽出し、正規化CSVを出力する。

使い方:
  python scripts/normalize_numbers4_csvs.py \
    --input-dir /home/kbkkbk/Develop/kubocchi/million-pocket/numbers4 \
    --output /home/kbkkbk/Develop/kubocchi/million-pocket/numbers4/draws_normalized.csv
"""
import argparse
import csv
import os
import re
from typing import Dict, Tuple


def parse_draw_number(raw: str) -> int | None:
    if not raw:
        return None
    # "第6890回" → 6890
    m = re.search(r"(\d+)", raw)
    if not m:
        return None
    return int(m.group(1))


def normalize_csvs(input_dir: str) -> Dict[int, Tuple[str, str]]:
    data: Dict[int, Tuple[str, str]] = {}
    for name in sorted(os.listdir(input_dir)):
        if not name.endswith(".csv"):
            continue
        path = os.path.join(input_dir, name)
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 3:
                    continue
                draw_number = parse_draw_number(row[0])
                draw_date = row[1].strip() if len(row) > 1 else ""
                numbers = row[2].strip() if len(row) > 2 else ""
                if draw_number is None or not draw_date or not numbers:
                    continue
                data[draw_number] = (draw_date, numbers)
    return data


def write_output(output_path: str, data: Dict[int, Tuple[str, str]]) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["draw_number", "draw_date", "numbers"])
        for draw_number in sorted(data.keys()):
            draw_date, numbers = data[draw_number]
            writer.writerow([draw_number, draw_date, numbers])


def main():
    parser = argparse.ArgumentParser(description="numbers4月次CSVの正規化")
    parser.add_argument("--input-dir", required=True, help="numbers4 CSVディレクトリ")
    parser.add_argument("--output", required=True, help="出力CSVパス")
    args = parser.parse_args()

    data = normalize_csvs(args.input_dir)
    write_output(args.output, data)
    print(f"✅ normalized rows: {len(data)}")
    print(f"✅ output: {args.output}")


if __name__ == "__main__":
    main()
