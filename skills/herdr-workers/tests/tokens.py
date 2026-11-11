#!/usr/bin/env python3
"""Total the paid tokens of one agent session, from the file the agent itself writes.

Usage: python3 skills/herdr-workers/tests/tokens.py claude <session.jsonl>
       python3 skills/herdr-workers/tests/tokens.py codex <rollout.jsonl>

Claude Code writes one file per session under ~/.claude/projects/<directory-slug>/.
Codex writes one file per session under ~/.codex/sessions/<year>/<month>/<day>/.
A pi worker on a local model spends no paid tokens and has nothing to total.
"""
import json
import sys

CLAUDE_FIELDS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
CODEX_FIELDS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens")


def records(path):
    with open(path) as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def claude(path):
    # One message is written on several lines with the same id and the same
    # usage, so keep one usage per message id.
    usage = {}
    for record in records(path):
        message = record.get("message")
        if isinstance(message, dict) and isinstance(message.get("usage"), dict) and message.get("id"):
            usage[message["id"]] = message["usage"]
    totals = {field: sum(int(item.get(field) or 0) for item in usage.values()) for field in CLAUDE_FIELDS}
    return {"messages": len(usage), **totals}


def codex(path):
    # Each token_count event carries the running total of the session.
    totals = {}
    for record in records(path):
        payload = record.get("payload")
        if record.get("type") == "event_msg" and isinstance(payload, dict) and payload.get("type") == "token_count":
            totals = (payload.get("info") or {}).get("total_token_usage") or totals
    return {field: int(totals.get(field) or 0) for field in CODEX_FIELDS}


def main():
    readers = {"claude": claude, "codex": codex}
    if len(sys.argv) != 3 or sys.argv[1] not in readers:
        sys.exit(__doc__)
    totals = readers[sys.argv[1]](sys.argv[2])
    print("TOKENS", sys.argv[1], " ".join(f"{name}={value}" for name, value in totals.items()))


if __name__ == "__main__":
    main()
