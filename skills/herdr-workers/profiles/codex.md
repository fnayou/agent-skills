# Profile: codex

What a foreman needs to run a codex worker. Every line here was seen in a run, on codex-cli 0.162.1 unless the line names another version.

A codex worker spends the operator's codex limits, a five-hour one and a weekly one. Eight short probe prompts took 10% of the first and 2% of the second. Ask the operator before a run when they have not named codex themselves, and see **Limits** below.

## Modes

A mode is the sandbox the worker is started in, together with `--ask-for-approval on-request`: what the sandbox blocks comes up as a dialog. Pick the least capable mode that can execute the brief.

| Mode | Start arguments | Runs without a dialog | Asks or fails |
|---|---|---|---|
| `read-only` | `--sandbox read-only` | reading files, read-only commands, a test run (`python3 -m unittest`, which then writes no cache) | every edit and every command that writes asks, one dialog each |
| `workspace-write` | `--sandbox workspace-write` | edits and commands that write inside the working tree | git commands that write (`switch -c`, `add`, `commit`) fail: the sandbox keeps `.git` read-only |
| `workspace-write` with git | `--sandbox workspace-write --add-dir <working tree>/.git` | the above, and `git switch -c`, `git add`, `git commit` | — |

- Never pass `--dangerously-bypass-approvals-and-sandbox`, `--approve-for-me` or `--ask-for-approval never`: each removes the dialogs.
- `workspace-write` ends at the working tree, with one exception: the system's temporary directories. A `touch` of a file in `/private/tmp`, outside the working tree, ran with no dialog. A write to a directory beside the working tree, under the home directory, failed with `PermissionError: [Errno 1] Operation not permitted`; no dialog, and the worker stopped as its rules say.
- Under `read-only`, a command the operator or the foreman approves runs outside the sandbox, for that one time: `✔ You approved codex to run … this time`. A branch, two edits, a staging and a commit were five dialogs.
- In `workspace-write` without the `.git` directory, a blocked git command raised no dialog: it failed with `cannot lock ref`, and the worker stopped as its rules say.
- codex has no allowlist argument. The sandbox takes that place: there is no standing allowlist and no run allowlist for this kind.

## Start

```bash
herdr agent start <name> --kind codex --pane "$P" --timeout 90000 -- <mode arguments> --ask-for-approval on-request --no-alt-screen -c "developer_instructions=<the rules line>"
```

**Rules.** codex takes instructions at start through `-c developer_instructions=…`, and herdr refuses an argument of several lines (`invalid_agent_argument`). So the argument is one line that points at the rule files, and the worker reads them itself before it acts:

```text
developer_instructions=You are a worker. Before you act on any brief, read these two files in full and follow them: <skill directory>/worker-rules.md and <home directory>/.config/herdr-workers/operator-rules.md . Their rules rank above the brief.
```

- Write both paths in full, as absolute paths. Leave the operator rules out when that file does not exist.
- The worker read both files at the start of every brief, and quoted them correctly when asked.
- Any `-c` argument makes codex run without its shared background server, and shows one start-up warning that says so. Nothing else changed.
- codex also loads the operator's own `~/.codex/AGENTS.md`: `/status` names it. That it loads the operator's codex skills rests on a worker saying it applied one, unasked, to a one-word edit; no probe has shown it.

**A directory codex has not been started in** raises a dialog at start: `Trust this folder?`, with `1. Trust and continue` selected, and `2. Quit`. On 0.163.0 the second choice is `2. Back to Agent Command Center`, with the line `enter continue · esc back` below, and a directory that is not a git repository raised no dialog. The answer is saved in the operator's codex configuration, so the dialog is the operator's. Every new worktree is such a directory, and so is a repository below a directory that is already trusted: trust of the home directory did not cover a repository in it. A second worker started in the same directory raised no dialog.

- On 0.162.1 `agent start` returned `agent_not_ready` and the status was `blocked`. On 0.163.0 it returned a result with status `idle`, the dialog on screen. Read the pane after every start, before the first prompt: a prompt sent into the dialog ends with Enter, and Enter trusts the folder.
- Keys, when the operator answers through you: `herdr agent send-keys <name> enter` trusts the folder. The digit `1` did nothing, in four tries. `2` and `esc` opened codex's Agent Command Center and saved nothing, except once (0.163.0): an `esc` after a `1` ended at codex's prompt with the folder saved as trusted, where the same two keys in another try saved nothing. Offer `esc` as the declining key, and after it look for the folder in `~/.codex/config.toml` before you report the dialog as declined.
- The Agent Command Center lists the operator's codex tasks in other directories, by path and title, in the worker's pane. `herdr agent send-keys <name> C-c` ends codex there and returns the pane to its shell prompt.
- Once, on 0.163.0, the folder was saved as trusted while the dialog was still on screen and before any key reached it: 8 s after launch codex's log records the start of a session, and the configuration file was written in the same second. That start returned `agent_not_ready`. So after any start in a folder codex does not trust, look in `~/.codex/config.toml` once the dialog is gone, whatever key ended it, and tell the operator about an entry they did not give.

Read the pane after the start. codex has been seen to update itself at start and exit while herdr reported it ready, which lost the first prompt.

To end the worker and free its pane for a fresh one: `herdr agent prompt <name> '/quit'`. The pane returns to its shell prompt.

## Brief

A codex worker takes a **literal brief** or a **goal brief**. With the rules loaded, the brief carries only the task: for a literal brief its fence, the numbered steps with their `Expect:` lines, and the report wanted.

- A goal brief was seen on one small task: find the cause of a failing test, fix it on a new branch, one commit. Under `workspace-write` with git it raised no dialog and took 48 seconds; the worker chained its own checks after the commit. Harder goals have not been tried.
- Write an edit as the whole old line and the whole new line. Given only the word to change, a worker sent a patch that looked for a line holding that word alone: `apply_patch verification failed: Failed to find expected lines`, and it stopped.

- Under `read-only`, write git commands as `/usr/bin/git`. A plain `git -C <dir> status` that a hook had rewritten failed there with `Failed to create unified exec process`; `/usr/bin/git` ran, with warnings about a cache file it could not write.
- Under `workspace-write` plain `git` commands ran, hook included.

## Dialogs

For an edit:

```text
Would you like to make the following edits?
› 1. Yes, proceed (y)
  2. Yes, and don't ask again for these files (a)
  3. No, and tell Codex what to do differently (esc)
```

For a command, with the reason codex gives and the command whole:

```text
Would you like to run the following command?
› 1. Yes, proceed (y)
  2. Yes, and don't ask again for commands that start with `<command>` (p)
  3. No, and tell Codex what to do differently (esc)
```

- herdr reports `blocked` while a dialog is open. Sort the dialog with the guard rails.
- `herdr agent send-keys <name> y` approves this one edit or command. `herdr agent send-keys <name> esc` declines. Options 2 are the operator's.
- A declined command ends the worker's turn: `✗ You canceled the request`, then `Conversation interrupted`, and no report. Send the next prompt to say what to do instead.
- A dialog about a rate limit has been seen with status `idle`. Read the pane after every wait.

## Waiting

- When a turn ends herdr has reported `done` in some runs and `idle` in others. `herdr agent prompt … --wait` returns on either; `herdr agent wait <name> --until idle` alone timed out on a worker that had finished with `done`. After a dialog, wait with `herdr agent wait <name> --until done --until idle --until blocked`.
- That wait, sent straight after a key, returned `blocked` while `herdr agent get` already said `working`: the key had landed. Check `herdr agent get <name>` before you read the pane as a new dialog.

## Limits

`herdr agent prompt <name> '/status'` prints the account, the sandbox in force and both limits with what is left of each, without a model turn. herdr answers it with `agent_prompt_stalled`; read the pane. Check it before the first brief when the operator has given a budget, and give what is left in the summary.

## Seen in runs

- A worker asked which instruction files it had loaded named a file that does not exist. Its own account of its context is not evidence; a word planted in the rules and asked back is.

## Under Rex

Seen on Rex 0.1.0-preview.14 with codex-cli 0.167.1, in one probe run per step. [`../multiplexers/rex.md`](../multiplexers/rex.md) has the commands.

- **Start:** type `env -u REX_SESSION -u REX_BLOCK codex <mode arguments> --ask-for-approval on-request --no-alt-screen -c '<the rules line>'` into the pane's shell, with the rules line in single quotes. The status read `idle` within two seconds; a trusted directory raised no dialog. The footer shows what is left of both limits (`5h 62% left · weekly 94% left`), which a capture reads without `/status`.
- **Status:** `done` at the end of a turn; `blocked` with `kind=permission` at a dialog, with an empty `msg`: capture the pane to read the command.
- **Dialog:** `esc` declined: `Conversation interrupted`, the status became `idle`, and no report followed.
- **Sandbox:** under `read-only`, a `touch` of a file in `/private/tmp` failed with `Operation not permitted` and raised no dialog; the worker stopped as its rules say. A `rex` command under the same sandbox raised a dialog.
- **Quit:** type `/quit` and Enter. The status records were removed and the shell came back to the foreground.
- Started with the foreman's `REX_SESSION`, a worker asked to run `rex session rename "$REX_SESSION" agent-skills-gate0` before it read its brief, following Rex's start-up instruction. That is why the start line unsets both ids and the worker rules leave the multiplexer to the foreman.
