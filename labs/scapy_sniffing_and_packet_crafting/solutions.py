"""Scapy live sniffing and explicit ICMP/ARP packet construction."""

from __future__ import annotations

import argparse
import ipaddress
import re
from collections.abc import Callable

from scapy.all import ARP, ICMP, IP, Ether, Raw, sniff, srp1
from scapy.packet import Packet

HOSTNAME_PATTERN = re.compile(r"^[A-Za-z0-9.-]+$")


def require_live(live: bool) -> None:
    if not live:
        raise PermissionError("capture and transmission require explicit live mode")


def validate_host(value: str) -> str:
    try:
        ipaddress.ip_address(value)
    except ValueError:
        if not HOSTNAME_PATTERN.fullmatch(value) or ".." in value:
            raise ValueError("target must be an IP address or a simple hostname") from None
    return value


def build_icmp_packet(target: str, payload: bytes = b"CYS403 ICMP exercise") -> Packet:
    return Ether() / IP(dst=validate_host(target)) / ICMP() / Raw(payload)


def build_arp_request(target_ip: str) -> Packet:
    ipaddress.ip_address(target_ip)
    return Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip, op=1)


def packet_details(packet: Packet) -> str:
    return str(packet.show(dump=True))


def capture_host(
    host: str,
    interface: str,
    *,
    count: int = 10,
    timeout: float = 30.0,
    live: bool = False,
    capture: Callable[..., object] = sniff,
) -> object:
    require_live(live)
    if not interface.strip() or count < 1 or timeout <= 0:
        raise ValueError("provide an interface, positive count, and positive timeout")
    return capture(
        filter=f"host {validate_host(host)}",
        iface=interface,
        count=count,
        timeout=timeout,
        store=True,
    )


def send_for_reply(
    packet: Packet,
    interface: str,
    *,
    timeout: float = 3.0,
    live: bool = False,
    send_receive: Callable[..., Packet | None] = srp1,
) -> Packet | None:
    require_live(live)
    if not interface.strip() or timeout <= 0:
        raise ValueError("provide an interface and positive timeout")
    return send_receive(packet, iface=interface, timeout=timeout, verbose=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("--target", default="192.0.2.10")
    show_parser.add_argument("--arp-target", default="192.0.2.1")

    sniff_parser = subparsers.add_parser("sniff")
    sniff_parser.add_argument("--host", required=True)
    sniff_parser.add_argument("--interface", required=True)
    sniff_parser.add_argument("--count", type=int, default=10)
    sniff_parser.add_argument("--timeout", type=float, default=30.0)
    sniff_parser.add_argument("--live", action="store_true")

    send_parser = subparsers.add_parser("send")
    send_parser.add_argument("--kind", choices=("icmp", "arp"), required=True)
    send_parser.add_argument("--target", required=True)
    send_parser.add_argument("--interface", required=True)
    send_parser.add_argument("--timeout", type=float, default=3.0)
    send_parser.add_argument("--live", action="store_true")

    args = parser.parse_args()
    if args.command == "show":
        print("ICMP packet:\n", packet_details(build_icmp_packet(args.target)), sep="")
        print("ARP packet:\n", packet_details(build_arp_request(args.arp_target)), sep="")
    elif args.command == "sniff":
        packets = capture_host(
            args.host,
            args.interface,
            count=args.count,
            timeout=args.timeout,
            live=args.live,
        )
        for packet in packets:
            print(packet.summary())
    else:
        packet = (
            build_icmp_packet(args.target)
            if args.kind == "icmp"
            else build_arp_request(args.target)
        )
        reply = send_for_reply(packet, args.interface, timeout=args.timeout, live=args.live)
        print(packet_details(reply) if reply is not None else "No reply received")


if __name__ == "__main__":
    main()
