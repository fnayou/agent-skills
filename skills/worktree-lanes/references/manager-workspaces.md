# Manager workspaces

Apply this reference only when a terminal or session manager is used to
inspect, create, operate, or close lane state, or when the environment, the
lane contract, or an inventory indicates existing manager state. It extends
the core skill: the lane census, authorization boundaries, and closure
readiness in [SKILL.md](../SKILL.md) still govern, and every term is defined
in [the canonical terminology](terminology.md).

Each gate below is an observation, not a permission. Stop at the first gate
that is unsupported, ambiguous, or fails, and report what was observed.

## Observe each object separately

Observe each of these from its own current source:

- the local branch ref;
- the locally recorded remote-tracking ref;
- the remote branch, only when current evidence establishes it; otherwise it
  is unknown, and no fetch is made to find out without authorization;
- the Git worktree registration: listed, listed-prunable, or absent;
- the checkout path: present or absent;
- the manager workspace;
- its manager tabs and manager panes;
- agent occupancy.

Creating or removing one never implies another. Never infer one from another,
from a name or path, or from earlier output.

A command that requested branch deletion or cleanup is not evidence that it
happened. Report each object from the current inventory, and attribute a cause
only when evidence supports it.

## Extend the lane census

Append this block to the lane census for each lane the request touches. Gather
it read-only.

```text
Manager-backed lane state
- Manager: <identity-or-unknown>
- Local branch ref: <present-or-absent>
- Remote-tracking ref: <present-or-absent>
- Remote branch: <present-or-absent with evidence, or unknown>
- Worktree registration: <listed, listed-prunable, or absent>
- Checkout path: <present-or-absent>
- Manager workspace: <workspace-id> for <resolved-path>, none, or unknown
- Layout: <relevant-tabs-and-panes, or not-applicable>
- Agent occupancy: <agent, pane, directory, lifecycle state>, none, or unknown
- Focus: <focused-object>
```

Include the focus line only when the manager exposes focus and the requested
action can change it.

## Create or open

1. Give the manager an explicit worktree path. Do not rely on its current
   directory, a default, or the focused object.
2. Take workspace, tab, and pane IDs from the manager's responses. Treat them
   as opaque; never predict, construct, or reuse one from earlier output.
3. Read the Git worktree list and the manager inventory again. Continue only
   when the resolved worktree path from each is the same.
4. When the request specifies layout or focus, verify that state from the
   manager.
5. Start an agent only in a manager pane whose ID and working directory were
   verified. Call it ready only when the manager detects the intended agent in
   that pane; a launch command that returned is not readiness.

## Close

### Authorization

Each of these actions needs explicit authorization, though one operator
instruction may name several:

- stopping or releasing agents;
- closing the manager workspace;
- removing the Git worktree or a stale registration;
- deleting the local branch ref;
- deleting the remote branch ref.

A merge request alone authorizes none of them. An explicit branch-deletion
request covers the local ref, the remote ref, or both, as named, and grants no
authority over agents, the manager workspace, or the worktree. Perform only
the authorized actions and report every other object as retained.

A stale remote-tracking ref is reported and retained unless its removal is
explicitly named.

### Teardown

An agent or session outside the target lane performs manager and worktree
teardown. If the closing agent occupies the target lane, it stops and hands
off the remaining teardown to an agent outside it.

The core closure readiness items are observed in this order rather than all at
once. Verify each step by reading the relevant inventory again before starting
the next.

1. Observe **Work preserved** and **No shared resource owned**.
2. Classify every manager pane from the current manager inventory:
   - **idle shell:** report it; it does not block workspace closure;
   - **live agent:** exit or release it only when authorized, then verify that
     the manager no longer reports it live;
   - **foreground command, editor, server, watcher, or unknown:** stop until
     the operator explicitly covers ending it and any work in it is preserved.

   A terminal record of a finished agent is reported only; clear it only when
   the manager supports that and the authorization covers it.
3. Close the manager workspace only when that is authorized and every pane is
   an idle shell or was released, then verify that it is absent from the
   manager inventory.
4. Observe **No running process**. The pane classification and the verified
   absence of the manager workspace establish that no manager-pane process
   remains. Apply every project-declared check for detached or background
   processes as well; missing required evidence is unknown and blocks the next
   step.
5. Observe **Tree clean**, including the ignored files that removal would
   discard, immediately before removing the Git worktree. Remove it only when
   authorized, then verify that the registration and the checkout path are
   both absent.

Removing the Git worktree requires its manager workspace, agents, and
processes to be absent. If worktree removal is authorized but manager closure
is not, retain the worktree and stop.

### Branch refs

Deleting a branch ref is independent of the teardown above. Attempt it
whenever that ref's deletion is explicitly authorized, then verify that the
ref is absent. An authorized ref-only deletion may run from any lane, because
it requires no manager or worktree teardown.

If the ref is checked out or deletion otherwise fails, report that and stop
rather than changing any other lifecycle object. If local deletion is refused
because a registered worktree uses the branch, retain and report the ref.
Never remove a worktree merely to enable deletion.

If safe deletion is rejected after a squash or rebase, do not force it; an
ancestry check that fails is not proof that integration is missing. Apply the
core **Work preserved** rule: use patch-equivalence evidence against refs
already recorded locally when the tooling supports it, otherwise require the
operator's verification. Do not fetch implicitly. Delete by force only on
explicit authority for forced deletion.

### Checkout path already absent

Report **Tree clean** as not observable because the path is absent, and do not
recreate the path. Clean up a stale manager object or Git record only when it
is verified from the current inventory and its removal is authorized.

Removing a listed-prunable registration is a separately observed cleanup under
worktree-removal authority. Use a prune that affects every prunable record
only when all of them are in the authorized scope; otherwise retain the record
and report it.

### Completion

Closure is complete only when every object intended for removal is absent from
the current inventory and every retained branch, ref, record, and manager
object is reported.
