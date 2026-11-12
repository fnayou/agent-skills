# herdr-workers

Runs the session as a **foreman** for a task the operator delegates
explicitly. The foreman plans, writes the brief, and verifies the result. It
changes nothing itself: every change of state, however small, goes through a
**worker**, an agent in a pane of a terminal multiplexer (herdr or Rex) that
the operator can watch while it runs.

Paid models think; the local model executes. Work that can be written as
exact steps goes to pi on a local model. Work that needs investigation goes to
a paid worker, which makes a small change itself or drafts the steps for pi.

## When to use it

Only when the operator asks for it by name, in a session running inside
herdr or Rex: "use pi workers", "herdr workers", "a worker pane", or "delegate this
through herdr". The role covers the delegated task and ends when the foreman
has reported it.

## Requirements

- **A terminal multiplexer**, with the foreman session running inside one of
  its panes. Each has a file in the skill's `multiplexers/` directory with the
  commands the foreman uses there; the loop is the same for both.
  - **herdr**: the skill checks `HERDR_ENV=1`. Built against herdr 0.9.3.
    `herdr --skill` and herdr's own command help are the authority for CLI
    syntax.
  - **Rex** (preview): the skill checks that `REX_SESSION` is set. Probed on
    Rex 0.1.0-preview.14 with all four profiled kinds; the scenario suite and
    real runs are still to come. Every kind reports its own status to Rex
    (`working`, `done`, `blocked`), which is how the foreman waits on it.

  With neither, the foreman says so and does the work the normal way. When the
  session runs inside both, it drives the innermost one.
- **A foreman.** Claude Code is the reference foreman: the scenario suite runs
  it, and the guard rails were written against its permission checks. Another
  harness can take the role as an **unprofiled foreman**: it says so in its
  first message and holds the guard rails itself, because its harness may not
  ask before a write.
- **At least one worker agent** that the multiplexer can start. Four kinds have a
  profile: `pi` (built against 1.1.0), `claude`, `opencode` (2.0.25), and
  `codex` (0.162.1).

Install the skill with the repository's installer (see
[Getting Started](../getting-started.md)). codex does not see a new skill in a
session that is already open: restart it after linking.

## Optional setup

The skill holds no machine facts and no personal rules of its own. It reads
them from files in `~/.config/herdr-workers/`, copied from templates in the
skill directory. Each file is optional.

```sh
mkdir -p ~/.config/herdr-workers
cp <checkout>/skills/herdr-workers/machine.example.md ~/.config/herdr-workers/machine.md
cp <checkout>/skills/herdr-workers/operator-rules.example.md ~/.config/herdr-workers/operator-rules.md
cp <checkout>/skills/herdr-workers/run-log.example.md ~/.config/herdr-workers/run-log.md
```

- **`machine.md`**: facts a foreman cannot find by looking: the default local
  model and its server, models pi may take a goal brief on, a stronger model to
  escalate to, output-condensing hooks and the prefix they add to commands,
  shell aliases and directory-change hooks, sleep settings, and the time limit
  of the foreman's shell tool. The foreman reads it once before the first
  spawn. Keep the entries that hold on your machine and delete the rest.
- **`operator-rules.md`**: your own rules for workers, for example how commits
  are authored and named. They rank above the worker rules and above any
  brief, and are loaded into every worker that does not read your own agent
  instructions. Without the file, workers get the worker rules only.
- **`run-log.md`**: while it exists, the foreman appends one row per run after
  its summary. The last column is yours, for a result that turned out wrong
  later. `python3 skills/herdr-workers/tests/runlog.py`, from the checkout,
  totals the rows and the paid tokens of their sessions.

## How a run goes

A **run** is one brief executed by one worker, from its start to its verified
end. A pane hosts one worker at a time and can host several runs in turn.

1. **Facts first.** The foreman looks up, read-only, every fact the brief
   needs: paths, line contents, counts, branch names. A worker that has to
   discover facts will guess.
2. **The brief.** It is the whole of the worker's knowledge.
   - A **literal brief** is numbered steps, one command or one exact edit each,
     each followed by an `Expect:` line. A mismatch stops the worker.
   - A **goal brief** states the goal, its context, what to leave alone, and a
     fixed report shape that ends on a sentinel line.
   - Work longer than a screen goes in a **runbook** file outside the working
     tree. A **script** replaces written-out steps only for long repetitive
     work, and the operator hears about it before the start.
3. **Spawn.** The foreman finds where the project lives (a herdr workspace or
   session, a Rex tab), places the pane by size, labels it (`pi: archive plan`), and
   starts the worker with the start arguments from its profile. It reuses a
   free pane before it splits a new one.
4. **Send and wait.** The brief goes to the worker, and the foreman waits for
   the run to end or reach a dialog.
5. **Verify from ground truth**: the diff, the commit author and message, the
   files on disk. The worker's report says where to look, not what is true.
6. **Report and close.** The foreman reports the run and closes every pane it
   opened once no further run of the task is planned for it.

One worker at a time per working tree. Parallel workers each get a worktree of
their own, made the way the project makes worktrees. When a run fails, the
foreman climbs an escalation ladder one rung at a time: stop and look; correct
the brief and retry once; a stronger model of the same kind; a paid worker on
a goal brief.

### Every change goes through a worker

**Worker rules** ship with the skill and are loaded into every worker at
start: do the brief and nothing beyond it, leave the multiplexer's panes to
the foreman, stop on a mismatch, ask before any
delete or overwrite the brief does not spell out, commit and push only where
the brief writes the command, and report raw output.

The foreman's role does not widen what the operator authorised. A worker may do
only what the operator authorised the foreman to do, and a worker never starts
workers of its own.

### Guard rails: who answers a dialog

A worker at an approval or question dialog waits for an answer. The foreman
sorts each dialog before touching a key; when in doubt it belongs to the
operator.

- **Foreman-handled**: routine, reversible, called for by the brief, inside the
  working tree: read-only commands, edits in the working tree, running tests
  after reading the code, `git add` and `git commit` on the task's branch, and
  pushing that branch or opening its pull request when the brief calls for it.
  The foreman answers once, with the single-use option.
- **Operator-reserved**: deletes, bulk moves and overwrites, anything outside
  the working tree, force-push, pushes to the default branch, merges, history
  rewrites, secrets, `sudo`, package installs, any "don't ask again" option,
  and every dialog of an unprofiled kind. The foreman reports it with the
  dialog's own keys, declining first, with no recommendation, and waits.

**Allowlists** cut routine dialogs before a run. Each profile has a short
**standing allowlist** of reversible git commands. A **run allowlist** is
proposed with the plan and approved by the operator for one worker, and
stored nowhere.

### Reporting

The foreman numbers runs and gives every event its own block: `STARTED`,
`DIALOG`, `RETRYING`, `ESCALATED`, `DONE`, `FAILED` or `DISCARDED`, and
`CLOSED`.

```text
🤖 ── run <n> · <worker> · <kind> · <brief> · <mode> · pane <id> "<label>" ── <EVENT>
```

When all runs are finished it ends with a summary of runs, panes, results,
dialogs, what was kept, and what is left for the operator.

## Worker kinds

Each kind has a **profile**: the observed facts a foreman needs to run it as a
worker. A profile holds only what a test run showed. The foreman starts each
worker in the least capable **mode** that can execute the brief.

| Kind | Takes | Modes | Dialogs |
|---|---|---|---|
| `pi` | literal briefs; goal briefs only on a model the operator names | tool sets: `read-only`, `edit`, `full` | none: held by its mode and its brief |
| `claude` | goal and literal briefs; costs paid tokens | permission modes: `acceptEdits`, `default` | asks before each command no allowlist covers |
| `opencode` | literal and goal briefs; runs on the operator's opencode subscription | permission rules in a configuration directory written per worker: `read-only`, `edit`, `ask` | asks under `ask` |
| `codex` | literal and goal briefs; spends the operator's codex limits | sandboxes: `read-only`, `workspace-write`, `workspace-write` with git | asks for what the sandbox blocks |
| any other kind the multiplexer starts | literal briefs only | the most restrictive arguments its help shows | every dialog is the operator's |

A kind with no profile is an **unprofiled kind**. The foreman uses one only
when the operator names it, reads only its help, says what a run would spend,
sends no destructive step, closes the pane after one run, and writes down what
it saw as a draft profile.

The profiles are in the skill's
[`profiles/`](https://github.com/fnayou/agent-skills/tree/main/skills/herdr-workers/profiles)
directory, and the vocabulary is in its
[terminology reference](https://github.com/fnayou/agent-skills/blob/main/skills/herdr-workers/references/terminology.md).

## Tests

The skill's tests are scenario runs: a task given to a fresh Claude Code
foreman against a throwaway repository, then checked from ground truth by a
script. Nineteen scenarios cover pi, claude, opencode, codex and unprofiled
workers, literal and goal briefs, a mismatch stop, a retry, an
operator-reserved delete, parallel workers, and planning before execution.

- `tests/fixture/build.py` builds the throwaway repository.
- `tests/check.py` runs the read-only checks of one scenario.
- `tests/run_scenario.py` drives a scenario from a session inside herdr; it
  does not drive Rex yet.
- `tests/tokens.py` and `tests/runlog.py` total paid tokens and the run log.

`./scripts/verify` builds the fixture offline and runs its own check. The
scenario runs need herdr and live agents, and some need the operator at the
keyboard; the
[tests README](https://github.com/fnayou/agent-skills/blob/main/skills/herdr-workers/tests/README.md)
says how to run them.

## Limits

- The guard rails were tested against a Claude Code foreman only. Another
  foreman is unprofiled, and its harness may not stop a write the skill
  forbids.
- pi has no dialogs: a `full` pi worker runs any command, and its only gate is
  its brief. Tasks with destructive steps go to a kind that asks.
- codex has no allowlist argument, and its trust dialog in a new directory is
  the operator's.
- Even with allowlists, a claude worker on a goal brief raised 18 to 55
  foreman-handled dialogs per run in one project's runs.
- An unprofiled kind gets every dialog sent to the operator and one run per
  pane.
- One foreman supervises a flat set of workers: no nested foremen.
- Rex support is a preview: it has passed a probe of each kind, not yet the
  scenario suite. Rex tells a new agent to rename the session; the foreman
  starts workers without the session's ids, and the worker rules leave the
  multiplexer to the foreman.
