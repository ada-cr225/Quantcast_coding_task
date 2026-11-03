<p align="center">This is for the Coding Assessment from Quantcast.</p>

<p align="center">Hello, thank you for assessing me, hope it goes well!</p>

# most_active_cookie

A command-line tool that finds the most active cookies on a given day in a cookie log.

## Installation

Install directly from GitHub:

```
pip install git+https://github.com/ada-cr225/Quantcast_coding_task.git
```

Or clone the repository and install it in a virtual environment:

```
git clone https://github.com/ada-cr225/Quantcast_coding_task.git
cd Quantcast_coding_task
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Usage

```
most_active_cookie -f <log file> -d <YYYY-MM-DD>
```

| Option | Description |
|---|---|
| `-f`, `--file` | Path to the cookie log CSV |
| `-d`, `--date` | Day to query, as a UTC date in `YYYY-MM-DD` format |

Example, using the sample log in `data/`:

```
$ most_active_cookie -f data/cookie_log.csv -d 2018-12-09
AtY0laUfhglK3lC7
```

If several cookies tie for most active, each one is printed on its own line:

```
$ most_active_cookie -f data/cookie_log.csv -d 2018-12-08
SAZuXPGUrfbcn5UA
4sMM2LxV07bPJzwf
fbcn5UAVanZf6UtG
```

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Success, including a day with no entries (prints nothing) |
| 1 | The log file is missing, unreadable or malformed |
| 2 | Invalid command-line arguments |

Results go to stdout and error messages go to stderr.

## Log format

A CSV file with a `cookie,timestamp` header, followed by one entry per line:

```
cookie,timestamp
AtY0laUfhglK3lC7,2018-12-09T14:19:00+00:00
SAZuXPGUrfbcn5UA,2018-12-09T10:13:00+00:00
```

Timestamps are ISO 8601 and must include a UTC offset. Entries must be sorted newest first.

## Development

Install the project with its development tools (see Installation), then run the same checks CI runs on every push to `main`:

```
pytest -v
pytest --cov=most_active_cookie --cov-report=term-missing
ruff check .
ruff format --check .
mypy src
```

Tests live in `tests/`, one file per module: `test_cookie.py` (core logic), `test_parser.py` (reading the log) and `test_cli.py` (end-to-end runs through `main`).

## Design

The code is split into three modules under `src/most_active_cookie/`, each with a single job:

- `cli.py`: parses arguments, prints results, and maps errors to exit codes.
- `parser.py`: reads the log file into `CookieRecord`s, and rejects malformed lines.
- `cookie.py`: the core logic. It counts each cookie's occurrences on the target day, then returns those with the highest count.

The core logic never touches files or the terminal, so it can be tested and reused independently of the CLI.

### Generating larger test logs

`generate_cookie_log.py` creates a large synthetic log in the same format, for manual testing. It was written with help from Claude. The generated files are not committed.

```
python generate_cookie_log.py -o data/cookie_log_large.csv
python generate_cookie_log.py -o data/cookie_log_mixed_offsets.csv --mixed-offsets
```

Run `python generate_cookie_log.py --help` for options. With the default seed, both files have `3CfT45Vmut9ERDrc` as the most active cookie on `2018-12-09`.
