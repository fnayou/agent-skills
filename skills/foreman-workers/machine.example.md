# Machine facts

Copy this file to `~/.config/foreman-workers/machine.md` and edit it. The skill reads it once before the first spawn. Keep it to facts a foreman cannot find by looking.

Every entry below is an example of a fact that has cost a run on some machine. Keep the ones that hold on yours, with your own names in place of the `<…>`, and delete the rest.

## Local model

- pi's default model is a local one served by `<model server>`. When that server is not running, a prompt to a pi worker stalls or times out.

- Models pi may be given a goal brief on: none. Name a model here to allow it.
- Stronger pi model to escalate to when the default fails a step: none. Name one here (`--provider <p> --model <m>`) to give the escalation ladder its third rung.

## Hooks

- A hook that shortens command output is active for `<kinds>`. It changes what `ls`, `grep`, `find` and git commands print: `git commit` prints `<what it prints>`.
- That hook rewrites a command before the permission check: `git status` reaches the check as `<prefix> git status`. In allowlist patterns for the commands it rewrites, write the prefix: `Bash(<prefix> git status *)`. Commands it leaves alone take no prefix.
- A plugin that shortens replies is active for `<kinds>`: workers answer in clipped sentences. Raw command output is not affected.

## Shell

- A function runs on every directory change and has hung an agent's shell for minutes. Use absolute paths and `git -C <dir>`; for a command that needs a working directory, `/bin/sh -c 'cd <dir> && <command>'`.
- `ls` is an alias for `<another tool>`. Use `/bin/ls`.
- `cp`, `mv` and `rm` are aliases that ask before they overwrite or delete, and `cat` is an alias for a pager. In an agent's shell nobody answers the question. Use `/bin/cp`, `/bin/mv`, `/bin/rm` and `/bin/cat`.

## Power

- The machine goes to sleep after `<n>` minutes without input, and a run that is under way then stalls. Start long runs only while the operator is at the machine.

## Limits

- The foreman's shell tool stops a foreground command after 10 minutes. Keep `herdr agent prompt --wait --timeout` at 540000 or less.
