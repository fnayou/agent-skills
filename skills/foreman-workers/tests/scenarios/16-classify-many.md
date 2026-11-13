# 16 — classify-many

A task whose execution is long and repetitive next to its plan: twelve documents, each to be given a first line that names its category. Deciding the category takes a look at each document; writing the twelve lines is the same step twelve times. The paid models decide; a pi worker makes the edits.

Compare with 15, where the change is one line.

## Prompt

```text
Use herdr workers for this. In the repository <FIXTURE>, the inbox directory holds twelve documents. Each is an invoice, a letter or a report. On a new branch chore/classify created from main, add a first line to every document that reads "Category: invoice", "Category: letter" or "Category: report", according to its content, and leave the rest of each document as it is. Commit all of it as one commit with the message "chore: classify inbox". Do not push. Leave main untouched.
```

## Expected behaviour

- The categories are decided by a paid model: by the foreman, which reads the twelve documents itself, or by a paid worker on a goal brief that returns a runbook.
- The twelve edits and the commit are made by a pi worker, from a literal brief or a runbook that names each file and its line. No paid worker makes the edits.
- Twelve documents are below the count at which a script takes the place of steps: the edits are written out, and no script is written.
- The foreman verifies every document from ground truth before it reports.

## Operator's part

A trust dialog may appear when a Claude Code worker starts. Answer nothing else unless the foreman hands you a dialog.

## Check

```bash
python3 skills/foreman-workers/tests/check.py 16-classify-many <FIXTURE>
```

Pass: `RESULT 16-classify-many PASS 8/8`. The answer key is in `skills/foreman-workers/tests/check.py`.

## Observe

- Who decided the categories, and who made the edits: how many runs, which kinds, which brief types.
- The size of the brief or runbook the pi worker got, and the mode it was started in.
- Did the pi worker get through twelve edits in one prompt? Any stop, any retry?
- Was a script written? If so: where, and what did the foreman tell the operator before the start?
- Paid tokens of the foreman and of every paid worker.
