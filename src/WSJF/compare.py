"""Compare values using various operators.

This module provides functions to compare values using binary, ternary, and string case operators.
"""

from WSJF.enums import BinaryCompOp, StringCaseOp, TernaryCompOp


def compare_binary[T: (str, float)](value: T, limit: T, operator: BinaryCompOp) -> bool:
    """Compare a value against a single limit.

    * `T`: `str | float`

    Example:
        >>> # Check if 1.2 < 1.5
        >>> compare_binary(1.2, 1.5, TernaryCompOp.GREATER_THAN_OR_LESS_THAN)
        True

    """
    match operator:
        case BinaryCompOp.EQUAL:
            return value == limit
        case BinaryCompOp.NOT_EQUAL:
            return value != limit
        case BinaryCompOp.GREATER_THAN:
            return value > limit
        case BinaryCompOp.GREATER_OR_EQUAL:
            return value >= limit
        case BinaryCompOp.LESS_THAN:
            return value < limit
        case BinaryCompOp.LESS_OR_EQUAL:
            return value <= limit
        case _:
            errmsg = f"Unsupported operator: {operator}"
            raise ValueError(errmsg)


def compare_ternary(value: float, low_limit: float, high_limit: float, operator: TernaryCompOp) -> bool:
    """Compare a value with two limits using the specified ternary operator.

    Example:
        >>> # Check if 1 < 5 < 10
        >>> compare_ternary(5, 1, 10, TernaryCompOp.GREATER_THAN_OR_LESS_THAN)
        True
        >>> compare_ternary(5, 1, 10, TernaryCompOp.GREATER_EQUAL_OR_LESS_EQUAL)
        True

    """
    match operator:
        case TernaryCompOp.GREATER_THAN_OR_LESS_THAN:
            # (low_limit, high_limit)
            return low_limit < value < high_limit
        case TernaryCompOp.GREATER_EQUAL_OR_LESS_EQUAL:
            # [low_limit, high_limit]
            return low_limit <= value <= high_limit
        case TernaryCompOp.GREATER_EQUAL_OR_LESS_THAN:
            # [low_limit, high_limit)
            return low_limit <= value < high_limit
        case TernaryCompOp.GREATER_THAN_OR_LESS_EQUAL:
            # (low_limit, high_limit]
            return low_limit < value <= high_limit
        case TernaryCompOp.LESS_THAN_OR_GREATER_THAN:
            # I'm not entirely sure if this is what they mean.
            # My interpretation is that value is not in the interval [low_limit, high_limit]
            return value < low_limit or high_limit < value
        case TernaryCompOp.LESS_EQUAL_OR_GREATER_EQUAL:
            # value not in interval (low_limit, high_limit)
            return value <= low_limit or high_limit <= value
        case TernaryCompOp.LESS_EQUAL_OR_GREATER_THAN:
            # value not in interval (low_limit, high_limit]
            return value <= low_limit or high_limit < value
        case TernaryCompOp.LESS_THAN_OR_GREATER_EQUAL:
            # value not in interval [low_limit, high_limit)
            return value < low_limit or high_limit <= value
        case _:
            errmsg = f"Unsupported operator: {operator}"
            raise ValueError(errmsg)


def compare_case(value: str, limit: str, operator: StringCaseOp) -> bool:
    """Compare two strings using the specified case-sensitive operator.

    Example:
        >>> check_case("hello", "Hello", StringCaseOp.CASE_SENSITIVE)
        False
        >>> check_case("hello", "Hello", StringCaseOp.IGNORECASE)
        True

    """
    match operator:
        case StringCaseOp.CASE_SENSITIVE:
            return value == limit
        case StringCaseOp.IGNORECASE:
            return value.lower() == limit.lower()
        case _:
            errmsg = f"Unsupported operator: {operator}"
            raise ValueError(errmsg)
