# Run log

Copy this file to `~/.config/foreman-workers/run-log.md` to have every run recorded. A foreman adds one row per run after its summary; without the file nothing is recorded. `python3 skills/foreman-workers/tests/runlog.py`, run from the root of the agent-skills repository, totals it.

The last column is yours. Replace `-` with a few words when a result turned out wrong later or a guard rail did not hold, and add the word `resolved` once it is dealt with.

| date | tree | session | run | kind | brief | mode | result | foreman-handled | operator-reserved | open |
|---|---|---|---|---|---|---|---|---|---|---|
