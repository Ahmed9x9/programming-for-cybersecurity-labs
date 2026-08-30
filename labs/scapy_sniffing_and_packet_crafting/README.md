# Scapy sniffing and packet crafting

This topic builds an Ethernet/IP/ICMP packet and an Ethernet/ARP request from the lowest requested
layer. Packet details can be inspected offline. Capturing or sending requires an explicit interface,
target, and `--live` flag, normally from an administrator/root shell.

```bash
python -m labs.scapy_sniffing_and_packet_crafting.solutions show --target 192.0.2.10
python -m labs.scapy_sniffing_and_packet_crafting.solutions sniff \
  --host scanme.nmap.org --interface Ethernet --count 10 --timeout 30 --live
python -m labs.scapy_sniffing_and_packet_crafting.solutions send \
  --kind icmp --target scanme.nmap.org --interface Ethernet --live
```

Only capture or transmit on networks where you have authorization.
