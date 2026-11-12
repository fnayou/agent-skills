# Multiplexer: Rex

How a foreman runs workers in Rex panes. The loop in [`../SKILL.md`](../SKILL.md) says what each step does; this file gives the Rex commands for it. Every line was seen on Rex 0.1.0-preview.14 (API revision 12) unless it names another version. `rex COMMAND --help` and `rex api describe METHOD` are the authority for CLI syntax.

Rex support is a **preview**: it has passed a probe of every kind, not yet the scenario suite and real runs.

You are inside Rex when `REX_SESSION` is set. It names your session and `REX_BLOCK` your pane. In the CLI a tab is a **window** and a pane is a **block**; pass full ids (`block:…`, `window:…`), since labels and id suffixes can match more than one.

## Find where the project lives

An operator keeps one Rex session with a tab per project. `rex session inspect "$REX_SESSION" --json` lists the tabs under `windows`, each with its `window_id`, `label` and `focused_block_id`; `rex block call -s "$REX_SESSION" -b <block> pwd` gives a pane's working directory. The project's tab is the one whose label names the project or whose panes work in the task's working tree. Your own tab is the `window_id` of `rex block inspect -s "$REX_SESSION" "$REX_BLOCK" --json`.

When the project has no tab of its own, or it is yours, spawn beside yourself. When it is another one, stop before the spawn and give the operator two answers:

- a fresh foreman, started by the operator in that project's tab, keeps the foreman and its workers in one view. Write down what you have established for it, and end your part there;
- this foreman spawns there: split from a pane of that tab (`-b <block of that tab>`), never from `$REX_BLOCK`, which splits your own pane. A project in another session gets `-s <session>` on every command of the run; `rex ls --json` lists the sessions.

## Spawn

Split a pane that opens a shell, then type the worker's start command into it:

```bash
P=$(rex split -s "$REX_SESSION" -b <anchor block> --split=<right|below> --label "<kind>: <task in 2-4 words>" \
    --focus=false -c "$PWD" --json | python3 -c 'import sys,json;print(json.load(sys.stdin)["block_ids"][0])')
rex send -s "$REX_SESSION" -b "$P" "env -u REX_SESSION -u REX_BLOCK <start command and arguments from the profile>" && \
  rex send-key -s "$REX_SESSION" -b "$P" enter
```

- The shell stays in the pane after the worker quits, so the pane can host the next worker.
- `env -u REX_SESSION -u REX_BLOCK` keeps your session and pane ids from the worker. Rex installs a start-up hook in Claude Code and codex that tells an agent to rename `$REX_SESSION`; a codex worker that inherited the ids tried to rename the operator's session before reading its brief. With both unset the hook says nothing.
- An environment variable the profile asks for goes on the same line, before the command (`OPENCODE_CONFIG_DIR=<dir> opencode …`).
- The worker is ready when its status reads `idle` (see **Status**): every kind reported it within two seconds. Read the pane once before the first brief.
- **Reuse a pane:** relabel it with `rex block rename -s "$REX_SESSION" "$P" "<kind>: <task>"`. For a fresh worker, end the old one with the quit command in its profile, check the pane is back at its shell prompt, and type the start command again.

**Place by size.** `rex block call -s "$REX_SESSION" -b <block> size` gives a pane's `columns` and `rows`; `rex block ls -s "$REX_SESSION" -w <tab> --json` lists the panes of a tab. When no pane can be split, open a tab for the workers:

```bash
rex window new -s "$REX_SESSION" "workers: <task>" -c "$PWD" --focus=false --json
```

and start the worker in the pane it returns, `.block_ids[0]`.

## Send the brief and wait

Write the brief to a file in your scratch directory and send one line that points at it:

```bash
rex send -s "$REX_SESSION" -b "$P" "Read <brief file> and follow it exactly." && \
  rex send-key -s "$REX_SESSION" -b "$P" enter
```

One line is all `rex send` carries safely: it types the text into the worker's prompt, where a newline can submit early. Every kind read its brief file, a file outside the working tree included.

### Status

Each kind reports its own status to Rex. Read it with:

```bash
rex block call -s "$REX_SESSION" -b "$P" program_status
```

Use the record without an `id`: opencode adds a second record per opencode session. `state` is `idle`, `working`, `done` or `blocked`; a `blocked` record carries `kind=permission`. The record of the last turn stays until the worker starts the next: after a prompt, wait for `working`, then for the turn to end. **A turn has ended when the state leaves `working`**, for `done`, `idle` or `blocked`, depending on the kind and on how it ended; its profile says which. Then read the pane.

Poll every two seconds in a loop that stops before your shell tool's time limit, and start a new loop for a longer turn. `rex events -s "$REX_SESSION" --json` streams the same changes as `block_event` entries named `program_status_changed`, with the pane's `block_id`; the stream also carries your own pane and a `client_connected` for every `rex` call, so filter by the worker's pane.

### Read the pane

```bash
rex capture -s "$REX_SESSION" -b "$P" --trim | tail -n 60
```

The capture holds the screen as rendered: a markdown heading comes back without its `#`, and an option selected by colour alone looks like the others. For an exact output, have the worker print it with a command and read that, or read its session file. To see which option of a dialog is selected, capture with `--format=vt`.

Kinds rename the pane's title as they work (`π - pi-gate0 - agent-skills`, the task in a few words); the label set with `--label` is a separate field.

## Answer a dialog

- Enter the answer with `rex send-key -s "$REX_SESSION" -b "$P" <key>`, after reading the dialog to pick the key; the profile names the keys. Then wait for the status to change.
- When the operator answers in the pane, stay in the same turn: say which pane to go to, then poll the status every few seconds until it is no longer `blocked`.
- A declined dialog ends the worker's turn with `idle` and no report. Send the next prompt to say what to do instead.

## Run in parallel

- Split each worktree's pane with `-c <worktree>`, so its worker starts in that worktree.
- Prompt each worker without waiting on it, then read the status of every worker's pane in one loop and act on whichever leaves `working` first.

## Close

- A worker has quit when its status records are gone (`{"records":[]}`) and `rex block call -s "$REX_SESSION" -b "$P" process` names the shell as `foreground`.
- A pane: `rex block close -s "$REX_SESSION" "$P"`. A tab: `rex window close -s "$REX_SESSION" <tab>`, which closes all of its panes.
- Rex has no worktree command of its own; make a worktree the way the loop in `SKILL.md` says.
