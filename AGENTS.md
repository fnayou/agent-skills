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
- Brand assets live in `brand/` and are generated: edit `brand/src` or
  `brand/data`, run `task brand:generate`, and never edit `brand/generated` by
  hand. `task brand:check` and `task docs:check` must pass.
- Public documentation lives in `website/`; `docs/` is internal and is not
  published.

Make focused changes and explain behavioral decisions in the affected skill or
its reference material rather than creating parallel sources of truth.

## Agent skills

### Issue tracker

Issues live in GitHub Issues, used through the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one root `GLOSSARY.md` plus `docs/adr/`. See `docs/agents/domain.md`.
