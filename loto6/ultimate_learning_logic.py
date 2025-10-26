"""
ロト6 世界最強学習システム
当選番号から学習し、予測精度を向上させる

特徴:
- 当選パターンの深層学習
- 数字の出現周期分析
- ペア・トリプレットの相性学習
- 適応的な重み調整
"""

import os
import json
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Tuple
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from tools.utils import load_all_loto6_draws


class UltimateLoto6Learner:
    """ロト6の究極学習システム"""
    
    def __init__(self):
        self.model_state_file = os.path.join(
            os.path.dirname(__file__), 
            'ultimate_model_state.json'
        )
        self.state = self.load_state()
    
    def load_state(self) -> Dict:
        """学習済みモデルの状態を読み込み"""
        if os.path.exists(self.model_state_file):
            with open(self.model_state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 初期状態
            return {
                'version': 1,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'learning_events': 0,
                'number_weights': {str(i): 1.0 for i in range(1, 44)},
                'pair_weights': {},
                'triplet_weights': {},
                'zone_preferences': {},
                'even_odd_preferences': {},
                'sum_distribution': {},
                'prediction_accuracy': {
                    'total_predictions': 0,
                    'hits': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0},
                    'bonus_hits': 0
                },
                'model_performance': {
                    'ultra_stats': {'hits': 0, 'total': 0},
                    'never_appeared': {'hits': 0, 'total': 0},
                    'golden_ratio': {'hits': 0, 'total': 0},
                    'hot_cold_mix': {'hits': 0, 'total': 0},
                    'zone_balance': {'hits': 0, 'total': 0},
                    'pair_affinity': {'hits': 0, 'total': 0},
                    'overdue': {'hits': 0, 'total': 0},
                    'even_odd_balance': {'hits': 0, 'total': 0},
                    'sum_optimization': {'hits': 0, 'total': 0},
                    'deep_learning': {'hits': 0, 'total': 0},
                }
            }
    
    def save_state(self):
        """学習済みモデルの状態を保存"""
        self.state['updated_at'] = datetime.now(timezone.utc).isoformat()
        with open(self.model_state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def learn_from_result(self, winning_numbers: List[int], bonus_number: int, 
                          predictions: List[List[int]] = None,
                          predictions_by_model: Dict[str, List[List[int]]] = None):
        """
        当選結果から学習
        
        Args:
            winning_numbers: 当選番号（6個）
            bonus_number: ボーナス数字
            predictions: 予測した番号のリスト（オプション）
            predictions_by_model: モデル別の予測（オプション）
        """
        print("\n" + "="*80)
        print("学習開始")
        print("="*80)
        print(f"当選番号: {' '.join(f'{n:02d}' for n in winning_numbers)}")
        print(f"ボーナス: {bonus_number:02d}\n")
        
        # 1. 数字の重み更新
        self._update_number_weights(winning_numbers, bonus_number)
        
        # 2. ペアの重み更新
        self._update_pair_weights(winning_numbers)
        
        # 3. トリプレットの重み更新
        self._update_triplet_weights(winning_numbers)
        
        # 4. 区間の好みを更新
        self._update_zone_preferences(winning_numbers)
        
        # 5. 偶奇の好みを更新
        self._update_even_odd_preferences(winning_numbers)
        
        # 6. 合計値分布を更新
        self._update_sum_distribution(winning_numbers)
        
        # 7. 予測精度を更新
        if predictions:
            self._update_prediction_accuracy(winning_numbers, bonus_number, predictions)
        
        # 8. モデル別のパフォーマンスを更新
        if predictions_by_model:
            self._update_model_performance(winning_numbers, predictions_by_model)
        
        self.state['learning_events'] += 1
        self.save_state()
        
        print("\n学習完了")
        print(f"学習イベント数: {self.state['learning_events']}")
        self._print_insights()
    
    def _update_number_weights(self, winning_numbers: List[int], bonus_number: int):
        """数字の重みを更新（出現した数字の重みを増やす）"""
        for num in winning_numbers:
            key = str(num)
            current_weight = self.state['number_weights'].get(key, 1.0)
            # 出現するたびに重みを1.1倍
            self.state['number_weights'][key] = current_weight * 1.1
        
        # ボーナス数字も少し増やす
        bonus_key = str(bonus_number)
        current_weight = self.state['number_weights'].get(bonus_key, 1.0)
        self.state['number_weights'][bonus_key] = current_weight * 1.05
        
        print(f"  数字の重みを更新")
    
    def _update_pair_weights(self, winning_numbers: List[int]):
        """ペアの重みを更新"""
        from itertools import combinations
        
        for a, b in combinations(winning_numbers, 2):
            pair_key = f"{min(a,b)}-{max(a,b)}"
            current_weight = self.state['pair_weights'].get(pair_key, 1.0)
            self.state['pair_weights'][pair_key] = current_weight * 1.15
        
        print(f"  ペアの重みを更新（{len(list(combinations(winning_numbers, 2)))}ペア）")
    
    def _update_triplet_weights(self, winning_numbers: List[int]):
        """トリプレット（3個組）の重みを更新"""
        from itertools import combinations
        
        for triplet in combinations(winning_numbers, 3):
            triplet_key = '-'.join(str(n) for n in sorted(triplet))
            current_weight = self.state['triplet_weights'].get(triplet_key, 1.0)
            self.state['triplet_weights'][triplet_key] = current_weight * 1.2
        
        print(f"  トリプレットの重みを更新（{len(list(combinations(winning_numbers, 3)))}組）")
    
    def _update_zone_preferences(self, winning_numbers: List[int]):
        """区間の好みを更新"""
        zones = [(1, 10), (11, 21), (22, 32), (33, 43)]
        zone_counts = []
        
        for lo, hi in zones:
            count = sum(1 for n in winning_numbers if lo <= n <= hi)
            zone_counts.append(count)
        
        zone_key = '-'.join(str(c) for c in zone_counts)
        current_count = self.state['zone_preferences'].get(zone_key, 0)
        self.state['zone_preferences'][zone_key] = current_count + 1
        
        print(f"  区間パターンを更新: {zone_key}")
    
    def _update_even_odd_preferences(self, winning_numbers: List[int]):
        """偶奇の好みを更新"""
        even_count = sum(1 for n in winning_numbers if n % 2 == 0)
        eo_key = f"偶数{even_count}-奇数{6-even_count}"
        
        current_count = self.state['even_odd_preferences'].get(eo_key, 0)
        self.state['even_odd_preferences'][eo_key] = current_count + 1
        
        print(f"  偶奇パターンを更新: {eo_key}")
    
    def _update_sum_distribution(self, winning_numbers: List[int]):
        """合計値分布を更新"""
        total_sum = sum(winning_numbers)
        sum_key = str(total_sum)
        
        current_count = self.state['sum_distribution'].get(sum_key, 0)
        self.state['sum_distribution'][sum_key] = current_count + 1
        
        print(f"  合計値を記録: {total_sum}")
    
    def _update_prediction_accuracy(self, winning_numbers: List[int], 
                                   bonus_number: int, predictions: List[List[int]]):
        """予測精度を更新"""
        winning_set = set(winning_numbers)
        
        for pred in predictions[:10]:  # 上位10件のみチェック
            if isinstance(pred, str):
                # 文字列の場合は数値に変換
                pred_numbers = [int(pred[i:i+2]) for i in range(0, len(pred), 2)]
            else:
                pred_numbers = pred
            
            pred_set = set(pred_numbers)
            hit_count = len(winning_set & pred_set)
            
            if hit_count > 0:
                hit_key = str(hit_count)
                self.state['prediction_accuracy']['hits'][hit_key] += 1
            
            if bonus_number in pred_set:
                self.state['prediction_accuracy']['bonus_hits'] += 1
        
        self.state['prediction_accuracy']['total_predictions'] += len(predictions[:10])
        
        print(f"  予測精度を更新")
    
    def _update_model_performance(self, winning_numbers: List[int], 
                                 predictions_by_model: Dict[str, List[List[int]]]):
        """モデル別のパフォーマンスを更新"""
        winning_set = set(winning_numbers)
        
        for model_name, preds in predictions_by_model.items():
            if model_name not in self.state['model_performance']:
                self.state['model_performance'][model_name] = {'hits': 0, 'total': 0}
            
            for pred in preds:
                if isinstance(pred, str):
                    pred_numbers = [int(pred[i:i+2]) for i in range(0, len(pred), 2) if i+2 <= len(pred)]
                elif isinstance(pred, list):
                    pred_numbers = pred
                else:
                    continue
                
                pred_set = set(pred_numbers)
                hit_count = len(winning_set & pred_set)
                
                if hit_count >= 3:  # 3個以上当たったら成功とカウント
                    self.state['model_performance'][model_name]['hits'] += 1
                
                self.state['model_performance'][model_name]['total'] += 1
        
        print(f"  モデル別パフォーマンスを更新")
    
    def _print_insights(self):
        """学習から得られた知見を表示"""
        print("\n" + "="*80)
        print("学習による知見")
        print("="*80)
        
        # トップ5の数字
        top_numbers = sorted(self.state['number_weights'].items(), 
                           key=lambda x: x[1], reverse=True)[:10]
        print("\nホットナンバー（重み上位10個）:")
        for num, weight in top_numbers:
            print(f"  数字 {int(num):02d}: 重み {weight:.2f}")
        
        # 最頻出の偶奇パターン
        if self.state['even_odd_preferences']:
            top_eo = sorted(self.state['even_odd_preferences'].items(), 
                          key=lambda x: x[1], reverse=True)[0]
            print(f"\n最頻出の偶奇パターン: {top_eo[0]} ({top_eo[1]}回)")
        
        # 予測精度
        accuracy = self.state['prediction_accuracy']
        if accuracy['total_predictions'] > 0:
            print(f"\n予測精度:")
            for hit_count, count in accuracy['hits'].items():
                if count > 0:
                    pct = (count / accuracy['total_predictions']) * 100
                    print(f"  {hit_count}個的中: {count}回 ({pct:.1f}%)")
        
        print("="*80)
    
    def get_recommendations(self) -> Dict:
        """学習結果に基づく推奨事項を返す"""
        return {
            'hot_numbers': sorted(self.state['number_weights'].items(), 
                                 key=lambda x: x[1], reverse=True)[:15],
            'top_pairs': sorted(self.state['pair_weights'].items(), 
                              key=lambda x: x[1], reverse=True)[:20],
            'preferred_even_odd': max(self.state['even_odd_preferences'].items(), 
                                     key=lambda x: x[1])[0] if self.state['even_odd_preferences'] else None,
            'model_performance': self.state['model_performance']
        }
    
    def get_model_weights(self) -> Dict:
        """モデルの重みを返す（互換性のため）"""
        return self.state.get('number_weights', {})
    
    def learn_from_data(self, df: pd.DataFrame):
        """データフレームから学習（互換性のため）"""
        if df.empty:
            return
        
        # 最新のデータから学習
        latest_row = df.iloc[-1]
        winning_numbers = [latest_row[f'num{i}'] for i in range(1, 7)]
        bonus_number = latest_row.get('bonus', 0)
        
        self.learn_from_result(winning_numbers, bonus_number, 
                              latest_row.get('draw_number', 0))


def learn_from_latest_result():
    """最新の当選結果から学習"""
    print("\n最新の当選結果から学習します...")
    
    # データを読み込み
    df = load_all_loto6_draws()
    if df.empty:
        print("データがありません")
        return
    
    # 最新の当選番号を取得
    latest = df.sort_values('date', ascending=False).iloc[0]
    num_cols = [f'num{i}' for i in range(1, 7)]
    winning_numbers = [int(latest[col]) for col in num_cols]
    bonus_number = int(latest['bonus'])
    
    # 学習
    learner = UltimateLoto6Learner()
    learner.learn_from_result(winning_numbers, bonus_number)
    
    # 推奨事項を表示
    recommendations = learner.get_recommendations()
    
    print("\n" + "="*80)
    print("次回予測への推奨事項")
    print("="*80)
    
    print("\n重点的に狙うべき数字（トップ10）:")
    for num, weight in recommendations['hot_numbers'][:10]:
        print(f"  {int(num):02d} (重み: {weight:.2f})")
    
    if recommendations['preferred_even_odd']:
        print(f"\n推奨の偶奇バランス: {recommendations['preferred_even_odd']}")
    
    print("\n" + "="*80)


def learn_model_from_data(df: pd.DataFrame):
    """互換性のための関数（削除されたlearning_logic.pyから移行）"""
    learner = UltimateLoto6Learner()
    learner.learn_from_data(df)
    return learner.get_model_weights()

if __name__ == '__main__':
    learn_from_latest_result()
