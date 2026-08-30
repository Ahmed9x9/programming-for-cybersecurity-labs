"""File, lambda, and exception-handling exercises."""

from __future__ import annotations

import argparse
from pathlib import Path


def add_lists(first: list[int], second: list[int]) -> list[int]:
    """Add corresponding items using the requested map/lambda approach."""
    if len(first) != len(second):
        raise ValueError("lists must have the same length")
    return list(map(lambda pair: pair[0] + pair[1], zip(first, second, strict=True)))


def write_odd_even_files(output_directory: Path, maximum: int = 100) -> tuple[Path, Path]:
    """Write positive odd and even numbers up to *maximum* into separate files."""
    if maximum < 1:
        raise ValueError("maximum must be positive")
    output_directory.mkdir(parents=True, exist_ok=True)
    odd_path = output_directory / "odd.txt"
    even_path = output_directory / "even.txt"
    with (
        odd_path.open("w", encoding="utf-8") as odd_file,
        even_path.open("w", encoding="utf-8") as even_file,
    ):
        for number in range(1, maximum + 1):
            destination = even_file if number % 2 == 0 else odd_file
            destination.write(f"{number}\n")
    return odd_path, even_path


def read_text(path: Path) -> str:
    with path.open(encoding="utf-8") as input_file:
        return input_file.read()


def read_line(path: Path, line_number: int) -> str:
    if line_number < 1:
        raise ValueError("line_number starts at 1")
    with path.open(encoding="utf-8") as input_file:
        for current, line in enumerate(input_file, 1):
            if current == line_number:
                return line.rstrip("\n")
    raise IndexError(f"{path} contains fewer than {line_number} lines")


def append_text(path: Path, text: str) -> None:
    with path.open("a", encoding="utf-8") as output_file:
        output_file.write(text)


def delete_file(path: Path) -> bool:
    try:
        path.unlink()
    except FileNotFoundError:
        return False
    return True


def safe_read(path: Path) -> tuple[str | None, str | None]:
    """Return file content or a concise error without hiding unrelated exceptions."""
    try:
        return read_text(path), None
    except FileNotFoundError:
        return None, f"{path.name} does not exist"
    except PermissionError:
        return None, f"permission denied while reading {path.name}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("generated_files"))
    args = parser.parse_args()

    print("Added lists:", add_lists([1, 2, 3], [4, 5, 6]))
    odd_path, even_path = write_odd_even_files(args.output_dir)
    print("Created:", odd_path, "and", even_path)
    print("Fifth odd number:", read_line(odd_path, 5))
    append_text(odd_path, "This is a file of odd numbers\n")
    print("Even numbers:\n", read_text(even_path), sep="")
    print("Deleted even.txt:", delete_file(even_path))
    print("Read after deletion:", safe_read(even_path)[1])


if __name__ == "__main__":
    main()
