# 06 — pi-sequence

Three independent chores for pi, one after the other. They must share one pane: a fresh worker for each brief, no new pane per chore, and one report block per run.

## Prompt

```text
Use pi workers through herdr for this. In the repository <FIXTURE>, on a new branch chore/three created from main, there are three independent chores. Treat each as its own task with its own brief, one after the other, in this order. Chore 1: in README.md change the word "recieve" to "receive"; commit as "docs: fix typo". Chore 2: in README.md change "Version: 0.1.0" to "Version: 0.1.1"; commit as "chore: bump version". Chore 3: create the file CHANGELOG.md containing the single line "0.1.1 - fix typo"; commit as "docs: add changelog". Do not push. Leave main untouched.
```

## Expected behaviour

- One pane, split once, relabelled for each run.
- Three runs, numbered 1 to 3. Each brief goes to a fresh pi worker: the previous one is ended and a new one started in the same pane.
- The foreman verifies each commit before it starts the next run.
- The pane is closed once, after run 3.

## Operator's part

None. No dialog is expected.

## Check

```bash
python3 skills/foreman-workers/tests/check.py 06-pi-sequence <FIXTURE>
```

Pass: `RESULT 06-pi-sequence PASS 8/8`.

## Observe

- Number of `herdr pane split` commands the foreman ran. Expected: 1.
- Number of `herdr agent start` commands. Expected: 3.
- Did every run get its own blocks, with `reused pane` and `fresh worker` on runs 2 and 3?
- Did the summary count 3 runs, 1 pane opened, 2 reuses?
