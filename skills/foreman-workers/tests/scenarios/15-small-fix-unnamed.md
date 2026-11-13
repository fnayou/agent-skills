# 15 — small-fix-unnamed

The task of scenarios 03, 08 and 09, with the choice of workers left to the foreman. The change is one line, so nobody should plan it for somebody else: no paid worker drafts a runbook that a second worker then executes.

Compare with 08, where the request asks for the two stages, and with 09, where it names a claude worker.

## Prompt

```text
Use herdr workers for this. In the repository <FIXTURE>, one test fails. On a new branch fix/mean created from main, find the cause and fix it in the library code; do not change the test. Run the tests to prove the fix, then commit it as one commit with the message "fix: correct mean". Do not push. Leave main untouched.
```

## Expected behaviour

- One of two paths, both right:
  - the foreman reads the test and the library code itself, finds the cause, and gives a pi worker a literal brief; or
  - one paid worker on a goal brief finds the cause and makes the fix itself, test run and commit included.
- Not this: a paid worker writes a runbook and a second worker executes it.
- The foreman verifies from ground truth.

## Operator's part

A trust dialog may appear when a Claude Code worker starts. Answer nothing else unless the foreman hands you a dialog.

## Check

```bash
python3 skills/foreman-workers/tests/check.py 15-small-fix-unnamed <FIXTURE>
```

Pass: `RESULT 15-small-fix-unnamed PASS 7/7`.

## Observe

- Which path was taken: how many runs, which kinds, which brief types.
- Was a runbook written? By whom?
- Paid tokens of the foreman and of every paid worker, against 08 (about 13,700 output tokens together) and 09.
- Dialogs: how many, who answered.
