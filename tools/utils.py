import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# このファイルの親ディレクトリの親ディレクトリをROOTとする
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_db_connection():
    """データベース接続を取得します。"""
    db_url = os.environ.get('DATABASE_URL')
    if db_url and '?schema' in db_url:
        db_url = db_url.split('?schema')[0]
    return psycopg2.connect(db_url)

def load_all_numbers4_draws() -> pd.DataFrame:
    """
    SQLiteデータベースからすべてのナンバーズ4の抽選結果を読み込み、
    前処理を行ってDataFrameとして返します。
    """
    conn = get_db_connection()
    try:
        # 'numbers' 列を 'winning_numbers' にエイリアスして互換性を保つ
        query = "SELECT draw_date as date, numbers as winning_numbers FROM numbers4_draws ORDER BY draw_date ASC"
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    # 日付はdatetime型のまま返す（フォーマット変換しない）
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # winning_numbersがNoneや空文字列の行を除外
    df = df.dropna(subset=['winning_numbers'])
    df = df[df['winning_numbers'] != '']

    # winning_numbersを各桁に分割
    df['d1'] = df['winning_numbers'].str[0]
    df['d2'] = df['winning_numbers'].str[1]
    df['d3'] = df['winning_numbers'].str[2]
    df['d4'] = df['winning_numbers'].str[3]

    # データ型を整数に変換
    for col in ['d1', 'd2', 'd3', 'd4']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 変換でNaNになった行を削除
    df = df.dropna(subset=['d1', 'd2', 'd3', 'd4'])

    for col in ['d1', 'd2', 'd3', 'd4']:
        df[col] = df[col].astype(int)

    return df

def load_all_loto6_draws() -> pd.DataFrame:
    """
    SQLiteデータベースからすべてのロト6の抽選結果を読み込み、
    前処理を行ってDataFrameとして返します。
    """
    conn = get_db_connection()
    try:
        # カラム名をloto6_drawsテーブルのスキーマに合わせる
        query = "SELECT draw_date as date, numbers, bonus_number as bonus FROM loto6_draws ORDER BY draw_date ASC"
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    # 日付はdatetime型のまま返す（フォーマット変換しない）
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # 'numbers' 列を6つの数値列に分割
    num_cols = ['num1', 'num2', 'num3', 'num4', 'num5', 'num6']
    
    # 'numbers' 列が '1,2,3,4,5,6' のようなカンマ区切り、または '1 2 3 4 5 6' のようなスペース区切りの文字列に対応
    # 不正な形式のデータに対応するため、列数が6に満たない場合はNaNで埋める
    split_numbers = df['numbers'].str.split(r'[,\s]+', expand=True)
    
    # 列名が整数インデックスになるようにリセット
    split_numbers.columns = range(split_numbers.shape[1])

    if split_numbers.shape[1] < 6:
        for i in range(split_numbers.shape[1], 6):
            split_numbers[i] = pd.NA
    
    for i, col in enumerate(num_cols):
        # split_numbersにi番目の列が存在するか確認
        if i < split_numbers.shape[1]:
            df[col] = pd.to_numeric(split_numbers[i], errors='coerce')
        else:
            df[col] = pd.NA

    # 'bonus' 列のデータ型を変換
    df['bonus'] = pd.to_numeric(df['bonus'], errors='coerce')

    # 本数字のいずれかが欠損している行は除外
    df.dropna(subset=num_cols, inplace=True)
    
    # 本数字を整数型に変換
    for col in num_cols:
        df[col] = df[col].astype(int)

    return df
