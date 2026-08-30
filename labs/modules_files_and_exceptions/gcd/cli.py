"""Command-line interface for the GCD package."""

import argparse

from .algorithm import gcd


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=int)
    parser.add_argument("second", type=int)
    args = parser.parse_args()
    print(gcd(args.first, args.second))


if __name__ == "__main__":
    main()
