"""Corrected solutions for the introductory Python exercises."""

from __future__ import annotations

import argparse
import math
from collections.abc import Iterable

SERVICES: dict[str, int] = {"HTTP": 80, "SSH": 22, "FTP": 21, "SNMP": 161}


def assign_same_value(value: str) -> tuple[str, str, str]:
    """Return the result of assigning one value to three variables."""
    x = y = z = value
    return x, y, z


def replace_repeated_letter(word: str, letter: str = "A", replacement: str = "$") -> str:
    """Replace every occurrence of *letter* except its first occurrence."""
    if len(letter) != 1 or len(replacement) != 1:
        raise ValueError("letter and replacement must each contain one character")
    first_index = word.find(letter)
    if first_index == -1:
        return word
    return word[: first_index + 1] + word[first_index + 1 :].replace(letter, replacement)


def repeat_suffix(word: str, copies: int = 4, suffix_length: int = 2) -> str:
    """Repeat the final characters of a word a requested number of times."""
    if suffix_length <= 0 or suffix_length > len(word):
        raise ValueError("suffix_length must be between 1 and the word length")
    if copies < 0:
        raise ValueError("copies cannot be negative")
    return word[-suffix_length:] * copies


def format_without_decimal_places(values: Iterable[float]) -> list[str]:
    """Format floating-point values with no decimal places."""
    return [f"{value:.0f}" for value in values]


def degrees_to_radians(degrees: float) -> float:
    """Convert an angle from degrees to radians."""
    return math.radians(degrees)


def generate_university_email(first_name: str, last_name: str, domain: str = "iau.edu.sa") -> str:
    """Build an email from two first-name letters and the full family name."""
    first_name = first_name.strip()
    last_name = last_name.strip().replace(" ", "")
    domain = domain.strip().lower()
    if len(first_name) < 2 or not last_name or "." not in domain:
        raise ValueError("provide a two-letter first name, a last name, and a valid domain")
    local_part = first_name[:2].capitalize() + last_name[0].upper() + last_name[1:]
    return f"{local_part}@{domain}"


def password_issues(
    username: str, password: str, confirmation: str, minimum_length: int = 8
) -> list[str]:
    """Return every introductory password-policy problem that was detected."""
    issues: list[str] = []
    if len(password) < minimum_length:
        issues.append(f"password must contain at least {minimum_length} characters")
    if username and username.casefold() in password.casefold():
        issues.append("password must not contain the username")
    if not any(character.isupper() for character in password):
        issues.append("password must contain an uppercase letter")
    if not any(character.isdigit() for character in password):
        issues.append("password must contain a number")
    if not any(character in "@$" for character in password):
        issues.append("password must contain @ or $")
    if password != confirmation:
        issues.append("password and confirmation do not match")
    return issues


def service_port_lines(services: dict[str, int] | None = None) -> list[str]:
    """Format service names and port numbers."""
    return [f"{name}: {port}" for name, port in (services or SERVICES).items()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first-name", default="Ahmed")
    parser.add_argument("--last-name", default="Al-Shaikh")
    parser.add_argument("--username", default="ahmed")
    parser.add_argument("--password", default="Secure@403")
    args = parser.parse_args()

    print("Shared assignment:", assign_same_value("Cyber security"))
    print("Repeated-letter replacement:", replace_repeated_letter("ADVANTAGE"))
    print("Repeated suffix:", repeat_suffix("PYTHON"))
    print("Formatted numbers:", *format_without_decimal_places([3.225, -12.333]))
    print("90 degrees in radians:", degrees_to_radians(90))
    print("Generated email:", generate_university_email(args.first_name, args.last_name))
    print(
        "Password issues:", password_issues(args.username, args.password, args.password) or "none"
    )
    print(*service_port_lines(), sep="\n")


if __name__ == "__main__":
    main()
