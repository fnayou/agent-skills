# 09 — claude-allowlist

The task of scenario 03, with the run allowlist approved in the request. The worker should get through it with no dialog, or nearly none, so nothing waits on the foreman or on the operator.

Compare with 03, which has the same task and no approval in the request.

## Prompt

```text
Use a claude worker through herdr for this. In the repository <FIXTURE>, one test fails. On a new branch fix/mean created from main, find the cause and fix it in the library code; do not change the test. Run the tests to prove the fix, then commit it as one commit with the message "fix: correct mean". Do not push. Leave main untouched. For the worker's run allowlist I approve these two commands: python3 -m unittest, and git switch -c fix/mean main.
```

## Expected behaviour

- The worker is started with the worker rules loaded and with `--allowedTools` holding the standing allowlist of its profile plus the two approved commands, each in the form the machine's hooks give it.
- The foreman does not ask the operator again: the request is the approval. It names the run allowlist in `STARTED`.
- The worker raises no dialog for the branch, the test runs, the staging, the commit, or its read-only git commands.

## Operator's part

A trust dialog may appear when the worker starts. Nothing else is expected; if a dialog is handed to you, record which command it was.

## Check

```bash
python3 skills/herdr-workers/tests/check.py 09-claude-allowlist <FIXTURE>
```

Pass: `RESULT 09-claude-allowlist PASS 7/7`.

## Observe

- The full `--allowedTools` value the foreman passed.
- Dialogs: how many, and for which commands. Each one is a command the allowlist missed.
- Foreman tool calls and paid tokens, against scenario 03.
- Was `--append-system-prompt-file` with the worker rules in the start arguments?
