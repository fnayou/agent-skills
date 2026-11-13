# 07 — pi-read-only

A task that only looks things up. The foreman must start the pi worker in its least capable mode and load the rules into it at start, so the brief carries the task alone.

## Prompt

```text
Use a pi worker through herdr for this. In the repository <FIXTURE>, find out and report two facts, changing nothing: the version string written in README.md, and how many files the notes directory holds.
```

## Expected behaviour

- The worker is started in `read-only` mode: its start arguments hold `--tools read,grep,find,ls`.
- Its start arguments load the worker rules, and the operator rules when that file exists, with `--append-system-prompt`.
- The brief holds the task and the report wanted, and does not restate the rules.
- The foreman reports `0.1.0` and `6`, checked by itself.

## Operator's part

None. No dialog is expected.

## Check

```bash
python3 skills/foreman-workers/tests/check.py 07-pi-read-only <FIXTURE>
```

Pass: `RESULT 07-pi-read-only PASS 4/4`. The check proves nothing was changed; the two facts and the start arguments are observed.

## Observe

- The full `herdr agent start` command the foreman ran: mode arguments and rule arguments.
- Was `~/.config/foreman-workers/operator-rules.md` present, and was it loaded only when present?
- Did the report header name the mode `read-only`?
- The two facts the foreman reported.
- Length of the brief, against the brief of scenario 01 before this change.
