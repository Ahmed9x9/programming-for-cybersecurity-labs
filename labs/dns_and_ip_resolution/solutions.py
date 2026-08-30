"""Socket methods for resolving domains, IP addresses, services, and ports."""

from __future__ import annotations

import argparse
import ipaddress
import socket
from dataclasses import dataclass


def is_loopback_target(host: str) -> bool:
    if host.casefold() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def require_remote_permission(host: str, live: bool) -> None:
    if not live and not is_loopback_target(host):
        raise PermissionError("external network operations require explicit live mode")


@dataclass(frozen=True)
class DomainInformation:
    hostname: str
    primary_address: str
    aliases: list[str]
    addresses: list[str]
    fully_qualified_name: str
    address_info: list[tuple[object, ...]]


def resolve_domain(host: str, *, live: bool = False) -> DomainInformation:
    require_remote_permission(host, live)
    primary = socket.gethostbyname(host)
    canonical, aliases, addresses = socket.gethostbyname_ex(host)
    return DomainInformation(
        hostname=canonical,
        primary_address=primary,
        aliases=aliases,
        addresses=addresses,
        fully_qualified_name=socket.getfqdn(host),
        address_info=socket.getaddrinfo(host, 80, proto=socket.IPPROTO_TCP),
    )


def reverse_lookup(ip_address: str, *, live: bool = False) -> tuple[str, list[str], list[str]]:
    require_remote_permission(ip_address, live)
    return socket.gethostbyaddr(ip_address)


def service_to_port(service_name: str, protocol: str | None = None) -> int:
    if protocol is None:
        return socket.getservbyname(service_name)
    return socket.getservbyname(service_name, protocol)


def port_to_service(port: int, protocol: str | None = None) -> str:
    if protocol is None:
        return socket.getservbyport(port)
    return socket.getservbyport(port, protocol)


def scan_tcp_ports(
    host: str, ports: list[int], *, timeout: float = 1.0, live: bool = False
) -> dict[int, bool]:
    require_remote_permission(host, live)
    if timeout <= 0 or any(not 1 <= port <= 65535 for port in ports):
        raise ValueError("use a positive timeout and ports between 1 and 65535")
    results: dict[int, bool] = {}
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(timeout)
            results[port] = client.connect_ex((host, port)) == 0
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    domain_parser = subparsers.add_parser("domain")
    domain_parser.add_argument("--host", required=True)
    domain_parser.add_argument("--live", action="store_true")

    reverse_parser = subparsers.add_parser("reverse")
    reverse_parser.add_argument("--ip", required=True)
    reverse_parser.add_argument("--live", action="store_true")

    scan_parser = subparsers.add_parser("scan")
    scan_parser.add_argument("--host", required=True)
    scan_parser.add_argument("--ports", type=int, nargs="+", required=True)
    scan_parser.add_argument("--timeout", type=float, default=1.0)
    scan_parser.add_argument("--live", action="store_true")

    service_parser = subparsers.add_parser("service")
    group = service_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--name")
    group.add_argument("--port", type=int)
    service_parser.add_argument("--protocol")

    args = parser.parse_args()
    if args.command == "domain":
        print(resolve_domain(args.host, live=args.live))
    elif args.command == "reverse":
        print(reverse_lookup(args.ip, live=args.live))
    elif args.command == "scan":
        for port, is_open in scan_tcp_ports(
            args.host, args.ports, timeout=args.timeout, live=args.live
        ).items():
            print(f"Port {port}: {'open' if is_open else 'closed'}")
    elif args.name:
        print(service_to_port(args.name, args.protocol))
    else:
        print(port_to_service(args.port, args.protocol))


if __name__ == "__main__":
    main()
