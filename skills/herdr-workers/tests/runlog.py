#!/usr/bin/env python3
"""Total the run log a foreman keeps: runs, days covered, brief types, dialogs, paid tokens.

Usage: python3 skills/herdr-workers/tests/runlog.py [<run-log.md>]

The default file is ~/.config/herdr-workers/run-log.md. Rows whose tree starts
with "hw-fixture" are scenario runs and are counted apart. A row without the
eleven fields is listed as malformed, with its line number, and left out of
every total.

The multiplexer of a run is read from its foreman's session file: the one
whose panes it split or whose workers it started. A row whose session file
is not found counts as unknown.

Paid tokens come from the session files Claude Code writes. The foreman's are
exact: its session id is in the row. A claude worker's session is found by
where and when it ran: the same directory as the foreman, or a worktree of
it, and started while the foreman session was open. Another Claude Code
session opened there by hand in that time is counted too. Sessions of codex
and opencode workers are not looked up.
"""
import glob
import json
import os
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import tokens

COLUMNS = ("date", "tree", "session", "run", "kind", "brief", "mode", "result", "foreman-handled", "operator-reserved", "open")
PROJECTS = os.path.expanduser("~/.claude/projects")
FIXTURE = "hw-fixture"


def rows(path):
    """The rows of the log, and the line numbers of rows without the eleven fields."""
    good, malformed = [], []
    for index, line in enumerate(open(path), 1):
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if line.startswith("|") and cells[0][:1].isdigit():
            if len(cells) == len(COLUMNS):
                good.append(dict(zip(COLUMNS, cells)))
            else:
                malformed.append(index)
    return good, malformed


def number(text):
    digits = "".join(character for character in text.split(" ")[0] if character.isdigit())
    return int(digits or 0)


def multiplexer(path):
    """The multiplexer a foreman session drove: herdr, rex, or unknown."""
    text = "\n".join(str(call["input"].get("command", "")) for call in tool_calls(path))
    found = [name for name, sign in (("herdr", "herdr agent start"), ("rex", "rex split")) if sign in text]
    return found[0] if len(found) == 1 else "unknown"


def tool_calls(path):
    for record in tokens.records(path):
        content = (record.get("message") or {}).get("content")
        for item in content if isinstance(content, list) else []:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                yield item


def span(path):
    stamps = [record["timestamp"] for record in tokens.records(path) if record.get("timestamp")]
    return (min(stamps), max(stamps)) if stamps else None


def worker_sessions(foreman, logged):
    """Session files started beside the foreman's while it was open."""
    own = span(foreman)
    found = []
    for path in glob.glob(f"{Path(foreman).parent}*/*.jsonl"):
        other = span(path)
        if Path(path).stem not in logged and own and other and own[0] <= other[0] <= own[1]:
            found.append(path)
    return found


def add(total, usage):
    for field in tokens.CLAUDE_FIELDS:
        total[field] += usage[field]


def show(total):
    return " ".join(f"{field}={total[field]}" for field in tokens.CLAUDE_FIELDS)


def main():
    path = sys.argv[1] if len(sys.argv) == 2 else os.path.expanduser("~/.config/herdr-workers/run-log.md")
    if len(sys.argv) > 2 or not os.path.isfile(path):
        sys.exit(__doc__)
    every, malformed = rows(path)
    real = [row for row in every if not row["tree"].startswith(FIXTURE)]
    print("ROWS", len(every), "real", len(real), "fixture", len(every) - len(real), "malformed", len(malformed))
    for index in malformed:
        print("  MALFORMED line", index)
    if not real:
        return
    days = sorted(row["date"] for row in real)
    print("DAYS", days[0], days[-1], (date.fromisoformat(days[-1]) - date.fromisoformat(days[0])).days + 1)
    for name in ("result", "brief", "kind"):
        print(name.upper(), " ".join(f"{value}={count}" for value, count in sorted(Counter(row[name] for row in real).items())))
    print(
        "DIALOGS foreman-handled", sum(number(row["foreman-handled"]) for row in real),
        "operator-reserved", sum(number(row["operator-reserved"]) for row in real),
    )
    unresolved = [row for row in real if row["open"] != "-" and "resolved" not in row["open"]]
    print("OPEN", len(unresolved))
    for row in unresolved:
        print("  ", row["date"], row["tree"], "run", row["run"], row["open"])

    driven = {}
    for row in real:
        if row["session"] not in driven:
            files = glob.glob(f"{PROJECTS}/*/{row['session']}.jsonl")
            driven[row["session"]] = multiplexer(files[0]) if files else "unknown"
        row["multiplexer"] = driven[row["session"]]
    print("MULTIPLEXER", " ".join(f"{value}={count}" for value, count in sorted(Counter(row["multiplexer"] for row in real).items())))
    print("OPEN rex", sum(row in unresolved for row in real if row["multiplexer"] == "rex"))

    logged = {row["session"] for row in real if row["session"] not in ("", "-")}
    foreman_total, worker_total, missing, workers = Counter(), Counter(), 0, 0
    for session in sorted(logged):
        files = glob.glob(f"{PROJECTS}/*/{session}.jsonl")
        if not files:
            missing += 1
            continue
        add(foreman_total, tokens.claude(files[0]))
        for worker in worker_sessions(files[0], logged):
            workers += 1
            add(worker_total, tokens.claude(worker))
    print("SESSIONS", len(logged), "not found", missing)
    print("TOKENS foreman", show(foreman_total))
    print("TOKENS claude-workers", workers, show(worker_total))


if __name__ == "__main__":
    main()
