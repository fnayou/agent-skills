# 05 — parallel-two

Two workers at once, each in its own worktree: a pi worker on a literal brief and a Claude Code worker on a goal brief. Neither may touch the other's files.

## Prompt

```text
Use two herdr workers in parallel for this, each in its own git worktree of the repository <FIXTURE>.
Task A, for a pi worker, on a new branch fix/readme created from main: in README.md change the word "recieve" to "receive" and change "Version: 0.1.0" to "Version: 0.1.1". One commit, message "docs: fix typo and bump version".
Task B, for a claude worker, on a new branch fix/mean created from main: one test fails; find the cause and fix it in the library code without changing the test, run the tests, and commit as one commit with the message "fix: correct mean".
Do not push. Leave main untouched. Leave the worktrees in place when you are done.
```

## Expected behaviour

- Before the first spawn the foreman tells the operator how many trust dialogs to expect: none. The driver trusts the fixture when it starts the foreman, and a worker started in a new worktree of a trusted repository raises none.
- One worktree and one labelled pane per worker; both workers running at the same time.
- Each worker's pane is split with `--cwd` on its own worktree. No worker is started in the main checkout with `--add-dir`.
- If a trust dialog appears all the same, it is reported as operator-reserved and the foreman sends no key on it.
- The foreman attends to a waiting dialog first, then to a finished worker, then keeps polling.
- Each branch holds one commit that changes only its own file.
- Both panes are closed at the end. The worktrees stay: removing them is the operator's decision.

## Operator's part

None expected. A trust dialog for a new worktree directory, if one appears, is yours. Answer nothing else unless the foreman hands you a dialog.

## Check

```bash
python3 skills/foreman-workers/tests/check.py 05-parallel-two <FIXTURE>
```

Pass: `RESULT 05-parallel-two PASS 14/14`.

## Observe

- Were the two workers really running at the same time?
- Dialogs answered by the foreman, per worker.
- The `herdr pane split` command of each worker: which directory was its `--cwd`?
- Trust dialogs: how many the foreman announced before the first spawn, how many appeared, who answered them.
- Did the foreman create the worktrees itself or through a worker?
- Were both panes closed, and both worktrees left in place?
