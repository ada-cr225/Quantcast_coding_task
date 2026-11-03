from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, timezone

# simple data structure to hold cookie records
@dataclass(frozen=True)
class CookieRecord:
    cookie: str
    timestamp: datetime

# count cookie occurrences for a given date by linearly iterating through the records and comparing the record's date with the user-specified target date
def count_cookies_on_day(records: Iterable[CookieRecord], target: date) -> dict[str, int]:
    # store counts in a dictionary
    counts: dict[str, int] = {}
    # iterate through the records and count cookies for the target date
    for record in records:
        day = record.timestamp.astimezone(timezone.utc).date() # convert to UTC and extract the date
        # compare the record's date with the user-specified target date
        if day > target:
            continue
        if day < target:
            break
        # if the record's date matches the target date, increment the count for that cookie
        counts[record.cookie] = counts.get(record.cookie, 0) + 1

    return counts

# return most frequent cookie by finding the highest count in the counts dictionary and returning all cookies that have that count
def most_frequent(counts: dict[str, int]) -> list[str]:
    # if there is nothing in the counts dictionary, return an empty list
    if not counts:
        return []
    # if there are counts, find the highest count and return all cookies that have that count
    highest_count = max(counts.values())
    return [cookie for cookie, count in counts.items() if count == highest_count] 

    
# put it all together to find the most active cookie(s) for a given date
def most_active_cookies(records: Iterable[CookieRecord], target: date) -> list[str]:
     # return the most frequent cookie(s) for the target date
    return most_frequent(count_cookies_on_day(records, target))
