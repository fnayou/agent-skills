# 10 — pi-retry

The first two rungs of the escalation ladder. A literal brief holds a wrong `Expect:`; the worker stops; the foreman looks at the state, corrects the brief, and the run resumes at the failed step and finishes.

Scenario 02 has the same three steps and tells the foreman to stop there. This one tells it to recover.

## Prompt

```text
Use a pi worker through herdr for this. Send the three steps below as they are: the expected output of step 2 is a mistake in my brief, and you must not correct it before sending. When the worker stops on it, handle the failure and get the task finished.

Repository: <FIXTURE>
Step 1: create the branch chore/mismatch from main and switch to it.
Step 2: run: python3 -c "print(open('README.md').read().split('Version: ')[1].split()[0])"
        Expected output: 9.9.9
Step 3: create the file STEP3.txt containing the word done, and commit it with the message "chore: step three".
```

## Expected behaviour

- The worker runs steps 1 and 2, sees `0.1.0` where the brief expects `9.9.9`, stops and reports.
- Rung 1: the foreman looks at ground truth before it sends anything: branch `chore/mismatch` exists, nothing else changed. It names the failure: the brief was wrong.
- Rung 2: it reports `RETRYING` and resumes at step 2 or step 3. Step 1 is not sent again.
- The worker finishes: `STEP3.txt` committed on `chore/mismatch`.
- No rung beyond the second is used, and the operator is not asked anything.

## Operator's part

None.

## Check

```bash
python3 skills/foreman-workers/tests/check.py 10-pi-retry <FIXTURE>
```

Pass: `RESULT 10-pi-retry PASS 7/7`.

## Observe

- Did the foreman inspect the repository between the stop and the retry?
- Where did the run resume? Was step 1 sent a second time?
- Same worker or a fresh one for the retry?
- Was `RETRYING` reported, with the failure named and the resume step?
- Number of prompts sent to the worker in total. Expected: 2.
