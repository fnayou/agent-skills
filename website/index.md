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
- **`agent-browser`** gives agents an agent-only browser through Playwright
  and Safari MCP servers, with a separate signed-in profile for sites that
  need the user's login and a read-only readiness check.
- **`project-bootstrap`** creates, adopts, or audits an AI-ready project
  foundation with guarded file generation, GitHub governance templates, and
  opt-in Taskfile/Docker conventions.
- **`herdr-workers`** runs the session as a foreman for an explicitly
  delegated task: it plans, briefs, and verifies while worker agents execute
  in visible herdr panes, with guard rails on who answers each dialog.

Each skill follows the open Agent Skills `SKILL.md` format. Transferable
guidance works across Claude Code, Codex, OpenCode, and Pi where each host
supports the relevant discovery and invocation behavior.

## Where to go next

- [Getting Started](getting-started.md) installs the skills from a checkout.
- Skills: [worktree-lanes](skills/worktree-lanes.md), [project-presentation](skills/project-presentation.md), [agent-browser](skills/agent-browser.md), [project-bootstrap](skills/project-bootstrap.md), and [herdr-workers](skills/herdr-workers.md) each have their own page.
