from __future__ import annotations

import pytest

from labs.concurrency.solutions import (
    ip_range,
    is_perfect,
    perfect_numbers,
    perfect_numbers_parallel,
    ping_command,
    ping_host,
    ping_range,
    run_sleeping_threads,
)


def test_sleeping_threads_report_both_states() -> None:
    messages = run_sleeping_threads(count=3, delay=0)
    assert len(messages) == 6
    for number in range(1, 4):
        assert f"Thread {number} is sleeping" in messages
        assert f"Thread {number} is awake" in messages


def test_cross_platform_ping_commands_and_range() -> None:
    assert ping_command("192.0.2.1", system="Windows") == [
        "ping",
        "-n",
        "1",
        "-w",
        "1000",
        "192.0.2.1",
    ]
    assert ping_command("192.0.2.1", system="Linux") == [
        "ping",
        "-c",
        "1",
        "-W",
        "1",
        "192.0.2.1",
    ]
    assert ip_range("192.0.2.1", "192.0.2.3") == ["192.0.2.1", "192.0.2.2", "192.0.2.3"]
    with pytest.raises(ValueError):
        ip_range("192.0.2.3", "192.0.2.1")


def test_ping_requires_live_and_supports_an_injected_checker() -> None:
    with pytest.raises(PermissionError):
        ping_host("192.0.2.1")
    with pytest.raises(PermissionError):
        ping_range("192.0.2.1", "192.0.2.2")

    def fake_checker(host: str, timeout: float, *, live: bool) -> bool:
        assert timeout == 0.5
        assert live
        return host.endswith("1")

    assert ping_range(
        "192.0.2.1",
        "192.0.2.2",
        timeout=0.5,
        live=True,
        checker=fake_checker,
    ) == {"192.0.2.1": True, "192.0.2.2": False}


def test_perfect_numbers_sequential_and_parallel() -> None:
    assert is_perfect(6)
    assert is_perfect(28)
    assert not is_perfect(12)
    assert perfect_numbers(30) == [6, 28]
    assert perfect_numbers_parallel(30, workers=2) == [6, 28]
