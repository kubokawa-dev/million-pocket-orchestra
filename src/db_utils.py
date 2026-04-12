"""
データベース操作のユーティリティ（セキュリティ強化版）

すべてのSQLクエリはこのモジュールを通じて実行する必要があります。
パラメータ化クエリを強制することでSQLインジェクションを防止します。
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Any, Generator, List, Optional, Tuple, Dict

import pandas as pd


def get_db_connection() -> sqlite3.Connection:
    """
    データベース接続を取得します。
    SQLite用にRow Factoryを設定して辞書形式でアクセスできるようにします。
    """
    import os
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(ROOT_DIR, 'lottery.db')
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_transaction() -> Generator[sqlite3.Connection, None, None]:
    """
    データベーストランザクションのコンテキストマネージャー
    
    使用例:
        with db_transaction() as conn:
            conn.execute("INSERT INTO ...", (param1, param2))
    """
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_query(
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
) -> List[sqlite3.Row]:
    """
    SELECTクエリを安全に実行します。
    
    Args:
        query: SQLクエリ（パラメータは ? プレースホルダー使用）
        params: クエリパラメータのタプル
        
    Returns:
        結果行のリスト
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur.fetchall()
    finally:
        conn.close()


def execute_query_df(
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
) -> pd.DataFrame:
    """
    SELECTクエリを実行し、DataFrameを返します。
    
    Args:
        query: SQLクエリ
        params: クエリパラメータ
        
    Returns:
        結果のDataFrame
    """
    conn = get_db_connection()
    try:
        if params:
            return pd.read_sql_query(query, conn, params=params)
        else:
            return pd.read_sql_query(query, conn)
    finally:
        conn.close()


def execute_update(
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
) -> int:
    """
    UPDATE/INSERT/DELETEクエリを実行します。
    
    Args:
        query: SQLクエリ
        params: クエリパラメータ
        
    Returns:
        影響を受けた行数
    """
    with db_transaction() as conn:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur.rowcount


def execute_many(
    query: str,
    params_list: List[Tuple[Any, ...]],
) -> int:
    """
    複数のパラメータセットでクエリを一括実行します。
    
    Args:
        query: SQLクエリ
        params_list: パラメータのリスト
        
    Returns:
        影響を受けた総行数
    """
    with db_transaction() as conn:
        cur = conn.cursor()
        cur.executemany(query, params_list)
        return cur.rowcount


def validate_draw_number(draw_number: Any) -> int:
    """
    draw_numberパラメータを検証・変換します。
    
    Args:
        draw_number: 検証する値
        
    Returns:
        int: 検証済みのdraw_number
        
    Raises:
        ValueError: 無効な値の場合
    """
    try:
        dn = int(draw_number)
        if dn <= 0:
            raise ValueError(f"draw_number must be positive, got {dn}")
        return dn
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid draw_number: {draw_number}") from e


def validate_limit(limit: Any, max_limit: int = 1000) -> int:
    """
    limitパラメータを検証・変換します。
    
    Args:
        limit: 検証する値
        max_limit: 最大値
        
    Returns:
        int: 検証済みのlimit
        
    Raises:
        ValueError: 無効な値の場合
    """
    try:
        l = int(limit)
        if l <= 0:
            raise ValueError(f"limit must be positive, got {l}")
        if l > max_limit:
            raise ValueError(f"limit must not exceed {max_limit}, got {l}")
        return l
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid limit: {limit}") from e
