# 08 — plan-then-execute

The chain for work whose scope is not known in advance: a paid worker investigates and drafts a runbook, the foreman reviews it, a pi worker executes it. The foreman changes nothing itself at any point.

The fixture is small, so the prompt asks for the two stages outright; the scenario tests the mechanics of the chain, not the foreman's choice to use it.

## Prompt

```text
Use herdr workers for this, in two stages. In the repository <FIXTURE>, one test fails. Stage 1: have a claude worker investigate and write a runbook for the fix; it must change nothing in the repository. Stage 2: review the runbook, then have a pi worker execute it. The result wanted: on a new branch fix/mean created from main, the library code fixed, the test untouched, the tests passing, one commit with the message "fix: correct mean". Do not push. Leave main untouched.
```

## Expected behaviour

- Run 1: a Claude Code worker on a goal brief, started with a scratch directory outside the repository allowed for writing. It reads the repository and writes one runbook file there.
- The foreman reads the runbook whole and runs its read-only commands before anything else happens.
- Run 2: a pi worker in `full` mode executes the runbook: branch, edit, test run, one commit.
- The foreman verifies from ground truth and reports two runs.

## Operator's part

A trust dialog may appear when the Claude Code worker starts. Answer nothing else unless the foreman hands you a dialog; if it does, record which one and why.

## Check

```bash
python3 skills/herdr-workers/tests/check.py 08-plan-then-execute <FIXTURE>
```

Pass: `RESULT 08-plan-then-execute PASS 7/7`.

## Observe

- Did the foreman change anything itself: an edit in the repository, a `git` command with an effect? Expected: nothing.
- Where the runbook was written, and by whom.
- Did the foreman correct the runbook before giving it to pi, and how: by a new prompt to the planner, or by writing a corrected file itself outside the repository?
- Dialogs raised by the planner. Expected: none for writing the runbook.
- Paid tokens of the planner against the Claude Code worker of scenario 03, which does the whole fix itself.
