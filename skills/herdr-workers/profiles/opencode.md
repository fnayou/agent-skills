# Profile: opencode

What a foreman needs to run an opencode worker. Every line here was seen in a run, on opencode 2.0.25.

## What it does when left alone

Started with no arguments, an opencode worker runs every shell command and makes every edit without a dialog: its default agent carries the rule "allow everything". Its help names no read-only mode and no tool list, only `--auto`, which removes what asking is left. Never pass `--auto`.

So an opencode worker gets its mode and its rules from a **configuration directory** that you write for it, outside the working tree.

## The configuration directory

Write it in a scratch directory, one per worker. It holds two files:

- `AGENTS.md` — the rules. opencode loads it as its instruction file.
- `opencode.jsonc` — the mode: permission rules.

```bash
D=<scratch directory>/opencode-<name>
/bin/mkdir -p "$D"
/bin/cat <skill directory>/worker-rules.md ~/.config/herdr-workers/operator-rules.md > "$D/AGENTS.md"
/bin/cat > "$D/opencode.jsonc" <<'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "permissions": [
    <the rules of the mode, then the allowlist>
  ]
}
EOF
```

Leave the operator rules out of the `cat` when that file does not exist.

It reaches the worker through the environment of its pane, and only when opencode runs its own server:

```bash
P=$(herdr pane split --current --direction right --cwd "$PWD" --no-focus --env OPENCODE_CONFIG_DIR="$D" \
    | python3 -c 'import sys,json;print(json.load(sys.stdin)["result"]["pane"]["pane_id"])')
herdr pane rename "$P" "opencode: <task in 2-4 words>"
herdr agent start <name> --kind opencode --pane "$P" --timeout 90000 -- --standalone
```

- `--standalone` is required. Without it the worker talks to the operator's background opencode service, which was started in another environment and does not see the directory.
- The directory is read when the worker starts. To change the mode of a reused pane, rewrite the files, then start a fresh worker there.
- A worker started this way named that `AGENTS.md` as its only instruction file: the operator's own opencode instructions were not loaded.
- These do not work: the `OPENCODE_CONFIG` variable, an `instructions` list in `opencode.jsonc`, and an agent file under the working tree's `.opencode/agents/`. An `opencode.jsonc` in the working tree does work, and is not used: it is a change to the repository.
- Do not set `XDG_CONFIG_HOME` for this: opencode follows it, and so do git and gh in every command the worker runs.

## Modes

A mode is the set of permission rules in `opencode.jsonc`. Each rule is `{ "action": …, "resource": …, "effect": … }`, where the effect is `allow`, `ask` or `deny`. When several rules match, the last one wins. Pick the least capable mode that can execute the brief.

| Mode | Rules | What it leaves | For |
|---|---|---|---|
| `read-only` | `shell * deny`, `edit * deny` | reading and searching | looking things up, reporting |
| `edit` | `shell * deny` | reading, and edits without a dialog | exact edits and new files, with no command to run |
| `ask` | `shell * ask` | edits without a dialog; every shell command not on an allowlist asks | briefs with commands: git, tests, scripts |

Written out, the rules of `ask` are:

```jsonc
{ "action": "shell", "resource": "*", "effect": "ask" }
```

- For a task where each write should be approved, add `{ "action": "edit", "resource": "*", "effect": "ask" }` to `ask`.
- `deny` removes the tool: the worker reported that it had no shell tool, and did not look for another way.
- `edit * deny` without a shell rule is no fence. A worker whose edit was denied went on to make the same change with `perl -pi` in the shell. Deny or ask the shell whenever edits are denied.
- Under `read-only` a worker read a file, and reported an edit and a shell command as refused: it had neither tool. The working tree stayed unchanged.

## Allowlists

An allowlist is a list of `allow` rules for `shell`, written after the `ask` rule so that they win.

**Standing allowlist.** Put these in every `ask` configuration:

```jsonc
{ "action": "shell", "resource": "git -C * status *", "effect": "allow" },
{ "action": "shell", "resource": "git -C * diff *", "effect": "allow" },
{ "action": "shell", "resource": "git -C * log *", "effect": "allow" },
{ "action": "shell", "resource": "git -C * show *", "effect": "allow" },
{ "action": "shell", "resource": "git -C * add *", "effect": "allow" },
{ "action": "shell", "resource": "git -C * commit -m *", "effect": "allow" }
```

- All are read-only or undone with one command. The worker rules make workers address the repository with `git -C <dir>`, which is the form these match.
- The pattern is matched against the command as the worker wrote it. Write no hook prefix in it.
- A command chained behind an allowed one still asks: `git -C <dir> status --porcelain && <another command>` raised a dialog under an allow rule for `git -C * status *`.

**Run allowlist.** Add one `allow` rule per pattern the operator approved for this run, after the standing ones. A rule for `git -C * switch -c *` and one for `python3 -m unittest` each let their command through without a dialog.

## Brief

An opencode worker takes **literal briefs** and **goal briefs**. With the rules loaded through `AGENTS.md`, the brief carries only the task: its fence, the numbered steps with their `Expect:` lines, and the report wanted.

- On a goal brief (find the cause of a failing test, fix it on a new branch, one commit, a fixed report shape) a worker on the operator's model did all of it correctly. It chose its own commands: `git branch` and then `git switch` where a literal brief would write `git switch -c`, so the run allowlist written for that form missed twice. Expect a few dialogs on a goal brief, and say in it how git is addressed and that commands run alone.
- Write each command as one short command, with absolute paths. A chain defeats the allowlist.
- Name the tool for an edit ("with your file edit tool") and give old text and new text.
- A closing line that the brief itself quotes cannot be waited for in the pane: the brief is on the screen too. Wait on the status.

## Dialogs

```text
△ Permission required

$ <the command, whole>                     (for an edit: the file name and the diff)

 Allow once   Always allow   Reject                    ⇆ select  enter confirm
```

- herdr reports `blocked` while a dialog is open. Sort the dialog with the guard rails.
- `Allow once` is selected when the dialog opens: `herdr agent send-keys <name> enter` approves this one command. `herdr agent send-keys <name> right right enter` rejects. `Always allow` is the operator's.
- After an approval herdr goes on reporting `blocked` for some seconds while the worker is already working, and `agent wait` returns at once. Wait with `herdr agent wait <name> --until idle`, or for the next dialog with `herdr pane wait-output <pane> --match "Permission required"`.
- While the worker is `blocked` only `--source visible` can be read.
- The status lags the other way too: after a worker had printed its closing line, herdr went on reporting `working`. When a wait runs long, read the pane.
- A rejected command ends the worker's turn: the pane shows `The user declined this tool call` and `interrupted`, the status becomes `idle`, and no report follows. Send the next prompt to say what to do instead.

## Start, model, end

- `agent start` returns `idle` and ready while the pane still shows the splash. Read the pane again a few seconds later, until the prompt box `Ask anything…` is there, before you send the brief.
- The line under the prompt box names the agent and the model (`Build · <model>`). The worker runs on the model the operator last used, on the operator's opencode subscription; the interactive command has no model argument.
- To end the worker and free its pane for a fresh one: `herdr agent prompt <name> '/exit'`. The pane returns to its shell prompt. herdr may answer `agent_not_running`: the worker has quit.

## Seen in runs

- A subcommand that needs the background service can hang: `opencode auth list`, from an agent's shell, ended after two minutes with `Transport: The operation timed out.` `opencode debug agents` and `opencode debug config`, run in the working directory, answered and show the permission rules and the configuration files in force for the background service; they take no `--standalone`.
- On its first shell command a worker made two failed tool calls (`Unknown tool 'shell'`, a malformed search) before it found its shell tool. No effect on the result.
- A literal brief of about 2,900 characters arrived whole through `herdr agent prompt`.

## Under Rex

Seen on Rex 0.1.0-preview.14 with opencode 2.2.7, in one probe run per step. [`../multiplexers/rex.md`](../multiplexers/rex.md) has the commands.

- **Start:** type `env -u REX_SESSION -u REX_BLOCK OPENCODE_CONFIG_DIR=<configuration directory> opencode --standalone` into the pane's shell. The status read `idle` within two seconds, with the prompt box on screen. The `permissions` rules above still applied on 2.2.7: under `shell * ask` a `touch` raised a dialog.
- **Status:** a turn ends with `idle`; no `done` was seen. At a dialog, `blocked` with `kind=permission` and the `msg` `Permission needs input`; `title` names the task. opencode writes two records, one without an `id` and one per opencode session (`id=ses_…`): read the one without an `id`.
- **Dialog:** `right right enter` rejected: `The user declined this tool call`, the status became `idle`, and no report followed. The selected option is shown by colour alone; capture with `--format=vt` before a key that matters.
- **Quit:** type `/exit` and Enter. The status records were removed and the shell came back to the foreground.
