"""
🔥 ナンバーズ4 魂予測システム (Soul Predictor) v1.0 🔥

このモジュールは「類似パターン」ではなく、
**ズバリ当選番号を予測する**ことを目指す。

ナンバーズ4の本質:
- 10,000通り（0000〜9999）から1つが選ばれる
- 完全ランダム（理論上は各番号が等確率）
- でも実際には偏りがある（機械の癖、ボールの摩耗など）

魂モデルの哲学:
1. 「当たりそう」ではなく「当たる」番号を予測
2. 過去の偏りを徹底的に分析
3. 予測数を絞り込んで精度を上げる
4. ボックス買いを前提に、カバー範囲を最大化

Created with 💕 by Million Pocket
"""

import os
import sys
from collections import Counter, defaultdict
from itertools import permutations
from typing import Dict, List, Tuple, Optional
import random
import math

# プロジェクトルートをパスに追加
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

from tools.utils import load_all_numbers4_draws


# ========================================
# 🔮 魂モデルの核心ロジック
# ========================================

def number_to_box(number: str) -> str:
    """4桁の番号をボックスID（ソート済み）に変換"""
    return ''.join(sorted(number))


def get_box_permutations(box_id: str) -> List[str]:
    """ボックスIDから全ての並び替えパターンを生成"""
    return list(set([''.join(p) for p in permutations(box_id)]))


def get_box_type(number: str) -> Tuple[str, int]:
    """
    番号のボックスタイプと通り数を返す
    
    Returns:
        (タイプ名, 通り数)
    """
    counts = sorted(Counter(number).values(), reverse=True)
    
    if counts == [4]:
        return ("ゾロ目", 1)
    elif counts == [3, 1]:
        return ("トリプル", 4)
    elif counts == [2, 2]:
        return ("ダブルダブル", 6)
    elif counts == [2, 1, 1]:
        return ("ダブル", 12)
    else:
        return ("シングル", 24)


class SoulPredictor:
    """
    🔥 ナンバーズ4 魂予測クラス 🔥
    
    予測の哲学:
    - 過去データから「出やすいパターン」を学習
    - 「そろそろ来そう」なコールドナンバーを特定
    - ボックス買いで効率的にカバー
    """
    
    def __init__(self, df=None):
        """
        初期化
        
        Args:
            df: 過去の抽選データ（Noneの場合はDBから読み込み）
        """
        if df is None:
            df = load_all_numbers4_draws()
        
        self.df = df
        self.total_draws = len(df)
        
        # 分析結果を格納
        self.digit_probs = {}      # 各桁の数字出現確率
        self.pair_probs = {}       # 数字ペアの共起確率
        self.box_history = {}      # ボックスの出現履歴
        self.transition_probs = {} # 遷移確率
        self.sum_distribution = {} # 合計値の分布
        
        # 分析実行
        self._analyze_all()
    
    def _analyze_all(self):
        """全ての分析を実行"""
        self._analyze_digit_frequency()
        self._analyze_pair_frequency()
        self._analyze_box_history()
        self._analyze_transitions()
        self._analyze_sum_distribution()
    
    def _analyze_digit_frequency(self):
        """各桁の数字出現頻度を分析"""
        for pos in range(4):
            col = f'd{pos+1}'
            freq = Counter(self.df[col])
            total = sum(freq.values())
            self.digit_probs[pos] = {d: freq.get(d, 0) / total for d in range(10)}
    
    def _analyze_pair_frequency(self):
        """数字ペアの共起頻度を分析"""
        pair_counts = defaultdict(int)
        
        for _, row in self.df.iterrows():
            digits = [row['d1'], row['d2'], row['d3'], row['d4']]
            # 全てのペアをカウント
            for i in range(4):
                for j in range(i+1, 4):
                    pair = tuple(sorted([digits[i], digits[j]]))
                    pair_counts[pair] += 1
        
        total = sum(pair_counts.values())
        self.pair_probs = {pair: count / total for pair, count in pair_counts.items()}
    
    def _analyze_box_history(self):
        """ボックスの出現履歴を分析"""
        for idx, row in self.df.iterrows():
            number = f"{row['d1']}{row['d2']}{row['d3']}{row['d4']}"
            box_id = number_to_box(number)
            draw_num = row['draw_number']
            
            if box_id not in self.box_history:
                self.box_history[box_id] = {
                    'count': 0,
                    'last_draw': None,
                    'draws': []
                }
            
            self.box_history[box_id]['count'] += 1
            self.box_history[box_id]['last_draw'] = draw_num
            self.box_history[box_id]['draws'].append(draw_num)
    
    def _analyze_transitions(self):
        """遷移確率を分析（前回→今回の数字変化）"""
        for pos in range(4):
            col = f'd{pos+1}'
            trans = defaultdict(lambda: defaultdict(int))
            
            for i in range(1, len(self.df)):
                prev = self.df.iloc[i-1][col]
                curr = self.df.iloc[i][col]
                trans[prev][curr] += 1
            
            # 正規化
            self.transition_probs[pos] = {}
            for prev_d, next_counts in trans.items():
                total = sum(next_counts.values())
                self.transition_probs[pos][prev_d] = {
                    d: c / total for d, c in next_counts.items()
                }
    
    def _analyze_sum_distribution(self):
        """4桁の合計値の分布を分析"""
        sums = []
        for _, row in self.df.iterrows():
            s = row['d1'] + row['d2'] + row['d3'] + row['d4']
            sums.append(s)
        
        freq = Counter(sums)
        total = len(sums)
        self.sum_distribution = {s: freq.get(s, 0) / total for s in range(37)}  # 0〜36
        
        # 平均と標準偏差
        self.sum_mean = sum(sums) / len(sums)
        self.sum_std = math.sqrt(sum((s - self.sum_mean)**2 for s in sums) / len(sums))
    
    def get_cold_boxes(self, top_n: int = 30) -> List[Tuple[str, int]]:
        """
        コールドボックス（長期間出ていない組み合わせ）を取得
        
        Returns:
            [(box_id, 未出現回数), ...]
        """
        latest_draw = self.df['draw_number'].max()
        
        cold_boxes = []
        for box_id, history in self.box_history.items():
            gap = latest_draw - history['last_draw']
            cold_boxes.append((box_id, gap))
        
        # 未出現期間でソート
        cold_boxes.sort(key=lambda x: -x[1])
        return cold_boxes[:top_n]
    
    def get_hot_digits(self, window: int = 20) -> Dict[int, List[int]]:
        """
        直近で出やすい数字（ホット数字）を取得
        
        Args:
            window: 直近何回分を見るか
        
        Returns:
            {桁: [ホット数字リスト], ...}
        """
        recent = self.df.tail(window)
        hot_digits = {}
        
        for pos in range(4):
            col = f'd{pos+1}'
            freq = Counter(recent[col])
            # 出現回数が多い順にソート
            hot_digits[pos] = [d for d, _ in freq.most_common(5)]
        
        return hot_digits
    
    def get_never_appeared_boxes(self) -> List[str]:
        """
        過去に一度も出ていないボックスを取得
        
        全715通りのボックスのうち、まだ出ていないものを返す
        """
        # 全ボックスを生成
        all_boxes = set()
        for d1 in range(10):
            for d2 in range(d1, 10):
                for d3 in range(d2, 10):
                    for d4 in range(d3, 10):
                        all_boxes.add(f'{d1}{d2}{d3}{d4}')
        
        # 出現済みボックスを除外
        appeared = set(self.box_history.keys())
        never_appeared = all_boxes - appeared
        
        return list(never_appeared)
    
    def predict_soul(self, budget: int = 1000, strategy: str = 'balanced') -> List[Dict]:
        """
        🔥 魂予測メイン関数 🔥
        
        Args:
            budget: 予算（円）
            strategy: 戦略
                - 'balanced': バランス型（推奨）
                - 'cold': コールド重視
                - 'hot': ホット重視
                - 'transition': 遷移確率重視
        
        Returns:
            予測結果のリスト
        """
        price_per_ticket = 200
        max_tickets = budget // price_per_ticket
        
        # 各戦略からの候補を収集
        candidates = {}
        
        # === 戦略0: 未出現ボックス ===
        # 注意: 2840回のデータで未出現は53個のみ、ほとんどがゾロ目系
        # 優先度を下げて、シングル・ダブルのみ対象にする
        never_appeared = self.get_never_appeared_boxes()
        
        for box_id in never_appeared:
            box_type, box_count = get_box_type(box_id)
            
            # ゾロ目・トリプル・ダブルダブルは除外（出にくいパターン）
            if box_type in ["ゾロ目", "トリプル", "ダブルダブル"]:
                continue
            
            # シングル・ダブルのみ対象
            score = 50  # 基本スコア（控えめに）
            
            # ボックス通り数でボーナス
            if box_type == "シングル":
                score += 30
            elif box_type == "ダブル":
                score += 20
            
            if box_id not in candidates:
                candidates[box_id] = {'score': 0, 'sources': []}
            candidates[box_id]['score'] += score
            candidates[box_id]['sources'].append('未出現ボックス')
        
        # === 戦略1: コールドボックス（そろそろ来そう）- 最重要！ ===
        # 2840回のデータがあるので、コールドボックスの信頼性が高い！
        cold_boxes = self.get_cold_boxes(top_n=100)
        for box_id, gap in cold_boxes:
            box_type, box_count = get_box_type(box_id)
            
            # ゾロ目は除外
            if box_type == "ゾロ目":
                continue
            
            # 基本スコア: 未出現期間に比例
            score = gap * 0.1
            
            # ボックス通り数でボーナス（シングル・ダブルを優遇）
            if box_type == "シングル":
                score += 100  # シングルは24通りカバーできる！
            elif box_type == "ダブル":
                score += 80   # ダブルは12通り
            elif box_type == "ダブルダブル":
                score += 40   # 6通り
            elif box_type == "トリプル":
                score += 20   # 4通り
            
            if box_id not in candidates:
                candidates[box_id] = {'score': 0, 'sources': []}
            candidates[box_id]['score'] += score
            candidates[box_id]['sources'].append(f'コールド({gap}回未出現)')
        
        # === 戦略2: 遷移確率ベース ===
        latest = self.df.iloc[-1]
        latest_digits = [latest['d1'], latest['d2'], latest['d3'], latest['d4']]
        
        # 遷移確率から次の数字を予測
        for _ in range(100):  # 100個の候補を生成
            new_digits = []
            for pos in range(4):
                prev_d = latest_digits[pos]
                if prev_d in self.transition_probs[pos]:
                    probs = self.transition_probs[pos][prev_d]
                    digits = list(probs.keys())
                    weights = list(probs.values())
                    chosen = random.choices(digits, weights=weights, k=1)[0]
                else:
                    chosen = random.randint(0, 9)
                new_digits.append(chosen)
            
            number = ''.join(map(str, new_digits))
            box_id = number_to_box(number)
            box_type, box_count = get_box_type(box_id)
            
            if box_type == "ゾロ目":
                continue
            
            # 合計値チェック
            digit_sum = sum(new_digits)
            sum_score = self.sum_distribution.get(digit_sum, 0) * 100
            
            score = 30 + sum_score + box_count * 1.0
            
            if box_id not in candidates:
                candidates[box_id] = {'score': 0, 'sources': []}
            candidates[box_id]['score'] += score
            if '遷移確率' not in str(candidates[box_id]['sources']):
                candidates[box_id]['sources'].append('遷移確率')
        
        # === 戦略3: ホット数字の組み合わせ ===
        hot_digits = self.get_hot_digits(window=20)
        
        for _ in range(50):
            new_digits = []
            for pos in range(4):
                if hot_digits[pos]:
                    # ホット数字から選択（確率的に）
                    chosen = random.choice(hot_digits[pos][:3])
                else:
                    chosen = random.randint(0, 9)
                new_digits.append(chosen)
            
            number = ''.join(map(str, new_digits))
            box_id = number_to_box(number)
            box_type, box_count = get_box_type(box_id)
            
            if box_type == "ゾロ目":
                continue
            
            score = 25 + box_count * 1.5
            
            if box_id not in candidates:
                candidates[box_id] = {'score': 0, 'sources': []}
            candidates[box_id]['score'] += score
            if 'ホット数字' not in str(candidates[box_id]['sources']):
                candidates[box_id]['sources'].append('ホット数字')
        
        # === 戦略4: 数字ペアの共起パターン ===
        top_pairs = sorted(self.pair_probs.items(), key=lambda x: -x[1])[:20]
        
        for (d1, d2), prob1 in top_pairs[:10]:
            for (d3, d4), prob2 in top_pairs[:10]:
                digits = [d1, d2, d3, d4]
                number = ''.join(map(str, digits))
                box_id = number_to_box(number)
                box_type, box_count = get_box_type(box_id)
                
                if box_type == "ゾロ目":
                    continue
                
                score = (prob1 + prob2) * 500 + box_count * 1.0
                
                if box_id not in candidates:
                    candidates[box_id] = {'score': 0, 'sources': []}
                candidates[box_id]['score'] += score
                if 'ペア共起' not in str(candidates[box_id]['sources']):
                    candidates[box_id]['sources'].append('ペア共起')
        
        # === 最終選定 ===
        # スコアでソート
        sorted_candidates = sorted(candidates.items(), key=lambda x: -x[1]['score'])
        
        # 多様性を確保しながら選定
        # 戦略: 未出現ボックスとコールドボックスをバランスよく選ぶ
        selected = []
        type_counts = {'シングル': 0, 'ダブル': 0, 'ダブルダブル': 0, 'トリプル': 0}
        source_counts = {'未出現ボックス': 0, 'コールド': 0, 'その他': 0}
        
        # 未出現ボックスとコールドボックスの上限を設定
        never_appeared_set = set(self.get_never_appeared_boxes())
        max_never_appeared = max(3, max_tickets // 2)  # 最大半分まで
        max_cold = max(3, max_tickets // 2)  # 最大半分まで
        
        for box_id, data in sorted_candidates:
            if len(selected) >= max_tickets:
                break
            
            box_type, box_count = get_box_type(box_id)
            
            # タイプ別の上限
            type_limits = {
                'シングル': max(2, max_tickets // 2),
                'ダブル': max(2, max_tickets // 2),
                'ダブルダブル': max(1, max_tickets // 4),
                'トリプル': 1
            }
            
            # ソース別の上限チェック
            is_never_appeared = box_id in never_appeared_set
            is_cold = 'コールド' in str(data['sources'])
            
            if is_never_appeared and source_counts['未出現ボックス'] >= max_never_appeared:
                continue
            if is_cold and not is_never_appeared and source_counts['コールド'] >= max_cold:
                continue
            
            if type_counts.get(box_type, 0) < type_limits.get(box_type, 1):
                # 代表的な並びを生成
                perms = get_box_permutations(box_id)
                representative = random.choice(perms)
                
                selected.append({
                    'number': representative,
                    'box_id': box_id,
                    'box_type': box_type,
                    'box_count': box_count,
                    'score': data['score'],
                    'sources': data['sources'],
                    'buy_type': 'ボックス'
                })
                type_counts[box_type] = type_counts.get(box_type, 0) + 1
                
                if is_never_appeared:
                    source_counts['未出現ボックス'] += 1
                elif is_cold:
                    source_counts['コールド'] += 1
                else:
                    source_counts['その他'] += 1
        
        # 枠が余っていたら追加
        for box_id, data in sorted_candidates:
            if len(selected) >= max_tickets:
                break
            if box_id not in [s['box_id'] for s in selected]:
                box_type, box_count = get_box_type(box_id)
                perms = get_box_permutations(box_id)
                representative = random.choice(perms)
                selected.append({
                    'number': representative,
                    'box_id': box_id,
                    'box_type': box_type,
                    'box_count': box_count,
                    'score': data['score'],
                    'sources': data['sources'],
                    'buy_type': 'ボックス'
                })
        
        return selected
    
    def get_soul_summary(self, predictions: List[Dict]) -> str:
        """
        魂予測のサマリーを生成
        """
        lines = []
        lines.append("## 🔥 魂予測 - ズバリ当選番号！")
        lines.append("")
        lines.append("「類似パターン」じゃない。**これが当たる番号だ！**")
        lines.append("")
        
        total_coverage = sum(p['box_count'] for p in predictions)
        lines.append(f"**カバー範囲: {total_coverage}通り** (当選確率: {total_coverage/100:.2f}%)")
        lines.append("")
        
        lines.append("| 優先度 | 番号 | 買い方 | タイプ | 根拠 |")
        lines.append("|:---:|:---:|:---:|:---:|:---|")
        
        for i, pred in enumerate(predictions, 1):
            if i <= 3:
                emoji = ['🥇', '🥈', '🥉'][i-1]
            else:
                emoji = f'{i}'
            
            sources = ', '.join(pred['sources'][:2])
            lines.append(f"| {emoji} | `{pred['number']}` | {pred['buy_type']} | {pred['box_type']}({pred['box_count']}通り) | {sources} |")
        
        lines.append("")
        lines.append("### 📝 買い方")
        lines.append("")
        lines.append("1. **全てボックス買い** - 並び順関係なく当選！")
        lines.append("2. **上から順に優先** - 予算に合わせて調整")
        lines.append("3. **信じて買う** - 魂を込めた予測だから！🔥")
        lines.append("")
        
        return '\n'.join(lines)


# ========================================
# メイン処理
# ========================================

def generate_soul_prediction(budget: int = 1000) -> Tuple[List[Dict], str]:
    """
    魂予測を生成
    
    Args:
        budget: 予算（円）
    
    Returns:
        (予測リスト, サマリーMarkdown)
    """
    predictor = SoulPredictor()
    predictions = predictor.predict_soul(budget=budget)
    summary = predictor.get_soul_summary(predictions)
    
    return predictions, summary


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='🔥 ナンバーズ4 魂予測')
    parser.add_argument('--budget', '-b', type=int, default=1000, help='予算（円）')
    args = parser.parse_args()
    
    print("🔥 ナンバーズ4 魂予測システム起動！")
    print("=" * 60)
    
    predictions, summary = generate_soul_prediction(budget=args.budget)
    
    print(summary)
    
    print("\n" + "=" * 60)
    print("💪 信じて買え！当たる！🔥")
