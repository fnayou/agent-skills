# 01 — pi-literal

A pi worker executes a short literal brief with no surprises. This is the cheapest path the skill has and the baseline for every cost comparison.

## Prompt

```text
Use a pi worker through herdr for this. In the repository <FIXTURE>, on a new branch fix/readme created from main: in README.md change the word "recieve" to "receive" and change "Version: 0.1.0" to "Version: 0.1.1". Commit both changes as one commit with the message "docs: fix typo and bump version". Do not push. Leave main untouched.
```

## Expected behaviour

- The foreman looks up the facts itself, then sends one literal brief to one pi worker in its own labelled pane.
- The worker makes one commit on `fix/readme`.
- The foreman verifies the diff and the commit itself, closes the pane and reports.

## Operator's part

None. No dialog is expected.

## Check

```bash
python3 skills/herdr-workers/tests/check.py 01-pi-literal <FIXTURE>
```

Pass: `RESULT 01-pi-literal PASS 8/8`.

## Observe

- Did the foreman change any file or run any state-changing command itself?
- Number of prompts sent to the worker, and whether any step was retried.
- Was the pane labelled, and closed at the end?
- Was every worker event reported in a block, and a summary given?
