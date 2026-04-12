"""
予測システム全体の設定クラス

このファイルには予測ロジックで使用される定数と設定値が含まれています。
予測精度を変更したい場合はこのファイルの値を変更してください。
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Numbers4Config:
    """ナンバーズ4予測システムの設定"""

    sum_ideal: int = 18
    sum_tolerance: int = 8
    sum_bonus_max: float = 0.25
    sum_out_of_range_penalty: float = 0.95

    max_permutation_candidates: int = 400

    abcd_min_in_top20: int = 10

    learning_blend_ratio: float = 0.6

    default_box_distribution: dict = field(default_factory=lambda: {
        'ABCD': 0.51,
        'AABC': 0.42,
        'AABB': 0.025,
        'AAAB': 0.035,
        'AAAA': 0.002,
    })

    diversity_penalty_strength: float = 0.4
    diversity_similarity_threshold: int = 2

    temperature_scaling: float = 1.5
    temperature_min_prob: float = 0.05

    decay_rate_factor: float = 3.0

    hot_model_bonus_multiplier: float = 0.5
    hot_model_max_bonus: float = 20.0
    second_hot_model_bonus_multiplier: float = 0.2
    second_hot_model_max_bonus: float = 10.0


NUMBERS4_CONFIG = Numbers4Config()


@dataclass(frozen=True)
class Numbers3Config:
    """ナンバーズ3予測システムの設定"""

    learning_blend_ratio: float = 0.6

    temperature_scaling: float = 1.5
    temperature_min_prob: float = 0.05

    recent_history_limit: int = 60
    cold_digits_count: int = 4
    hot_pairs_weight: float = 200.0
    state_chain_weight: float = 260.0


NUMBERS3_CONFIG = Numbers3Config()


@dataclass(frozen=True)
class DefaultEnsembleWeights:
    """アンサンブル予測のデフォルト重み"""

    NUMBERS4: dict = field(default_factory=lambda: {
        'box_model': 45.0,
        'ml_neighborhood': 30.0,
        'even_odd_pattern': 40.0,
        'low_sum_specialist': 35.0,
        'sequential_pattern': 25.0,
        'adjacent_digit': 35.0,
        'lgbm_box': 40.0,
        'cold_revival': 22.0,
        'hot_pair': 18.0,
        'box_pattern': 16.0,
        'digit_freq_box': 14.0,
        'state_chain': 10.0,
        'transition_probability': 12.0,
        'global_frequency': 18.0,
        'digit_repetition': 4.0,
        'digit_continuation': 3.0,
        'realistic_frequency': 4.0,
        'large_change': 8.0,
        'advanced_heuristics': 3.0,
        'exploratory': 10.0,
        'extreme_patterns': 3.0,
        'basic_stats': 2.0,
        'ml_model_new': 2.0,
        'lightgbm': 12.0,
    })

    NUMBERS3: dict = field(default_factory=lambda: {
        'box_model': 30.0,
        'ml_neighborhood': 24.0,
        'even_odd_pattern': 22.0,
        'lgbm_box': 22.0,
        'sequential_pattern': 20.0,
        'cold_revival': 20.0,
        'hot_pair': 18.0,
        'adjacent_digit': 18.0,
        'digit_freq_box': 16.0,
        'global_frequency': 16.0,
        'lightgbm': 14.0,
        'state_chain': 14.0,
        'box_pattern': 14.0,
        'low_sum_specialist': 12.0,
    })


DEFAULT_WEIGHTS = DefaultEnsembleWeights()
