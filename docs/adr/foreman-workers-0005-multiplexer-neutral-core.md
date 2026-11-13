# One core, one file per multiplexer

Its consequence on the skill's name is superseded by [0006](foreman-workers-0006-neutral-name.md).

The foreman loop, the guard rails, the briefs, the reporting and the worker rules do not depend on herdr. Only the commands that open a pane, start a worker, send it a brief, wait on it, press its keys and close it do. `SKILL.md` therefore holds the loop with no multiplexer command in it, and each multiplexer the skill supports has one **multiplexer file** under `skills/foreman-workers/multiplexers/` with those commands. herdr is the first; Rex is to follow, side by side with herdr, and may later replace it.

We chose this because Rex, probed on 2026-11-12, offers every primitive the loop needs: panes and splits, reading a pane, sending keys, and a status each worker kind reports itself (`working`, `done`, `blocked` with `kind=permission`). The loop held for claude, pi, codex and opencode workers with only the commands changed.

## Considered Options

- **A separate `rex-workers` skill.** Rejected: it copies the whole loop, the guard rails and the terminology, against the rule that each meaning has one source.
- **A thin `rex-workers` skill that links into `herdr-workers`.** Rejected: it makes herdr the base of a skill meant to outlive it, and couples two skills.

## Consequences

- A change to the loop is made once, in `SKILL.md`. A change to how one multiplexer is driven is made in its file.
- Where a worker kind behaves differently under one multiplexer, its profile says so in a section for that multiplexer; the rest of the profile is shared.
- The skill keeps its name and triggers while herdr is supported. A neutral name is chosen if Rex replaces herdr, in one change that also moves the installed links, these ADRs' prefix and the website page.
- When the foreman's session runs inside two multiplexers at once, it drives the innermost one, where the operator is looking. This rule is provisional and may change once both have been used side by side.
