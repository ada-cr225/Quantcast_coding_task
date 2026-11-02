"""Generate a synthetic cookie log in the take-home's format.

Output is newest-first, one ``cookie,timestamp`` row per line, with a header.
Cookie activity follows a heavy-tailed (Zipf-like) distribution so a few
cookies are very active and most are seen rarely, as in real web traffic.

Example:
    python generate_cookie_log.py -o cookie_log_large.csv --lines 50000 --days 30
"""

from __future__ import annotations

import argparse
import random
import string
from datetime import date, datetime, timedelta, timezone

COOKIE_ALPHABET = string.ascii_letters + string.digits
COOKIE_LENGTH = 16
NON_UTC_OFFSETS = [-8, -5, 1, 2, 5.5, 9]


def make_cookie(rng: random.Random) -> str:
    return "".join(rng.choices(COOKIE_ALPHABET, k=COOKIE_LENGTH))


def make_cookie_pool(rng: random.Random, size: int) -> list[str]:
    pool: set[str] = set()
    while len(pool) < size:
        pool.add(make_cookie(rng))
    return sorted(pool)


def zipf_weights(n: int, exponent: float) -> list[float]:
    return [1.0 / (rank**exponent) for rank in range(1, n + 1)]


def random_instant(rng: random.Random, start: datetime, days: int) -> datetime:
    seconds = rng.randrange(days * 24 * 60 * 60)
    # Timestamps in the sample are whole minutes.
    return start + timedelta(seconds=seconds - seconds % 60)


def format_timestamp(instant: datetime, rng: random.Random, mixed_offsets: bool) -> str:
    if mixed_offsets and rng.random() < 0.2:
        hours = rng.choice(NON_UTC_OFFSETS)
        tz = timezone(timedelta(hours=hours))
        return instant.astimezone(tz).isoformat()
    return instant.isoformat()


def generate(
    lines: int,
    cookies: int,
    days: int,
    start: date,
    seed: int,
    exponent: float,
    mixed_offsets: bool,
) -> list[str]:
    rng = random.Random(seed)
    pool = make_cookie_pool(rng, cookies)
    rng.shuffle(pool)
    weights = zipf_weights(len(pool), exponent)
    start_dt = datetime(start.year, start.month, start.day, tzinfo=timezone.utc)

    events = [
        (random_instant(rng, start_dt, days), rng.choices(pool, weights=weights)[0])
        for _ in range(lines)
    ]
    # Most recent first, ordered by true instant regardless of displayed offset.
    events.sort(key=lambda event: event[0], reverse=True)

    rows = ["cookie,timestamp"]
    rows.extend(
        f"{cookie},{format_timestamp(instant, rng, mixed_offsets)}"
        for instant, cookie in events
    )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-o", "--output", default="cookie_log_large.csv")
    parser.add_argument("--lines", type=int, default=50_000)
    parser.add_argument("--cookies", type=int, default=2_000, help="distinct cookies")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--start", type=date.fromisoformat, default=date(2018, 11, 10),
                        help="first UTC day, YYYY-MM-DD")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--exponent", type=float, default=1.1,
                        help="Zipf exponent; higher = more skewed activity")
    parser.add_argument("--mixed-offsets", action="store_true",
                        help="render ~20%% of timestamps in non-UTC offsets")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = generate(args.lines, args.cookies, args.days, args.start,
                    args.seed, args.exponent, args.mixed_offsets)
    with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(rows) + "\n")
    print(f"Wrote {len(rows) - 1} rows to {args.output}")


if __name__ == "__main__":
    main()
