from datetime import datetime, timezone
from pathlib import Path

import pytest

from most_active_cookie.cookie import CookieRecord
from most_active_cookie.parser import LogFormatError, read_log


def test_reads_valid_log(tmp_path: Path) -> None:
    path = tmp_path / "log.csv"
    path.write_text(
        "cookie,timestamp\n"
        "AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00\n"
        "SAZuXPGUrfbcn5UA,2018-12-09T10:13:00+00:00\n",
        encoding="utf-8",
    )

    assert read_log(path) == [
        CookieRecord(
            "AtY0laUfhglK3lC7", datetime(2018, 12, 9, 14, 19, tzinfo=timezone.utc)
        ),
        CookieRecord(
            "SAZuXPGUrfbcn5UA", datetime(2018, 12, 9, 10, 13, tzinfo=timezone.utc)
        ),
    ]


def test_header_only_log_has_no_records(tmp_path: Path) -> None:
    path = tmp_path / "log.csv"
    path.write_text("cookie,timestamp\n", encoding="utf-8")

    assert read_log(path) == []


def test_rejects_line_with_wrong_number_of_columns(tmp_path: Path) -> None:
    path = tmp_path / "log.csv"
    path.write_text("cookie,timestamp\nabc\n", encoding="utf-8")

    with pytest.raises(LogFormatError, match="expected 'cookie,timestamp'"):
        read_log(path)


def test_rejects_invalid_timestamp(tmp_path: Path) -> None:
    path = tmp_path / "log.csv"
    path.write_text("cookie,timestamp\nabc,not-a-timestamp\n", encoding="utf-8")

    with pytest.raises(LogFormatError, match="line 2"):
        read_log(path)


def test_rejects_timestamp_without_offset(tmp_path: Path) -> None:
    path = tmp_path / "log.csv"
    path.write_text("cookie,timestamp\nabc,2018-12-09T14:19:00\n", encoding="utf-8")

    with pytest.raises(LogFormatError, match="no UTC offset"):
        read_log(path)


def test_rejects_non_utf8_file(tmp_path: Path) -> None:
    path = tmp_path / "log.csv"
    path.write_bytes(b"cookie,timestamp\n\xff\xfe,2018-12-09T14:19:00+00:00\n")

    with pytest.raises(LogFormatError, match="UTF-8"):
        read_log(path)


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_log(tmp_path / "missing.csv")
