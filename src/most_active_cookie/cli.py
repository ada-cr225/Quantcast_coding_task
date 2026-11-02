# CLI for finding the most active cookie

import argparse
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path

# address errors in date input:
def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"invalid date {value!r}, expected YYYY-MM-DD"
        ) from None

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="most_active_cookie",
        description="Print the most active cookie(s) for a given UTC day.",
    )
    parser.add_argument(
        "-f", "--file", type=Path, required=True, help="path to the cookie log CSV"
    )
    parser.add_argument(
        "-d", "--date", type=parse_date, required=True, help="UTC day as YYYY-MM-DD"
    )
    return parser

def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(f"file={args.file} date={args.date}")
    return 0


if __name__ == "__main__":
    sys.exit(main())