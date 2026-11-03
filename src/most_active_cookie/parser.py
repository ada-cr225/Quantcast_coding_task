import csv
from datetime import datetime
from pathlib import Path

from most_active_cookie.cookie import CookieRecord


class LogFormatError(ValueError):
    pass


def read_log(path: Path) -> list[CookieRecord]:
    """
    Read a cookie log CSV into records, skipping the header line.
    Raises LogFormatError on a malformed line or a timestamp without an offset.
    """
    records: list[CookieRecord] = []

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        try:
            next(reader, None)  # skip the "cookie,timestamp" header

            for line_number, row in enumerate(reader, start=2):
                if len(row) != 2:
                    raise LogFormatError(
                        f"line {line_number}: expected 'cookie,timestamp'"
                    )
                cookie, raw_timestamp = row
                try:
                    timestamp = datetime.fromisoformat(raw_timestamp)
                except ValueError:
                    raise LogFormatError(
                        f"line {line_number}: invalid timestamp {raw_timestamp!r}"
                    ) from None
                if timestamp.tzinfo is None:
                    raise LogFormatError(
                        f"line {line_number}: timestamp has no UTC offset"
                    )
                records.append(CookieRecord(cookie, timestamp))
        except UnicodeDecodeError:
            raise LogFormatError("file is not valid UTF-8 text") from None

    return records
