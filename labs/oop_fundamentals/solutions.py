"""Bank-account and prime-number class exercises."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class BankAccount:
    holder_name: str
    account_number: str
    balance: Decimal = Decimal("0.00")

    def __post_init__(self) -> None:
        self.balance = Decimal(self.balance)
        if not self.holder_name.strip() or not self.account_number.strip():
            raise ValueError("holder name and account number are required")
        if self.balance < 0:
            raise ValueError("initial balance cannot be negative")

    def deposit(self, amount: Decimal) -> Decimal:
        amount = Decimal(amount)
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: Decimal) -> Decimal:
        amount = Decimal(amount)
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount
        return self.balance

    def dump(self) -> dict[str, str]:
        return {
            "holder_name": self.holder_name,
            "account_number": self.account_number,
            "balance": f"{self.balance:.2f}",
        }


class PrimeNumberChecker:
    def __init__(self, number: int) -> None:
        self.number = number

    def factors(self) -> list[int]:
        if self.number < 1:
            return []
        return [
            candidate for candidate in range(1, self.number + 1) if self.number % candidate == 0
        ]

    def is_prime(self) -> bool:
        return self.number > 1 and self.factors() == [1, self.number]

    def result(self) -> str:
        if self.is_prime():
            return f"{self.number} is prime"
        return f"{self.number} is not prime; factors: {self.factors()}"


class DetailedPrimeNumberChecker(PrimeNumberChecker):
    """Child class used to exercise inherited methods."""

    def result(self) -> str:
        classification = "prime" if self.is_prime() else "not prime"
        return f"Number: {self.number}; classification: {classification}; factors: {self.factors()}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--number", type=int, default=28)
    args = parser.parse_args()

    account = BankAccount("Ahmed Al-Shaikh", "CYS403", Decimal("100.00"))
    account.deposit(Decimal("50.00"))
    account.withdraw(Decimal("25.00"))
    print("Account:", account.dump())
    print(DetailedPrimeNumberChecker(args.number).result())


if __name__ == "__main__":
    main()
