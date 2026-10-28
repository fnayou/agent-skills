# worktree-lanes

Treat each Git worktree as an operational lane. Before the first
repository-affecting action, the skill reads the repository's instructions and
produces a lane census that names:

- the current lane and the primary lane;
- the integration branch;
- other linked lanes and the state of the current tree;
- shared resources and who owns them;
- the repository's lane contract, or that none was found.

It also covers handing off a shared resource and closing a lane, with a rule
that work is preserved before anything is removed. The canonical vocabulary is
in the skill's
[terminology reference](https://github.com/fnayou/agent-skills/blob/main/skills/worktree-lanes/references/terminology.md).
