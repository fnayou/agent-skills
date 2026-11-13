# Multiplexer: herdr

How a foreman runs workers in herdr panes. The loop in [`../SKILL.md`](../SKILL.md) says what each step does; this file gives the herdr commands for it. `herdr --skill` and the bare command groups (`herdr agent`, `herdr pane`) are the authority for CLI syntax.

You are inside herdr when `HERDR_ENV=1`.

## Find where the project lives

An operator may keep each project in a workspace of one herdr session, or in a session of its own. herdr sends every command to the session named by `HERDR_SESSION`, the session of your own pane; the working directory does not choose it. A split opens in the workspace of the pane it splits. A foreman kept open from one project to the next can sit in one project's workspace or session while it works in another, and its panes then open where the operator is not looking. Before the first spawn, find where the project lives:

- `herdr workspace list`: a workspace whose `worktree.checkout_path` is the task's working tree, or whose label names the project. Your own workspace is the `workspace_id` of `herdr pane get "$HERDR_PANE_ID"`.
- only when no workspace is the project's, `herdr session list`: a `running` session whose name names the project. Yours is `$HERDR_SESSION`.

When the project has no workspace and no session of its own, or it is yours, spawn beside yourself. When it is another one, stop before the spawn and give the operator two answers:

- a fresh foreman, started by the operator in that project's workspace or session, keeps the foreman and its workers in one view. Write down what you have established for it, and end your part there;
- this foreman spawns there: split from a pane of that workspace (`herdr pane list --workspace <id>`), never with `--current`, which splits your own pane. For another session, also put `--session <name>` on every herdr command of the run, and list its panes with `herdr --session <name> pane list`.

## Spawn

Spawn as its own command, with nothing slow in front of it:

```bash
P=$(herdr pane split <pane> --direction <right|down> --cwd "$PWD" --no-focus \
    | python3 -c 'import sys,json;print(json.load(sys.stdin)["result"]["pane"]["pane_id"])')
herdr pane rename "$P" "<kind>: <task in 2-4 words>"
herdr agent start <name> --kind <kind> --pane "$P" --timeout 90000 -- <start arguments from the profile>
```

- Everything after `--` goes to the agent. An agent's option written before it is read by herdr, which refuses it: `--append-system-prompt` there failed with `unknown option`.
- Give the worker a name that matches the pane label (`pi-archive`, `cl-review`).
- `agent start` straight after `pane split` can fail because the new shell is not at its prompt yet: check the response has a `result`; if not, start again.
- **Reuse a pane:** relabel it with `herdr pane rename`. For a fresh worker, end the old one with the quit command in its profile, check the pane is back at its shell prompt, and `agent start` again.

**Place by size.** Read `herdr pane layout --pane "$HERDR_PANE_ID"`: it gives every pane of your tab with its width and height in cells. When no pane can be split, open a tab for the workers:

```bash
herdr tab create --workspace <workspace> --cwd "$PWD" --label "workers: <task>" --no-focus
```

and start the worker in the pane it returns, `.result.root_pane.pane_id`. `<workspace>` is the workspace the panes belong in, your own unless the project lives in another: without `--workspace` the tab opened in another project's workspace.

## Send the brief and wait

```bash
PROMPT=$(/bin/cat <<'EOF'
…the brief…
EOF
)
herdr agent prompt <name> "$PROMPT" --wait --timeout 540000
herdr agent read <name> --source recent-unwrapped --lines 60
```

- The quoted heredoc carries any brief intact. Call `cat` by its full path: where `cat` is an alias for a pager, `$(cat <<'EOF' …)` came back empty, and a pull request was opened with an empty body. Inside it, write worker commands as `python3 -c "…"` with single-quoted Python strings, and avoid `$`, backticks and `!` in them. Anything hairier belongs in the runbook file.
- Keep `--timeout` under your shell tool's own limit. For longer work, cut the brief at a natural stop ("do R01–R08, then STOP and wait") and send the next part as a second prompt to the same worker; its context carries over.
- `blocked` means the worker is at a dialog. `agent_prompt_stalled` or a timeout does not mean the prompt was lost: read the pane before resending.

## Answer a dialog

- Enter the answer with `herdr agent send-keys <name> <key>`, after reading the dialog to pick the right key. Then resume with `herdr agent wait <name> --timeout 540000`.
- When the operator answers in the pane, stay in the same turn: say which pane to go to, then poll `herdr agent get <name>` every few seconds until the status is no longer `blocked`.
- The first `agent wait` after `send-keys` can return a stale `blocked`: the key had landed and the worker was already working. Wait a second time, or check `herdr agent get <name>`, before concluding the dialog is still open.
- A blocked pane shows only its visible screen; scrollback cannot be read while a worker is blocked (`agent_not_idle`).

## Run in parallel

- Split each worktree's pane with `--cwd <dir>`, so its worker starts in that worktree.
- Prompt each worker without `--wait`, then poll `herdr agent list` every few seconds and act on whichever worker leaves `working` first. Let a few seconds pass after a prompt before trusting a status: a worker still reads `idle` for a moment after it was prompted.

## Close

- A pane: `herdr pane close "$P"`. A tab: `herdr tab close <tab>`.
- `herdr worktree create` runs none of a project's own worktree steps; make a worktree the way the loop in `SKILL.md` says.
