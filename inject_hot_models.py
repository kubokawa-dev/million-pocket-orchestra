import json
with open('predictions/daily/numbers4_6950.json', 'r') as f:
    data = json.load(f)

data['predictions'][-1]['hot_models'] = [{"model": "global_frequency", "score": 1827.5999999999997}, {"model": "cold_revival", "score": 1672.7849999999999}, {"model": "box_model", "score": 1633.4125}, {"model": "box_pattern", "score": 1459.35}, {"model": "hot_pair", "score": 1358.8874999999998}, {"model": "digit_freq_box", "score": 1198.6}, {"model": "low_sum_specialist", "score": 1041.6}, {"model": "state_chain", "score": 955.3375}, {"model": "even_odd_pattern", "score": 830.0}, {"model": "sequential_pattern", "score": 670.75}, {"model": "ml_neighborhood", "score": 0.0}, {"model": "lightgbm", "score": 0.0}, {"model": "adjacent_digit", "score": 0.0}, {"model": "lgbm_box", "score": 0.0}]

with open('predictions/daily/numbers4_6950.json', 'w') as f:
    json.dump(data, f, indent=2)
