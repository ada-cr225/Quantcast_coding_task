from datetime import date, datetime
import pytest
from most_active_cookie.cookie import CookieRecord
from most_active_cookie.cookie import count_cookies_on_day
from most_active_cookie.cookie import most_active_cookies
from most_active_cookie.cookie import most_frequent

def record(cookie: str, timestamp: str) -> CookieRecord:
    return CookieRecord(cookie, datetime.fromisoformat(timestamp))



##################### most_frequent #######################################


def test_most_frequent_returns_single_winner() -> None:
    assert most_frequent({"a": 3, "b": 1}) == ["a"]


def test_most_frequent_returns_all_tied_cookies_in_order() -> None:
    assert most_frequent({"z": 2, "a": 2, "m": 1}) == ["z", "a"]


def test_most_frequent_of_nothing_is_empty() -> None:
    assert most_frequent({}) == []


# ###################### count_cookies_on_day ##############################


def test_counts_only_the_target_day() -> None:
    records = [
        record("newer", "2018-12-10T08:00:00+00:00"),
        record("a", "2018-12-09T14:00:00+00:00"),
        record("b", "2018-12-09T10:00:00+00:00"),
        record("a", "2018-12-09T06:00:00+00:00"),
        record("older", "2018-12-08T22:00:00+00:00"),
    ]
    assert count_cookies_on_day(records, date(2018, 12, 9)) == {"a": 2, "b": 1}


def test_missing_day_gives_no_counts() -> None:
    records = [
        record("a", "2018-12-10T08:00:00+00:00"),
        record("b", "2018-12-08T08:00:00+00:00"),
    ]
    assert count_cookies_on_day(records, date(2018, 12, 9)) == {}


def test_timestamps_are_grouped_by_utc_day() -> None:
    records = [
        record("in", "2018-12-10T01:00:00+02:00"),  # 2018-12-09 23:00 UTC
        record("out", "2018-12-09T23:00:00-02:00"),  # 2018-12-10 01:00 UTC
    ]
    # "out" is newer in UTC, so it must come first to keep the log sorted
    records.reverse()
    assert count_cookies_on_day(records, date(2018, 12, 9)) == {"in": 1}


# ###################### most_active_cookies ##############################

SAMPLE = [
    record("AtY0laUfhglK3lC7", "2018-12-09T14:19:00+00:00"),
    record("SAZuXPGUrfbcn5UA", "2018-12-09T10:13:00+00:00"),
    record("5UAVanZf6UtGyKVS", "2018-12-09T07:25:00+00:00"),
    record("AtY0laUfhglK3lC7", "2018-12-09T06:19:00+00:00"),
    record("SAZuXPGUrfbcn5UA", "2018-12-08T22:03:00+00:00"),
    record("4sMM2LxV07bPJzwf", "2018-12-08T21:30:00+00:00"),
    record("fbcn5UAVanZf6UtG", "2018-12-08T09:30:00+00:00"),
    record("4sMM2LxV07bPJzwf", "2018-12-07T23:30:00+00:00"),
]


def test_sample_answer_for_9th() -> None:
    assert most_active_cookies(SAMPLE, date(2018, 12, 9)) == ["AtY0laUfhglK3lC7"]


def test_sample_tie_for_8th() -> None:
    assert most_active_cookies(SAMPLE, date(2018, 12, 8)) == [
        "SAZuXPGUrfbcn5UA",
        "4sMM2LxV07bPJzwf",
        "fbcn5UAVanZf6UtG",
    ]