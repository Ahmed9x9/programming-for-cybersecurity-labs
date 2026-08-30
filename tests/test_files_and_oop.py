from __future__ import annotations

from decimal import Decimal

import pytest

from labs.modules_files_and_exceptions.gcd import gcd
from labs.modules_files_and_exceptions.solutions import (
    add_lists,
    append_text,
    delete_file,
    read_line,
    read_text,
    safe_read,
    write_odd_even_files,
)
from labs.oop_fundamentals.solutions import (
    BankAccount,
    DetailedPrimeNumberChecker,
    PrimeNumberChecker,
)


def test_gcd_and_list_addition() -> None:
    assert gcd(252, 105) == 21
    assert gcd(-12, 8) == 4
    assert gcd(0, 0) == 0
    assert add_lists([1, 2, 3], [4, 5, 6]) == [5, 7, 9]
    with pytest.raises(ValueError):
        add_lists([1], [1, 2])


def test_file_exercises_use_the_requested_directory(tmp_path) -> None:
    odd_path, even_path = write_odd_even_files(tmp_path, maximum=10)
    assert read_text(even_path) == "2\n4\n6\n8\n10\n"
    assert read_line(odd_path, 5) == "9"

    append_text(odd_path, "This is a file of odd numbers\n")
    assert read_text(odd_path).endswith("This is a file of odd numbers\n")
    assert delete_file(even_path) is True
    assert delete_file(even_path) is False
    assert safe_read(even_path) == (None, "even.txt does not exist")
    with pytest.raises(IndexError):
        read_line(odd_path, 99)


def test_bank_account_state_and_validation() -> None:
    account = BankAccount("Ahmed", "CYS403", Decimal("100.00"))
    assert account.deposit(Decimal("25.50")) == Decimal("125.50")
    assert account.withdraw(Decimal("20.50")) == Decimal("105.00")
    assert account.dump()["balance"] == "105.00"
    with pytest.raises(ValueError, match="insufficient"):
        account.withdraw(Decimal("1000"))
    with pytest.raises(ValueError):
        account.deposit(Decimal("0"))


@pytest.mark.parametrize(
    ("number", "expected"),
    [(0, False), (1, False), (2, True), (13, True), (28, False)],
)
def test_prime_number_checker(number: int, expected: bool) -> None:
    checker = PrimeNumberChecker(number)
    assert checker.is_prime() is expected
    assert DetailedPrimeNumberChecker(number).is_prime() is expected
    if number == 28:
        assert checker.factors() == [1, 2, 4, 7, 14, 28]
