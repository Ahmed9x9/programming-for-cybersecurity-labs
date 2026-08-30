# Scapy scanning and PCAP

This topic implements SYN scanning, UDP traceroute, PCAP inspection, and ICMP/ICMPv6 filtering.
Live network operations require administrator/root privileges, `--live`, and an explicit target.

```bash
python -m labs.scapy_scanning_and_pcap.solutions generate \
  --output labs/scapy_scanning_and_pcap/data/sample_packets.pcap
python -m labs.scapy_scanning_and_pcap.solutions filter \
  --input labs/scapy_scanning_and_pcap/data/sample_packets.pcap \
  --output generated_files/icmp_only.pcap --protocol icmp
python -m labs.scapy_scanning_and_pcap.solutions scan \
  --target scanme.nmap.org --ports 22 80 --live
```

The committed PCAP contains only synthetic packets using reserved addresses.
