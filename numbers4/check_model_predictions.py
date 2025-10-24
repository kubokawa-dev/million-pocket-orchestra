import psycopg2
import os
import json
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get('DATABASE_URL')
if db_url and '?schema' in db_url:
    db_url = db_url.split('?schema')[0]

conn = psycopg2.connect(db_url)
cur = conn.cursor()

# Get the latest prediction ID
cur.execute("SELECT MAX(id) FROM numbers4_ensemble_predictions")
latest_id = cur.fetchone()[0]

# Get the model predictions from the ensemble
cur.execute("""
    SELECT model_predictions
    FROM numbers4_ensemble_predictions
    WHERE id = %s
""", (latest_id,))

result = cur.fetchone()
if result:
    model_predictions = json.loads(result[0])
    
    print('\n' + '='*80)
    print(f'予測ID {latest_id} のモデル別予測')
    print('='*80 + '\n')
    
    # Check extreme_patterns model predictions
    if 'extreme_patterns' in model_predictions:
        extreme_preds = model_predictions['extreme_patterns']['predictions']
        print(f"【extreme_patterns モデル】({len(extreme_preds)}件)")
        for i, pred in enumerate(extreme_preds, 1):
            digit_sum = sum(int(d) for d in pred)
            print(f"  {i:2d}. {pred} (合計: {digit_sum})")
        
        if '0100' in extreme_preds:
            print(f"\n✅ 0100はextreme_patternsモデルの予測に含まれています！")
        else:
            print(f"\n❌ 0100はextreme_patternsモデルの予測に含まれていません")
            print(f"\n合計値1のパターン:")
            sum1_patterns = [p for p in extreme_preds if sum(int(d) for d in p) == 1]
            for p in sum1_patterns:
                print(f"  {p}")
    else:
        print("extreme_patternsモデルの予測が見つかりません")

conn.close()
