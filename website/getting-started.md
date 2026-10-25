# Getting Started

Review the repository before installing it. The installer creates two
symlinks for each skill under `skills/` and refuses to replace any existing
file, directory, or different symlink. It inspects every destination first, so
a conflict leaves all targets untouched.

## Install

From a checkout that you keep in a persistent location:

```sh
./scripts/verify
./scripts/install
./scripts/install --check
```

The links are:

```text
~/.agents/skills/<skill>  -> <checkout>/skills/<skill>
~/.claude/skills/<skill>  -> <checkout>/skills/<skill>
```

`<skill>` is `worktree-lanes` and `project-presentation`. Moving or deleting
the checkout breaks the links.

Codex, OpenCode, and Pi discover the shared Agent Skills location. Claude Code
uses its compatible personal-skills location. Both links resolve to the same
source, so a skill cannot drift between agents.

## Use another target

Override the two target roots to test an installation without touching your
home directory:

```sh
AGENT_SKILLS_TARGET=/tmp/agents-skills \
CLAUDE_SKILLS_TARGET=/tmp/claude-skills \
./scripts/install
```

## Verify

`./scripts/verify` checks the skill structure and exercises installation and
repeat installation in an isolated temporary directory. It never changes links
in your home directory.
