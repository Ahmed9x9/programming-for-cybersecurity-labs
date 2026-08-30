"""Loopback-safe TCP/UDP clients and one-request servers."""

from __future__ import annotations

import argparse
import ipaddress
import socket
from collections.abc import Callable


def is_loopback_host(host: str) -> bool:
    if host.casefold() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def require_endpoint_permission(host: str, live: bool) -> None:
    if not live and not is_loopback_host(host):
        raise PermissionError("non-loopback socket operations require explicit live mode")


def create_tcp_listener(
    host: str = "127.0.0.1", port: int = 0, *, timeout: float = 5.0, live: bool = False
) -> socket.socket:
    require_endpoint_permission(host, live)
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.settimeout(timeout)
        listener.bind((host, port))
        listener.listen(1)
    except Exception:
        listener.close()
        raise
    return listener


def serve_tcp_once(
    listener: socket.socket, responder: Callable[[bytes], bytes] | None = None
) -> tuple[bytes, tuple[str, int]]:
    responder = responder or (lambda message: b"TCP server received: " + message)
    connection, address = listener.accept()
    with connection:
        request = connection.recv(65_535)
        connection.sendall(responder(request))
    return request, address


def tcp_request(
    host: str,
    port: int,
    message: bytes,
    *,
    timeout: float = 5.0,
    live: bool = False,
) -> bytes:
    require_endpoint_permission(host, live)
    with socket.create_connection((host, port), timeout=timeout) as client:
        client.sendall(message)
        return client.recv(65_535)


def create_udp_server(
    host: str = "127.0.0.1", port: int = 0, *, timeout: float = 5.0, live: bool = False
) -> socket.socket:
    require_endpoint_permission(host, live)
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server.settimeout(timeout)
        server.bind((host, port))
    except Exception:
        server.close()
        raise
    return server


def serve_udp_once(
    server: socket.socket, responder: Callable[[bytes], bytes] | None = None
) -> tuple[bytes, tuple[str, int]]:
    responder = responder or (lambda message: b"UDP server received: " + message)
    request, address = server.recvfrom(65_535)
    server.sendto(responder(request), address)
    return request, address


def udp_request(
    host: str,
    port: int,
    message: bytes,
    *,
    timeout: float = 5.0,
    live: bool = False,
) -> bytes:
    require_endpoint_permission(host, live)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(timeout)
        client.sendto(message, (host, port))
        response, _ = client.recvfrom(65_535)
    return response


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("tcp-server", "tcp-client", "udp-server", "udp-client"):
        child = subparsers.add_parser(name)
        child.add_argument("--host", default="127.0.0.1")
        child.add_argument("--port", type=int, required=True)
        child.add_argument("--timeout", type=float, default=30.0)
        child.add_argument("--live", action="store_true")
        if name.endswith("client"):
            child.add_argument("--message", required=True)

    args = parser.parse_args()
    if args.command == "tcp-server":
        with create_tcp_listener(
            args.host, args.port, timeout=args.timeout, live=args.live
        ) as listener:
            request, address = serve_tcp_once(listener)
            print(f"Received {request.decode()} from {address}")
    elif args.command == "tcp-client":
        response = tcp_request(
            args.host,
            args.port,
            args.message.encode(),
            timeout=args.timeout,
            live=args.live,
        )
        print(response.decode())
    elif args.command == "udp-server":
        with create_udp_server(
            args.host, args.port, timeout=args.timeout, live=args.live
        ) as server:
            request, address = serve_udp_once(server)
            print(f"Received {request.decode()} from {address}")
    else:
        response = udp_request(
            args.host,
            args.port,
            args.message.encode(),
            timeout=args.timeout,
            live=args.live,
        )
        print(response.decode())


if __name__ == "__main__":
    main()
