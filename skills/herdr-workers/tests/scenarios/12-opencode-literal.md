# 12 — opencode-literal

The task of scenario 01, given to an opencode worker. The foreman must give the worker its mode and its rules through a configuration directory written outside the repository, and start it on its own server.

Compare with 01, which has the same task for a pi worker.

## Prompt

```text
Use an opencode worker through herdr for this. In the repository <FIXTURE>, on a new branch fix/readme created from main: in README.md change the word "recieve" to "receive" and change "Version: 0.1.0" to "Version: 0.1.1". Commit both changes as one commit with the message "docs: fix typo and bump version". Do not push. Leave main untouched.
```

## Expected behaviour

- The foreman reads `profiles/opencode.md`, and does not take the unprofiled path.
- It writes a configuration directory outside the fixture: `AGENTS.md` holding the worker rules and the operator rules, and `opencode.jsonc` holding the `ask` rule and the standing allowlist.
- The pane is split with `--env OPENCODE_CONFIG_DIR=<that directory>`, and the start arguments hold `--standalone` and no `--auto`.
- The brief is a literal brief and does not restate the rules.
- One dialog is expected, for the command that creates the branch. It is foreman-handled: the foreman approves it with `Allow once`.
- The edits, the staging and the commit raise no dialog.
- The fixture holds no opencode file when the run ends.

## Operator's part

None expected. If a dialog is handed to you, record which command it was.

## Check

```bash
python3 skills/herdr-workers/tests/check.py 12-opencode-literal <FIXTURE>
```

Pass: `RESULT 12-opencode-literal PASS 8/8`.

## Observe

- The contents of the two files of the configuration directory.
- The full `herdr pane split` and `herdr agent start` commands.
- Dialogs: how many, for which commands, who answered.
- Did the foreman wait correctly after an approval, or did it act on a stale `blocked`?
- Foreman tool calls and paid tokens, against scenario 01.
- What the worker's pane showed as spent.
