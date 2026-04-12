"""
予測モデルの基底クラス

すべての予測モデルは、この基底クラスを継承して実装します。
これにより、コードの重複が減り、テストもしやすくなります。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

import pandas as pd


@dataclass
class PredictionResult:
    """予測結果を保持するデータクラス"""
    predictions: List[str]
    scores: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dataframe(self) -> pd.DataFrame:
        """予測結果をDataFrameに変換"""
        if self.scores:
            data = [
                {'prediction': p, 'score': s}
                for p, s in zip(self.predictions, self.scores)
            ]
        else:
            data = [{'prediction': p} for p in self.predictions]
        return pd.DataFrame(data)


class PredictionModel(ABC):
    """予測モデルの基底クラス"""

    @property
    @abstractmethod
    def name(self) -> str:
        """モデル名を返す"""
        pass

    @property
    def description(self) -> str:
        """モデルの説明文（デフォルトは空）"""
        return ""

    @abstractmethod
    def predict(
        self,
        df: pd.DataFrame,
        limit: int = 100,
    ) -> PredictionResult:
        """
        予測を実行する

        Args:
            df: 過去の結果を含むDataFrame
            limit: 返す予測の数

        Returns:
            PredictionResult: 予測結果
        """
        pass

    def validate_input(self, df: pd.DataFrame) -> bool:
        """
        入力データを検証する

        Args:
            df: 検証するDataFrame

        Returns:
            bool: 検証結果
        """
        if df is None or df.empty:
            return False
        return True

    def get_default_limit(self) -> int:
        """デフォルトの予測数を返す"""
        return 100


class EnsembleAggregator:
    """複数の予測モデルを集約するクラス"""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or {}

    def aggregate(
        self,
        predictions_by_model: Dict[str, List[str]],
        top_n: int = 100,
        normalize: bool = True,
    ) -> pd.DataFrame:
        """
        複数のモデルの予測を集約する

        Args:
            predictions_by_model: モデル名 -> 予測リスト
            top_n: 返す上位予測数
            normalize: スコアを正規化するか

        Returns:
            pd.DataFrame: 集約結果
        """
        import numpy as np

        model_scores: Dict[str, float] = {}

        for model_name, predictions in predictions_by_model.items():
            weight = self.weights.get(model_name, 1.0)

            if normalize and predictions:
                n = len(predictions)
                decay_rate = 3.0 / n
                for rank, pred in enumerate(predictions):
                    normalized_score = np.exp(-decay_rate * rank)
                    if pred not in model_scores:
                        model_scores[pred] = 0.0
                    model_scores[pred] += normalized_score * weight
            else:
                for pred in predictions:
                    if pred not in model_scores:
                        model_scores[pred] = 0.0
                    model_scores[pred] += weight

        if not model_scores:
            return pd.DataFrame({'prediction': [], 'score': []})

        df = pd.DataFrame(
            model_scores.items(),
            columns=['prediction', 'score']
        )
        df = df.sort_values(by='score', ascending=False).reset_index(drop=True)
        return df.head(top_n)
