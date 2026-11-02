# Profiles and questions

Support POC, CLI, library, and application profiles. Detect likely profile from
existing files, explain the evidence, and confirm with the user. Unknown stack
means no source starter, CI workflow, or claimed build/test commands.

## Required choices

For Create, confirm repository display name and slug, owner, description,
visibility (private default), and license choice, including explicit “no
license.” For non-POC profiles, ask release convention (SemVer, CalVer, or
none); POCs default to none. Ask whether Docker is wanted. If yes, ask whether
the image is for the application, development dependencies, or both.

Ask only for unresolved project facts. Use detected values as proposals, never
as confirmed facts. Do not invent contacts, URLs, project claims, or labels.
Generate selected license text only from canonical content confirmed by the
user; `scaffold.py` accepts that content through `--license-text`.

## Baseline

Generate a meaningful README, root `AGENTS.md`, `.editorconfig`, `.gitignore`,
`.gitattributes`, root `Taskfile.yml`, and GitHub contribution/security/support
files and issue forms when supported by verified project facts. Never create
empty source, test, docs, changelog, or CI placeholders. License files require
the user’s selected license. For an existing `AGENTS.md`, present a minimal
patch; preserve other agent instruction files and report conflicts.

Issue forms must cover problem/outcome and reproduction or acceptance criteria.
Use GitHub issue forms and their `config.yml`; align labels to the Matt setup
or repository configuration. PR template belongs at
`.github/PULL_REQUEST_TEMPLATE.md` and covers summary, issue, validation,
impact/risk/rollback, and a concise checklist.
