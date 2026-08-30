from __future__ import annotations

import socket
from threading import Thread

import pytest

import labs.dns_and_ip_resolution.solutions as dns_solutions
from labs.tcp_udp_sockets.solutions import (
    create_tcp_listener,
    create_udp_server,
    require_endpoint_permission,
    serve_tcp_once,
    serve_udp_once,
    tcp_request,
    udp_request,
)


def test_dns_methods_with_mocked_socket_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "gethostbyname", lambda host: "192.0.2.10")
    monkeypatch.setattr(
        socket,
        "gethostbyname_ex",
        lambda host: (host, ["alias.example.test"], ["192.0.2.10", "192.0.2.11"]),
    )
    monkeypatch.setattr(socket, "getfqdn", lambda host: f"fqdn.{host}")
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, proto: [(socket.AF_INET, socket.SOCK_STREAM, proto, "", (host, port))],
    )
    monkeypatch.setattr(
        socket,
        "gethostbyaddr",
        lambda address: ("host.example.test", [], [address]),
    )

    information = dns_solutions.resolve_domain("example.test", live=True)
    assert information.primary_address == "192.0.2.10"
    assert information.addresses == ["192.0.2.10", "192.0.2.11"]
    assert dns_solutions.reverse_lookup("192.0.2.10", live=True)[0] == "host.example.test"


def test_external_dns_and_scanning_require_live_mode() -> None:
    with pytest.raises(PermissionError):
        dns_solutions.resolve_domain("example.test")
    with pytest.raises(PermissionError):
        dns_solutions.scan_tcp_ports("192.0.2.10", [80])
    assert dns_solutions.is_loopback_target("127.0.0.1")
    assert dns_solutions.is_loopback_target("localhost")


def test_service_and_port_resolution() -> None:
    assert dns_solutions.service_to_port("http") == 80
    assert dns_solutions.port_to_service(80) == "http"


def test_tcp_client_and_server_over_loopback() -> None:
    listener = create_tcp_listener(timeout=2)
    port = listener.getsockname()[1]
    received: list[bytes] = []

    def server() -> None:
        request, _ = serve_tcp_once(listener, lambda message: message.upper())
        received.append(request)

    thread = Thread(target=server)
    thread.start()
    response = tcp_request("127.0.0.1", port, b"hello", timeout=2)
    thread.join(timeout=2)
    listener.close()

    assert not thread.is_alive()
    assert received == [b"hello"]
    assert response == b"HELLO"


def test_udp_client_and_server_over_loopback() -> None:
    server_socket = create_udp_server(timeout=2)
    port = server_socket.getsockname()[1]
    received: list[bytes] = []

    def server() -> None:
        request, _ = serve_udp_once(server_socket, lambda message: b"reply:" + message)
        received.append(request)

    thread = Thread(target=server)
    thread.start()
    response = udp_request("127.0.0.1", port, b"hello", timeout=2)
    thread.join(timeout=2)
    server_socket.close()

    assert not thread.is_alive()
    assert received == [b"hello"]
    assert response == b"reply:hello"


def test_non_loopback_socket_operations_require_live_mode() -> None:
    with pytest.raises(PermissionError):
        require_endpoint_permission("192.0.2.10", live=False)
    require_endpoint_permission("192.0.2.10", live=True)
