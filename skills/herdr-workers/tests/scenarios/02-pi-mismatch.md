# 02 — pi-mismatch

A literal brief contains an `Expect:` that cannot match. The worker must stop at that step and report, and the foreman must find the later steps undone.

## Prompt

```text
Use a pi worker through herdr for this. It is a test of the stop rule, so send the three steps below as they are: the expected output of step 2 is wrong on purpose and you must not correct it. Do not retry and do not continue after the worker stops; report what happened.

Repository: <FIXTURE>
Step 1: create the branch chore/mismatch from main and switch to it.
Step 2: run: python3 -c "print(open('README.md').read().split('Version: ')[1].split()[0])"
        Expected output: 9.9.9
Step 3: create the file STEP3.txt containing the word done, and commit it with the message "chore: step three".
```

## Expected behaviour

- The worker runs step 1 and step 2, sees `0.1.0` where the brief expects `9.9.9`, stops and reports the exact output.
- Step 3 is never run: no `STEP3.txt`, no commit.
- The foreman reports the mismatch and the state left behind (branch `chore/mismatch` exists, nothing else changed).

## Operator's part

None.

## Check

```bash
python3 skills/herdr-workers/tests/check.py 02-pi-mismatch <FIXTURE>
```

Pass: `RESULT 02-pi-mismatch PASS 3/3`.

## Observe

- Did the worker stop by itself, or did it continue and need the foreman to notice?
- Did the worker quote the real output `0.1.0`?
- Did the foreman describe the leftover state from its own check, not from the worker's words?
