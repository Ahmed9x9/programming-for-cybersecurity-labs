from __future__ import annotations

from pathlib import Path

import pytest
from scapy.all import ARP, ICMP, IP, TCP, Ether, IPv6

from labs.scapy_scanning_and_pcap.solutions import (
    build_syn_packet,
    filter_pcap,
    generate_sample_pcap,
    sample_packets,
    scan_ports,
    traceroute,
)
from labs.scapy_sniffing_and_packet_crafting.solutions import (
    build_arp_request,
    build_icmp_packet,
    capture_host,
    packet_details,
    send_for_reply,
    validate_host,
)


def test_sample_packets_use_expected_layers_and_reserved_addresses() -> None:
    packets = sample_packets()
    assert len(packets) == 4
    assert packets[0].haslayer(Ether)
    assert packets[0].haslayer(IP)
    assert packets[0].haslayer(ICMP)
    assert packets[0][IP].src == "192.0.2.10"
    assert packets[2].haslayer(IPv6)
    assert packets[3].haslayer(ARP)


def test_generate_and_filter_pcap(tmp_path: Path) -> None:
    source = tmp_path / "sample.pcap"
    icmp_output = tmp_path / "icmp.pcap"
    icmpv6_output = tmp_path / "icmpv6.pcap"
    both_output = tmp_path / "both.pcap"

    assert generate_sample_pcap(source) == 4
    assert filter_pcap(source, icmp_output, "icmp") == 1
    assert filter_pcap(source, icmpv6_output, "icmpv6") == 1
    assert filter_pcap(source, both_output, "both") == 2
    with pytest.raises(ValueError):
        filter_pcap(source, tmp_path / "bad.pcap", "tcp")


def test_syn_scanner_requires_live_and_supports_an_injected_transport() -> None:
    assert build_syn_packet("192.0.2.10", 80)[TCP].flags == "S"
    with pytest.raises(PermissionError):
        scan_ports("192.0.2.10", [80])

    def fake_send_receive(packet, **kwargs):
        assert kwargs["timeout"] == 0.25
        return IP(src="192.0.2.10") / TCP(flags="SA" if packet[TCP].dport == 80 else "RA")

    assert scan_ports(
        "192.0.2.10",
        [22, 80],
        timeout=0.25,
        live=True,
        send_receive=fake_send_receive,
    ) == {22: False, 80: True}


def test_traceroute_stops_at_destination_response() -> None:
    replies = iter(
        [
            IP(src="192.0.2.1") / ICMP(type=11),
            IP(src="198.51.100.20") / ICMP(type=3),
        ]
    )

    def fake_send_receive(packet, **kwargs):
        assert packet[IP].ttl in (1, 2)
        return next(replies)

    assert traceroute("198.51.100.20", max_hops=5, live=True, send_receive=fake_send_receive) == [
        (1, "192.0.2.1"),
        (2, "198.51.100.20"),
    ]


def test_packet_building_and_offline_display() -> None:
    icmp_packet = build_icmp_packet("192.0.2.10")
    arp_packet = build_arp_request("192.0.2.1")
    assert icmp_packet.haslayer(Ether) and icmp_packet.haslayer(ICMP)
    assert arp_packet[Ether].dst == "ff:ff:ff:ff:ff:ff"
    assert arp_packet.haslayer(ARP)
    assert "ICMP" in packet_details(icmp_packet)
    assert validate_host("scanme.nmap.org") == "scanme.nmap.org"
    with pytest.raises(ValueError):
        validate_host("invalid host; command")


def test_capture_and_send_require_live_mode_and_allow_test_doubles() -> None:
    packet = build_icmp_packet("192.0.2.10")
    with pytest.raises(PermissionError):
        capture_host("192.0.2.10", "Ethernet")
    with pytest.raises(PermissionError):
        send_for_reply(packet, "Ethernet")

    captured_arguments = {}

    def fake_capture(**kwargs):
        captured_arguments.update(kwargs)
        return [packet]

    result = capture_host(
        "192.0.2.10", "Ethernet", count=1, timeout=1, live=True, capture=fake_capture
    )
    assert result == [packet]
    assert captured_arguments["filter"] == "host 192.0.2.10"

    def fake_send_receive(sent_packet, **kwargs):
        assert kwargs["iface"] == "Ethernet"
        return sent_packet

    assert send_for_reply(packet, "Ethernet", live=True, send_receive=fake_send_receive) is packet
