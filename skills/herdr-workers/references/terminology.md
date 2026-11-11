# Herdr-workers terminology

The language of a skill in which one session delegates execution to agents
running in herdr panes. Use these terms consistently in briefs, reports to the
operator, profiles, and documentation.

Decisions that are hard to reverse are recorded in the repository's
`docs/adr/herdr-workers-*.md` files.

| Preferred term | Definition | Avoid as a synonym |
|---|---|---|
| **foreman** | The session that plans the work, writes the brief and verifies the result. It reads but never changes state itself: every change goes through a worker. Claude Code by default; another agent that takes the role is an unprofiled foreman until it has a foreman profile. | orchestrator, main agent, lead |
| **worker** | An agent in a herdr pane, visible to the operator while it runs, that executes what the foreman briefed. A worker never starts workers of its own. | subagent, child |
| **kind** | The agent program a worker runs, as herdr names it: pi, claude, codex, opencode and others. | agent type, tool |
| **profile** | The observed facts about one kind that a foreman needs to run it as a worker: how it starts, how it asks for approval, how it is restricted, which instruction files it loads. A profile holds only what a test run showed. | adapter, driver, config |
| **unprofiled kind** | A kind herdr can start but for which no profile exists yet. Its workers get the most conservative handling. | |
| **mode** | The restriction a worker is started under, which bounds what it can do whatever its brief says: a tool set for pi, a permission mode for claude, a sandbox for codex. The foreman picks the least capable mode that can execute the brief. | permission level, sandbox (as the general word) |
| **brief** | The complete instructions a foreman sends to a worker, and the whole of what that worker knows about the task. | prompt, task description |
| **literal brief** | A brief made of numbered steps with exact commands and edits, each followed by the output to expect. Any worker kind can receive one. | instruction-led, light worker, pi brief |
| **goal brief** | A brief that states a goal, its context, what to leave alone and the shape of the report, and leaves the steps to the worker. Any worker kind on a capable model can receive one. | goal-led, heavy worker, claude brief |
| **run** | One brief executed by one worker, from its start to its verified end. It is the unit the foreman reports on; a pane may host several runs in turn. | task, job, session |
| **worker rules** | The discipline every worker follows whatever its task, shipped with the skill and loaded when the worker starts, so that a brief carries only the task. | system prompt, standing instructions |
| **operator rules** | The operator's own standing rules, which rank above worker rules and above any brief. They are the operator's property and live outside the skill. | global instructions, user rules |
| **runbook** | A literal brief stored as a file because it is too long for one prompt. Written outside the working tree it is the foreman's planning artifact; inside the repository it is a change, made by a worker. | plan file, script |
| **dialog** | Anything a worker shows that waits for an answer before it continues: an approval request, a question, a notice with choices. It is judged by what the pane shows, whatever status herdr reports. | prompt, popup |
| **foreman-handled dialog** | A dialog the operator has authorised the foreman to answer for single use: routine, reversible, called for by the brief, inside the working tree. | first class, routine dialog |
| **operator-reserved dialog** | A dialog only the operator answers: everything that is not foreman-handled, and every dialog of an unprofiled kind. | second class, operator-only dialog |
| **standing allowlist** | The short list of narrow, reversible commands in a profile that workers of that kind may run without a dialog in every run. The operator approved it once, in review. | |
| **run allowlist** | The task-specific commands the foreman proposes with its plan and the operator approves once for that run. It applies to one worker and is stored nowhere. | always-allow, permissions |
| **run log** | The operator's record of runs on this machine, one row per run, which the foreman adds after its summary. It exists only where the operator created the file, and lives outside the skill. | history, journal |
| **operator** | The human who owns the machine, watches the panes and keeps every decision the foreman may not take. | user |

## Terms owned elsewhere

This skill uses herdr's workspaces, tabs and panes, and Git worktrees. Those
terms are defined once, in the worktree-lanes vocabulary:
[`../../worktree-lanes/references/terminology.md`](../../worktree-lanes/references/terminology.md).
This file does not define them again.

| herdr-workers says | Defined there as |
|---|---|
| herdr workspace | **manager workspace** |
| herdr tab | **manager tab** |
| herdr pane, pane | **manager pane** |
| worktree | **worktree** |
