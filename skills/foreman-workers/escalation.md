# Escalation

Read this when a run does not end in a verified result: the worker stopped on a mismatch, it asked something that blocks it, or your own verification found the result wrong.

Climb one rung at a time. Every rung starts from state you have verified yourself.

## The ladder

1. **Stop and look.** Send nothing yet. Inspect ground truth: the diff, `git status`, files the run left behind, processes still running. Name the failure:
   - *the brief was wrong*: an `Expect:` that could not match, a command that could not work;
   - *the world differs*: the facts the brief was built on have changed;
   - *the worker went wrong*: it did something else than the step said.

   A retry waits until you know what state the run left and that continuing from it is safe.

2. **Correct the brief and retry once, on the same kind.** Resume at the failed step, never at step 1: steps that succeeded stay done. To the same worker when it is still there, as its next prompt, saying which step was accepted or corrected and where to resume; otherwise to a fresh worker, with a brief that starts by stating the current state. Report `RETRYING`.

   A step gets two attempts on a local model, the first one included.

3. **A stronger model of the same kind**, when the machine file names one for this. Without one, skip this rung.

4. **A paid worker on a goal brief.** Give it the state as you verified it and the part still to do ("finish steps 6 to 10 of runbook X from the current state"), not the history of failures. Report `ESCALATED`, naming the rung you leave and the rung you go to.

The run has `FAILED` when no rung is left that is safe and that you are authorised to take, or when rung 4 fails. Report the state it leaves.

## What stays with the operator

Ask the operator only for what is theirs:

- **Cleanup that destroys.** Undoing a half-done run with a delete, a `git reset`, a `git checkout -- .` is an operator-reserved action. Say what would be removed, and wait. Often no cleanup is needed: resume from the state as it is.
- **Intent.** When the failure shows the task itself is unclear, a stronger worker does not help. Ask.
- **Authority.** A rung that needs a model, a command or an access the operator has not granted is not yours to take.
