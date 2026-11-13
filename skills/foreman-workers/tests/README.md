# Tests

Scenario runs that show whether the skill still does what it promises, and what it costs. A scenario is a task given to a fresh foreman session against a throwaway repository; a script then checks the result from ground truth.

Setup, the foreman's start and the checks are scripts. What the workers do is not scripted, and some scenarios need the operator at the keyboard: each scenario file says so under "Operator's part".

## Run a scenario with the driver

From a session inside herdr or Rex, at the root of the agent-skills repository, with the branch under test checked out:

```bash
python3 skills/foreman-workers/tests/run_scenario.py 01-pi-literal /tmp/hw-fixture-01
```

The fixture directory must not exist yet. The driver builds the fixture, opens a pane in it, starts a fresh Claude Code foreman there, answers the trust dialog of that new directory, sends the prompt of the scenario file, and waits until the foreman and all its workers are done. Then it prints:

- the last screen of the foreman, with its report;
- the check result, `RESULT <scenario-id> PASS n/n`;
- per session file: paid tokens, the number of tool calls, the worker start commands, the size of each brief, and what the foreman changed itself (`FOREMAN_CHANGES`, which must be 0).

A scenario in which the foreman first asks the operator something runs in two halves:

```bash
python3 skills/foreman-workers/tests/run_scenario.py 11-unprofiled-kind /tmp/hw-fixture-11 hold --kind <kind>
# answer the foreman in its pane, then:
python3 skills/foreman-workers/tests/run_scenario.py 11-unprofiled-kind /tmp/hw-fixture-11 finish
```

`--kind` fills `<KIND>` in a prompt that names no kind of its own.

The driver runs the foreman in the multiplexer it is started from: herdr when `HERDR_ENV=1`, otherwise Rex when `REX_SESSION` is set; `--multiplexer herdr|rex` chooses. Under Rex:

- the foreman's pane is split beside the driver's own pane, and the prompt reaches `claude` as its start argument;
- the word `herdr` in a prompt becomes `Rex`, as an operator inside Rex would say it;
- Rex's start-up hook asks the foreman to rename the session; the driver puts the session's label back after the run and prints `SESSION_RENAMED` when it had to.

Start `finish` only after the foreman's first question has been answered. A question asked in plain text at the end of a turn looks to the driver like a finished foreman, and `finish` then closes its pane. A dialog the foreman has reported as `WAITING FOR OPERATOR` keeps the driver waiting until the foreman's summary follows.

Things that have cost a run:

- Name the fixture directory `hw-fixture-…`. When the operator keeps a run log, the foreman under test adds its rows there, and `runlog.py` tells them from real runs by that name.
- Keep the machine awake. A run that sleeps halfway stalls: the local model's stream times out, and a foreman ends on an API error.
- One driver at a time, and close your own worker panes first. Narrow panes cannot show a dialog whole.
- A run takes longer than the shell tool of an agent allows in the foreground. From an agent, start the driver in the background.
- Do not press a key in a worker's pane while its foreman is alive, unless the foreman says it waits for you.
- Answer a dialog with the single-use option, never with an "always allow" one.
- A delete dialog must be declined by a person: a key press on it from another agent session is refused.

## Run a scenario by hand

1. Build a fresh fixture. The target must not exist yet:

   ```bash
   python3 skills/foreman-workers/tests/fixture/build.py /tmp/hw-fixture-01
   python3 skills/foreman-workers/tests/check.py 00-fixture /tmp/hw-fixture-01
   ```

   The second command must end with `RESULT 00-fixture PASS 7/7`.

2. Open a new pane in the fixture directory and start a fresh Claude Code session there. A session that has already read the scenario files or worked on the skill is not fresh.

3. Paste the prompt from the scenario file, with `<FIXTURE>` replaced by the fixture path. Answer the dialogs the scenario says are yours, the way it says.

4. When the foreman reports that it is finished, check the result:

   ```bash
   python3 skills/foreman-workers/tests/check.py <scenario-id> /tmp/hw-fixture-01
   ```

5. Total the paid tokens of the foreman session and of every paid worker session:

   ```bash
   python3 skills/foreman-workers/tests/tokens.py claude ~/.claude/projects/<directory-slug>/<session>.jsonl
   python3 skills/foreman-workers/tests/tokens.py codex ~/.codex/sessions/<year>/<month>/<day>/rollout-<...>.jsonl
   ```

6. Record the run, with the observations the scenario lists under "Observe". The results of earlier runs are kept in the private `herdr-workers-archive` repository, under `tests/results/`; they are not part of this repository.

Use one fixture per run. Scenarios change it, and the checks assume the starting state.

## Files

| Path | Role |
|---|---|
| `fixture/build.py` | builds the fixture: one commit on `main`, one failing test, one typo, six old notes, twelve unsorted documents |
| `run_scenario.py` | drives one scenario: fixture, fresh foreman, prompt, wait, check, report |
| `check.py` | read-only ground-truth checks, one set per scenario |
| `tokens.py` | totals paid tokens from a Claude Code or codex session file |
| `runlog.py` | totals the operator's run log: runs, days, brief types, dialogs, multiplexer, paid tokens |
| `scenarios/` | one file per scenario: prompt, expected behaviour, what to observe |

Recorded runs are not imported here: they stay in `tests/results/` of the private `herdr-workers-archive` repository.

## What a run records

The goal is the lowest paid-token spend for a verified result, so the primary number is total paid tokens per passing run, split between foreman and workers. A run also records: skill commit, kinds and models, brief type, dialogs answered by the foreman and by the operator, wall time, and every deviation from the expected behaviour.
