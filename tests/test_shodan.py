from __future__ import annotations

from typing import Any

import pytest
import shodan

from labs.shodan_api.solutions import (
    api_key_from_environment,
    friendly_api_error,
    host_geolocation,
    host_ports,
    require_live,
    search_hosts,
)


class FakeShodanClient:
    def host(self, ip_address: str) -> dict[str, Any]:
        return {
            "ip_str": ip_address,
            "country_name": "Example Country",
            "city": "Example City",
            "latitude": 1.25,
            "longitude": 2.5,
            "org": "Example Organization",
            "ports": [443, 22, 80, 22],
        }

    def search(self, query: str) -> dict[str, Any]:
        assert query == "port:21 Anonymous user logged in"
        return {
            "total": 3,
            "matches": [
                {"ip_str": "192.0.2.10"},
                {"ip_str": "198.51.100.20"},
                {"ip_str": "203.0.113.30"},
            ],
        }


def test_host_and_search_result_processing() -> None:
    client = FakeShodanClient()
    location = host_geolocation(client, "192.0.2.10")
    assert location["city"] == "Example City"
    assert location["organization"] == "Example Organization"
    assert host_ports(client, "192.0.2.10") == [22, 80, 443]
    total, addresses = search_hosts(client, "port:21 Anonymous user logged in", limit=2)
    assert total == 3
    assert addresses == ["192.0.2.10", "198.51.100.20"]


def test_key_and_live_guards(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SHODAN_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        api_key_from_environment()
    monkeypatch.setenv("SHODAN_API_KEY", "example-test-value")
    assert api_key_from_environment() == "example-test-value"
    with pytest.raises(PermissionError):
        require_live(False)
    require_live(True)


def test_api_error_message_explains_free_plan_limit() -> None:
    message = friendly_api_error(shodan.APIError("Access denied (403 Forbidden)"))
    assert "plan" in message.casefold()
