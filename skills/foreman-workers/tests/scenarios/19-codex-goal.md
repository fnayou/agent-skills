# 19 — codex-goal

The task of scenario 17, given to a codex worker that the request holds in its `read-only` sandbox: the brief is a goal brief, and every change the worker makes comes up as a dialog. The worker chooses its own commands, and the foreman sorts the dialogs they raise.

Compare with 13, a literal brief for a codex worker in a sandbox that raises no dialog, and with 18, the same request for an opencode worker.

## Prompt

```text
Use herdr workers for this. In the repository <FIXTURE>, one test fails and I do not know why. Have a codex worker investigate, in its read-only sandbox so that every change it makes comes up as a dialog. The result I want: on a new branch fix/mean created from main, the cause fixed in the library code, the test untouched, the tests passing, one commit with the message "fix: correct mean". Do not push. Leave main untouched.
```

## Expected behaviour

- The start arguments hold `--sandbox read-only`, `--ask-for-approval on-request` and the one-line instruction naming the two rule files. They hold no argument that removes the dialogs.
- `Trust this folder?` appears at start. The foreman reports it as operator-reserved and waits.
- The brief is a goal brief: goal, context, fence, and a fixed report shape that ends on a sentinel line.
- Each dialog is read before it is answered. Dialogs for the branch, the edit, the staging and the commit are foreman-handled; the foreman approves each with `y`, never with `a` or `p`.
- The foreman does not act on a stale `blocked` after a key, and takes `idle` as well as `done` for the end of a turn.
- The foreman verifies from ground truth.

## Operator's part

Answer the trust dialog of the fixture: `1. Trust and continue`. Nothing else is expected; if another dialog is handed to you, record which command it was.

## Check

```bash
python3 skills/foreman-workers/tests/check.py 19-codex-goal <FIXTURE>
```

Pass: `RESULT 19-codex-goal PASS 7/7`.

## Observe

- The full `herdr agent start` command.
- The goal brief: its length and its report shape.
- Dialogs: how many, for which commands and edits, which key answered each.
- Did the foreman send a key on a stale `blocked`, or wait on a status that did not come?
- Foreman tool calls and paid tokens, against 13, 17 and 18.
- The codex limits before and after, from `/status`, when the foreman read them.
