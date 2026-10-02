# Agent instructions

This repository is the canonical source for portable Agent Skills shared
across coding-agent harnesses.

## Boundaries

- Follow the open Agent Skills `SKILL.md` format.
- Keep harness-specific metadata optional; the skill body must remain useful
  to Claude Code, Codex, OpenCode, and Pi.
- Keep project-specific commands, credentials, infrastructure identifiers, and
  local absolute paths out of global skills.
- Define each shared term once. For worktree coordination, the canonical
  definitions are in
  `skills/worktree-lanes/references/terminology.md`.
- Do not install skills or create links in a user's home directory without
  explicit approval for that installation.
- Run `./scripts/verify` before committing.

Make focused changes and explain behavioral decisions in the affected skill or
its reference material rather than creating parallel sources of truth.
