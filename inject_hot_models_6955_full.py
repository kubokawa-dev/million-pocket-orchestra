import json
with open('predictions/daily/numbers4_6955.json', 'r') as f:
    data = json.load(f)

data['predictions'][-1]['hot_models'] = [{"model": "global_frequency", "score": 1827.5999999999997}, {"model": "cold_revival", "score": 1672.7849999999999}, {"model": "box_model", "score": 1633.4125}, {"model": "box_pattern", "score": 1459.35}, {"model": "hot_pair", "score": 1358.8874999999998}, {"model": "digit_freq_box", "score": 1198.6}, {"model": "low_sum_specialist", "score": 1041.6}, {"model": "state_chain", "score": 955.3375}, {"model": "even_odd_pattern", "score": 830.0}, {"model": "sequential_pattern", "score": 670.75}, {"model": "ml_neighborhood", "score": 0.0}, {"model": "lightgbm", "score": 0.0}, {"model": "adjacent_digit", "score": 0.0}, {"model": "lgbm_box", "score": 0.0}]

data['predictions'][-1]['recent_flow'] = [{"draw": 6940, "model": "cold_revival", "score": 40.25}, {"draw": 6941, "model": "low_sum_specialist", "score": 51.74999999999999}, {"draw": 6942, "model": "box_model", "score": 79.35}, {"draw": 6943, "model": "state_chain", "score": 80.21249999999999}, {"draw": 6944, "model": "cold_revival", "score": 60.37499999999999}, {"draw": 6945, "model": "cold_revival", "score": 51.74999999999999}, {"draw": 6946, "model": "cold_revival", "score": 82.8}, {"draw": 6947, "model": "state_chain", "score": 84.52499999999999}, {"draw": 6948, "model": "cold_revival", "score": 68.13749999999999}, {"draw": 6949, "model": "digit_freq_box", "score": 79.35}]

data['predictions'][-1]['next_model_predictions'] = [{"model": "global_frequency", "probability": 0.5, "count": 1, "total": 2}, {"model": "sequential_pattern", "probability": 0.5, "count": 1, "total": 2}]

with open('predictions/daily/numbers4_6955.json', 'w') as f:
    json.dump(data, f, indent=2)
