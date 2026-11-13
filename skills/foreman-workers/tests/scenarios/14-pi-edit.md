# 14 — pi-edit

A task made of edits only, with no command to run and no commit. The foreman must start the pi worker in `edit` mode, which gives it no shell, and write a brief the worker can execute with its file tools alone.

Compare with 07, the `read-only` mode, and with 01, the same two edits in `full` mode with a commit.

## Prompt

```text
Use a pi worker through herdr for this. In the repository <FIXTURE>, make three changes and leave them uncommitted: in README.md change the word "recieve" to "receive"; in README.md change "Version: 0.1.0" to "Version: 0.1.1"; create the file CHANGELOG.md containing the single line "0.1.1 - fix typo". No commit, no branch, no command to run.
```

## Expected behaviour

- The worker is started in `edit` mode: its start arguments hold `--exclude-tools bash`.
- Its start arguments load the worker rules, and the operator rules when that file exists.
- The brief is a literal brief made of edits, each as old text and new text, and holds no shell command for the worker.
- The foreman checks the result itself, from the files and from `git status`.
- No branch, no commit.

## Operator's part

None. No dialog is expected.

## Check

```bash
python3 skills/foreman-workers/tests/check.py 14-pi-edit <FIXTURE>
```

Pass: `RESULT 14-pi-edit PASS 6/6`.

## Observe

- The full `herdr agent start` command: mode arguments and rule arguments.
- Did the brief hold a command for the worker? How did the worker report without a shell?
- Did the report header name the mode `edit`?
- Did the worker ask for a shell, or try to commit?
- Foreman tool calls and paid tokens, against scenarios 07 and 01.
