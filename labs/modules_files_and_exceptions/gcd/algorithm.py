"""Euclidean algorithm implementation."""


def gcd(first: int, second: int) -> int:
    """Return the non-negative greatest common divisor of two integers."""
    first, second = abs(first), abs(second)
    while second:
        first, second = second, first % second
    return first
