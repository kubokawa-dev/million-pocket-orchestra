"""
入力検証ユーティリティ

予測システムへの入力validationを行います。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional
import re


@dataclass
class ValidationResult:
    """検証結果"""
    is_valid: bool
    error_message: Optional[str] = None

    @classmethod
    def ok(cls) -> "ValidationResult":
        return cls(is_valid=True)

    @classmethod
    def error(cls, message: str) -> "ValidationResult":
        return cls(is_valid=False, error_message=message)


def validate_draw_number(draw_number: int) -> ValidationResult:
    """
    抽選回番号の検証
    
    Args:
        draw_number: 検証する抽選回番号
        
    Returns:
        ValidationResult: 検証結果
    """
    if not isinstance(draw_number, int):
        return ValidationResult.error(f"draw_number must be an integer, got {type(draw_number)}")
    
    if draw_number <= 0:
        return ValidationResult.error(f"draw_number must be positive, got {draw_number}")
    
    if draw_number > 99999:
        return ValidationResult.error(f"draw_number too large: {draw_number}")
    
    return ValidationResult.ok()


def validate_lottery_type(lottery_type: str) -> ValidationResult:
    """
    宝くじ種類の検証
    
    Args:
        lottery_type: 検証する宝くじ種類
        
    Returns:
        ValidationResult: 検証結果
    """
    valid_types = {'numbers3', 'numbers4', 'loto6'}
    
    if lottery_type not in valid_types:
        return ValidationResult.error(
            f"Invalid lottery_type: {lottery_type}. Must be one of {valid_types}"
        )
    
    return ValidationResult.ok()


def validate_numbers3_prediction(numbers: str) -> ValidationResult:
    """
    Numbers3の予測番号の検証
    
    Args:
        numbers: 3桁の数字文字列
        
    Returns:
        ValidationResult: 検証結果
    """
    if not isinstance(numbers, str):
        return ValidationResult.error(f"Prediction must be a string, got {type(numbers)}")
    
    if not re.match(r'^\d{3}$', numbers):
        return ValidationResult.error(
            f"Invalid Numbers3 format: '{numbers}'. Must be 3 digits (e.g., '123')"
        )
    
    return ValidationResult.ok()


def validate_numbers4_prediction(numbers: str) -> ValidationResult:
    """
    Numbers4の予測番号の検証
    
    Args:
        numbers: 4桁の数字文字列
        
    Returns:
        ValidationResult: 検証結果
    """
    if not isinstance(numbers, str):
        return ValidationResult.error(f"Prediction must be a string, got {type(numbers)}")
    
    if not re.match(r'^\d{4}$', numbers):
        return ValidationResult.error(
            f"Invalid Numbers4 format: '{numbers}'. Must be 4 digits (e.g., '1234')"
        )
    
    return ValidationResult.ok()


def validate_loto6_prediction(numbers: str) -> ValidationResult:
    """
    Loto6の予測番号の検証
    
    Args:
        numbers: 6つの数字をカンマ区切りで指定した文字列
        
    Returns:
        ValidationResult: 検証結果
    """
    if not isinstance(numbers, str):
        return ValidationResult.error(f"Prediction must be a string, got {type(numbers)}")
    
    parts = numbers.replace(' ', '').split(',')
    
    if len(parts) != 6:
        return ValidationResult.error(
            f"Invalid Loto6 format: '{numbers}'. Must be 6 numbers separated by commas"
        )
    
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return ValidationResult.error(
            f"Invalid Loto6 format: '{numbers}'. All values must be integers"
        )
    
    for i, num in enumerate(nums):
        if num < 1 or num > 43:
            return ValidationResult.error(
                f"Invalid Loto6 number: {num} at position {i+1}. Must be between 1 and 43"
            )
    
    if len(set(nums)) != 6:
        return ValidationResult.error(
            f"Invalid Loto6 format: '{numbers}'. All numbers must be unique"
        )
    
    return ValidationResult.ok()


def validate_prediction(
    numbers: str,
    lottery_type: Literal['numbers3', 'numbers4', 'loto6']
) -> ValidationResult:
    """
    宝くじ種類に応じた予測番号の検証
    
    Args:
        numbers: 予測番号
        lottery_type: 宝くじ種類
        
    Returns:
        ValidationResult: 検証結果
    """
    type_check = validate_lottery_type(lottery_type)
    if not type_check.is_valid:
        return type_check
    
    if lottery_type == 'numbers3':
        return validate_numbers3_prediction(numbers)
    elif lottery_type == 'numbers4':
        return validate_numbers4_prediction(numbers)
    elif lottery_type == 'loto6':
        return validate_loto6_prediction(numbers)
    
    return ValidationResult.error(f"Unknown lottery type: {lottery_type}")


def validate_limit(limit: int, max_limit: int = 1000) -> ValidationResult:
    """
    limitパラメータの検証
    
    Args:
        limit: 検証するlimit値
        max_limit: 最大値
        
    Returns:
        ValidationResult: 検証結果
    """
    if not isinstance(limit, int):
        return ValidationResult.error(f"limit must be an integer, got {type(limit)}")
    
    if limit <= 0:
        return ValidationResult.error(f"limit must be positive, got {limit}")
    
    if limit > max_limit:
        return ValidationResult.error(f"limit must not exceed {max_limit}, got {limit}")
    
    return ValidationResult.ok()
