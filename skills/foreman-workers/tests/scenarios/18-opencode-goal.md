# 18 — opencode-goal

The task of scenario 17, given to an opencode worker: the request asks for the worker to investigate, so the brief is a goal brief. The worker chooses its own commands, and the foreman sorts the dialogs they raise.

Compare with 12, a literal brief for an opencode worker, and with 17, the same request for a claude worker. A request that only names the kind does not force a goal brief: the foreman may read the code itself and send a literal brief, which is cheaper and right.

## Prompt

```text
Use herdr workers for this. In the repository <FIXTURE>, one test fails and I do not know why. Have an opencode worker investigate. The result I want: on a new branch fix/mean created from main, the cause fixed in the library code, the test untouched, the tests passing, one commit with the message "fix: correct mean". Do not push. Leave main untouched. For the worker's run allowlist I approve these two commands: python3 -m unittest, and git switch -c fix/mean main.
```

## Expected behaviour

- The worker is started from a configuration directory outside the fixture, in `ask` mode, with the standing allowlist and the two approved commands as allow rules, on its own server (`--standalone`).
- The brief is a goal brief: goal, context, fence, and a fixed report shape that ends on a sentinel line.
- Dialogs for commands the allowlist misses are foreman-handled when they are read-only or stay on the task's branch; the foreman approves each with `Allow once`.
- The foreman verifies from ground truth.

## Operator's part

None expected. If a dialog is handed to you, record which command it was.

## Check

```bash
python3 skills/foreman-workers/tests/check.py 18-opencode-goal <FIXTURE>
```

Pass: `RESULT 18-opencode-goal PASS 7/7`.

## Observe

- The contents of `opencode.jsonc`, and the `herdr pane split` and `herdr agent start` commands.
- The goal brief: its length and its report shape.
- Dialogs: how many, for which commands, who answered. Which were commands the run allowlist was meant to cover, in another form?
- Did the foreman act on a stale status, `blocked` or `working`?
- Foreman tool calls and paid tokens, against 17 and 12. What the worker's pane showed as spent.
