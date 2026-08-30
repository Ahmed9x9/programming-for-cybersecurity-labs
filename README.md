# Programming for Cybersecurity Labs

Clean, runnable Python solutions for **CYS 403 — Programming for Cybersecurity**.

- **Author:** Ahmed Al-Shaikh
- **Academic year:** 2024–2025
- **Term:** 2
- **Python:** 3.12

The repository reorganizes the supplied coursework by topic. Each topic contains a short guide,
reusable functions, and a runnable command-line demonstration. The solutions preserve the learning
outcomes while replacing hard-coded personal paths, embedded credentials, and fragile examples.

## Topics

| Topic | Exercises |
| --- | --- |
| [Python basics](labs/python_basics/) | Strings, numbers, email generation, password checks, services and ports |
| [Collections](labs/collections/) | Lists, tuples, dictionaries, ports, and an in-memory ARP-table exercise |
| [Control flow and functions](labs/control_flow_and_functions/) | Conditions, loops, password strength, XOR, leap years, and pyramid height |
| [Modules, files, and exceptions](labs/modules_files_and_exceptions/) | GCD package, list mapping, and safe file operations |
| [OOP fundamentals](labs/oop_fundamentals/) | Bank accounts, inheritance, and prime-number checking |
| [OOP, regex, and log analysis](labs/oop_regex_and_log_analysis/) | Polymorphic parsers, Apache logs, email validation, and age calculation |
| [Concurrency](labs/concurrency/) | Threads, threaded ping checks, and multiprocessing |
| [DNS and IP resolution](labs/dns_and_ip_resolution/) | Socket lookup methods and explicit TCP port checks |
| [TCP and UDP sockets](labs/tcp_udp_sockets/) | Loopback-safe clients and one-request servers |
| [Scapy scanning and PCAP](labs/scapy_scanning_and_pcap/) | SYN scanning, traceroute, and packet-capture filtering |
| [Scapy sniffing and packet crafting](labs/scapy_sniffing_and_packet_crafting/) | Sniffing, ICMP/ARP construction, and explicit transmission |
| [Shodan API](labs/shodan_api/) | Host details, ports, geolocation, and search queries |

## Setup

```bash
python -m venv .venv
```

Activate the environment, then install the project and development tools:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run a topic using the command shown in its README. Run the quality checks with:

```bash
ruff check .
ruff format --check .
pytest
```

## Safe use

Remote scanning, packet capture, packet transmission, ping sweeps, DNS queries, and Shodan calls
require the `--live` flag and explicit targets. Only use them on systems and networks you own or
have permission to test. Loopback TCP/UDP examples and offline PCAP exercises do not need live mode.

Shodan examples read `SHODAN_API_KEY` from the environment. The repository never stores a real key.
Free Shodan plans may return `403 Forbidden` for search operations; the scripts report that condition
without exposing credentials.

## Data policy

The original reports, screenshots, lecture files, and real packet captures are intentionally excluded.
Committed fixtures use reserved example networks and synthetic data so they are safe to share later.
