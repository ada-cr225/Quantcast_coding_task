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


# ###################################### sucess runs #################################################


def test_prints_most_active_cookie(
    sample_log: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["-f", str(sample_log), "-d", "2018-12-09"])

    assert exit_code == 0
    assert capsys.readouterr().out == "AtY0laUfhglK3lC7\n"


def test_prints_every_tied_cookie(
    sample_log: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["-f", str(sample_log), "-d", "2018-12-08"])

    assert exit_code == 0
    assert (
        capsys.readouterr().out
        == "SAZuXPGUrfbcn5UA\n4sMM2LxV07bPJzwf\nfbcn5UAVanZf6UtG\n"
    )


def test_prints_nothing_for_day_with_no_entries(
    sample_log: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["-f", str(sample_log), "-d", "2018-12-01"])

    assert exit_code == 0
    assert capsys.readouterr().out == ""


####################################### error runs #################################################


def test_missing_file_is_an_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["-f", str(tmp_path / "missing.csv"), "-d", "2018-12-09"])

    output = capsys.readouterr()
    assert exit_code == 1
    assert output.out == ""
    assert "file not found" in output.err


def test_malformed_log_is_an_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "log.csv"
    path.write_text("cookie,timestamp\nabc,not-a-timestamp\n", encoding="utf-8")

    exit_code = main(["-f", str(path), "-d", "2018-12-09"])

    output = capsys.readouterr()
    assert exit_code == 1
    assert output.out == ""
    assert "line 2" in output.err


def test_invalid_date_is_a_usage_error(sample_log: Path) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["-f", str(sample_log), "-d", "2018-13-45"])

    assert exc_info.value.code == 2
