# GitHub standards

Use `gh` exclusively for GitHub operations. The canonical pull request template
is `.github/PULL_REQUEST_TEMPLATE.md`. Bug and feature forms use
`.github/ISSUE_TEMPLATE/*.yml`; include `config.yml` only when it provides
working links or a deliberate blank-issue policy.

Create `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, and `SUPPORT.md`
with useful, accurate guidance. Do not invent security contacts or support
channels. Link private vulnerability reporting only after verifying it is
enabled; otherwise ask for a suitable channel and report the unresolved item.
Create a license only after an explicit choice. Use the confirmed display name
in documentation. Do not claim Actions, checks, release practices, or policies
that are not configured.

Before any remote write, present the exact operation and get explicit approval.
Check repository collisions; never overwrite an existing repository. A local
plan or approval to scaffold does not approve repository creation, commits, or
pushes.
