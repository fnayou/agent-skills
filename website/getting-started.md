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

`<skill>` is each directory under `skills/` with a `SKILL.md` entrypoint.
Moving or deleting the checkout breaks the links.

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

`./scripts/verify` runs offline. It checks the structure and links of every
skill, and exercises installation, `--check`, and the installer's refusals in
an isolated temporary directory. It also runs each skill's own checks: the
`worktree-lanes` terminology, the `project-presentation` brand and
documentation starters, the `agent-browser` launcher and readiness check, the
`project-bootstrap` unit tests, and the `herdr-workers` test scripts and
scenario fixture. It never changes links in your home directory.
