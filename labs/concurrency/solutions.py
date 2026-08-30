"""Thread, threaded ping, and multiprocessing exercises."""

from __future__ import annotations

import argparse
import ipaddress
import platform
import subprocess
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from multiprocessing import Pool, cpu_count
from threading import Lock, Thread


def run_sleeping_threads(count: int = 10, delay: float = 5.0) -> list[str]:
    """Start workers that report before sleeping and after waking."""
    if count < 1 or delay < 0:
        raise ValueError("count must be positive and delay cannot be negative")
    messages: list[str] = []
    lock = Lock()

    def worker(number: int) -> None:
        with lock:
            messages.append(f"Thread {number} is sleeping")
        time.sleep(delay)
        with lock:
            messages.append(f"Thread {number} is awake")

    threads = [Thread(target=worker, args=(number,)) for number in range(1, count + 1)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return messages


def ping_command(host: str, timeout: float = 1.0, system: str | None = None) -> list[str]:
    """Build a one-packet ping command for Windows or POSIX."""
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    system = system or platform.system()
    if system == "Windows":
        return ["ping", "-n", "1", "-w", str(round(timeout * 1000)), host]
    return ["ping", "-c", "1", "-W", str(max(1, round(timeout))), host]


def ping_host(host: str, timeout: float = 1.0, *, live: bool = False) -> bool:
    if not live:
        raise PermissionError("ping requires explicit live mode")
    completed = subprocess.run(
        ping_command(host, timeout),
        capture_output=True,
        check=False,
        timeout=timeout + 2,
    )
    return completed.returncode == 0


def ip_range(start: str, end: str) -> list[str]:
    first = ipaddress.ip_address(start)
    last = ipaddress.ip_address(end)
    if first.version != last.version or int(last) < int(first):
        raise ValueError("start and end must be an ordered range of the same IP version")
    if int(last) - int(first) > 1023:
        raise ValueError("range is limited to 1024 addresses")
    return [str(ipaddress.ip_address(value)) for value in range(int(first), int(last) + 1)]


def ping_range(
    start: str,
    end: str,
    *,
    workers: int = 20,
    timeout: float = 1.0,
    live: bool = False,
    checker: Callable[..., bool] = ping_host,
) -> dict[str, bool]:
    if not live:
        raise PermissionError("ping range requires explicit live mode")
    addresses = ip_range(start, end)
    if workers < 1:
        raise ValueError("workers must be positive")
    with ThreadPoolExecutor(max_workers=min(workers, len(addresses))) as executor:
        states = executor.map(lambda host: checker(host, timeout, live=True), addresses)
    return dict(zip(addresses, states, strict=True))


def is_perfect(number: int) -> bool:
    if number < 2:
        return False
    divisor_sum = 1
    candidate = 2
    while candidate * candidate <= number:
        if number % candidate == 0:
            divisor_sum += candidate
            partner = number // candidate
            if partner != candidate:
                divisor_sum += partner
        candidate += 1
    return divisor_sum == number


def perfect_numbers(limit: int) -> list[int]:
    if limit < 1:
        return []
    return [number for number in range(2, limit + 1) if is_perfect(number)]


def perfect_numbers_parallel(limit: int, workers: int | None = None) -> list[int]:
    if limit < 1:
        return []
    process_count = workers or max(1, cpu_count() - 1)
    if process_count < 1:
        raise ValueError("workers must be positive")
    with Pool(processes=process_count) as pool:
        matches = pool.map(is_perfect, range(2, limit + 1), chunksize=max(1, limit // 100))
    return [number for number, match in zip(range(2, limit + 1), matches, strict=True) if match]


@dataclass(frozen=True)
class TimedResult:
    numbers: list[int]
    elapsed_seconds: float


def time_perfect_numbers(limit: int, *, parallel: bool = False) -> TimedResult:
    started = time.perf_counter()
    numbers = perfect_numbers_parallel(limit) if parallel else perfect_numbers(limit)
    return TimedResult(numbers, time.perf_counter() - started)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    thread_parser = subparsers.add_parser("threads")
    thread_parser.add_argument("--count", type=int, default=10)
    thread_parser.add_argument("--delay", type=float, default=5.0)

    ping_parser = subparsers.add_parser("ping")
    ping_parser.add_argument("--start", required=True)
    ping_parser.add_argument("--end", required=True)
    ping_parser.add_argument("--workers", type=int, default=20)
    ping_parser.add_argument("--timeout", type=float, default=1.0)
    ping_parser.add_argument("--live", action="store_true")

    perfect_parser = subparsers.add_parser("perfect")
    perfect_parser.add_argument("--limit", type=int, default=100_000)
    perfect_parser.add_argument("--parallel", action="store_true")

    args = parser.parse_args()
    if args.command == "threads":
        print(*run_sleeping_threads(args.count, args.delay), sep="\n")
    elif args.command == "ping":
        results = ping_range(
            args.start,
            args.end,
            workers=args.workers,
            timeout=args.timeout,
            live=args.live,
        )
        for host, is_up in results.items():
            print(f"{host}: {'up' if is_up else 'down'}")
    else:
        result = time_perfect_numbers(args.limit, parallel=args.parallel)
        print("Perfect numbers:", result.numbers)
        print(f"Elapsed: {result.elapsed_seconds:.4f} seconds")


if __name__ == "__main__":
    main()
