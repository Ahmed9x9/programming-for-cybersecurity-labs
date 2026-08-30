# DNS and IP resolution

This topic modernizes the original `socket` examples: forward and reverse lookups, fully qualified
domain names, address information, service/port conversion, and a small TCP connect scan.

```bash
python -m labs.dns_and_ip_resolution.solutions domain --host scanme.nmap.org --live
python -m labs.dns_and_ip_resolution.solutions scan --host scanme.nmap.org --ports 22 80 --live
python -m labs.dns_and_ip_resolution.solutions service --name http
```

External DNS and scan operations require `--live`. `localhost` is allowed without it.
