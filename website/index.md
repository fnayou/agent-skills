# agent-skills

![agent-skills: Portable Agent Skills for cross-agent development workflows.](assets/readme-banner.svg)

Portable [Agent Skills](https://agentskills.io/) for coordinating AI coding
agents across repositories and harnesses. The skills carry tool-independent
operating policy; repository-specific commands stay in each project's own
instructions.

## What it provides

- **`worktree-lanes`** establishes the current Git worktree lane, the primary
  lane, the integration branch, and any project-declared shared resources
  before parallel work. It also defines safe rules for lane handoff and
  cleanup.
- **`project-presentation`** audits, bootstraps, or aligns a repository's
  brand identity and public documentation. It inspects the repository first
  and asks only about missing or conflicting choices.

Each skill works with Claude Code, Codex, OpenCode, and Pi, because it follows
the open Agent Skills `SKILL.md` format.

## Where to go next

- [Getting Started](getting-started.md) installs the skills from a checkout.
- [Skills](skills.md) describes each skill in more detail.
