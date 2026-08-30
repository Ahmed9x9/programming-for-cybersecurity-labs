"""Conditions, loops, functions, and small algorithmic scenarios."""

from __future__ import annotations

import argparse
import math
import string
from collections.abc import Callable
from enum import StrEnum

ATTACKS = ["Phishing", "Spoofing", "DDoS", "SQL injection", "Password attack", "Hacktivism"]
SPECIAL_CHARACTERS = set("!@#$%^&*()-+")


class PasswordStrength(StrEnum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"


def numbered_attacks(attacks: list[str] | None = None) -> list[str]:
    return [
        f"The attack number {index} is: {name}" for index, name in enumerate(attacks or ATTACKS, 1)
    ]


def classify_password(password: str) -> PasswordStrength:
    checks = (
        any(character.islower() for character in password),
        any(character.isupper() for character in password),
        any(character in SPECIAL_CHARACTERS for character in password),
        len(password) >= 8,
        any(character.isdigit() for character in password),
    )
    score = sum(checks)
    if score == len(checks):
        return PasswordStrength.STRONG
    if score >= 3:
        return PasswordStrength.MODERATE
    return PasswordStrength.WEAK


def xor_cipher(text: str, key: int) -> str:
    """Encrypt or decrypt text by XORing every Unicode code point with the same key."""
    if not 0 <= key <= 255:
        raise ValueError("key must be an integer between 0 and 255")
    return "".join(chr(ord(character) ^ key) for character in text)


def xor_display(text: str) -> str:
    """Return non-printable encrypted text in an unambiguous escaped form."""
    return "".join(
        character if character in string.printable[:-5] else f"\\x{ord(character):02x}"
        for character in text
    )


def classify_year(year: int) -> str:
    if year < 1582:
        return "Not within the Gregorian calendar period"
    if year % 4 != 0:
        return "Common year"
    if year % 100 != 0:
        return "Leap year"
    return "Leap year" if year % 400 == 0 else "Common year"


def guess_result(guess: int, secret_number: int = 777) -> tuple[bool, str]:
    if guess == secret_number:
        return True, f"{guess}\nWell done, muggle! You are free now."
    return False, "Ha ha! You're stuck in my loop!"


def play_secret_number(
    secret_number: int = 777,
    input_function: Callable[[str], str] = input,
    output_function: Callable[[str], None] = print,
) -> int:
    """Prompt in a while loop until the secret number is entered; return attempt count."""
    attempts = 0
    while True:
        try:
            guess = int(input_function("Enter an integer number: "))
        except ValueError:
            output_function("Please enter a valid integer.")
            continue
        attempts += 1
        correct, message = guess_result(guess, secret_number)
        output_function(message)
        if correct:
            return attempts


def pyramid_height(blocks: int) -> int:
    if blocks < 0:
        raise ValueError("blocks cannot be negative")
    return (math.isqrt(8 * blocks + 1) - 1) // 2


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--password", default="GoodJob1!")
    parser.add_argument("--plaintext", default="Cyber security")
    parser.add_argument("--key", type=int, default=23)
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--blocks", type=int, default=20)
    parser.add_argument("--play-secret-number", action="store_true")
    args = parser.parse_args()

    print(*numbered_attacks(), sep="\n")
    print("Password strength:", classify_password(args.password))
    ciphertext = xor_cipher(args.plaintext, args.key)
    print("XOR ciphertext:", xor_display(ciphertext))
    print("XOR decrypted:", xor_cipher(ciphertext, args.key))
    print("Year:", classify_year(args.year))
    print("Pyramid height:", pyramid_height(args.blocks))
    if args.play_secret_number:
        play_secret_number()


if __name__ == "__main__":
    main()
