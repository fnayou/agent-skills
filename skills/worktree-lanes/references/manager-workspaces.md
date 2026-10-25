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
- the manager workspace group and its current members, where grouping exists;
- the manager workspace;
- its manager tabs and manager panes;
- agent occupancy.

Creating or removing one never implies another. Never infer one from another,
from a name or path, or from earlier output.

A command that requested branch deletion or cleanup is not evidence that it
happened. Report each object from the current inventory, and attribute a cause
only when evidence supports it.

Use Git state for worktree registrations, local branch refs, remote-tracking
refs, divergence, and tree cleanliness. Use current remote evidence for remote
branches. Use manager inventory for workspace groups, workspaces, tabs, panes,
processes, and agent occupancy. These sources complement one another; none
substitutes for another.

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
- Manager workspace group: <group-id and member-workspaces, none, not-applicable, or unknown>
- Manager workspace: <workspace-id> for <resolved-path>, none, or unknown
- Layout: <relevant-tabs-and-panes, or not-applicable>
- Agent occupancy: <agent, pane, directory, lifecycle state>, none, or unknown
- Focus: <focused-object>
```

Include the focus line only when the manager exposes focus and the requested
action can change it.

## Compound manager actions

Before any manager command that can change a lifecycle object, establish from
current manager help or documentation for the installed version whether it is
compound and what effects it has. If either remains unknown, stop. Do not infer
effects from the command name, observed state, or an earlier run.

For a compound manager action:

1. Enumerate every affected object in
   [Observe each object separately](#observe-each-object-separately), plus every
   affected process and lane.
2. Obtain authorization covering each affected object and action.
3. Observe every applicable readiness gate that the action would make
   unavailable. Do not use the action when it crosses ordered teardown steps
   and prevents a required intermediate inventory.

Afterwards, inventory every lifecycle object separately. A partial effect is
a partial failure: report the resulting state and do not repair or clean it up
without separate authorization.

## Create or open

1. Choose the manager layout:
   - When one request creates or opens several linked lanes, use one manager
     workspace group when the manager supports grouping and neither the lane
     contract nor the operator requires independent workspaces. Record the
     expected member workspaces and resolved paths. Create a group, or reuse
     one only when the operator names it or every current member resolves to
     the current lane or a lane named by the request. Add each linked-lane
     workspace using the opaque group identifier returned by the manager or
     read from current inventory, then verify that actual membership matches
     the expected membership. If it differs, stop and report it.
   - Otherwise, use independent top-level workspaces.
2. Give the manager an explicit worktree path. Do not rely on its current
   directory, a default, or the focused object.
3. Take workspace, tab, and pane IDs from the manager's responses. Treat them
   as opaque; never predict, construct, or reuse one from earlier output.
4. Read the Git worktree list and the manager inventory again. Continue only
   when the resolved worktree path from each is the same.
5. When the request specifies layout or focus, verify that state from the
   manager.
6. Start an agent only in a manager pane whose ID and working directory were
   verified. Call it ready only when the manager detects the intended agent in
   that pane; a launch command that returned is not readiness.

## Close

### Authorization

Each of these actions needs explicit authorization, though one operator
instruction may name several:

- stopping or releasing agents;
- closing or removing the manager workspace group;
- closing the manager workspace;
- removing the Git worktree or a stale registration;
- deleting the local branch ref;
- deleting the remote branch ref.

A merge request alone authorizes none of them. An explicit branch-deletion
request covers the local ref, the remote ref, or both, as named, and grants no
authority over agents, the manager workspace, or the worktree. Perform only
the authorized actions and report every other object as retained.

A stale remote-tracking ref is reported and retained unless its removal is
explicitly named or an authorized remote-branch deletion removes it as a side
effect. Include that side effect in the deletion scope and verify it afterwards.

A manager workspace group is retained and reported unless its removal is
explicitly authorized. Apply the compound-action rules when its removal is
compound, and verify its resulting state.

Authorization for a manager workspace group covers only the members and
affected lifecycle objects reported when the operator grants it. If membership
or expected effects change, obtain new authorization for the changed scope.

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
5. Re-observe **Work preserved** and **Tree clean**, including the ignored files
   that removal would discard, immediately before removing the Git worktree.
   Remove it only when authorized, then verify that the registration and the
   checkout path are both absent.

Removing the Git worktree requires its manager workspace, agents, and
processes to be absent. If worktree removal is authorized but manager closure
is not, retain the worktree and stop.

### Branch refs

Deleting a branch ref is independent of the teardown above. Re-observe **Work
preserved** against refs that will remain after every authorized deletion and
its side effects. Then attempt each explicitly authorized deletion and verify
that the ref is absent. An authorized ref-only deletion may run from any lane,
because it requires no manager or worktree teardown.

If the ref is checked out or deletion otherwise fails, report that and stop
rather than changing any other lifecycle object. If local deletion is refused
because a registered worktree uses the branch, retain and report the ref.
Never remove a worktree merely to enable deletion.

If safe deletion is rejected after a squash or rebase, do not force it; an
ancestry check that fails is not proof that integration is missing. Apply the
core **Work preserved** rule. Do not fetch implicitly. Delete by force only on
explicit authority for forced deletion.

### Checkout path already absent

Report **Tree clean** as not observable because the path is absent, and do not
recreate the path. Clean up a stale manager object or Git record only when it
is verified from the current inventory and its removal is authorized.

Removing a listed-prunable registration is a separately observed cleanup under
worktree-removal authority. Use a prune that affects every prunable record
only when all of them are in the authorized scope; otherwise retain the record
and report it.

### After a squash or rebase merge

A merged pull request leaves several independent objects behind. Observe each
from its own source, in this order, and report each as removed or retained:

1. Pull request state, from current remote evidence.
2. Remote branch: the host may delete it automatically on merge.
3. Local branch ref.
4. Locally recorded remote-tracking ref.
5. Git worktree registration.
6. Checkout path, with the ignored files that removal would discard.
7. Manager workspace, and its group where one exists.

Rebase and squash rewrite commits, so an ancestry check on the lane HEAD fails
even though the work is integrated. Use the core **Work preserved** rule: name
a retained ref that contains the integrated work, then record patch-equivalence
evidence against it. A worktree manager may also report the branch as
integrated by tree equivalence; treat that as evidence to record, not as
authorization.

A manager removal command such as `wt remove` is a compound manager action. It
can delete the checkout, the local branch ref, and the ignored files in one
step. Read the installed version's help first, enumerate those objects, and
obtain authorization that covers each one.

Remote branch deletion by the host leaves a stale remote-tracking ref. Report
and retain it. Removing it contacts the remote, for example
`git remote prune origin` or `git fetch --prune`, so run it only when the
operator names that action.

The manager can drop a workspace on its own after a merge while Git still lists
the worktree. Never infer one from the other; read both inventories.

### Completion

Closure is complete only when every object intended for removal is absent from
the current inventory and every retained branch, ref, record, and manager
object is reported.
