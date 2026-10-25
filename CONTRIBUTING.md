# Contributing

Thanks for helping improve these skills. This repository is the canonical
source for portable [Agent Skills](https://agentskills.io/), so changes are
held to a few strict rules. Read [`AGENTS.md`](AGENTS.md) first.

## Before you start

- Open an issue to discuss a new skill or a behavior change. Small fixes can go
  straight to a pull request.
- Keep skills tool-independent: the body must stay useful to Claude Code,
  Codex, OpenCode, and Pi. Harness-specific metadata is optional.
- Keep project-specific commands, credentials, infrastructure identifiers, and
  local absolute paths out of skills.
- Define each shared term once. Worktree vocabulary lives in
  [`skills/worktree-lanes/references/terminology.md`](skills/worktree-lanes/references/terminology.md);
  extend it rather than creating a parallel definition.

## Making a change

1. Fork the repository and create a branch.
2. Make a focused change. Explain behavioral decisions in the affected skill or
   its reference material, not in a separate document.
3. Run the checks and make sure they pass:

   ```sh
   ./scripts/verify
   ```

4. Commit with [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/),
   for example `docs(worktree-lanes): clarify closure order`.
5. Open a pull request. Its title follows the same form.

## Conduct and security

Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
Report vulnerabilities as described in [SECURITY.md](SECURITY.md), not in
public issues.
