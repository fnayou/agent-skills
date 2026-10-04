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

### Install with a coding agent

To have a coding agent do the installation, paste this prompt into it. It
needs bash and symbolic links (macOS, Linux, or WSL). The checkout must stay
in a persistent location that you choose, because the installed links point
into it; moving or deleting the checkout breaks them.

```text
Install the worktree-lanes skill from https://github.com/fnayou/agent-skills.git
for me. This needs bash and symbolic links (macOS, Linux, or WSL); stop if
either is missing.

Work in two phases. Phase 1 changes nothing on my computer; the only
exception is the inspection clone in step 4, which needs its own
permission. Phase 2 starts only after I explicitly approve both cloning
into the agreed path, if the checkout is not there yet, and creating the
two links.

Phase 1 - inspect and explain.
1. Ask me for the full final path of the checkout. You may suggest a
   persistent path, but I decide. Never use a temporary location.
2. Work out the two actual link paths, each on its own, because one
   variable may be set while the other is not:
   - $AGENT_SKILLS_TARGET/worktree-lanes if AGENT_SKILLS_TARGET is set and
     non-empty,
     otherwise ~/.agents/skills/worktree-lanes
   - $CLAUDE_SKILLS_TARGET/worktree-lanes if CLAUDE_SKILLS_TARGET is set and
     non-empty,
     otherwise ~/.claude/skills/worktree-lanes
   Before reading or running anything stored locally, check what already
   exists at the checkout path and at those two actual link paths. If
   either variable is set and non-empty, tell me the exact resulting paths
   and ask whether to continue with them.
3. If a checkout already exists at that path, confirm that it comes from
   fnayou/agent-skills on GitHub (HTTPS or SSH address) and has no
   uncommitted changes. Tell me its branch and commit. Then find the
   remote's default branch and its latest commit with a read-only lookup
   that fetches nothing and changes nothing (for example
   git ls-remote --symref origin HEAD). The checkout is suitable only if
   it is on that default branch and its current commit equals that remote
   commit. If its origin, cleanliness, branch, or commit does not match or
   cannot be determined, stop and ask. Do not pull, fetch, switch
   branches, reset, stash, change any refs, or install it as it is unless
   I approve a specific plan for that.
4. Read README.md, AGENTS.md, scripts/install, and scripts/verify. Use the
   existing checkout if step 3 found it suitable. Otherwise read them
   online from the public repository. Only if you cannot browse it, ask me
   for separate permission to clone into the agreed path solely to inspect
   the files. That permission does not cover installing.
5. Tell me in plain language exactly what would be created, where, and what
   each link would point to. Then ask for my explicit approval of both
   actions: cloning into the agreed path, if the checkout is not there
   yet, and creating the two links.

Phase 2 - clone if needed and install, only after that approval.
6. If the checkout is not there yet, clone into the agreed path. Then
   re-read the four files in the local checkout before running anything,
   and stop if they differ in any way that matters from what you explained.
7. From the checkout, run exactly ./scripts/verify, then ./scripts/install,
   then ./scripts/install --check.
8. Report both resulting links and where they point, plus anything that
   failed. Remind me that moving or deleting the checkout breaks the links.

Stop and ask me instead of continuing if:
- the checkout path or either actual link path already holds something
  different or conflicting. Never overwrite, delete, move, reset, stash, or
  otherwise alter it.
- any command fails or reports something you did not expect.

Do not print or copy secrets, credentials, or tokens. Do not install
anything else, change other settings, or widen the task beyond these steps
without asking me.
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
