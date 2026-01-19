"""
ナンバーズ4 組み合わせ（ボックス）統計分析

過去の当選番号を分析して以下を出力:
1. ボックス出現回数TOP50
2. 直近で熱い組み合わせ（2025-2026年）
3. 出現回数が少ない組み合わせ
"""
import os
import sys
from datetime import datetime, timedelta
from collections import Counter

# プロジェクトルートをパスに追加
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from tools.utils import load_all_numbers4_draws


def get_box_combination(number: str) -> str:
    """
    4桁の番号をボックス組み合わせ（ソート済み）に変換
    例: "6436" -> "3466"
    """
    return ''.join(sorted(number))


def get_combination_type(combo: str) -> str:
    """
    組み合わせのタイプを判定
    - シングル: 4桁全部違う (例: 1234)
    - ダブル: 2つが同じ (例: 1123)
    - ダブルダブル: 2組のペア (例: 1122)
    - トリプル: 3つが同じ (例: 1112)
    - ゾロ目: 4つ全部同じ (例: 1111)
    """
    counts = Counter(combo)
    values = sorted(counts.values(), reverse=True)
    
    if values == [4]:
        return "ゾロ目"
    elif values == [3, 1]:
        return "トリプル"
    elif values == [2, 2]:
        return "ダブルダブル"
    elif values == [2, 1, 1]:
        return "ダブル"
    else:
        return "シングル"


def analyze_box_statistics(df, top_n=50, recent_years=2):
    """
    ボックス統計を分析
    
    Args:
        df: 当選番号のDataFrame
        top_n: TOP何位まで表示するか
        recent_years: 直近何年を「最近」とするか
    
    Returns:
        dict: 分析結果
    """
    # ボックス組み合わせを計算
    df = df.copy()
    df['box_combo'] = df['winning_numbers'].apply(get_box_combination)
    
    # 全期間の集計
    all_counts = Counter(df['box_combo'])
    
    # 直近のデータを抽出
    recent_cutoff = datetime.now() - timedelta(days=365 * recent_years)
    recent_df = df[df['date'] >= recent_cutoff]
    recent_counts = Counter(recent_df['box_combo'])
    
    # TOP N の組み合わせ
    top_combos = all_counts.most_common(top_n)
    
    # 出現回数が少ない組み合わせ（シングルのみ）
    single_combos = {k: v for k, v in all_counts.items() if get_combination_type(k) == "シングル"}
    rare_combos = sorted(single_combos.items(), key=lambda x: x[1])[:20]
    
    # 直近で熱い組み合わせ（TOP50の中で直近出現が多いもの）
    hot_combos = []
    for combo, total_count in top_combos:
        recent_count = recent_counts.get(combo, 0)
        if recent_count >= 2:  # 直近2回以上出現
            # 最新の出現日を取得
            latest_date = recent_df[recent_df['box_combo'] == combo]['date'].max()
            hot_combos.append({
                'combo': combo,
                'total_count': total_count,
                'recent_count': recent_count,
                'latest_date': latest_date
            })
    
    # 直近出現回数でソート
    hot_combos.sort(key=lambda x: (-x['recent_count'], -x['total_count']))
    
    return {
        'top_combos': top_combos,
        'rare_combos': rare_combos,
        'hot_combos': hot_combos[:10],  # TOP10
        'total_draws': len(df),
        'recent_draws': len(recent_df),
        'recent_cutoff': recent_cutoff
    }


def print_analysis_report(results):
    """
    分析結果をコンソールに出力
    """
    print("\n" + "="*60)
    print("📊 ナンバーズ4 組み合わせ（ボックス）統計分析")
    print("="*60)
    print(f"総抽選回数: {results['total_draws']}回")
    print(f"直近データ: {results['recent_draws']}回 ({results['recent_cutoff'].strftime('%Y/%m/%d')}以降)")
    
    # TOP50
    print("\n" + "-"*60)
    print("🏆 ボックス出現回数 TOP50")
    print("-"*60)
    print(f"{'順位':>4} | {'組み合わせ':^10} | {'タイプ':^12} | {'出現回数':>8}")
    print("-"*60)
    
    for i, (combo, count) in enumerate(results['top_combos'], 1):
        combo_type = get_combination_type(combo)
        print(f"{i:>4} | {combo:^10} | {combo_type:^12} | {count:>8}回")
    
    # 直近で熱い組み合わせ
    print("\n" + "-"*60)
    print("🔥 直近で熱い組み合わせ TOP10")
    print("-"*60)
    print(f"{'組み合わせ':^10} | {'総出現':>6} | {'直近出現':>8} | {'最新当選日':^12}")
    print("-"*60)
    
    for item in results['hot_combos']:
        latest = item['latest_date'].strftime('%Y/%m/%d') if item['latest_date'] else '-'
        print(f"{item['combo']:^10} | {item['total_count']:>6}回 | {item['recent_count']:>8}回 | {latest:^12}")
    
    # 出現回数が少ない組み合わせ
    print("\n" + "-"*60)
    print("❄️ 出現回数が少ない組み合わせ（シングル）TOP20")
    print("-"*60)
    print(f"{'順位':>4} | {'組み合わせ':^10} | {'出現回数':>8}")
    print("-"*60)
    
    for i, (combo, count) in enumerate(results['rare_combos'], 1):
        print(f"{i:>4} | {combo:^10} | {count:>8}回")
    
    print("\n" + "="*60)


def save_analysis_to_db(results):
    """
    分析結果をデータベースに保存（オプション）
    将来的に予測に活用するため
    """
    # TODO: 必要に応じてDB保存を実装
    pass


def main():
    """
    メイン処理
    """
    print("📊 組み合わせ統計分析を開始...")
    
    # データ読み込み
    df = load_all_numbers4_draws()
    
    if df.empty:
        print("❌ データが見つかりません")
        return None
    
    # 分析実行
    results = analyze_box_statistics(df, top_n=50, recent_years=2)
    
    # レポート出力
    print_analysis_report(results)
    
    return results


if __name__ == '__main__':
    main()
