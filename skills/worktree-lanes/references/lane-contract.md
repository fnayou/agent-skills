# Lane contract

Apply this reference only when the lane census reports the lane contract as
`none-found` and the operator asks for one. The contract is repository-owned:
write it in the project's own instructions, not in this skill. Terms are
defined in [the canonical terminology](terminology.md).

## Ask the operator

Ask once, listing everything that is missing:

- Which resources, if any, can only be used by one lane at a time?
- For each one, which command reports its owner and which command claims it?
- Which branch receives integrated work, and by what method (merge, squash,
  rebase)?
- Which files that Git ignores must a new lane receive, and how?
- Which agents may perform a claim without asking?
- How is a lane closed and its worktree removed?

Do not guess an answer from files in the repository.

## Contract skeleton

Copy this into the project's agent instructions and replace every
placeholder. Delete a section that does not apply and say so.

```markdown
## Worktree lanes

- Integration branch: <branch>, integrated by <merge|squash|rebase> through
  <pull request|local merge>.
- Create a lane: <command or manual steps>.
- Files copied into a new lane: <list or none>.
- Lanes are concurrency boundaries, not credential sandboxes.

### Shared resources

| Resource | Ownership check | Claim command | Agents may claim |
|---|---|---|---|
| <name> | <command> | <command> | <yes or operator only> |

### Closing a lane

<project-specific cleanup, and anything that must not be removed>
```

## Example: shared containers

Use when containers have fixed names, so two lanes cannot run them together.

| Resource | Ownership check | Claim command | Agents may claim |
|---|---|---|---|
| `<project>` containers | `<task> docker:owner` | `<task> docker:claim` | operator only |

The claim refuses while anything runs in the containers. Dependent work
starts only after the ownership check names the receiving lane.

## Example: host port only

Use when each lane already gets isolated containers, for example because
compose derives the project name from the directory, and only a published
host port can collide.

| Resource | Ownership check | Claim command | Agents may claim |
|---|---|---|---|
| host port `<port>` | none, each lane sets its own | set a distinct `HOST_PORT` in the lane's copied `.env` | yes |

State the rule in the contract: no two lanes use the same `HOST_PORT`, and the
`.env` file is copied into each new lane rather than shared.

## Rules for the contract

- Declare only what exists. An undeclared resource stays `unknown`.
- Give every claim an ownership check that can be repeated afterwards.
- Keep tool installation and version pinning in the project's installer. If the
  project depends on a worktree manager behavior, such as refusing local
  merges through hooks, record the exact version at which the project measured
  that behavior and re-measure it on any other version.
