from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, timezone

@dataclass(frozen=True)
class CookieRecord:
    cookie: str
    timestamp: datetime

def count_cookies_on_day(records: Iterable[CookieRecord], target: date) -> dict[str, int]:
    """
    Count occurrences of each cookie on the given UTC day

    since records are ordered newest-first, records newer than the target day are skipped,
    and scanning stops at the first record older than it, keys are in order of first appearance
    """

    counts: dict[str, int] = {}

    for record in records:
        day = record.timestamp.astimezone(timezone.utc).date() # convert to UTC and extract the date
        if day > target:
            continue # skip records newer than the target day
        if day < target:
            break # stop scanning at the first record older than the target day
        counts[record.cookie] = counts.get(record.cookie, 0) + 1

    return counts

def most_frequent(counts: dict[str, int]) -> list[str]:
    """
    Return every cookie with the highest count, in the order of `counts`
    Returns an empty list if `counts` is empty
    """
    if not counts:
        return []
    
    highest_count = max(counts.values())
    return [cookie for cookie, count in counts.items() if count == highest_count] 

    
def most_active_cookies(records: Iterable[CookieRecord], target: date) -> list[str]:
    """Return the most active cookies on the given UTC day"""
    return most_frequent(count_cookies_on_day(records, target))
