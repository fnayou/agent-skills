# Operator rules

Copy this file to `~/.config/foreman-workers/operator-rules.md` and make it yours. It is loaded into every worker that does not read your own agent instructions. These rules rank above the worker rules and above any brief.

Keep it short: every line is read by every worker, at every start.

## Git

- Commit with the git identity already configured. Leave author and committer as they are.
- A commit message holds the change and nothing about how it was made: no co-author trailer for an assistant, no "generated with" line, no tool name.
- Commit messages and pull request titles follow Conventional Commits 1.0.0: `<type>[optional scope]: <description>`.
- Changes reach the default branch through a pull request. Work on a branch; leave the default branch, merging and force-pushing to the operator.
