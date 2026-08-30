from __future__ import annotations

import math

import pytest

from labs.collections.solutions import ArpTable, port_list_exercise
from labs.control_flow_and_functions.solutions import (
    PasswordStrength,
    classify_password,
    classify_year,
    guess_result,
    numbered_attacks,
    play_secret_number,
    pyramid_height,
    xor_cipher,
)
from labs.python_basics.solutions import (
    assign_same_value,
    degrees_to_radians,
    format_without_decimal_places,
    generate_university_email,
    password_issues,
    repeat_suffix,
    replace_repeated_letter,
    service_port_lines,
)


def test_python_basics_happy_paths() -> None:
    assert assign_same_value("Cyber security") == ("Cyber security",) * 3
    assert replace_repeated_letter("ADVANTAGE") == "ADV$NT$GE"
    assert replace_repeated_letter("CYBER") == "CYBER"
    assert repeat_suffix("PYTHON") == "ONONONON"
    assert format_without_decimal_places([3.225, -12.333]) == ["3", "-12"]
    assert math.isclose(degrees_to_radians(90), math.pi / 2)
    assert generate_university_email("Ahmed", "Al-Shaikh") == "AhAl-Shaikh@iau.edu.sa"
    assert service_port_lines() == ["HTTP: 80", "SSH: 22", "FTP: 21", "SNMP: 161"]


def test_python_basics_validation() -> None:
    with pytest.raises(ValueError):
        repeat_suffix("A", suffix_length=2)
    with pytest.raises(ValueError):
        generate_university_email("A", "Student")
    assert password_issues("ahmed", "Secure@403", "Secure@403") == []
    issues = password_issues("ahmed", "ahmed", "different")
    assert len(issues) == 6


def test_collection_exercises() -> None:
    results = port_list_exercise()
    assert results["initial_count"] == 5
    assert results["ports_before_53"] == 3
    assert results["reversed_ports"] == [443, 53, 23, 21]
    assert results["count_53"] == 2
    assert results["merged_after_clear"] == []
    assert results["contains_433"] is False

    table = ArpTable()
    assert table.lookup("192.0.2.20") == "02:00:00:00:00:20"
    original = table.simulate_spoof("192.0.2.20", "02:ff:ff:ff:ff:ff")
    assert original == "02:00:00:00:00:20"
    assert table.lookup("192.0.2.20") == "02:ff:ff:ff:ff:ff"
    deleted_ip, _ = table.delete_first()
    assert deleted_ip == "192.0.2.10"


def test_control_flow_and_functions() -> None:
    assert numbered_attacks()[0] == "The attack number 1 is: Phishing"
    assert classify_password("GoodJob1!") is PasswordStrength.STRONG
    assert classify_password("GoodJob1") is PasswordStrength.MODERATE
    assert classify_password("short") is PasswordStrength.WEAK

    plaintext = "Cyber security"
    ciphertext = xor_cipher(plaintext, 23)
    assert ciphertext != plaintext
    assert xor_cipher(ciphertext, 23) == plaintext
    with pytest.raises(ValueError):
        xor_cipher("text", 256)

    assert classify_year(2000) == "Leap year"
    assert classify_year(1900) == "Common year"
    assert classify_year(2023) == "Common year"
    assert classify_year(1500) == "Not within the Gregorian calendar period"
    assert guess_result(777)[0] is True
    assert guess_result(1)[0] is False
    guesses = iter(["not-an-integer", "1", "777"])
    messages: list[str] = []
    attempts = play_secret_number(
        input_function=lambda prompt: next(guesses), output_function=messages.append
    )
    assert attempts == 2
    assert messages[-1].endswith("You are free now.")
    assert pyramid_height(20) == 5
    assert pyramid_height(2) == 1
    with pytest.raises(ValueError):
        pyramid_height(-1)
