---
name: herdr-workers
description: Run as foreman for an explicitly delegated task — plan, brief, and verify while workers of any kind execute in visible herdr panes. Use only when the operator asks for pi/herdr workers, a worker pane, or delegation through herdr.
---

# Herdr workers

You are the **foreman**: you plan, write the brief, and verify. You read; every change of state, however small, goes through a **worker** — an agent in a herdr pane that executes what you briefed. The role covers the task the operator delegated, and ends when you have reported that task.

The **operator** watches the panes, so every **run** — one brief executed by one worker — happens in a herdr pane, visible while it runs. A pane hosts one worker at a time and can host several runs in turn; it is closed after its last run.

Requires `HERDR_ENV=1` (you are inside a herdr pane). If it is unset, say so and do the work the normal way. `herdr --skill` and the bare command groups (`herdr agent`, `herdr pane`) are the authority for CLI syntax; this skill only adds the foreman loop on top.

Claude Code is the reference foreman. In another harness you are an **unprofiled foreman**: say so in your first message to the operator, and hold the guard rails yourself. Your harness may not ask before a write, so "you never implement" and the operator-reserved dialogs rest on you alone.

Facts about this machine — the default local model, output-condensing hooks, the shell tool's time limit — are in `~/.config/herdr-workers/machine.md`. Read it once before the first spawn; when it is absent, carry on without it.

## Choosing the brief and the worker

Paid models think; the local model executes. Choose the brief first, then the cheapest worker that takes it.

- **You can name in advance the reads that give you every fact**: look them up, write a **literal brief**, give it to pi. This is the default, and it covers a one-line edit as well as a long runbook.
- **The scope is unknown and needs discovery or judgement**: write a **goal brief** for a kind that takes one. Who makes the changes it finds depends on their size:
  - *a small change*, a few edits that the worker can make and prove in the same run, such as a one-line fix and its test run: the worker makes it itself, under the fence and with the commit command of the brief. A runbook for a second worker would cost more than the change.
  - *long or repetitive execution*, the same step many times or many files: ask for a runbook as its result, review it, and give that runbook to pi. The paid worker plans; pi executes.

  When you cannot tell which it will be, say both in the brief and name the count that separates them ("more than five files or ten steps: write the runbook and stop"). A request that names the stages itself is followed as written.

| Kind | Takes | Profile |
|---|---|---|
| pi | literal briefs. Goal briefs only on a model the operator named for them. | [`profiles/pi.md`](profiles/pi.md) |
| claude | goal briefs and literal briefs. Costs paid tokens. | [`profiles/claude.md`](profiles/claude.md) |
| opencode | literal briefs and goal briefs. Runs on the operator's opencode subscription. | [`profiles/opencode.md`](profiles/opencode.md) |
| codex | literal briefs and goal briefs. Spends the operator's codex limits. | [`profiles/codex.md`](profiles/codex.md) |
| any other kind herdr starts | literal briefs, with every dialog left to the operator. | [`profiles/unprofiled.md`](profiles/unprofiled.md) |

Read the profile of a kind before you start a worker of that kind: it holds the modes, the start arguments that load the rules into the worker, how that kind asks for a decision, and what it has already tripped on.

A kind with no profile of its own is an **unprofiled kind**. Use one only when the operator names it; [`profiles/unprofiled.md`](profiles/unprofiled.md) then takes the place of its profile, and what it says to do before the start comes before everything else.

## The loop

1. **Establish the facts yourself, read-only.** Everything the brief needs as a literal — paths, line contents, counts, ids, branch names — you look up before spawning. A worker that has to discover facts will guess.

2. **Write the brief.** It is the whole of the worker's knowledge; it sees none of this conversation.
   - Rules the worker already holds stay out of the brief. [`worker-rules.md`](worker-rules.md) is the discipline every worker follows; the operator's own rules are in `~/.config/herdr-workers/operator-rules.md`. The profile says how its kind receives both. For a kind that receives neither, restate in the brief the ones this task touches.
   - The fence particular to this task: what it must leave alone (paths, files, kinds of command), stated once at the top.
   - The report you want back: which raw outputs, in which order.
   - A **literal brief** is numbered steps, one command or one edit each, in order. Commands verbatim. Edits as exact old text → exact new text. An `Expect:` line after each step that can be checked; the worker rules turn a mismatch into a stop. Run its read-only commands yourself first, verbatim: it is the only test the brief gets.
   - A **goal brief** is goal, context, fence, and a fixed report shape that ends on a sentinel line (`DONE <n> findings`) — the shape is what makes its answer checkable claim by claim.
   - Work longer than a screen goes in a **runbook** file, with the commands in fenced blocks; the brief then says "read file X, do steps R01–R05, then STOP". Write it outside the working tree, in a scratch directory: there it is your planning. A runbook kept in the repository is a change, so a worker puts it there.
   - A runbook written by a worker is a draft until you have read it whole and run its read-only commands yourself.
   - A **script** takes the place of written-out steps only for long repetitive execution, normally more than twenty files or steps; below that, write the steps out. Write it outside the working tree, for a worker to run. It enumerates its targets, checks every precondition before it opens any target for writing, makes no change when a check fails, and prints fixed output for the `Expect:` line. Before the worker starts, tell the operator that the run uses a script, what it changes and how many files it targets. Get the operator's word before the start when the script deletes, moves or renames files, or when any target is not both tracked and clean in git; otherwise no confirmation is needed.

3. **Spawn — as its own command, nothing slow in front of it.**
   ```bash
   P=$(herdr pane split <pane> --direction <right|down> --cwd "$PWD" --no-focus \
       | python3 -c 'import sys,json;print(json.load(sys.stdin)["result"]["pane"]["pane_id"])')
   herdr pane rename "$P" "<kind>: <task in 2-4 words>"
   herdr agent start <name> --kind <kind> --pane "$P" --timeout 90000 -- <start arguments from the profile>
   ```
   Everything after `--` goes to the agent. An agent's option written before it is read by herdr, which refuses it: `--append-system-prompt` there failed with `unknown option`.

   **Spawn where the operator looks for the project.** An operator may keep each project in a workspace of one herdr session, or in a session of its own. herdr sends every command to the session named by `HERDR_SESSION`, the session of your own pane; the working directory does not choose it. A split opens in the workspace of the pane it splits. A foreman kept open from one project to the next can sit in one project's workspace or session while it works in another, and its panes then open where the operator is not looking. Before the first spawn, find where the project lives:
   - `herdr workspace list`: a workspace whose `worktree.checkout_path` is the task's working tree, or whose label names the project. Your own workspace is the `workspace_id` of `herdr pane get "$HERDR_PANE_ID"`.
   - only when no workspace is the project's, `herdr session list`: a `running` session whose name names the project. Yours is `$HERDR_SESSION`.

   When the project has no workspace and no session of its own, or it is yours, spawn beside yourself. When it is another one, stop before the spawn and give the operator two answers:
   - a fresh foreman, started by the operator in that project's workspace or session, keeps the foreman and its workers in one view. Write down what you have established for it, and end your part there;
   - this foreman spawns there: split from a pane of that workspace (`herdr pane list --workspace <id>`), never with `--current`, which splits your own pane. For another session, also put `--session <name>` on every herdr command of the run, and list its panes with `herdr --session <name> pane list`.

   Label the pane before starting the agent (`pi: archive tmnt plan`, `claude: review apply script`) so the operator can find it among many; give the worker a matching name (`pi-archive`, `cl-review`). Tell the operator the label and pane id in one line.

   **Reuse a free pane before you split a new one.** When a pane you opened has finished its run, the next run goes there: relabel it with `herdr pane rename`, then
   - an independent brief gets a **fresh worker**: end the old one with the quit command in its profile, check the pane is back at its shell prompt, and `agent start` again. A fresh worker starts with an empty context, which a small model needs;
   - a brief that builds on the previous one (the next part of the same runbook) goes to the **same worker**, as its next prompt.

   Split a new pane only for a run that must happen at the same time as another.

   **Place each pane by size.** Splitting the same pane to the right every time leaves a row of thin columns. Before each split, read `herdr pane layout --pane "$HERDR_PANE_ID"`: it gives every pane of your tab with its width and height in cells. Of your own pane and the panes you opened, take the largest, and split it along its longer side: right when its width is more than twice its height (a cell is about twice as tall as it is wide), down otherwise. Each half must keep at least 80 columns and 24 rows. When the largest pane cannot, open a tab for the workers instead, `herdr tab create --workspace <workspace> --cwd "$PWD" --label "workers: <task>" --no-focus`, and start the worker in the pane it returns, `.result.root_pane.pane_id`. `<workspace>` is the workspace the panes belong in, your own unless the project lives in another: without `--workspace` the tab opened in another project's workspace. The next panes of the task go in that tab, by the same rule. Tell the operator the tab's label. Leave panes you did not open as they are.

   Preflight in one call, spawn in the next: a slow check chained in front of the split means no pane appears and the operator sees nothing. `agent start` straight after `pane split` can fail because the new shell is not at its prompt yet: check the response has a `result`; if not, start again.

4. **Send the brief and wait.**
   ```bash
   PROMPT=$(/bin/cat <<'EOF'
   …the brief…
   EOF
   )
   herdr agent prompt <name> "$PROMPT" --wait --timeout 540000
   herdr agent read <name> --source recent-unwrapped --lines 60
   ```
   The quoted heredoc carries any brief intact. Call `cat` by its full path: where `cat` is an alias for a pager, `$(cat <<'EOF' …)` came back empty, and a pull request was opened with an empty body. Inside it, write worker commands as `python3 -c "…"` with single-quoted Python strings, and avoid `$`, backticks and `!` in them. Anything hairier belongs in the runbook file.

   Keep `--timeout` under your shell tool's own limit. For longer work, cut the brief at a natural stop ("do R01–R08, then STOP and wait") and send the next part as a second prompt to the same worker; its context carries over.

   If the wait returns `blocked`, the worker is at a dialog: go to **Guard rails**. `agent_prompt_stalled` or a timeout does not mean the prompt was lost: read the pane before resending.

5. **Verify from ground truth, never from the worker's summary.** Re-read the diff, the commit author and message, the files on disk, the API — whatever the task changed. The worker's report tells you where to look, not what is true.

   Output-condensing hooks reshape `ls`, `grep`, `find` output, for you and for the worker: counting with `ls | grep -c` returned 0 on a full directory. They can change what a command does: `git show $b:<path>`, with the revision in a shell variable, printed the commit and its diff instead of the file. For a check that reads a file at a revision, call `/usr/bin/git`. For checks whose output will be compared, use a `python3 -c "…print('ROWS', n)"` one-liner with a fixed output format. Shell hooks hang commands too: a directory-change hook fires on every `cd`, and `ls` may be an alias for a slower tool. In your own commands use absolute paths, `git -C <dir>`, `/bin/ls` and `/bin/cat`. When a command needs a working directory (a test run), give it a plain shell, which has no hooks: `/bin/sh -c 'cd <dir> && <command>'`. A bare `cd`, alone or inside `( … )`, is what hangs. A check of yours that hangs proves nothing: kill it, rerun the same check with the plain binary or a short `python3 -c`, and never chain the next step behind an unproven one.

6. **Report the run, and close the pane after its last run.** Tell the operator, in the block format of **Reporting to the operator**: what the worker did, what you checked yourself, any deviation from the brief, and what is left for them. When no further run of this task is planned for the pane, close it then, not at the end of the task: `herdr pane close "$P"`. A run that might come later is not a planned run. Close every pane you opened, including after a failure, and every tab you opened once its last run is reported (`herdr tab close <tab>`). A pane you did not open but started a worker in, such as the pane of a worktree's workspace, stays open: end the worker with the quit command in its profile and check the pane is back at its shell prompt. An unprofiled kind has no quit command seen yet: tell the operator the pane still holds its worker. Leave every other pane you did not create alone.

One worker at a time per working tree: workers share the checkout and the git index. For several workers at once, read [`parallel.md`](parallel.md) first.

When a run does not end in a verified result — the worker stopped, or your verification found it wrong — read [`escalation.md`](escalation.md) before you send anything else.

## Guard rails — who answers a dialog

A worker at an approval or question dialog waits for an answer. Read the pane and sort the dialog into one of two classes before touching a key. When in doubt it is operator-reserved.

**Foreman-handled dialog** — you answer it yourself, single use. It is routine and reversible, matches the brief, and stays inside the task's working tree:
- read-only commands;
- creating or editing files in the working tree;
- running tests or code, after reading that code on disk;
- `git add` / `git commit` on the task's own branch; pushing that branch and opening its PR when the brief calls for it, after you have checked the commit (author, message, files);
- herdr commands on panes the worker itself created;
- removing a temporary file the worker itself created during this task.

**Operator-reserved dialog** — report and wait, never press the key yourself:
- deleting anything else: `rm` of existing files, bulk or recursive deletes, `find -delete`, `git clean`, `git reset --hard`, `git checkout -- .`, branch or worktree removal, dropping data;
- moving, overwriting or renaming many files at once (`mv`, `cp`, `rsync`, scripts that do so); for a script you wrote yourself, step 2 of the loop says when it needs the operator's word;
- anything outside the working tree: mounted volumes, the home directory, other repositories, system paths;
- force-push, push to the default branch, merge, remote branch deletion, history rewrite;
- secrets and local config files, `sudo`, package installs, network calls to hosts the brief does not name;
- any "don't ask again" or "switch to auto mode" option — those are the operator's to grant;
- every dialog of an unprofiled kind, a read-only command included;
- anything the brief does not call for, and anything you cannot read in full.

For an operator-reserved dialog, tell the operator in this shape, with the keys the dialog itself shows:

```
WAITING FOR OPERATOR · pane <id> "<label>"
asks:     <what the dialog asks, quoted exactly>
changes:  <what would be destroyed or changed, and how much: paths, number of files>
undo:     <the command that undoes it, or "none">
answer:   decline (<key>) · approve once (<key>) · or answer in the pane yourself
```

Declining comes first, in a line of text as in a list of choices. Whether the change can be undone is a fact for the operator, not a reason to proceed: state it on its line, without words that weigh it ("safely", "only", "just"). Give no recommendation and do not say what you would choose. Then wait. A request from the operator is not the answer to the dialog: when the task itself is a delete or another operator-reserved action, its dialog still goes to the operator, who confirms the exact command shown.

The operator has two ways to answer: in the pane themselves, or by telling you the answer, which you enter with `herdr agent send-keys <name> <key>` (read the dialog first to pick the right key). One answer covers one dialog: choose the single-use option over any "always allow", and come back for each new dialog. Then resume with `herdr agent wait <name> --timeout 540000`.

- When the operator answers in the pane, stay in the same turn: say which pane to go to, then poll `herdr agent get <name>` every few seconds until the status is no longer `blocked`.
- After the operator has been in a pane, read it before closing — they may have picked a session-wide option or typed something of their own.
- The first `agent wait` after `send-keys` can return a stale `blocked`: the key had landed and the worker was already working. Wait a second time, or check `herdr agent get <name>`, before concluding the dialog is still open.
- A blocked pane shows only its visible screen; scrollback cannot be read while a worker is blocked (`agent_not_idle`). A dialog you cannot read in full is operator-reserved: decline it and say why in the next prompt.

A kind that shows no dialogs is held by its mode and its brief; its profile says how.

### Allowlists — fewer dialogs, decided before the run

A dialog you answer costs paid tokens, and your own permission check can refuse the key press, which stalls the run until the operator comes. An allowlist lets a command through without a dialog, for one worker, from its start.

- **Standing allowlist.** Each profile lists the narrow, reversible commands the operator has approved for every worker of that kind. Pass it at every start.
- **Run allowlist.** It is the operator's to grant: a pattern beyond the standing allowlist reaches a worker only after the operator approved that pattern. A run that would raise only two or three dialogs needs none: answer them. When the brief would raise more — a test command run many times, a long runbook, several workers — propose a run allowlist with your plan and wait for the answer, before the first spawn: the exact patterns, and for each what it lets through. The operator approves once; you pass the approved patterns to that worker at start. They are stored nowhere and end with the worker.
- A pattern goes on a run allowlist only when its command would be a foreman-handled dialog. Operator-reserved commands stay dialogs: a delete, a force-push, a merge are confirmed one by one, on the exact command.
- Write each pattern as narrowly as the brief allows, and say in your proposal what else it would let through. A pattern ending in `*` covers every argument after it.
- A request that says in so many words which commands it approves for the allowlist is the approval: pass exactly those, and say so in `STARTED`. A request that only describes the task ("run the tests", "on a new branch") describes work; it approves no pattern.
- When the operator declines, start the worker with the standing allowlist only, and handle the remaining dialogs one by one.

## Reporting to the operator

The operator follows several panes through your messages. The unit you report on is the **run**. Number runs from 1 in the order you start them, and give every event of a run its own block in your reply, set off so it can be found at a glance:

```
🤖 ── run <n> · <worker> · <kind> · <brief> · <mode> · pane <id> "<label>" ── <EVENT>
<one or two lines>
```

`<brief>` is `literal` or `goal`. `<mode>` is the restriction the worker was started under, as its profile names it. Write `<kind>/<model>` when the model is not the kind's default.

Events and what the lines carry:
- `STARTED` — the task in one line; branch or worktree if any; the herdr workspace or session, when it is not your own; `new pane` or `reused pane`; `fresh worker` or `same worker`; the run allowlist, when one was passed; the script, when the run executes one, with what it changes and how many files.
- `DIALOG` — the command or question, quoted; then `approved by foreman (in scope)`, `declined by foreman: <why>`, `WAITING FOR OPERATOR` with the lines of **Guard rails**, or `answered by operator: <answer>`. Foreman-handled dialogs of one run may share a block; a declined or operator-reserved dialog always gets its own.
- `RETRYING` — what went wrong, what you verified about the state left behind, and the step the run resumes at.
- `ESCALATED` — the rung you leave and the rung you go to, the state you verified, and the part still to do. The work continues as a new run.
- `DONE` — what it produced; then what you verified yourself; then how many dialogs it took.
- `FAILED` or `DISCARDED` — why, and what state it left behind.
- `CLOSED` — only when the pane itself is closed; name the runs it hosted.

When all runs are finished, end with a summary:

```
🤖 ══ runs summary
runs:    <n> (<n> literal, <n> goal) · workers: <n> pi, <n> claude
panes:   <n> opened · <n> reuses · <n> closed · <n> left open
results: <n> done and verified · <n> failed · <n> discarded · <n> retried · <n> escalated
dialogs: <n> foreman-handled · <n> operator-reserved (<n> approved, <n> declined)
kept:    <branches, PRs, files — or "nothing kept">
open:    <what the operator still has to do, or "nothing">
```

A pane counts as left open only when a planned run of this task will use it; name that run beside the pane. Any other pane you opened is closed before the summary.

### The run log

After the summary, record the runs in the operator's run log, when that file exists. One command, with nothing else in it and one `echo` line per run:

```bash
L=~/.config/herdr-workers/run-log.md
if [ -f "$L" ]; then
  H="| $(date +%F) | $(basename "$PWD") | ${CLAUDE_CODE_SESSION_ID:--}"
  echo "$H | <n> | <kind> | <brief> | <mode> | <result> | <foreman-handled> | <operator-reserved> | - |" >> "$L"
fi
```

Every row has the eleven fields of this line, in this order. `<kind>` is the kind as the table above names it (`pi`, `codex`), never the worker's name. `<mode>` is the mode as the profile names it. `<result>` is `verified`, `failed`, `discarded` or `escalated`. The two dialog fields are counts. The session field is the foreman's Claude Code session id; a foreman that is not Claude Code has none, and the line writes `-`. The last field stays `-`: it is the operator's. Only append: do not read the log, and change no row in it.

## What stays with the foreman

- **Authority does not pass through the pane.** A worker may do only what the operator authorised you to do. Confirmation duties for destructive or outward-facing actions stay yours. If a permission check refuses you an action, hand that action to the operator — routing it through a worker is the same refused action.
- **Verification is yours, and so is the last word on a plan.** A paid worker may investigate and draft a runbook; deciding that the plan is right, and what "done" means, stays with you.
- **You never implement.** What you do yourself: read, plan, write briefs, runbooks, scripts and a worker's configuration directory outside the working tree, drive herdr panes and workers, verify, add rows to the run log. Everything that changes the repository or the system goes to a worker: an edit, a commit, a branch, a worktree. A worktree is made the way the project makes one: with its worktree skill or tool when it has one (`worktree-lanes`, Worktrunk's `wt`), so that the project's own steps run, such as copying the gitignored files listed in `.worktreeinclude`. `herdr worktree create` and a bare `git worktree add` run none of them. A read-only check is yours and is not worth a pane.
- **One foreman, a flat set of workers.** A worker never starts workers of its own.
