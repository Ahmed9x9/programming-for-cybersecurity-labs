"""Scapy SYN scanning, traceroute, and PCAP filtering exercises."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

from scapy.all import ARP, ICMP, IP, TCP, UDP, Ether, IPv6, Raw, rdpcap, sr1, wrpcap
from scapy.layers.inet6 import ICMPv6EchoReply, ICMPv6EchoRequest
from scapy.packet import Packet


def require_live(live: bool) -> None:
    if not live:
        raise PermissionError("network transmission requires explicit live mode")


def build_syn_packet(target: str, port: int) -> Packet:
    if not 1 <= port <= 65535:
        raise ValueError("port must be between 1 and 65535")
    return IP(dst=target) / TCP(dport=port, flags="S")


def syn_response_is_open(response: Packet | None) -> bool:
    return response is not None and response.haslayer(TCP) and int(response[TCP].flags) == 0x12


def scan_ports(
    target: str,
    ports: list[int],
    *,
    timeout: float = 1.0,
    live: bool = False,
    send_receive: Callable[..., Packet | None] = sr1,
) -> dict[int, bool]:
    require_live(live)
    results: dict[int, bool] = {}
    for port in ports:
        response = send_receive(build_syn_packet(target, port), timeout=timeout, verbose=False)
        results[port] = syn_response_is_open(response)
    return results


def traceroute(
    target: str,
    *,
    max_hops: int = 28,
    timeout: float = 2.0,
    live: bool = False,
    send_receive: Callable[..., Packet | None] = sr1,
) -> list[tuple[int, str | None]]:
    require_live(live)
    if max_hops < 1:
        raise ValueError("max_hops must be positive")
    hops: list[tuple[int, str | None]] = []
    for ttl in range(1, max_hops + 1):
        reply = send_receive(
            IP(dst=target, ttl=ttl) / UDP(dport=33434), timeout=timeout, verbose=False
        )
        source = reply[IP].src if reply is not None and reply.haslayer(IP) else None
        hops.append((ttl, source))
        if reply is not None and reply.haslayer(ICMP) and int(reply[ICMP].type) == 3:
            break
    return hops


def packet_matches_protocol(packet: Packet, protocol: str) -> bool:
    if protocol == "icmp":
        return packet.haslayer(ICMP)
    if protocol == "icmpv6":
        return packet.haslayer(ICMPv6EchoRequest) or packet.haslayer(ICMPv6EchoReply)
    if protocol == "both":
        return packet_matches_protocol(packet, "icmp") or packet_matches_protocol(packet, "icmpv6")
    raise ValueError("protocol must be icmp, icmpv6, or both")


def filter_pcap(input_path: Path, output_path: Path, protocol: str = "icmp") -> int:
    packets = rdpcap(str(input_path))
    selected = [packet for packet in packets if packet_matches_protocol(packet, protocol)]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wrpcap(str(output_path), selected)
    return len(selected)


def sample_packets() -> list[Packet]:
    """Return deterministic packets that contain no real capture data."""
    return [
        Ether(src="02:00:00:00:00:01", dst="02:00:00:00:00:02")
        / IP(src="192.0.2.10", dst="198.51.100.20")
        / ICMP()
        / Raw(b"CYS403 ICMP example"),
        Ether(src="02:00:00:00:00:02", dst="02:00:00:00:00:01")
        / IP(src="198.51.100.20", dst="192.0.2.10")
        / TCP(sport=443, dport=49152, flags="SA"),
        Ether(src="02:00:00:00:00:03", dst="02:00:00:00:00:04")
        / IPv6(src="2001:db8::10", dst="2001:db8::20")
        / ICMPv6EchoRequest()
        / Raw(b"CYS403 ICMPv6 example"),
        Ether(src="02:00:00:00:00:04", dst="ff:ff:ff:ff:ff:ff")
        / ARP(psrc="192.0.2.40", pdst="192.0.2.1", op=1),
    ]


def generate_sample_pcap(output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    packets = sample_packets()
    wrpcap(str(output_path), packets)
    return len(packets)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan")
    scan_parser.add_argument("--target", required=True)
    scan_parser.add_argument("--ports", type=int, nargs="+", required=True)
    scan_parser.add_argument("--timeout", type=float, default=1.0)
    scan_parser.add_argument("--live", action="store_true")

    trace_parser = subparsers.add_parser("traceroute")
    trace_parser.add_argument("--target", required=True)
    trace_parser.add_argument("--max-hops", type=int, default=28)
    trace_parser.add_argument("--timeout", type=float, default=2.0)
    trace_parser.add_argument("--live", action="store_true")

    filter_parser = subparsers.add_parser("filter")
    filter_parser.add_argument("--input", type=Path, required=True)
    filter_parser.add_argument("--output", type=Path, required=True)
    filter_parser.add_argument("--protocol", choices=("icmp", "icmpv6", "both"), default="icmp")

    generate_parser = subparsers.add_parser("generate")
    generate_parser.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "scan":
        for port, is_open in scan_ports(
            args.target, args.ports, timeout=args.timeout, live=args.live
        ).items():
            print(f"Port {port}: {'open' if is_open else 'closed'}")
    elif args.command == "traceroute":
        for ttl, source in traceroute(
            args.target, max_hops=args.max_hops, timeout=args.timeout, live=args.live
        ):
            print(f"{ttl}: {source or '*'}")
    elif args.command == "filter":
        print("Packets written:", filter_pcap(args.input, args.output, args.protocol))
    else:
        print("Packets written:", generate_sample_pcap(args.output))


if __name__ == "__main__":
    main()
