# The foreman is always Claude Code

Superseded by [0004](foreman-workers-0004-claude-code-is-the-reference-foreman.md).

Any kind herdr can start may be a worker, but only Claude Code takes the foreman role. The guard rails, the rule that authority does not pass through the pane, and the skill format itself all rest on Claude Code's permission checks; one foreman contract keeps permissions, briefing, verification and reporting coherent.

## Considered Options

- **Any kind as foreman** (for example a codex foreman that starts pi workers). Rejected: the guard rails would have to be rewritten and tested for every kind.

## Consequences

- The skill cannot be reused from codex or opencode as it stands. Doing so later needs a foreman abstraction that does not exist today.
