# project-bootstrap

Creates, adopts, or audits an AI-ready project foundation. It focuses on
engineering conventions and governance, not application code.

## Modes

- **Create:** prepare the current directory with confirmed project details.
- **Adopt:** propose minimal additions while preserving existing files,
  history, and local changes.
- **Audit:** report compliance without changing local or remote state.

The generated foundation includes root `AGENTS.md`, a meaningful README,
editor and Git hygiene files, GitHub community guidance and issue forms, and a
working Taskfile. Docker is opt-in. The skill asks before writes and requires
separate approval for repository creation, commits, and pushes. Audit uses
read-only inspection and does not run project-defined tasks.

The Matt Pocock setup workflow is required. When its outputs are missing, the
skill asks the user to invoke the installed setup skill; it does not fabricate
those files or claim setup is complete before validating them.
