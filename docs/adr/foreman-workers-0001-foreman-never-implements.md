# The foreman never implements

The foreman reads, plans, briefs and verifies; every change of state, even a one-line edit, goes through a worker in a visible pane. We chose this over letting the foreman make small changes itself because a crisp boundary needs no judgement call, keeps every change observable and reported as a run, and pushes the most work to the local model.

## Considered Options

- **A cost judgement, case by case** ("do it yourself when the brief would cost more than the task"). Rejected: the judgement drifts toward the foreman doing the work.
- **A fixed allowance** of one reversible command or one edit for the foreman. Rejected: cheaper on trivial changes, but it reintroduces an exception the operator did not want.

## Consequences

- A trivial change costs more paid tokens and wall-clock than a direct edit: about five foreman tool calls instead of one. This is accepted.
- The foreman still writes briefs, and runbooks outside the working tree: those are planning artifacts. A runbook kept in the repository is a change, so a worker puts it there.
- The rule binds work on this skill itself: changes to this repository are made by workers.
