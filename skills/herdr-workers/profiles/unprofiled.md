# Profile: unprofiled kind

What a foreman does with a kind herdr can start and that has no profile in this directory. Nothing has been seen about such a kind, so it gets the most conservative handling, and its run is how its profile begins.

## Before the start

1. **Tell the operator the kind is unprofiled**, and what that means for this run: every dialog will be theirs to answer, and the pane is closed after one run. Name the profiled kind that would take the same brief.
2. **Read its help, and only its help**: `<kind> --help`, and `<kind> <subcommand> --help` for the subcommands it lists. Any other subcommand can hang your shell for minutes. Look for:
   - arguments that restrict it: a read-only or sandbox mode, a permission mode, a tool list;
   - arguments that stop it from asking: auto-approve, skip permissions and the like. Never pass one;
   - how its model is chosen, and how it is given instructions at start.
3. **Find out what a run would spend**: which provider and model it would use. Read its configuration files for that; leave its credential files closed. When it would spend paid tokens, or you cannot tell, say so and wait for the operator's word before you start it.

## Start

```bash
herdr agent start <name> --kind <kind> --pane "$P" --timeout 90000 -- <the most restrictive arguments its help showed>
```

- Pick the most restrictive mode the help names that can still execute the brief. When the help names none, start it with no arguments: its dialogs and the brief are then its only fence, and you say so in `STARTED`.
- Pass no allowlist. An allowlist is approved for a kind whose matching rules are known.
- A kind can be reported ready before it is. Read the pane after the start, and again after the first prompt, to see that the brief arrived.

In the report header write the kind as `<kind> (unprofiled)`.

## Brief

- Send a **literal brief**. A goal brief goes to an unprofiled kind only when the operator says its model takes one.
- No rule argument is known for this kind, so the brief carries the rules: the text of [`../worker-rules.md`](../worker-rules.md) at its top, then the operator rules this task touches.
- The brief holds no destructive step: no delete, no overwrite or move of many files, no history rewrite, nothing outside the working tree. A task that needs one goes to a profiled kind.

## Dialogs

Every dialog of an unprofiled kind is operator-reserved, a read-only command included. You do not know what its options mean, which key selects which, or whether one of them grants more than a single use.

- Read the pane after every wait, whatever status herdr reports. How this kind shows that it waits has not been seen.
- A kind may show no dialog at all: one ran shell commands under its default settings without asking. Its brief is then its only fence, which is why the brief holds no destructive step.
- Report the dialog as the guard rails say and wait. Enter the operator's answer for them only when they name the exact key.

## End

Close the pane after its run. How this kind quits has not been seen, so its pane is not reused.

## Record what you saw

The run is the first evidence about this kind. Write it down as a draft profile in a scratch directory outside the working tree, under the headings the other profiles use (Modes, Start, Brief, Dialogs, Seen in runs), and holding only what this run showed:

- the start command you ran, and what the pane showed when the worker was ready;
- the restricting arguments its help lists, marked as read in the help and not tried, unless you used them;
- each dialog: its text, its options, the status herdr reported while it was open;
- the instruction files it said it loaded, and the provider and model it ran on;
- whatever went wrong.

Name the draft's path under `kept:` in the summary. A draft becomes a profile through a change to the skill, made by a worker and reviewed by the operator.
