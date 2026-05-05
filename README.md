# cronscope

> Local cron job visualizer that parses crontab syntax and shows a human-readable schedule timeline.

---

## Installation

```bash
pip install cronscope
```

Or install from source:

```bash
git clone https://github.com/youruser/cronscope.git && cd cronscope && pip install .
```

---

## Usage

Pass a cron expression and cronscope will display the next scheduled run times in a readable timeline:

```bash
cronscope "*/15 9-17 * * 1-5"
```

**Example output:**

```
Expression : */15 9-17 * * 1-5
Description: Every 15 minutes, between 09:00–17:00, Monday through Friday

Upcoming runs:
  1. Mon, 14 Jul 2025  09:00
  2. Mon, 14 Jul 2025  09:15
  3. Mon, 14 Jul 2025  09:30
  4. Mon, 14 Jul 2025  09:45
  5. Mon, 14 Jul 2025  10:00
```

You can also specify how many upcoming runs to display:

```bash
cronscope "0 0 * * *" --count 10
```

Or parse your system crontab directly:

```bash
cronscope --file /etc/crontab
```

---

## Options

| Flag | Description |
|------|-------------|
| `--count N` | Number of upcoming runs to show (default: 5) |
| `--file PATH` | Parse a crontab file instead of a single expression |
| `--format` | Output format: `table`, `json`, or `plain` |

---

## License

[MIT](LICENSE)