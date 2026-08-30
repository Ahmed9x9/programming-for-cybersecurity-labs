# TCP and UDP sockets

This topic provides one-request TCP and UDP servers plus matching clients. Defaults bind to
`127.0.0.1`; non-loopback addresses require `--live`.

Start each server and client in separate terminals:

```bash
python -m labs.tcp_udp_sockets.solutions tcp-server --port 5000
python -m labs.tcp_udp_sockets.solutions tcp-client --port 5000 --message hello

python -m labs.tcp_udp_sockets.solutions udp-server --port 5001
python -m labs.tcp_udp_sockets.solutions udp-client --port 5001 --message hello
```

Both protocols use UTF-8 messages, socket timeouts, context managers, and clear connection errors.
