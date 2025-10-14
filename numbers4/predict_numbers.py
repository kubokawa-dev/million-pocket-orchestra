
import pandas as pd
import glob
import os
import json
import sqlite3
from collections import Counter
import numpy as np

ROOT = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(ROOT, 'millions.sqlite')
MODEL_PATH = os.path.join(ROOT, 'numbers4', 'model_state.json')

def _normalize(vec):
    s = sum(vec)
    return [v / s for v in vec] if s else [1.0 / len(vec) for _ in vec]

def load_model_prior():
    # Returns per-position prior probabilities (4 x 10)
    try:
        with open(MODEL_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            pos = data.get('pos_probs')
            if isinstance(pos, list) and len(pos) == 4 and all(len(row) == 10 for row in pos):
                return [list(map(float, row)) for row in pos]
    except Exception:
        pass
    # uniform fallback
    return [[0.1] * 10 for _ in range(4)]

def get_latest_numbers4():
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT numbers FROM numbers4_draws ORDER BY draw_date DESC, draw_number DESC LIMIT 1")
        row = cur.fetchone()
        con.close()
        return row[0] if row else None
    except Exception:
        return None

def analyze_and_predict():
    """
    過去のナンバーズ4の当選番号データを分析し、次回の当選番号を予想する関数。
    """
    try:
        # --- 1. データの読み込み ---
        # 指定されたパターンのCSVファイルをすべて読み込む
        files = glob.glob(os.path.join(ROOT, 'numbers4', '2025*.csv')) or glob.glob(os.path.join(ROOT, 'numbers4', '*.csv'))
        if not files:
            print("エラー: 分析対象のCSVファイルが見つかりません。")
            print("numbers4 フォルダに '2025'で始まるCSVファイルがあるか確認してください。")
            return

        df_list = []
        for file in files:
            # CSVを読み込み、ヘッダーがないため列名を指定
            df_temp = pd.read_csv(file, header=None, names=['kai', 'date', 'number', 's_kuchi', 's_kingaku', 'b_kuchi', 'b_kingaku', 'set_s_kuchi', 'set_s_kingaku', 'set_b_kuchi', 'set_b_kingaku'])
            df_list.append(df_temp)

        # 全てのデータフレームを結合
        df = pd.concat(df_list, ignore_index=True)

        # 当選番号を4桁の文字列として整形（例: 123 -> '0123'）
        df['number_str'] = df['number'].astype(str).str.zfill(4)

        # --- 分析結果の表示 ---
        print('--- ナンバーズ4 過去データ分析結果 ---')
        min_date = df['date'].min()
        max_date = df['date'].max()
        print(f'分析対象期間: {min_date} から {max_date}')
        print(f'分析対象の抽せん回数: {len(df)} 回')

        # --- 2. 傾向分析 ---

        # a. 全体の数字の出現頻度
        all_digits = ''.join(df['number_str'])
        digit_counts = Counter(all_digits)
        print('\n--- a. 全体の数字の出現頻度 (多い順) ---')
        for digit, count in digit_counts.most_common():
            print(f'数字「{digit}」: {count}回')

        # b. 桁ごとの数字の出現頻度
        positions = ['1桁目', '2桁目', '3桁目', '4桁目']
        position_counts = {pos: Counter() for pos in positions}
        for number in df['number_str']:
            for i, digit in enumerate(number):
                position_counts[positions[i]][digit] += 1

        print('\n--- b. 桁ごとの数字の出現頻度 (各桁で多い順) ---')
        for pos in positions:
            print(f'【{pos}】')
            for digit, count in position_counts[pos].most_common(3):
                print(f'  数字「{digit}」: {count}回')

        # c. 偶数と奇数のバランス
        def count_even_odd(number_str):
            evens = sum(1 for digit in number_str if int(digit) % 2 == 0)
            odds = 4 - evens
            return f'偶数{evens}:奇数{odds}'

        even_odd_balance = df['number_str'].apply(count_even_odd)
        balance_counts = Counter(even_odd_balance)
        print('\n--- c. 偶数と奇数のバランス ---')
        for balance, count in balance_counts.most_common():
            print(f'「{balance}」の組み合わせ: {count}回')

        # d. 数字の合計値
        def sum_digits(number_str):
            return sum(int(digit) for digit in number_str)

        df['sum'] = df['number_str'].apply(sum_digits)
        sum_stats = df['sum'].describe()
        print('\n--- d. 4つの数字の合計値 ---')
        print(f"平均合計値: {sum_stats['mean']:.1f}")
        print(f"最も多かった合計値: {df['sum'].mode()[0]}")
        print(f"合計値の範囲: {int(sum_stats['min'])} から {int(sum_stats['max'])}")

        # --- 3. 予想 ---
        print('\n--- 以上の分析に基づいた予想番号 ---')
        # 事前分布と頻度のブレンド（軽学習）
        prior = load_model_prior()  # 4 x 10
        alpha = 0.7  # 実データ側の重み
        pos_arrays = []
        for idx, pos in enumerate(positions):
            arr = [position_counts[pos].get(str(d), 0) for d in range(10)]
            arr = _normalize(arr)
            blended = [alpha * arr[d] + (1 - alpha) * prior[idx][d] for d in range(10)]
            pos_arrays.append(_normalize(blended))

        latest_num = get_latest_numbers4()
        def avoid_latest(s: str) -> str:
            if latest_num and s == latest_num:
                # 最後の桁だけ第2候補に置き換え
                last = 3
                order = sorted(range(10), key=lambda d: -pos_arrays[last][d])
                for cand in order:
                    if str(cand) != s[-1]:
                        return s[:-1] + str(cand)
            return s

        # 予想1: 全体的に出現頻度の高い数字で構成
        hot_digits = [d[0] for d in digit_counts.most_common(4)]
        pred1 = ''.join(hot_digits)
        pred1 = avoid_latest(pred1)
        print(f"【予想1】頻出数字の組み合わせ: 「{pred1}」")

        # 予想2: 各桁で最も出現頻度の高い数字を組み合わせる
        positional_hot_digits = [str(max(range(10), key=lambda d: pos_arrays[i][d])) for i in range(4)]
        pred2 = ''.join(positional_hot_digits)
        pred2 = avoid_latest(pred2)
        print(f"【予想2】各桁の頻出数字の組み合わせ: 「{pred2}」")

        # 予想3: 出現頻度の低い数字（コールドナンバー）を狙う
        cold_digits = [d[0] for d in digit_counts.most_common()[-4:]]
        pred3 = ''.join(cold_digits)
        pred3 = avoid_latest(pred3)
        print(f"【予想3】低頻度数字の組み合わせ（逆張り）: 「{pred3}」")

        # 予想4: バランスを考慮した組み合わせ
        second_balance = balance_counts.most_common(2)[1][0]
        pred4 = avoid_latest(''.join(positional_hot_digits))
        print(f'【予想4】頻出数字とバランス({second_balance})を考慮: 「{pred4}」')

        print('\n【注意】この予想は統計に基づくものであり、当選を保証するものではありません。')

    except ImportError:
        print("エラー: pandasライブラリが見つかりません。")
        print("ターミナルで 'python -m pip install pandas' を実行してインストールしてください。")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")

if __name__ == '__main__':
    analyze_and_predict()
