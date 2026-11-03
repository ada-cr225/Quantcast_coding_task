from pathlib import Path

import pytest

from most_active_cookie.cli import main

SAMPLE_LOG = """\
cookie,timestamp
AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00
SAZuXPGUrfbcn5UA,2018-12-09T10:13:00+00:00
5UAVanZf6UtGyKVS,2018-12-09T07:25:00+00:00
AtY0laUfhglK3lC7,2018-12-09T06:19:00+00:00
SAZuXPGUrfbcn5UA,2018-12-08T22:03:00+00:00
4sMM2LxV07bPJzwf,2018-12-08T21:30:00+00:00
fbcn5UAVanZf6UtG,2018-12-08T09:30:00+00:00
4sMM2LxV07bPJzwf,2018-12-07T23:30:00+00:00
"""


@pytest.fixture
def sample_log(tmp_path: Path) -> Path:
    """Write the sample log from the task description to a temp file."""
    path = tmp_path / "cookie_log.csv"
    path.write_text(SAMPLE_LOG, encoding="utf-8")
    return path


def run(capsys: pytest.CaptureFixture[str], *args: str) -> tuple[int, str, str]:
    """Run the CLI and return its exit code, stdout and stderr."""
    exit_code = main(list(args))
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


# ###################################### sucess runs #################################################


def test_prints_single_most_active_cookie(
    sample_log: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out, err = run(capsys, "-f", str(sample_log), "-d", "2018-12-09")

    assert code == 0
    assert out == "AtY0laUfhglK3lC7\n"
    assert err == ""


def test_prints_all_tied_cookies_in_file_order(
    sample_log: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out, _ = run(capsys, "-f", str(sample_log), "-d", "2018-12-08")

    assert code == 0
    assert out == "SAZuXPGUrfbcn5UA\n4sMM2LxV07bPJzwf\nfbcn5UAVanZf6UtG\n"


def test_date_with_no_entries_prints_nothing(
    sample_log: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out, err = run(capsys, "-f", str(sample_log), "-d", "2018-12-01")

    assert code == 0
    assert out == ""
    assert err == ""


def test_accepts_long_option_names(
    sample_log: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out, _ = run(capsys, "--file", str(sample_log), "--date", "2018-12-09")

    assert code == 0
    assert out == "AtY0laUfhglK3lC7\n"


def test_groups_timestamps_by_utc_day(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "log.csv"
    path.write_text(
        "cookie,timestamp\n"
        "late,2018-12-10T01:00:00+02:00\n"  # 2018-12-09T23:00 in UTC
        "late,2018-12-09T20:00:00+00:00\n"
        "early,2018-12-09T10:00:00+00:00\n",
        encoding="utf-8",
    )

    code, out, _ = run(capsys, "-f", str(path), "-d", "2018-12-09")

    assert code == 0
    assert out == "late\n"


####################################### error runs #################################################


def test_missing_file_reports_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "missing.csv"

    code, out, err = run(capsys, "-f", str(missing), "-d", "2018-12-09")

    assert code == 1
    assert out == ""
    assert "file not found" in err


def test_malformed_log_reports_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "log.csv"
    path.write_text("cookie,timestamp\nabc,not-a-timestamp\n", encoding="utf-8")

    code, out, err = run(capsys, "-f", str(path), "-d", "2018-12-09")

    assert code == 1
    assert out == ""
    assert "line 2" in err


####################################### args testing #################################################


@pytest.mark.parametrize(
    "args",
    [
        ["-f", "log.csv", "-d", "2018-13-45"],
        ["-f", "log.csv", "-d", "09-12-2018"],
        ["-d", "2018-12-09"],
        ["-f", "log.csv"],
        [],
    ],
    ids=[
        "impossible-date",
        "wrong-date-format",
        "missing-file",
        "missing-date",
        "no-args",
    ],
)
def test_invalid_arguments_exit_with_usage_error(
    args: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(args)

    assert exc_info.value.code == 2
    assert "usage:" in capsys.readouterr().err


def test_help_exits_successfully(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    assert "usage:" in capsys.readouterr().out
