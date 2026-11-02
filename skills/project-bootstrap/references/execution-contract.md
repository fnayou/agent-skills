# Execution contract

## Modes and boundaries

- **Create** initializes the current directory. Inspect first; never reinitialize
  Git or discard content. Offer Adopt when files or Git history already exist.
- **Adopt** preserves history, worktree state, user edits, and existing
  instructions. Propose minimal changes; apply only approved changes.
- **Audit** is strictly read-only, including Git configuration and remote
  hosting. Do not create caches, install dependencies, or alter local or remote
  state.

Read the target's `AGENTS.md`, other agent instructions, README, task runner,
CI, Git status, branch, remotes, ignored/untracked files, symlinks, and nested
Git/worktree boundaries. Never print credential-bearing URLs or secret values.
Use `gh` for GitHub operations; do not use browser/API writes.

The scripts provide deterministic inspection and file generation, not user
approval. Show the proposed file list and diff before `--apply --approved`.
Existing files are conflicts. Preserve them; do not overwrite or merge without
explicit approval of a concrete diff. Confine outputs to the target and reject
traversal or symlink escapes. A rejected approval means no writes.

## GitHub and commits

Use `gh` for GitHub reads and writes. Confirm authenticated account and owner.
Repository creation is private by default. Check name collisions before
proposing creation; never adopt or overwrite an existing remote implicitly.
Ask separately before repository creation, initial commit, and push. Stage only
approved task files. Use the configured Git author and Conventional Commits.
Never commit or publish as a side effect of local scaffolding.

Perform each remote or Git mutation in a separate command and check its exit
status before continuing. If repository creation, remote configuration, staging,
or commit fails, stop; do not attempt later steps. Never use `gh repo create
--push` to combine approvals. Before commit, compare the staged path list with
the exact approved file list and preserve pre-existing staged or unstaged work.
If the staged set cannot be isolated safely, stop and ask. After commit, verify
the commit and its file list before using the separately approved push.

## Completion

Report exact validation states: `pass`, `fail`, `not applicable`, or `not
verified`. Distinguish missing tools, invalid configuration, and checks that
could not run. State remaining blockers and an actionable next step. A missing
or uncompleted required Matt setup prevents claiming full bootstrap success.
