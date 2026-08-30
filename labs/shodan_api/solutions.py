"""Safe Shodan host-information and search examples."""

from __future__ import annotations

import argparse
import os
import socket
from typing import Any, Protocol

import shodan


class ShodanClient(Protocol):
    def host(self, ip_address: str) -> dict[str, Any]: ...

    def search(self, query: str) -> dict[str, Any]: ...


def require_live(live: bool) -> None:
    if not live:
        raise PermissionError("Shodan requests require explicit live mode")


def api_key_from_environment() -> str:
    api_key = os.environ.get("SHODAN_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("SHODAN_API_KEY is not set")
    return api_key


def resolve_target(target: str) -> str:
    return socket.gethostbyname(target)


def host_geolocation(client: ShodanClient, ip_address: str) -> dict[str, object]:
    host = client.host(ip_address)
    return {
        "ip_address": ip_address,
        "country": host.get("country_name", "N/A"),
        "city": host.get("city", "N/A"),
        "latitude": host.get("latitude", "N/A"),
        "longitude": host.get("longitude", "N/A"),
        "organization": host.get("org", "N/A"),
    }


def host_ports(client: ShodanClient, ip_address: str) -> list[int]:
    host = client.host(ip_address)
    return sorted({int(port) for port in host.get("ports", [])})


def search_hosts(client: ShodanClient, query: str, limit: int = 10) -> tuple[int, list[str]]:
    if not query.strip() or not 1 <= limit <= 100:
        raise ValueError("provide a query and a limit between 1 and 100")
    results = client.search(query)
    addresses = [
        str(match["ip_str"])
        for match in results.get("matches", [])
        if match.get("ip_str") is not None
    ][:limit]
    return int(results.get("total", len(addresses))), addresses


def friendly_api_error(error: shodan.APIError) -> str:
    message = str(error)
    if "403" in message or "access denied" in message.casefold():
        return "Shodan denied this operation; the API plan may not include search access."
    return f"Shodan API error: {message}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    host_parser = subparsers.add_parser("host")
    host_parser.add_argument("--target", required=True)
    host_parser.add_argument("--live", action="store_true")

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("--query", required=True)
    search_parser.add_argument("--limit", type=int, default=10)
    search_parser.add_argument("--live", action="store_true")

    args = parser.parse_args()
    require_live(args.live)
    client = shodan.Shodan(api_key_from_environment())
    try:
        if args.command == "host":
            ip_address = resolve_target(args.target)
            print("Geolocation:", host_geolocation(client, ip_address))
            print("Indexed ports:", host_ports(client, ip_address))
        else:
            total, addresses = search_hosts(client, args.query, args.limit)
            print("Total results:", total)
            print("Example addresses:", *addresses, sep="\n")
    except shodan.APIError as error:
        parser.exit(1, friendly_api_error(error) + "\n")


if __name__ == "__main__":
    main()
