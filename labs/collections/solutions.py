"""List, tuple, and dictionary exercises with cybersecurity-flavoured data."""

from __future__ import annotations

from dataclasses import dataclass, field


def port_list_exercise() -> dict[str, object]:
    """Perform the complete sequence of requested list and tuple operations."""
    ports = [21, 25, 80, 443, 23]
    initial_count = len(ports)
    initial_ports = ports.copy()

    ports.append(53)
    ports.sort()
    ports_before_53 = ports.index(53)

    ports.remove(80)
    ports.remove(25)
    ports.reverse()

    second_ports = [23, 53, 80]
    merged_ports = ports + second_ports
    count_53 = merged_ports.count(53)
    second_ports_tuple = tuple(second_ports)
    contains_433 = 433 in second_ports_tuple
    merged_ports.clear()

    return {
        "initial_count": initial_count,
        "initial_ports": initial_ports,
        "ports_before_53": ports_before_53,
        "reversed_ports": ports,
        "count_53": count_53,
        "merged_after_clear": merged_ports,
        "second_ports_tuple": second_ports_tuple,
        "contains_433": contains_433,
    }


@dataclass
class ArpTable:
    """A safe in-memory representation used to practice dictionary operations."""

    entries: dict[str, str] = field(
        default_factory=lambda: {
            "192.0.2.10": "02:00:00:00:00:10",
            "192.0.2.20": "02:00:00:00:00:20",
            "192.0.2.30": "02:00:00:00:00:30",
        }
    )

    def lookup(self, ip_address: str) -> str | None:
        return self.entries.get(ip_address)

    def mac_addresses(self) -> list[str]:
        return list(self.entries.values())

    def add(self, ip_address: str, mac_address: str) -> None:
        if not ip_address or not mac_address:
            raise ValueError("IP and MAC addresses cannot be empty")
        self.entries[ip_address] = mac_address

    def simulate_spoof(self, ip_address: str, replacement_mac: str) -> str:
        if ip_address not in self.entries:
            raise KeyError(ip_address)
        original = self.entries[ip_address]
        self.entries[ip_address] = replacement_mac
        return original

    def delete_first(self) -> tuple[str, str]:
        if not self.entries:
            raise KeyError("ARP table is empty")
        first_ip = next(iter(self.entries))
        return first_ip, self.entries.pop(first_ip)


def main() -> None:
    print("Port-list results:")
    for key, value in port_list_exercise().items():
        print(f"  {key}: {value}")

    table = ArpTable()
    print("\nMAC for 192.0.2.20:", table.lookup("192.0.2.20"))
    table.add("192.0.2.40", "02:00:00:00:00:40")
    old_mac = table.simulate_spoof("192.0.2.20", "02:ff:ff:ff:ff:ff")
    print("Spoof simulation replaced:", old_mac)
    print("ARP table:", table.entries)
    print("Deleted first entry:", table.delete_first())


if __name__ == "__main__":
    main()
