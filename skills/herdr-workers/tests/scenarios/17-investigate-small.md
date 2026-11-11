# 17 — investigate-small

The request asks for a paid worker to investigate, and says nothing about who makes the change. What the worker finds is a one-line fix. The worker that found it should make it: a runbook for a second worker costs more than the fix.

Compare with 08, where the request itself asks for the two stages, and with 15, where the request names no kind and the foreman may read the code itself.

## Prompt

```text
Use herdr workers for this. In the repository <FIXTURE>, one test fails and I do not know why. Have a claude worker investigate. The result I want: on a new branch fix/mean created from main, the cause fixed in the library code, the test untouched, the tests passing, one commit with the message "fix: correct mean". Do not push. Leave main untouched.
```

## Expected behaviour

- One run: a Claude Code worker on a goal brief finds the cause and, the change being small, makes the fix itself, with the test run and the commit.
- No runbook is written, and no second worker is started to execute one.
- The foreman verifies from ground truth.

## Operator's part

A trust dialog may appear when the Claude Code worker starts. Answer nothing else unless the foreman hands you a dialog.

## Check

```bash
python3 skills/herdr-workers/tests/check.py 17-investigate-small <FIXTURE>
```

Pass: `RESULT 17-investigate-small PASS 7/7`.

## Observe

- How many runs, which kinds, which brief types. Was a runbook written?
- What the goal brief said about the size of the change and about who makes it.
- Paid tokens of the foreman and of the worker, together, against 08 (about 13,700 output tokens) and 09 (about 9,000).
- Dialogs: how many, who answered.
