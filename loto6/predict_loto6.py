import os
import pandas as pd
import glob
from collections import Counter
import numpy as np

def analyze_loto6():
    """
    loto6のCSVデータを分析し、次回の当選番号の予想を出力します。
    """
    # --- 1. データの読み込み ---
    ROOT = os.path.dirname(os.path.dirname(__file__))
    files = glob.glob(os.path.join(ROOT, 'loto6', '*.csv'))
    if not files:
        print('分析対象のCSVファイルが見つかりません。')
        return

    df_list = []
    # CSVの列名を定義
    col_names = [
        'kai', 'date', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'bonus',
        '1st_winners', '1st_prize', '2nd_winners', '2nd_prize',
        '3rd_winners', '3rd_prize', '4th_winners', '4th_prize',
        '5th_winners', '5th_prize', 'carryover'
    ]
    for file in sorted(files):
        try:
            df_temp = pd.read_csv(file, header=None, names=col_names, dtype=str)
            df_list.append(df_temp)
        except Exception as e:
            print(f'ファイル {file} の読み込み中にエラーが発生しました: {e}')

    if not df_list:
        print("データが読み込めませんでした。")
        return

    df = pd.concat(df_list, ignore_index=True)

    # 当せん番号の列を選択
    num_cols = ['num1', 'num2', 'num3', 'num4', 'num5', 'num6']
    # データ型を数値に変換（エラーは無視）
    for col in num_cols + ['bonus']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 不正な行を削除
    df.dropna(subset=num_cols, inplace=True)
    for col in num_cols:
        df[col] = df[col].astype(int)
    # bonus は欠損があり得るため、厳密な int キャストは行わない（集計時に dropna する）
    # df['bonus'] はすでに to_numeric(errors='coerce') 済み


    print('--- ロト6 過去データ分析結果 ---')
    print(f"分析対象期間: {df['date'].min()} から {df['date'].max()}")
    print(f"分析対象の抽せん回数: {len(df)} 回")

    # --- 2. 傾向分析 ---

    # a. 本数字の出現頻度
    all_numbers = np.concatenate([df[col].values for col in num_cols])
    number_counts = Counter(all_numbers)
    print('\n--- a. 本数字の出現頻度 (多い順) ---')
    for num, count in number_counts.most_common():
        print(f'数字「{int(num)}」: {count}回')

    # b. ボーナス数字の出現頻度
    bonus_counts = Counter(df['bonus'].dropna())
    print('\n--- b. ボーナス数字の出現頻度 (多い順) ---')
    for num, count in bonus_counts.most_common(5):
        print(f'数字「{int(num)}」: {count}回')

    # c. 偶数と奇数のバランス
    def count_even_odd(row):
        evens = sum(1 for i in range(1, 7) if row[f'num{i}'] % 2 == 0)
        odds = 6 - evens
        return f'偶数{evens}:奇数{odds}'

    even_odd_balance = df.apply(count_even_odd, axis=1)
    balance_counts = Counter(even_odd_balance)
    print('\n--- c. 偶数と奇数のバランス ---')
    for balance, count in balance_counts.most_common():
        print(f'「{balance}」の組み合わせ: {count}回')

    # d. 数字の合計値
    df['sum'] = df[num_cols].sum(axis=1)
    sum_stats = df['sum'].describe()
    print('\n--- d. 6つの数字の合計値 ---')
    print(f"平均合計値: {sum_stats['mean']:.1f}")
    print(f"最も多かった合計値: {df['sum'].mode().iloc[0]}")
    print(f"合計値の範囲: {int(sum_stats['min'])} から {int(sum_stats['max'])}")

    # --- 3. 予想 ---
    print('\n--- 以上の分析に基づいた第2042回の予想番号 ---')

    # 予想1: 全体的に出現頻度の高い数字（ホットナンバー）で構成
    hot_numbers = [str(int(n[0])).zfill(2) for n in number_counts.most_common(6)]
    print(f"【予想1】頻出数字の組み合わせ: 「{' '.join(hot_numbers)}」")

    # 予想2: 出現頻度の低い数字（コールドナンバー）を狙う
    cold_numbers = [str(int(n[0])).zfill(2) for n in number_counts.most_common()[-6:]]
    print(f"【予想2】低頻度数字の組み合わせ（逆張り）: 「{' '.join(cold_numbers)}」")

    # 予想3: バランスを考慮した組み合わせ
    print(f'【予想3】バランス考慮の組み合わせ (例): 「08 13 22 30 35 40」')

    # 予想4: 直近の傾向を重視
    last = df.sort_values('date', ascending=False).iloc[0]
    recent_tuple = tuple(sorted(int(last[f'num{i}']) for i in range(1,7)))
    recent_nums = set(recent_tuple)
    
    # 直近で出ていない、かつ出現頻度が中程度の数字を選ぶ
    candidate_pool = [num for num, count in number_counts.items() if num not in recent_nums and count > 1]
    # 再現性のため乱数シードを固定
    np.random.seed(2042)
    if len(candidate_pool) >= 6:
        tried = 0
        while True:
            prediction_4 = np.random.choice(candidate_pool, 6, replace=False)
            prediction_4.sort()
            if tuple(int(x) for x in prediction_4) != recent_tuple:
                break
            tried += 1
            if tried > 50:
                break
        pred_4_str = [str(int(n)).zfill(2) for n in prediction_4]
        print(f"【予想4】直近の傾向を考慮した組み合わせ: 「{' '.join(pred_4_str)}」")
    else:
        print('【予想4】直近の傾向を考慮した組み合わせ: 候補不足のため生成できませんでした。')


    print('\n【注意】この予想は統計に基づくものであり、当選を保証するものではありません。')

if __name__ == '__main__':
    analyze_loto6()
