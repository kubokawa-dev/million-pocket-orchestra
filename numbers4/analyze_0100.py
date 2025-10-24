import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

db_url = os.environ.get('DATABASE_URL')
if db_url and '?schema' in db_url:
    db_url = db_url.split('?schema')[0]

conn = psycopg2.connect(db_url)
cur = conn.cursor()

print("="*80)
print("Analysis of '0100' and similar patterns")
print("="*80)

# Count numbers starting with 0
cur.execute("SELECT COUNT(*) FROM numbers4_draws WHERE numbers LIKE '0%'")
count_0 = cur.fetchone()[0]

# Total count
cur.execute("SELECT COUNT(*) FROM numbers4_draws")
total = cur.fetchone()[0]

print(f"\nNumbers starting with 0: {count_0} ({count_0/total*100:.1f}%)")
print(f"Total numbers: {total}")

# Count '0100' appearances
cur.execute("SELECT COUNT(*) FROM numbers4_draws WHERE numbers = '0100'")
count_0100 = cur.fetchone()[0]
print(f"\nTimes '0100' appeared: {count_0100}")

# Top numbers starting with 0
cur.execute("""
    SELECT numbers, COUNT(*) as cnt 
    FROM numbers4_draws 
    WHERE numbers LIKE '0%' 
    GROUP BY numbers 
    ORDER BY cnt DESC 
    LIMIT 20
""")
print('\nTop 20 numbers starting with 0:')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]} times')

# Analyze digit patterns
print("\n" + "="*80)
print("Digit Pattern Analysis for '0100'")
print("="*80)

# Get all draws
cur.execute("SELECT numbers FROM numbers4_draws ORDER BY draw_date ASC")
all_numbers = [row[0] for row in cur.fetchall()]

# Analyze '0100' pattern
print("\nPattern: 0100")
print("  - First digit: 0")
print("  - Second digit: 1")
print("  - Third digit: 0")
print("  - Fourth digit: 0")

# Count each digit at each position
cur.execute("""
    SELECT 
        SUBSTRING(numbers, 1, 1) as d1,
        COUNT(*) as cnt
    FROM numbers4_draws
    GROUP BY d1
    ORDER BY cnt DESC
""")
print("\nFirst digit distribution:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} times ({row[1]/total*100:.1f}%)")

# Patterns with repeated digits
cur.execute("""
    SELECT numbers, COUNT(*) as cnt 
    FROM numbers4_draws 
    WHERE numbers ~ '^(.)\\1.*$' OR numbers ~ '^.*(.)\\1$'
    GROUP BY numbers 
    ORDER BY cnt DESC 
    LIMIT 10
""")
print('\nNumbers with repeated digits (top 10):')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]} times')

# Analyze sum of digits
print("\nSum of digits analysis:")
sum_0100 = 0 + 1 + 0 + 0
print(f"  '0100' sum: {sum_0100}")

cur.execute("""
    SELECT 
        CAST(SUBSTRING(numbers, 1, 1) AS INTEGER) +
        CAST(SUBSTRING(numbers, 2, 1) AS INTEGER) +
        CAST(SUBSTRING(numbers, 3, 1) AS INTEGER) +
        CAST(SUBSTRING(numbers, 4, 1) AS INTEGER) as total_sum,
        COUNT(*) as cnt
    FROM numbers4_draws
    GROUP BY total_sum
    ORDER BY total_sum
""")
print("\nDistribution by sum of digits:")
for row in cur.fetchall():
    if row[0] <= 5:  # Show only low sums
        print(f"  Sum {row[0]}: {row[1]} times ({row[1]/total*100:.1f}%)")

conn.close()
