# Profile: claude

What a foreman needs to run a Claude Code worker. Every line here was seen in a run.

## Modes

A mode is the permission mode the worker is started in. Choose it at start: without one, a Claude Code worker starts in the operator's default permission mode, which may be an auto mode that never asks.

| Mode | Start arguments | What still asks | For |
|---|---|---|---|
| `acceptEdits` | `--permission-mode acceptEdits` | every shell command not on an allowlist | ordinary code tasks — the operator's stated preference |
| `default` | `--permission-mode default` | every write and every shell command not on an allowlist | tasks where each write should be approved, and tasks with destructive steps |

## Start

```bash
herdr agent start <name> --kind claude --pane "$P" --timeout 90000 -- <mode arguments> --append-system-prompt-file <skill directory>/worker-rules.md --allowedTools "<patterns, comma-separated>"
```

Start it without a `--name <name>` argument.

**Rules.** `--append-system-prompt-file <skill directory>/worker-rules.md` loads the worker rules. The operator's own rules need no argument: a Claude Code worker runs under the operator's Claude settings. Started with no tools, so that it could not read a file, a worker quoted word for word sentences of the operator's global `CLAUDE.md` and of a file it imports, and the line of the operator's start-up hook. It also named the operator's memory file for that working directory as loaded. In a repository with a `CLAUDE.md` of its own, the same probe quoted that file's first line beside the operator's global instructions: a worker gets both.

**Standing allowlist.** Pass these patterns at every start:

```text
Bash(git status *),Bash(git diff *),Bash(git log *),Bash(git show *),Bash(git add *),Bash(git commit -m *)
```

and the same six with `git -C *` for a worker that addresses its repository by path: `Bash(git -C * status *)`, and so on.

- All are read-only or undone with one command. `git commit -m *` also lets through `git commit -m <message> --amend` on the worker's own unpushed commit.
- A pattern is matched against the command after the machine's hooks have rewritten it. Where a hook puts a prefix in front of commands, the pattern needs the same prefix: the machine file names it.
- A pattern also matches its command with no arguments, and a `*` in the middle of a pattern matches any text there.

**Run allowlist.** Add the patterns the operator approved for this run to the same `--allowedTools` value. Typical ones: the test command, `git switch -c <branch> <base>`, `git push -u origin <branch>`, `gh pr create *`.

For a goal brief, read the ticket before you propose the run allowlist, and add the read-only commands of the tools it names: for a CI or pull request task `gh pr view *`, `gh pr checks *`, `gh run view *`, `gh run list *`, `git fetch origin *`; the project's linter in its check form; the project's task runner, for the tasks the ticket names. Most of a goal-brief worker's dialogs come from these, not from git.

**As planner.** To have it investigate and draft a runbook for pi, name a scratch directory outside the working tree and add `--add-dir <that directory>`: with `acceptEdits` it then writes the runbook there without a dialog. In the goal brief, fence it to reading the repository and writing that one file, give it the runbook shape (numbered steps, one command or exact edit each, an `Expect:` line per step, commands in fenced blocks), and have it end its report with the path of the file.

To end the worker and free its pane for a fresh one: `herdr agent prompt <name> '/exit'`. The pane returns to its shell prompt. A pane that is about to be closed needs no exit.

## Brief

A Claude Code worker takes **goal briefs** and literal briefs. With the rules loaded, the brief carries the task: goal, context, the fence particular to it, the report shape.

Put this in every brief: read files with the Read tool, create and change them with the Write and Edit tools, search with the Grep and Glob tools, and keep each Bash call to one short command — no heredocs, no chains, no pipes, no `cd` in front. A short single command is what an allowlist pattern can match, and what can be read in a dialog; a dialog you cannot read is declined. The worker rules name `/bin/cat` for kinds that have no read tool; a claude worker reads with Read.

The line in the brief does not hold on its own: workers that had it still chained a quarter of their commands (**Seen in runs**). Expect those dialogs, and sort each one with the guard rails as usual.

## Dialogs

It asks before each shell command that no allowlist covers, with status `blocked`; it has also been seen at a dialog with status `idle`, so read the pane after every wait. Sort each dialog with the guard rails.

- Before approving a run of code the worker wrote (its new test, its script), read that code on disk.
- A directory Claude Code has never been started in raises a trust dialog at start: `agent start` returns `agent_not_ready`, and the selected answer is "No, exit". A new worktree counts as such a directory only when its repository was never trusted: started in a new worktree of a repository whose main checkout had been trusted, a worker raised no dialog. The dialog is outside the brief, so it is the operator's.

## Seen in runs

- Without an allowlist, dialogs add up: 6 to 10 for a one-line fix with a test run, about 15 for a small code-plus-test task.
- With an allowlist, goal briefs still raise many: 18 to 55 foreman-handled dialogs per run on one project's goal briefs in `acceptEdits` on 2026-10-23. The foreman had passed the standing allowlist with its hook-prefixed twins and a run allowlist for tests, branch, push and pull request, and every brief carried the one-command line. Of 1325 Bash calls in the ten heaviest worker sessions: 29% matched the allowlist; 26% were chains, pipes or heredocs; 6% read or searched files through `grep`, `sed -n` or `cat`; 39% were single commands of the task's own tools that no pattern covered (`gh pr`, `gh api`, `gh run`, `git fetch`, `git ls-remote`, `docker`, the linter, the task runner).
- After about four approvals in a row, a foreman's own permission check has refused its next key press in the worker pane. The run then waits for the operator. An allowlist that covers the routine commands avoids the dialogs that lead there.

## Under Rex

Seen on Rex 0.1.0-preview.14 with Claude Code 2.1.311, in one probe run per step. [`../multiplexers/rex.md`](../multiplexers/rex.md) has the commands.

- **Start:** type `env -u REX_SESSION -u REX_BLOCK claude <mode arguments> --append-system-prompt-file <skill directory>/worker-rules.md --allowedTools "<patterns>"` into the pane's shell. The status read `idle` within two seconds; a trusted directory raised no dialog.
- **Status:** `working`, with `msg` naming the action in progress; `done` at the end of a turn; `blocked` with `kind=permission` at a dialog, with the request in `msg` (`approve Bash: touch …`).
- **Dialog:** the options read `1. Yes`, `2. Yes, and always allow access to <directory> from this project`, `3. Yes, and switch to auto mode`, `4. No`. Options 2 and 3 are the operator's. The key `4` declined: the turn ended `Interrupted`, the status became `idle`, and no report followed.
- **Quit:** type `/exit` and Enter. The status records were removed and the shell came back to the foreground.
- Started with the foreman's `REX_SESSION`, a worker received Rex's start-up instruction to rename the session, and did not act on it in that run.
