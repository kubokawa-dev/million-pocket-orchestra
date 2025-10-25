-- ML Model Events & Training Data Seed
-- このファイルは機械学習モデルの予測データと学習履歴をインポートします

-- Numbers4 ML Data (1 model event, 2 ensemble predictions, 34 candidates, 10 logs)
INSERT INTO numbers4_model_events (id, event_ts, actual_number, predictions, hit_exact, top_match, max_position_hits, notes) 
VALUES (1, '2025-10-17T14:53:41.292259+00:00', '0000', '[]', 0, NULL, 0, 'Model state restored from numbers4/model_state.json')
ON CONFLICT (id) DO NOTHING;

-- Numbers3 ML Data (1 model event, 1 ensemble prediction, 10 candidates, 10 logs)
INSERT INTO numbers3_model_events (id, event_ts, actual_number, predictions, hit_exact, top_match, max_position_hits, notes) 
VALUES (1, '2025-10-18T05:44:49.062417+00:00', '123', '["123", "456", "789", "012", "345"]', 1, '123', 3, 'テスト用の学習イベント')
ON CONFLICT (id) DO NOTHING;

-- Loto6 ML Data (2 model events, 2 ensemble predictions, 20 candidates, 20 logs)
INSERT INTO loto6_model_events (id, event_ts, actual_number, predictions, hit_exact, top_match, max_position_hits, notes) 
VALUES 
  (1, '2025-10-18T06:00:34.138906+00:00', '123456', '["123456", "234567", "345678", "456789", "567890"]', 1, '123456', 6, 'テスト用の学習イベント'),
  (2, '2025-10-18T06:02:07.055331+00:00', '123456', '["123456", "234567", "345678", "456789", "567890"]', 1, '123456', 6, 'テスト用の学習イベント')
ON CONFLICT (id) DO NOTHING;
