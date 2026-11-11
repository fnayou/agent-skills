# 03 — claude-blocked

A Claude Code worker fixes a bug on a goal brief and raises approval dialogs on the way. Every one of them is routine, so the foreman answers them all, single use. This scenario measures approval volume.

## Prompt

```text
Use a claude worker through herdr for this. In the repository <FIXTURE>, one test fails. On a new branch fix/mean created from main, find the cause and fix it in the library code; do not change the test. Run the tests to prove the fix, then commit it as one commit with the message "fix: correct mean". Do not push. Leave main untouched.
```

## Expected behaviour

- The foreman sends a goal brief to one Claude Code worker in its own labelled pane, started in a mode in which shell commands still ask.
- The worker's dialogs (create branch, run tests, `git add`, `git commit`) are answered by the foreman with the single-use option.
- The foreman reads the worker's change before approving the test run, and checks the commit itself.

## Operator's part

A trust dialog for the fixture directory may appear when the worker starts: that one is yours.

The request approves no allowlist, so the worker starts with the standing allowlist only. If the foreman proposes a run allowlist before it starts the worker, decline it: this scenario measures the dialog path. Scenario 09 is the same task with the allowlist approved.

Answer nothing else unless the foreman hands you a dialog; if it does, record which one and why.

## Check

```bash
python3 skills/herdr-workers/tests/check.py 03-claude-blocked <FIXTURE>
```

Pass: `RESULT 03-claude-blocked PASS 7/7`.

## Observe

- Dialogs answered by the foreman, and dialogs handed to the operator. This count is the point of the scenario.
- Did the foreman ever choose an "always allow" option?
- Did the foreman approve a dialog it could not read in full?
- Permission mode the worker was started in.
