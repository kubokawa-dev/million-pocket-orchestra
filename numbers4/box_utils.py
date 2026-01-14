"""
ボックスタイプ判定の共通ユーティリティ

Numbers4のボックスタイプ (シングル、ダブル、トリプル等) を判定する
共通ロジックを提供します。
"""
from collections import Counter
from typing import Tuple


def get_box_type_info(number: str) -> Tuple[str, str, int]:
    """
    ボックスタイプとカバー範囲を判定 (正規版)
    
    Args:
        number: 4桁の数字文字列
    
    Returns:
        (タイプ表記, 説明, カバー範囲)
        
    Examples:
        >>> get_box_type_info("1234")
        ('シングル(ABCD)', '4つの数字が全て異なる', 24)
        >>> get_box_type_info("1123")
        ('ダブル(AABC)', '1つの数字が2回出現', 12)
        >>> get_box_type_info("1122")
        ('ダブルダブル(AABB)', '2つの数字が2回ずつ', 6)
        >>> get_box_type_info("1112")
        ('トリプル(AAAB)', '1つの数字が3回出現', 4)
        >>> get_box_type_info("1111")
        ('クアッド(AAAA)', '全て同じ数字 (ゾロ目)', 1)
    """
    # 入力バリデーション
    if not number or not isinstance(number, str) or len(number) != 4:
        return "不明", "不明", 0
    
    if not number.isdigit():
        return "不明", "不明", 0
    
    counts = Counter(number)
    unique_count = len(counts)
    max_count = max(counts.values())
    
    if unique_count == 4:
        return "シングル(ABCD)", "4つの数字が全て異なる", 24
    elif unique_count == 3:
        return "ダブル(AABC)", "1つの数字が2回出現", 12
    elif unique_count == 2:
        if max_count == 3:
            return "トリプル(AAAB)", "1つの数字が3回出現", 4
        else:
            return "ダブルダブル(AABB)", "2つの数字が2回ずつ", 6
    elif unique_count == 1:
        return "クアッド(AAAA)", "全て同じ数字 (ゾロ目)", 1
    else:
        return "不明", "不明", 0


def get_box_type(number: str) -> Tuple[str, int]:
    """
    ボックスタイプとカバー範囲を判定 (簡易版)
    
    Args:
        number: 4桁の数字文字列
    
    Returns:
        (タイプ表記, カバー範囲)
        
    Examples:
        >>> get_box_type("1234")
        ('シングル(ABCD)', 24)
        >>> get_box_type("1123")
        ('ダブル(AABC)', 12)
    """
    name, _, coverage = get_box_type_info(number)
    return name, coverage
