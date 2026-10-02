# Agent Skills

Portable, public [Agent Skills](https://agentskills.io/) for coordinating AI
coding agents across repositories and harnesses.

The skills contain tool-independent operating policy. Repository-specific
commands and infrastructure rules stay in each project's own instructions.

## Skills

### `worktree-lanes`

Establishes the current Git worktree lane, the primary lane, the integration
branch, and any project-declared shared resources before parallel work. It also
defines safe rules for lane handoff and cleanup.

The canonical vocabulary is in
[`skills/worktree-lanes/references/terminology.md`](skills/worktree-lanes/references/terminology.md).

## Install

Review the repository before installing it. The installer creates two
per-skill symlinks and refuses to replace any existing file, directory, or
different symlink.

```sh
./scripts/install
./scripts/install --check
```

The links are:

```text
~/.agents/skills/worktree-lanes  -> <checkout>/skills/worktree-lanes
~/.claude/skills/worktree-lanes -> <checkout>/skills/worktree-lanes
```

Codex, OpenCode, and Pi discover the shared Agent Skills location. Claude Code
uses its compatible personal-skills location. Both links resolve to the same
source, so the skill cannot drift between agents.

The target roots can be overridden for testing:

```sh
AGENT_SKILLS_TARGET=/tmp/agents-skills \
CLAUDE_SKILLS_TARGET=/tmp/claude-skills \
./scripts/install
```

## Project lane contracts

The global skill deliberately does not prescribe container names, task-runner
commands, secret-copy rules, branch naming, or merge policy. A project that
shares mutable resources between lanes should declare those details in its
repository instructions and expose safe ownership checks and claim commands.

## Verify

```sh
./scripts/verify
```

Verification checks the portable skill structure and exercises installation
and repeat installation in an isolated temporary directory.

## License

MIT
