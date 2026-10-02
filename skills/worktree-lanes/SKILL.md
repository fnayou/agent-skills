---
name: worktree-lanes
description: Establish and coordinate Git worktree lanes before repository work. Use when operating in a linked worktree, when multiple worktrees or parallel agent sessions exist, or when work may contend for project-declared shared resources. Do not use for ordinary single-checkout Git work.
---

# Worktree Lanes

Treat each worktree as an operational lane. Establish lane identity before
acting, then obey the repository's lane contract without assuming that a
branch named `main`, a container runtime, or a particular worktree manager
exists.

Read [the canonical terminology](references/terminology.md) before producing a
lane report.

## Establish the lane census

Before the first repository-affecting action:

1. Read all applicable repository instructions.
2. Confirm that the current directory belongs to a Git worktree. If it does
   not, stop applying this skill. If the repository has one worktree and the
   request does not concern worktrees, continue normally without a lane report.
3. Inspect local Git state without fetching, switching, stashing, or changing
   refs. Resolve:
   - the current worktree root and branch or detached commit;
   - the Git common directory and primary worktree;
   - every linked worktree and its branch or detached commit;
   - cleanliness and local divergence where the required refs already exist.
4. Resolve the integration branch in this order: an explicit operator choice,
   the repository's lane contract, the current pull request's base, then the
   remote default branch already recorded locally. Report it as unknown rather
   than guessing.
5. Discover the repository's lane contract in its applicable agent
   instructions, development documentation, task runner, or worktree tooling.
   Identify only resources and ownership checks that the project explicitly
   declares. Do not infer that Docker, secrets, databases, ports, or caches are
   shared merely because they exist.
6. Report the census before proposing a lane-sensitive action.

Use this compact report:

```text
Lane census
- Current lane: <branch-or-detached> at <worktree-root>
- Primary lane: <branch-or-detached> at <primary-worktree-root>
- Integration branch: <branch-or-unknown>
- Other linked lanes: <list-or-none>
- Current tree: <clean-or-summary>
- Shared resources: <owners-and-state, none-declared, or unknown>
- Lane contract: <source-or-none-found>
```

The census is complete only when current, primary, and integration identities
are distinct in the report; never use `main` as a synonym for any of them.

## Operate within the lane

- Perform writes only in the current lane unless the operator explicitly
  directs work elsewhere.
- Treat another lane's branch, files, processes, and resource claim as active
  work. Read across lanes only when needed to establish state or compare a
  contract; do not clean up or repair another lane opportunistically.
- Treat worktree lanes as concurrency isolation, not security sandboxes.
  Branch code in a lane can access every credential and service available to
  its process.
- Before executing branch-controlled code that can affect a shared resource,
  verify that the current lane contains the relevant safety contract. If the
  contract may be stale, compare it read-only with the integration branch and
  stop on a material mismatch.
- Use only project-declared ownership checks and claim commands. A busy,
  unreachable, ambiguous, or differently owned resource is a refusal, not an
  invitation to kill processes or override ownership.
- A claim transfers resource ownership; it does not authorize rebuilds,
  refreshes, migrations, deployments, or server access. Authorize those
  separately through the ordinary task boundary.
- Preserve the operator's authority over rebase, force-push, merge, deploy,
  credential movement, destructive cleanup, and external mutations.

## Coordinate lane transitions

When handing a shared resource to another lane, establish that the current
owner is idle using the project's own check, perform the declared claim, and
verify the new owner before running dependent work. Stop if any part of that
sequence is unsupported or ambiguous.

When closing a lane, first establish that its work is preserved, its tree is
clean, and it owns no running process or shared resource. Removing a worktree
or branch requires explicit authorization. After integration, synchronize and
verify the primary lane before making it the resource owner; merging a pull
request alone does not perform that handoff.

When another coordination skill is active, include the intended worktree lane
in every actionable prompt and handoff. Do not duplicate this skill's lane
rules in that coordination skill.
