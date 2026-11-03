import argparse
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from most_active_cookie.cookie import most_active_cookies
from most_active_cookie.parser import LogFormatError, read_log


# address errors in date input:
def parse_date(value: str) -> date:
    """
    Used as an argparse ``type``: raising ArgumentTypeError makes argparse
    print a clean usage error instead of a traceback
    """
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"invalid date {value!r}, expected YYYY-MM-DD"
        ) from None


# sets up the command line interface parser
def build_parser() -> argparse.ArgumentParser:
    '''Build the argument parser for the -f/--file and -d/--date options'''
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
    """
    Run the command-line tool and return its exit code.

    Prints the most active cookie(s) for the requested day to stdout, one per line.
    Returns 0 on success, or 1 if the log file is missing or malformed.
    Invalid arguments make argparse exit with code 2.
    """
    args = build_parser().parse_args(argv)
    try:
        records = read_log(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"error: cannot read {args.file}: {error.strerror}", file=sys.stderr)
        return 1
    except LogFormatError as error:
        print(f"error: {args.file}: {error}", file=sys.stderr)
        return 1

    for cookie in most_active_cookies(records, args.date):
        print(cookie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
