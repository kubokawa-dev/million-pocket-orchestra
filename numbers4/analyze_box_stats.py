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


def generate_markdown_report(results):
    """
    分析結果をMarkdown形式で生成
    """
    now = datetime.now()
    lines = []
    
    # ヘッダー
    lines.append("# 📊 ナンバーズ4 組み合わせ（ボックス）統計分析")
    lines.append("")
    lines.append("## 📋 分析情報")
    lines.append("")
    lines.append("| 項目 | 内容 |")
    lines.append("|:---|:---|")
    lines.append(f"| 分析日時 | {now.strftime('%Y-%m-%d %H:%M')} |")
    lines.append(f"| 総抽選回数 | {results['total_draws']}回 |")
    lines.append(f"| 直近データ | {results['recent_draws']}回 ({results['recent_cutoff'].strftime('%Y/%m/%d')}以降) |")
    lines.append("")
    
    # TOP50
    lines.append("## 🏆 ボックス出現回数 TOP50")
    lines.append("")
    lines.append("過去全期間で最も多く出現した組み合わせをランキング！")
    lines.append("")
    lines.append("| 順位 | 組み合わせ | タイプ | 出現回数 |")
    lines.append("|:---:|:---:|:---:|:---:|")
    
    for i, (combo, count) in enumerate(results['top_combos'], 1):
        combo_type = get_combination_type(combo)
        if i <= 3:
            medal = ["🥇", "🥈", "🥉"][i-1]
            lines.append(f"| {medal} {i} | `{combo}` | {combo_type} | {count}回 |")
        elif i <= 10:
            lines.append(f"| ⭐ {i} | `{combo}` | {combo_type} | {count}回 |")
        else:
            lines.append(f"| {i} | `{combo}` | {combo_type} | {count}回 |")
    
    lines.append("")
    
    # 直近で熱い組み合わせ
    lines.append("## 🔥 直近で熱い組み合わせ TOP10")
    lines.append("")
    lines.append("直近2年間で複数回出現している注目の組み合わせ！")
    lines.append("")
    lines.append("| 順位 | 組み合わせ | 総出現 | 直近出現 | 最新当選日 |")
    lines.append("|:---:|:---:|:---:|:---:|:---:|")
    
    for i, item in enumerate(results['hot_combos'], 1):
        latest = item['latest_date'].strftime('%Y/%m/%d') if item['latest_date'] else '-'
        if i <= 3:
            medal = ["🥇", "🥈", "🥉"][i-1]
            lines.append(f"| {medal} {i} | `{item['combo']}` | {item['total_count']}回 | {item['recent_count']}回 | {latest} |")
        else:
            lines.append(f"| {i} | `{item['combo']}` | {item['total_count']}回 | {item['recent_count']}回 | {latest} |")
    
    lines.append("")
    
    # 出現回数が少ない組み合わせ
    lines.append("## ❄️ 出現回数が少ない組み合わせ（シングル）TOP20")
    lines.append("")
    lines.append("シングル（4桁全部違う）で最も出現が少ない組み合わせ。")
    lines.append("そろそろ来るかも...？🤔")
    lines.append("")
    lines.append("| 順位 | 組み合わせ | 出現回数 |")
    lines.append("|:---:|:---:|:---:|")
    
    for i, (combo, count) in enumerate(results['rare_combos'], 1):
        lines.append(f"| {i} | `{combo}` | {count}回 |")
    
    lines.append("")
    
    # 購入アドバイス
    lines.append("## 💡 購入アドバイス")
    lines.append("")
    lines.append("### 🎯 狙い目の組み合わせ")
    lines.append("")
    
    if results['hot_combos']:
        top3_hot = results['hot_combos'][:3]
        hot_list = ", ".join([f"`{item['combo']}`" for item in top3_hot])
        lines.append(f"**直近で熱い**: {hot_list}")
        lines.append("")
    
    lines.append("### 📝 ボックス買いのコツ")
    lines.append("")
    lines.append("1. **シングル（24通り）を優先** - 1口で24パターンカバー")
    lines.append("2. **ダブル（12通り）も狙い目** - 当選確率と配当のバランス◎")
    lines.append("3. **直近で熱い組み合わせ**を参考に！")
    lines.append("")
    
    # フッター
    lines.append("---")
    lines.append("")
    lines.append(f"*Generated at {now.strftime('%Y-%m-%d %H:%M:%S')} by 宝くじAI 📊*")
    
    return "\n".join(lines)


def save_markdown_report(results, output_dir=None):
    """
    分析結果をMarkdownファイルとして保存
    
    Args:
        results: 分析結果
        output_dir: 出力ディレクトリ（Noneの場合はreports/box_stats/）
    
    Returns:
        str: 保存したファイルパス
    """
    if output_dir is None:
        output_dir = os.path.join(ROOT, 'reports', 'box_stats')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # ファイル名: box_stats_YYYYMMDD.md
    date_str = datetime.now().strftime('%Y%m%d')
    filename = f"box_stats_{date_str}.md"
    filepath = os.path.join(output_dir, filename)
    
    # Markdown生成
    markdown_content = generate_markdown_report(results)
    
    # ファイル保存
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"✅ レポートを保存しました: {filepath}")
    
    return filepath


def save_analysis_to_db(results):
    """
    分析結果をデータベースに保存（オプション）
    将来的に予測に活用するため
    """
    # TODO: 必要に応じてDB保存を実装
    pass


def main(save_report=False):
    """
    メイン処理
    
    Args:
        save_report: Trueの場合、Markdownレポートを保存
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
    
    # Markdownレポート保存
    if save_report:
        save_markdown_report(results)
    
    return results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='ナンバーズ4 組み合わせ統計分析')
    parser.add_argument('--save', action='store_true', help='Markdownレポートを保存')
    args = parser.parse_args()
    
    main(save_report=args.save)
