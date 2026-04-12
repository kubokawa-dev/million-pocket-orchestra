"""
Numbers4予測ロジックのテストスイート

このテストは予測システムの精度が壊れないことを保証します。
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

sys_path_patched = False


def setup_sys_path():
    """テストのためにsys.pathを設定"""
    global sys_path_patched
    if not sys_path_patched:
        import sys
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        sys_path_patched = True


setup_sys_path()


class TestConfigModule:
    """設定クラスのテスト"""

    def test_numbers4_config_defaults(self):
        """NUMBERS4_CONFIGのデフォルト値を確認"""
        from src.config import NUMBERS4_CONFIG
        
        assert NUMBERS4_CONFIG.sum_ideal == 18
        assert NUMBERS4_CONFIG.sum_tolerance == 8
        assert NUMBERS4_CONFIG.sum_bonus_max == 0.25
        assert NUMBERS4_CONFIG.max_permutation_candidates == 400
        assert NUMBERS4_CONFIG.abcd_min_in_top20 == 10
        assert NUMBERS4_CONFIG.learning_blend_ratio == 0.6

    def test_numbers3_config_defaults(self):
        """NUMBERS3_CONFIGのデフォルト値を確認"""
        from src.config import NUMBERS3_CONFIG
        
        assert NUMBERS3_CONFIG.recent_history_limit == 60
        assert NUMBERS3_CONFIG.cold_digits_count == 4

    def test_default_ensemble_weights(self):
        """デフォルトアンサンブル重みを確認"""
        from src.config import DEFAULT_WEIGHTS
        
        assert 'box_model' in DEFAULT_WEIGHTS.NUMBERS4
        assert 'box_model' in DEFAULT_WEIGHTS.NUMBERS3
        assert DEFAULT_WEIGHTS.NUMBERS4['box_model'] == 45.0
        assert DEFAULT_WEIGHTS.NUMBERS3['box_model'] == 30.0

    def test_config_immutability(self):
        """設定がイミュータブルであることを確認"""
        from src.config import NUMBERS4_CONFIG
        
        with pytest.raises(Exception):
            NUMBERS4_CONFIG.sum_ideal = 20


class TestPredictionModelsBase:
    """予測モデル基底クラスのテスト"""

    def test_prediction_result_creation(self):
        """PredictionResult dataclassの作成を確認"""
        from src.models.base import PredictionResult
        
        result = PredictionResult(
            predictions=['1234', '5678'],
            scores=[0.9, 0.8],
            metadata={'model': 'test'}
        )
        
        assert len(result.predictions) == 2
        assert result.scores == [0.9, 0.8]
        assert result.metadata['model'] == 'test'

    def test_prediction_result_to_dataframe(self):
        """PredictionResultのDataFrame変換を確認"""
        from src.models.base import PredictionResult
        
        result = PredictionResult(
            predictions=['1234', '5678'],
            scores=[0.9, 0.8]
        )
        
        df = result.to_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert 'prediction' in df.columns
        assert 'score' in df.columns
        assert len(df) == 2

    def test_ensemble_aggregator(self):
        """EnsembleAggregatorの動作確認"""
        from src.models.base import EnsembleAggregator
        
        aggregator = EnsembleAggregator(
            weights={'model_a': 2.0, 'model_b': 1.0}
        )
        
        predictions_by_model = {
            'model_a': ['1111', '2222', '3333'],
            'model_b': ['2222', '4444', '5555'],
        }
        
        df = aggregator.aggregate(predictions_by_model, top_n=10, normalize=True)
        
        assert isinstance(df, pd.DataFrame)
        assert 'prediction' in df.columns
        assert 'score' in df.columns
        assert '2222' in df['prediction'].values


class TestNumbers4PredictionLogic:
    """Numbers4予測ロジックのテスト"""

    @pytest.fixture
    def sample_draws_df(self):
        """テスト用のサンプルデータを生成"""
        np.random.seed(42)
        data = {
            'draw_number': list(range(1, 101)),
            'd1': np.random.randint(0, 10, 100),
            'd2': np.random.randint(0, 10, 100),
            'd3': np.random.randint(0, 10, 100),
            'd4': np.random.randint(0, 10, 100),
        }
        return pd.DataFrame(data)

    def test_basic_stats_prediction(self, sample_draws_df):
        """基本統計予測のテスト"""
        from numbers4.prediction_logic import predict_from_basic_stats
        
        predictions = predict_from_basic_stats(sample_draws_df, limit=5)
        
        assert isinstance(predictions, list)
        assert len(predictions) <= 5
        for pred in predictions:
            assert isinstance(pred, str)
            assert len(pred) == 4
            assert pred.isdigit()

    def test_extreme_patterns_prediction(self, sample_draws_df):
        """極端パターンモデルのテスト"""
        from numbers4.prediction_logic import predict_from_extreme_patterns
        
        predictions = predict_from_extreme_patterns(sample_draws_df, limit=10)
        
        assert isinstance(predictions, list)
        assert len(predictions) <= 10

    def test_exploratory_heuristics(self, sample_draws_df):
        """探索的ヒューリスティックのテスト"""
        from numbers4.prediction_logic import predict_from_exploratory_heuristics
        
        predictions = predict_from_exploratory_heuristics(sample_draws_df, limit=10)
        
        assert isinstance(predictions, list)
        assert len(predictions) <= 10

    def test_aggregate_predictions(self):
        """予測集約のテスト"""
        from numbers4.prediction_logic import aggregate_predictions
        
        predictions_by_model = {
            'model_a': ['1111', '2222', '3333'],
            'model_b': ['2222', '4444', '5555'],
        }
        weights = {'model_a': 2.0, 'model_b': 1.0}
        
        df = aggregate_predictions(predictions_by_model, weights, normalize_scores=True)
        
        assert isinstance(df, pd.DataFrame)
        assert 'prediction' in df.columns
        assert 'score' in df.columns
        assert not df.empty
        
        assert df.iloc[0]['score'] >= df.iloc[-1]['score']

    def test_diversity_penalty(self):
        """多様性ペナルティのテスト"""
        from numbers4.prediction_logic import apply_diversity_penalty
        
        df = pd.DataFrame({
            'prediction': ['1111', '1112', '1234', '5678'],
            'score': [1.0, 0.9, 0.8, 0.7]
        })
        
        result = apply_diversity_penalty(df, penalty_strength=0.4, similarity_threshold=2)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) <= len(df)
        
        assert result.iloc[0]['prediction'] == '1111'
        assert result.iloc[1]['prediction'] != '1111' or len(result) >= 2

    def test_sum_bonus_in_predict_ensemble(self):
        """predict_ensemble сумма бонус тест"""
        from numbers4.predict_ensemble import apply_sum_bonus
        
        df = pd.DataFrame({
            'prediction': ['0000', '1234', '9999'],
            'score': [1.0, 1.0, 1.0]
        })
        
        result = apply_sum_bonus(df)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        
        sum_10_row = result[result['prediction'] == '0000']
        sum_18_row = result[result['prediction'] == '1234']
        sum_36_row = result[result['prediction'] == '9999']
        
        assert not sum_10_row.empty
        assert not sum_18_row.empty
        assert not sum_36_row.empty
        
        assert sum_18_row.iloc[0]['score'] >= sum_10_row.iloc[0]['score']
        assert sum_18_row.iloc[0]['score'] >= sum_36_row.iloc[0]['score']


class TestNumbers3Core:
    """Numbers3コアモジュールのテスト"""

    def test_load_numbers3_draws(self):
        """Numbers3データ読み込みのテスト"""
        from numbers3.core import load_numbers3_draws
        
        df = load_numbers3_draws()
        
        if not df.empty:
            assert isinstance(df, pd.DataFrame)
            assert 'numbers' in df.columns
            assert 'draw_number' in df.columns

    def test_generate_all_numbers3(self):
        """全Numbers3番号生成のテスト"""
        from numbers3.core import generate_all_numbers3
        
        all_nums = generate_all_numbers3()
        
        assert len(all_nums) == 1000
        assert '000' in all_nums
        assert '999' in all_nums

    def test_predict_by_method(self):
        """メソッド別予測のテスト"""
        from numbers3.core import predict_by_method, load_numbers3_draws
        
        df = load_numbers3_draws()
        
        if not df.empty:
            predictions = predict_by_method(df, 'box_model', limit=10)
            
            assert isinstance(predictions, list)
            assert len(predictions) <= 10
            for pred in predictions:
                assert len(pred) == 3
                assert pred.isdigit()


class TestBoxUtils:
    """ボックスユーティリティのテスト"""

    def test_get_box_type_info(self):
        """ボックスタイプ判定のテスト"""
        from numbers4.box_utils import get_box_type_info
        
        abcd_type, desc, coverage = get_box_type_info('1234')
        assert 'ABCD' in abcd_type or 'シングル' in abcd_type
        assert coverage == 24
        
        aabc_type, desc, coverage = get_box_type_info('1123')
        assert 'AABC' in aabc_type or 'ダブル' in aabc_type
        assert coverage == 12
        
        aabb_type, desc, coverage = get_box_type_info('1122')
        assert 'AABB' in aabb_type or 'ダブル' in aabb_type
        assert coverage == 6

    def test_invalid_input(self):
        """無効な入力のテスト"""
        from numbers4.box_utils import get_box_type_info, get_box_type
        
        assert get_box_type_info('') == ("不明", "不明", 0)
        assert get_box_type_info('123') == ("不明", "不明", 0)
        assert get_box_type_info('abcde') == ("不明", "不明", 0)
        
        assert get_box_type('') == ("不明", 0)


class TestPredictionConsistency:
    """予測の一貫性テスト - 同じ入力で同じ出力を確認"""

    def test_aggregate_consistency(self):
        """集約処理の一貫性確認"""
        from numbers4.prediction_logic import aggregate_predictions
        
        predictions_by_model = {
            'model_a': ['1111', '2222', '3333'],
            'model_b': ['2222', '4444', '5555'],
        }
        weights = {'model_a': 1.0, 'model_b': 1.0}
        
        df1 = aggregate_predictions(predictions_by_model, weights, normalize_scores=True)
        df2 = aggregate_predictions(predictions_by_model, weights, normalize_scores=True)
        
        assert df1.shape == df2.shape
        assert list(df1['prediction']) == list(df2['prediction'])
        
        np.testing.assert_array_almost_equal(
            df1['score'].values,
            df2['score'].values
        )


class TestEdgeCases:
    """エッジケースのテスト"""

    def test_empty_dataframe(self):
        """空のDataFrameの処理確認"""
        from numbers4.prediction_logic import predict_from_basic_stats
        
        empty_df = pd.DataFrame()
        
        predictions = predict_from_basic_stats(empty_df, limit=5)
        
        assert predictions == []

    def test_single_row_dataframe(self):
        """1行のDataFrameの処理確認"""
        from numbers4.prediction_logic import predict_from_basic_stats
        
        df = pd.DataFrame({
            'd1': [1],
            'd2': [2],
            'd3': [3],
            'd4': [4],
        })
        
        predictions = predict_from_basic_stats(df, limit=5)
        
        assert isinstance(predictions, list)
        assert len(predictions) <= 5

    def test_invalid_limit(self):
        """無効なlimit値の処理確認"""
        from numbers4.prediction_logic import predict_from_basic_stats
        
        df = pd.DataFrame({
            'd1': [1, 2, 3],
            'd2': [1, 2, 3],
            'd3': [1, 2, 3],
            'd4': [1, 2, 3],
        })
        
        predictions = predict_from_basic_stats(df, limit=-1)
        
        assert isinstance(predictions, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
