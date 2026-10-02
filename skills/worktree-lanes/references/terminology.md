# Worktree-lane terminology

Use these terms consistently in agent reports, prompts, project contracts, and
documentation.

| Preferred term | Definition | Avoid as a synonym |
|---|---|---|
| **worktree** | A Git working tree: one checkout attached to a shared Git repository. | workspace, when the Git object is meant |
| **worktree lane** | The operational workspace rooted at one worktree, including sessions and processes launched from it. | worktree branch, multi-lane |
| **current lane** | The worktree lane from which the agent is operating. | active branch |
| **primary worktree** | The repository's original, non-linked worktree. It may be on any branch. | main worktree |
| **primary lane** | The worktree lane rooted at the primary worktree. | main lane, base lane |
| **linked lane** | A worktree lane rooted at a linked Git worktree. | secondary lane |
| **integration branch** | The branch into which the current work is intended to merge. It can differ from the remote default branch. | main, base branch |
| **multi-lane state** | A repository state in which more than one worktree lane exists. | multi-worktree mode |
| **lane census** | A read-only account of current, primary, linked, integration, cleanliness, and declared resource state. | preflight, when specifically reporting lanes |
| **lane contract** | Repository-owned instructions for lane creation, shared resources, credentials, task execution, integration, and cleanup. | worktree config |
| **shared resource** | Mutable local state that the lane contract says cannot be used independently by multiple lanes. | Docker or database as a blanket category |
| **resource owner** | The lane currently authorized by the lane contract to serve or control a shared resource. | active lane |
| **claim** | The project-defined transfer of a shared resource to a new resource owner. | switch |
| **handoff** | The verified transition of work or resource ownership from one lane to another. | claim, when work as well as resources moves |

## Usage rules

- Use **worktree lanes** for the general practice and **worktree lane** for one
  operational workspace.
- Use **multi-lane** only as an adjective describing state or coordination.
- Use **main** only when referring to a branch literally named `main`.
- Keep **primary lane**, **integration branch**, and **resource owner** separate;
  they can identify three different lanes or refs.
- Name the lane in every action that could affect a branch, checkout, process,
  shared resource, or external system.
