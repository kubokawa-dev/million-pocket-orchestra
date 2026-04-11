-- 宝くじAI SQLite Schema
-- 宝くじ予測システム用データベーススキーマ

-- ============================================
-- Official Draw Results (抽選結果)
-- ============================================

CREATE TABLE IF NOT EXISTS numbers3_draws (
    draw_number INTEGER PRIMARY KEY,
    draw_date TEXT NOT NULL,
    numbers TEXT NOT NULL,
    tier1_winners INTEGER,
    tier1_payout_yen INTEGER,
    tier2_winners INTEGER,
    tier2_payout_yen INTEGER,
    tier3_winners INTEGER,
    tier3_payout_yen INTEGER,
    tier4_winners INTEGER,
    tier4_payout_yen INTEGER
);

-- numbers4 月次CSV列に対応: 当選番号の次から 口数・払戻金額 が4等級分（ストレート/ボックス/セットストレート/セットボックス）
CREATE TABLE IF NOT EXISTS numbers4_draws (
    draw_number INTEGER PRIMARY KEY,
    draw_date TEXT NOT NULL,
    numbers TEXT NOT NULL,
    tier1_winners INTEGER,
    tier1_payout_yen INTEGER,
    tier2_winners INTEGER,
    tier2_payout_yen INTEGER,
    tier3_winners INTEGER,
    tier3_payout_yen INTEGER,
    tier4_winners INTEGER,
    tier4_payout_yen INTEGER
);

CREATE TABLE IF NOT EXISTS loto6_draws (
    draw_number INTEGER PRIMARY KEY,
    draw_date TEXT NOT NULL,
    numbers TEXT NOT NULL,
    bonus_number INTEGER NOT NULL
);

-- ============================================
-- ML Model Events & Training Data
-- ============================================

-- Numbers3
CREATE TABLE IF NOT EXISTS numbers3_model_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_ts TEXT NOT NULL,
    actual_number TEXT NOT NULL,
    predictions TEXT NOT NULL,
    hit_exact INTEGER DEFAULT 0,
    top_match TEXT,
    max_position_hits INTEGER NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS numbers3_predictions_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    source TEXT NOT NULL,
    label TEXT,
    number TEXT NOT NULL,
    target_draw_number INTEGER
);
CREATE INDEX IF NOT EXISTS idx_numbers3_predictions_log_target ON numbers3_predictions_log(target_draw_number);

CREATE TABLE IF NOT EXISTS numbers3_ensemble_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT DEFAULT (datetime('now')),
    target_draw_number INTEGER,
    model_updated_at TEXT,
    model_events_count INTEGER,
    ensemble_weights TEXT NOT NULL,
    predictions_count INTEGER NOT NULL,
    top_predictions TEXT NOT NULL,
    model_predictions TEXT NOT NULL,
    actual_draw_number INTEGER,
    actual_numbers TEXT,
    hit_status TEXT,
    hit_count INTEGER,
    notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_numbers3_ensemble_created ON numbers3_ensemble_predictions(created_at);
CREATE INDEX IF NOT EXISTS idx_numbers3_ensemble_target ON numbers3_ensemble_predictions(target_draw_number);

CREATE TABLE IF NOT EXISTS numbers3_prediction_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ensemble_prediction_id INTEGER NOT NULL,
    rank INTEGER NOT NULL,
    number TEXT NOT NULL,
    score REAL NOT NULL,
    contributing_models TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (ensemble_prediction_id) REFERENCES numbers3_ensemble_predictions(id)
);
CREATE INDEX IF NOT EXISTS idx_numbers3_candidates_ensemble ON numbers3_prediction_candidates(ensemble_prediction_id);
CREATE INDEX IF NOT EXISTS idx_numbers3_candidates_number ON numbers3_prediction_candidates(number);

-- Numbers4
CREATE TABLE IF NOT EXISTS numbers4_model_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_ts TEXT NOT NULL,
    actual_number TEXT NOT NULL,
    predictions TEXT NOT NULL,
    hit_exact INTEGER DEFAULT 0,
    top_match TEXT,
    max_position_hits INTEGER NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS numbers4_predictions_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    source TEXT NOT NULL,
    label TEXT,
    number TEXT NOT NULL,
    target_draw_number INTEGER
);
CREATE INDEX IF NOT EXISTS idx_numbers4_predictions_log_target ON numbers4_predictions_log(target_draw_number);

CREATE TABLE IF NOT EXISTS numbers4_ensemble_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT DEFAULT (datetime('now')),
    target_draw_number INTEGER,
    model_updated_at TEXT,
    model_events_count INTEGER,
    ensemble_weights TEXT NOT NULL,
    predictions_count INTEGER NOT NULL,
    top_predictions TEXT NOT NULL,
    model_predictions TEXT NOT NULL,
    actual_draw_number INTEGER,
    actual_numbers TEXT,
    hit_status TEXT,
    hit_count INTEGER,
    notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_numbers4_ensemble_created ON numbers4_ensemble_predictions(created_at);
CREATE INDEX IF NOT EXISTS idx_numbers4_ensemble_target ON numbers4_ensemble_predictions(target_draw_number);

CREATE TABLE IF NOT EXISTS numbers4_prediction_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ensemble_prediction_id INTEGER NOT NULL,
    rank INTEGER NOT NULL,
    number TEXT NOT NULL,
    score REAL NOT NULL,
    contributing_models TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (ensemble_prediction_id) REFERENCES numbers4_ensemble_predictions(id)
);
CREATE INDEX IF NOT EXISTS idx_numbers4_candidates_ensemble ON numbers4_prediction_candidates(ensemble_prediction_id);
CREATE INDEX IF NOT EXISTS idx_numbers4_candidates_number ON numbers4_prediction_candidates(number);

-- predictions/daily/*.json の正本（アンサンブル / 手法別 / 予算プランを1行に丸ごと保持）
-- method_slug: ensemble・budget_plan は '' 固定、method のみ手法ディレクトリ名
CREATE TABLE IF NOT EXISTS numbers4_daily_prediction_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_draw_number INTEGER NOT NULL,
    doc_kind TEXT NOT NULL CHECK (doc_kind IN ('ensemble', 'method', 'budget_plan')),
    method_slug TEXT NOT NULL DEFAULT '',
    relative_path TEXT NOT NULL,
    payload TEXT NOT NULL,
    payload_sha256 TEXT,
    file_mtime TEXT,
    ingested_at TEXT DEFAULT (datetime('now')),
    CHECK (
        (doc_kind = 'method' AND method_slug != '')
        OR (doc_kind IN ('ensemble', 'budget_plan') AND method_slug = '')
    ),
    UNIQUE (target_draw_number, doc_kind, method_slug)
);
CREATE INDEX IF NOT EXISTS idx_numbers4_daily_docs_draw ON numbers4_daily_prediction_documents(target_draw_number);
CREATE INDEX IF NOT EXISTS idx_numbers4_daily_docs_kind ON numbers4_daily_prediction_documents(doc_kind);

-- Loto6
CREATE TABLE IF NOT EXISTS loto6_model_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_ts TEXT NOT NULL,
    actual_number TEXT NOT NULL,
    predictions TEXT NOT NULL,
    hit_exact INTEGER DEFAULT 0,
    top_match TEXT,
    max_position_hits INTEGER NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS loto6_predictions_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    source TEXT NOT NULL,
    label TEXT,
    number TEXT NOT NULL,
    target_draw_number INTEGER
);
CREATE INDEX IF NOT EXISTS idx_loto6_predictions_log_target ON loto6_predictions_log(target_draw_number);

CREATE TABLE IF NOT EXISTS loto6_ensemble_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT DEFAULT (datetime('now')),
    target_draw_number INTEGER,
    model_updated_at TEXT,
    model_events_count INTEGER,
    ensemble_weights TEXT NOT NULL,
    predictions_count INTEGER NOT NULL,
    top_predictions TEXT NOT NULL,
    model_predictions TEXT NOT NULL,
    actual_draw_number INTEGER,
    actual_numbers TEXT,
    actual_bonus_number INTEGER,
    hit_status TEXT,
    hit_count INTEGER,
    bonus_hit INTEGER,
    notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_loto6_ensemble_created ON loto6_ensemble_predictions(created_at);
CREATE INDEX IF NOT EXISTS idx_loto6_ensemble_target ON loto6_ensemble_predictions(target_draw_number);

CREATE TABLE IF NOT EXISTS loto6_prediction_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ensemble_prediction_id INTEGER NOT NULL,
    rank INTEGER NOT NULL,
    number TEXT NOT NULL,
    score REAL NOT NULL,
    contributing_models TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (ensemble_prediction_id) REFERENCES loto6_ensemble_predictions(id)
);
CREATE INDEX IF NOT EXISTS idx_loto6_candidates_ensemble ON loto6_prediction_candidates(ensemble_prediction_id);
CREATE INDEX IF NOT EXISTS idx_loto6_candidates_number ON loto6_prediction_candidates(number);




