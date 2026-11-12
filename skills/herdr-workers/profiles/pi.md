# Profile: pi

What a foreman needs to run a pi worker. Every line here was seen in a run.

## Modes

A mode is the tool set pi is started with. It bounds what the worker can do, whatever its brief says. Pick the least capable mode that can execute the brief; when unsure, `read-only`.

| Mode | Start arguments | Tools it leaves | For |
|---|---|---|---|
| `read-only` | `--tools read,grep,find,ls` | read, grep, find, ls | looking things up, classifying, reporting |
| `edit` | `--exclude-tools bash` | read, edit, write | exact edits and new files, with no command to run |
| `full` | none | read, bash, edit, write | briefs with commands: git, tests, scripts |

- `full` has no fence of its own: inside the shell tool pi runs anything. Its only gate is the brief.
- A brief that moves, overwrites or deletes many files needs the operator's approval of its commands before a `full` worker is started.

## Start

```bash
herdr agent start <name> --kind pi --pane "$P" --timeout 90000 -- --name <name> <mode arguments> <rule arguments>
```

**Rule arguments** load the rules into the worker, so the brief need not repeat them:

- `--append-system-prompt <skill directory>/worker-rules.md` — always. The skill directory is the one this profile was read from.
- `--append-system-prompt ~/.config/herdr-workers/operator-rules.md` — when that file exists. Check first: a path that does not exist is appended as plain text.

pi loads the project's `CLAUDE.md` / `AGENTS.md` by itself. It does not load the operator's global Claude instructions, which is why operator rules are injected.

**Another model:** add `--provider <p> --model <m>`. The default model comes from `~/.pi/agent/settings.json`; use another when the default is too weak or its server is down. `pi --list-models` lists what is configured.

To end the worker and free its pane for a fresh one: `herdr agent prompt <name> '/quit'`. The pane returns to its shell prompt. A pane that is about to be closed needs no quit.

## Brief

A pi worker on the default local model takes a **literal brief**, and only that. A goal brief goes to pi only on a model the operator named for goal briefs in `~/.config/herdr-workers/machine.md`; none is named by default. With the rules loaded, the brief carries only the task: the fence particular to this task, the numbered steps with their `Expect:` lines, and the report wanted.

A local model commits more often than told, inventing messages for intermediate steps. The worker rules cover it; keep one commit command per commit you want.

## Dialogs

pi has no permission dialogs and no question tool. It runs every command it is given and never reaches `blocked`. When it needs a decision it stops and asks in plain text, with status `idle`. With no dialog to spare it, pi has no standing allowlist and no run allowlist.

So a pi worker is held by its mode and its brief:

- Put the gate in the brief ("before step N, stop and ask: …"), relay its question to the operator, and send their answer as the next prompt to the same worker.
- Write no operator-reserved command into a pi brief unless the operator approved that exact command.
- For a task with destructive steps, prefer a kind that asks.

## Seen in runs

- `agent_prompt_stalled` or a timeout can mean the model server is down, not that the prompt was lost. Read the pane before resending.
- A worker that goes `idle` after long reasoning, with no command run and no edit made, may have hit the model's output cap rather than lost its way. Look at the last assistant entry of its session under `~/.pi/agent/sessions/`: `"stopReason":"length"` means the reply was cut at the cap. The cap is the model's `maxTokens` in `~/.pi/agent/models.json`. A model with thinking on spent the whole cap thinking: 45 replies of 48 that stopped at a cap of 8192 held only thinking, with no tool call. Raise `maxTokens` before you shorten the brief: shortening did not help, and raising the cap to 65536 ended the stops. Changing `models.json` is the operator's.
- Its closing summary can misquote an output it printed correctly a few lines above. Read the raw output.
- With an output-condensing hook active, `git commit` prints `ok <hash>`. Write `Expect:` lines that hold either way ("no error"), or the worker reports a mismatch on a correct commit.

## Under Rex

Seen on Rex 0.1.0-preview.14 with pi 1.5.2, in one probe run per step. [`../multiplexers/rex.md`](../multiplexers/rex.md) has the commands.

- **Start:** type `env -u REX_SESSION -u REX_BLOCK pi --name <name> <mode arguments> <rule arguments>` into the pane's shell. The status read `idle` within two seconds.
- **Status:** `app=pi`, with the process named `node`: tell a pi worker by `app`. `msg` holds the worker's name, not its action. A turn ends with `done`.
- **A question ends with `done` too.** pi asked its question in plain text and the status went to `done`, as for a finished brief. Tell them apart by the closing line the brief names: a reply without it is a question or a stop, and its next prompt is the answer.
- **Quit:** type `/quit` and Enter. The status records were removed and the shell came back to the foreground.
