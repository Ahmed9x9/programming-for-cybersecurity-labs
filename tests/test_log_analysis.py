from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from labs.oop_regex_and_log_analysis.solutions import (
    IPCountParser,
    Person,
    WebsiteParser,
    find_events_at,
    is_valid_email,
    parse_log_line,
    run_parser,
    valid_emails,
)

DATA_DIRECTORY = Path("labs/oop_regex_and_log_analysis/data")
LOG_PATH = DATA_DIRECTORY / "sample_apache_access.log"
EMAIL_PATH = DATA_DIRECTORY / "sample_emails.txt"


def test_apache_log_parsers() -> None:
    entry = parse_log_line(LOG_PATH.read_text(encoding="utf-8").splitlines()[0])
    assert entry.ip_address == "192.0.2.10"
    assert entry.path == "/index.html"
    assert run_parser(IPCountParser(LOG_PATH, "192.0.2.10")) == 3
    assert run_parser(WebsiteParser(LOG_PATH)) == [
        "/index.html",
        "/login",
        "/login",
        "/dashboard",
        "/logout",
    ]
    events = find_events_at(LOG_PATH, "03/Feb/2016:00:01:07 +0300")
    assert len(events) == 2
    with pytest.raises(ValueError):
        parse_log_line("not a log line")


def test_email_validation() -> None:
    assert is_valid_email("student@example.test")
    assert is_valid_email("security.team+alerts@example.test")
    assert not is_valid_email("missing-at.example.test")
    assert not is_valid_email("bad@domain")
    assert valid_emails(EMAIL_PATH) == [
        "student@example.test",
        "security.team+alerts@example.test",
        "name.surname@subdomain.example.test",
    ]


def test_person_age_calculation_and_adult_check() -> None:
    person = Person.from_birth_date("Student", date(2000, 9, 1), date(2025, 8, 31))
    assert person.age == 24
    assert Person.is_adult(person.age)
    assert not Person.is_adult(17)
    with pytest.raises(ValueError):
        Person.from_birth_date("Future", date(2030, 1, 1), date(2025, 1, 1))
