# Claude Code is the reference foreman

Supersedes [0002](foreman-workers-0002-foreman-is-always-claude-code.md).

Any agent that can load the skill and drive herdr may take the foreman role. Claude Code is the default and the reference: the scenario suite runs a Claude Code foreman, the release gates are measured with one, and the guard rails were written against its permission checks. Another harness is an **unprofiled foreman** until it has passed the foreman test and has a profile of its own.

We changed this because the operator ran the skill with other foremen, OpenCode for 21 real runs on 2026-10-20 and codex before, and the loop held: literal briefs, verification from ground truth, the report blocks. The same OpenCode session also showed that 0002's reason still stands. With nothing in its harness asking before a write, it changed this repository itself, wrote run-log rows in a form of its own, and described a herdr option that does not exist.

## Considered Options

- **Keep 0002**, Claude Code only. Rejected: the operator already uses other foremen, and a rule nobody follows protects nothing.
- **Any foreman, on equal terms.** Rejected: the guard rails have been tested against Claude Code alone, and equal standing would promise what no run has shown.

## Consequences

- An unprofiled foreman is used only when the operator chooses it. It says so in its first message, and holds the guard rails itself: its harness may not ask before a write, and a refusal by its own permission check may not exist to stop it. The operator watches its first runs.
- A harness earns a **foreman profile** by passing the foreman test: the guard-rail scenarios of the suite, run with that harness as the foreman. Which scenarios make up the test is decided with the first candidate; the scenario driver starts only Claude Code today and needs an option for it. The profile records what those runs showed, how the harness loads the skill, how its permission checks behave, what it tripped on, and, like a worker's profile, nothing else.
- The release gates stay measured with a Claude Code foreman. Another foreman neither blocks nor counts toward a release.
- A detail of the skill that only Claude Code provides needs a fallback that works elsewhere, as the run log's session field has with `${CLAUDE_CODE_SESSION_ID:--}`.
