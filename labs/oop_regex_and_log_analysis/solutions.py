"""Polymorphism, regular-expression, log-analysis, and class-method exercises."""

from __future__ import annotations

import argparse
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from pathlib import Path

LOG_PATTERN = re.compile(
    r"^(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^]]+)] "
    r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" '
    r'(?P<status>\d{3}) (?P<size>\S+) "(?P<referrer>[^"]*)" "(?P<agent>[^"]*)"$'
)
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$")


@dataclass(frozen=True)
class LogEntry:
    ip_address: str
    timestamp: str
    method: str
    path: str
    status: int
    referrer: str


def parse_log_line(line: str) -> LogEntry:
    match = LOG_PATTERN.fullmatch(line.rstrip("\n"))
    if match is None:
        raise ValueError("line is not valid Apache combined-log data")
    return LogEntry(
        ip_address=match["ip"],
        timestamp=match["timestamp"],
        method=match["method"],
        path=match["path"],
        status=int(match["status"]),
        referrer=match["referrer"],
    )


def read_entries(path: Path) -> list[LogEntry]:
    with path.open(encoding="utf-8") as log_file:
        return [parse_log_line(line) for line in log_file if line.strip()]


class LogParser(ABC):
    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path

    @abstractmethod
    def parse(self) -> object:
        """Parse and return one view of the log."""


class IPCountParser(LogParser):
    def __init__(self, log_path: Path, ip_address: str) -> None:
        super().__init__(log_path)
        self.ip_address = ip_address

    def parse(self) -> int:
        return sum(entry.ip_address == self.ip_address for entry in read_entries(self.log_path))


class WebsiteParser(LogParser):
    def parse(self) -> list[str]:
        return [entry.path for entry in read_entries(self.log_path)]


def run_parser(parser: LogParser) -> object:
    """Call the matching parse implementation through a common interface."""
    return parser.parse()


def find_events_at(path: Path, timestamp: str) -> list[LogEntry]:
    timestamp_pattern = re.compile(re.escape(timestamp))
    return [entry for entry in read_entries(path) if timestamp_pattern.fullmatch(entry.timestamp)]


def is_valid_email(address: str) -> bool:
    return EMAIL_PATTERN.fullmatch(address.strip()) is not None


def valid_emails(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as email_file:
        return [line.strip() for line in email_file if is_valid_email(line.strip())]


@dataclass(frozen=True)
class Person:
    name: str
    age: int

    @classmethod
    def from_birth_date(cls, name: str, birth_date: date, today: date | None = None) -> Person:
        today = today or date.today()
        if birth_date > today:
            raise ValueError("birth date cannot be in the future")
        had_birthday = (today.month, today.day) >= (birth_date.month, birth_date.day)
        return cls(name=name, age=today.year - birth_date.year - (not had_birthday))

    @staticmethod
    def is_adult(age: int) -> bool:
        return age >= 18


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--emails", type=Path, required=True)
    parser.add_argument("--ip", default="192.0.2.10")
    args = parser.parse_args()

    print("IP occurrences:", run_parser(IPCountParser(args.log, args.ip)))
    print("Requested paths:", run_parser(WebsiteParser(args.log)))
    print("Timestamp events:", len(find_events_at(args.log, "03/Feb/2016:00:01:07 +0300")))
    print("Valid emails:", valid_emails(args.emails))
    person = Person.from_birth_date("Ahmed", date(2000, 1, 1))
    print(f"{person.name}: age={person.age}, adult={person.is_adult(person.age)}")


if __name__ == "__main__":
    main()
