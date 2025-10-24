"""Test the extreme patterns generation logic"""
import pandas as pd
import numpy as np

# Simulate the enumeration logic
predictions = set()
latest_number = "5414"  # Example latest draw

# 1a. Enumerate all sum 0-2 patterns
print("Enumerating all sum 0-2 patterns...")
for d1 in range(3):  # 0, 1, 2
    for d2 in range(3):
        for d3 in range(3):
            for d4 in range(3):
                if d1 + d2 + d3 + d4 <= 2:
                    num_str = f"{d1}{d2}{d3}{d4}"
                    if num_str != latest_number:
                        predictions.add(num_str)

print(f"\nTotal patterns with sum 0-2: {len(predictions)}")
print(f"\nAll generated patterns:")
sorted_predictions = sorted(predictions)
for p in sorted_predictions:
    digit_sum = sum(int(d) for d in p)
    print(f"  {p} (sum: {digit_sum})")

# Check if 0100 is in the list
if "0100" in predictions:
    print(f"\n✅ 0100 is in the predictions!")
else:
    print(f"\n❌ 0100 is NOT in the predictions!")
    print(f"\nDebugging: checking generation logic")
    d1, d2, d3, d4 = 0, 1, 0, 0
    print(f"  d1={d1}, d2={d2}, d3={d3}, d4={d4}")
    print(f"  sum={d1+d2+d3+d4}")
    print(f"  Condition d1+d2+d3+d4 <= 2: {d1+d2+d3+d4 <= 2}")
    print(f"  num_str = f'{d1}{d2}{d3}{d4}' = '{d1}{d2}{d3}{d4}'")
    
    # Check if it's in the range
    if d1 < 3 and d2 < 3 and d3 < 3 and d4 < 3:
        print(f"  All digits are in range(3): True")
    else:
        print(f"  Some digits are out of range!")
