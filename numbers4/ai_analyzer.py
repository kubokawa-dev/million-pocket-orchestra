"""
Claude AI を使った予測結果の高度な分析モジュール

予測結果と当選番号を分析し、以下を生成：
- 良かった点の具体的な分析
- 反省点・改善点の詳細
- モデル重み調整の提案
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


def get_client() -> Optional['anthropic.Anthropic']:
    """Anthropic クライアントを取得"""
    if not ANTHROPIC_AVAILABLE:
        print("⚠️ anthropic ライブラリがインストールされていません")
        return None
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("⚠️ ANTHROPIC_API_KEY が設定されていません")
        return None
    
    return anthropic.Anthropic(api_key=api_key)


def analyze_with_ai(
    actual_numbers: str,
    target_draw: int,
    predictions: List[Dict],
    digit_analysis: Dict,
    position_hits: int,
    current_weights: Dict
) -> Optional[Dict]:
    """
    Claude AI で予測結果を分析
    
    Args:
        actual_numbers: 当選番号
        target_draw: 抽選回号
        predictions: 予測データのリスト
        digit_analysis: 桁別分析結果
        position_hits: 位置一致数
        current_weights: 現在のモデル重み
    
    Returns:
        分析結果の辞書、またはNone（エラー時）
    """
    client = get_client()
    if not client:
        return None
    
    # 予測データを整形
    prediction_summary = []
    for pred in predictions[:5]:  # 上位5件
        prediction_summary.append(f"- {pred['number']} (スコア: {pred['score']:.1f})")
    
    # 桁別分析を整形
    digit_summary = []
    for i in range(4):
        key = f'd{i+1}'
        if key in digit_analysis:
            info = digit_analysis[key]
            hit = "✅" if info['hit_in_top3'] else "❌"
            top3 = ', '.join([f"{d}({c}回)" for d, c in info['predicted_top3'][:3]])
            digit_summary.append(f"- {i+1}桁目: 当選={info['actual']} / 予測TOP3={top3} / {hit}")
    
    # 当選番号の特徴分析
    actual_features = analyze_number_features(actual_numbers)
    
    prompt = f"""あなたはナンバーズ4の予測分析エキスパートです。
以下の予測結果を分析し、JSON形式で回答してください。

## 当選番号
第{target_draw}回: {actual_numbers}

## 当選番号の特徴
{json.dumps(actual_features, ensure_ascii=False, indent=2)}

## 予測結果TOP5
{chr(10).join(prediction_summary)}

## 桁別分析
{chr(10).join(digit_summary)}

## 位置一致数
{position_hits}桁

## 現在のモデル重み
{json.dumps(current_weights, ensure_ascii=False, indent=2)}

## 分析してほしいこと

以下のJSON形式で回答してください。日本語で、具体的に分析してください。

```json
{{
  "good_points": [
    "良かった点1（具体的に）",
    "良かった点2（具体的に）"
  ],
  "improvement_points": [
    "改善点1（具体的に）",
    "改善点2（具体的に）"
  ],
  "weight_adjustments": {{
    "モデル名": 調整値（-5.0〜+5.0の範囲）,
    ...
  }},
  "weight_adjustment_reasons": [
    "調整理由1",
    "調整理由2"
  ],
  "next_prediction_tips": [
    "次回予測へのアドバイス1",
    "次回予測へのアドバイス2"
  ]
}}
```

注意：
- good_points は最低1つ、できれば2-3つ挙げてください
- improvement_points は具体的な改善策を含めてください
- weight_adjustments は本当に必要な場合のみ。成績が良い場合は空でOK
- 位置一致が3桁以上なら、現状維持を推奨してください
"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # JSONを抽出
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            result = json.loads(json_str)
            return result
        else:
            print("⚠️ AIレスポンスからJSONを抽出できませんでした")
            return None
            
    except Exception as e:
        print(f"❌ AI分析エラー: {e}")
        return None


def analyze_number_features(number: str) -> Dict:
    """当選番号の特徴を分析"""
    digits = [int(d) for d in number]
    
    features = {
        'number': number,
        'sum': sum(digits),
        'unique_digits': len(set(number)),
        'even_count': sum(1 for d in digits if d % 2 == 0),
        'odd_count': sum(1 for d in digits if d % 2 != 0),
        'high_count': sum(1 for d in digits if d >= 5),
        'low_count': sum(1 for d in digits if d < 5),
        'has_zero': '0' in number,
        'has_repeat': len(set(number)) < 4,
        'is_sequential': is_sequential(digits),
        'pattern': get_pattern_type(number)
    }
    
    return features


def is_sequential(digits: List[int]) -> bool:
    """連続数字かどうかを判定"""
    sorted_digits = sorted(digits)
    for i in range(len(sorted_digits) - 1):
        if sorted_digits[i+1] - sorted_digits[i] != 1:
            return False
    return True


def get_pattern_type(number: str) -> str:
    """番号のパターンタイプを判定"""
    unique = len(set(number))
    
    if unique == 1:
        return "ゾロ目（AAAA）"
    elif unique == 2:
        counts = sorted([number.count(d) for d in set(number)], reverse=True)
        if counts == [3, 1]:
            return "トリプル（AAAB）"
        elif counts == [2, 2]:
            return "ダブルダブル（AABB）"
        else:
            return "ダブル（AABCD）"
    elif unique == 3:
        return "1ペア（AABC）"
    else:
        return "オールユニーク（ABCD）"


def format_ai_analysis_for_markdown(ai_result: Dict) -> str:
    """AI分析結果をMarkdown形式にフォーマット"""
    md = []
    
    # 良かった点
    md.append("## 💡 今日の良かった点")
    md.append("")
    for point in ai_result.get('good_points', []):
        md.append(f"- {point}")
    md.append("")
    
    # 改善点
    md.append("## ⚠️ 反省点・改善点")
    md.append("")
    for point in ai_result.get('improvement_points', []):
        md.append(f"- {point}")
    md.append("")
    
    # 重み調整
    weight_adjustments = ai_result.get('weight_adjustments', {})
    if weight_adjustments:
        md.append("## 🔧 AI推奨の重み調整")
        md.append("")
        md.append("| モデル | 調整値 |")
        md.append("|:---|:---:|")
        for model, delta in weight_adjustments.items():
            sign = "+" if delta > 0 else ""
            md.append(f"| {model} | {sign}{delta:.1f} |")
        md.append("")
        
        # 調整理由
        reasons = ai_result.get('weight_adjustment_reasons', [])
        if reasons:
            md.append("### 調整理由")
            md.append("")
            for reason in reasons:
                md.append(f"- {reason}")
            md.append("")
    else:
        md.append("## 🔧 AI推奨の重み調整")
        md.append("")
        md.append("*現状維持を推奨*")
        md.append("")
    
    # 次回へのアドバイス
    tips = ai_result.get('next_prediction_tips', [])
    if tips:
        md.append("## 🎯 次回予測へのアドバイス")
        md.append("")
        for tip in tips:
            md.append(f"- {tip}")
        md.append("")
    
    return "\n".join(md)


if __name__ == '__main__':
    # テスト用
    print("AI Analyzer モジュール")
    print(f"Anthropic available: {ANTHROPIC_AVAILABLE}")
    
    # 特徴分析のテスト
    test_number = "7202"
    features = analyze_number_features(test_number)
    print(f"\n{test_number} の特徴:")
    print(json.dumps(features, ensure_ascii=False, indent=2))


