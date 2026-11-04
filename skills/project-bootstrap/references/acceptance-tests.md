# V1 acceptance traceability

Validation record for the `project-bootstrap-codex-handoff.md` 42 scenarios.
Automated evidence comes from `tests/test_project_bootstrap.py` (25 tests),
`./scripts/verify`, isolated installer checks, and pinned `skills-ref`.
Agent-level evidence comes from two kinds of runs. Codex CLI scenario runs,
including one discarded PATH preflight, used scripted answers and isolated fake
GitHub/Git commands; earlier scenario answers were supplied in prompts, not
live interactive approval turns, and the final Codex Adopt run used interactive
approvals. Actual host invocations were Codex (the successful commit/push to a
local bare remote), Claude Code, Pi, and OpenCode Audits; these host Audits were not scripted
scenario runs. The independent `validate.py --audit`
result on the unchanged fixture is 15 pass, 2 not verified, 2 not applicable;
Claude's reported 17 pass over-counted the two not-verified checks. No real GitHub writes occurred, and
container lifecycle did not run. The only push went to a local bare remote,
which proves mechanics, not GitHub. Pi 1.4.0 and OpenCode Audit invocations
were verified; each reported 15 pass, 2 not verified, 2 not applicable.

| # | Acceptance scenario | Implementation | Test or verification evidence | Status |
|---:|---|---|---|---|
| 1 | Agent Skills structure and metadata | `SKILL.md` | Pinned `skills-ref validate` on this skill and full skill set | passed |
| 2 | Existing installer discovers skill | root installer discovers `skills/*/SKILL.md` | `./scripts/verify` installer link and check-mode fixtures | passed |
| 3 | Useful, bounded trigger | `SKILL.md` description | Scope reviewed; Codex loaded it when explicitly requested, but automatic trigger selection was not tested | partially verified |
| 4 | Existing skills remain valid | repository verifier | `./scripts/verify` | passed |
| 5 | Empty directory detection | `scripts/inspect.py` | `test_inspection_is_read_only_and_reports_empty_directory` | passed |
| 6 | Git state, remotes, status and untracked files | `scripts/inspect.py` | Git inspection and zero-mutation Audit tests | passed |
| 7 | Nested Git/worktree boundaries | `scripts/inspect.py` reports nested `.git` boundaries | `test_inspection_reports_git_boundaries_and_redacts_remote_credentials`; linked-worktree-specific fixture absent | partially verified |
| 8 | Preserve existing instructions and ignore rules | conflict-aware `scripts/scaffold.py` | rerun and Adopt preservation tests | passed |
| 9 | Reject traversal and symlink escapes | slug validation, `confined()`, setup source confinement | invalid slug, scaffold symlink, inspection escape, and setup symlink tests | passed |
| 10 | Generic POC without fake runtime/CI | profile templates | POC scaffold and no-Docker assertions | passed |
| 11 | CLI profile without invented runtime | profile templates | `test_cli_profile_stays_language_agnostic_without_placeholder_tasks`; Task discovery if installed | passed |
| 12 | Display name and slug usage | README renderer and required slug input | Codex fixture generated `# Fixture Sample` and called fake create with `fixture-user/fixture-sample` | passed |
| 13 | Git/editor hygiene and secret exclusions | baseline templates | `git check-ignore` checks for `.env`, private variants, PEM/key files; `.env.example` remains trackable | passed |
| 14 | Community docs, issue forms and PR template | baseline templates | generated-content assertions; Ruby/Psych parses issue YAML when available | passed |
| 15 | Rerun and local customization preservation | add-only scaffold and setup | rerun preserves README; setup preserves local Compose and env files | passed |
| 16 | Adopt minimal patch, history and user state | add-only scaffold | Git fixture proves HEAD, staged state, remote and uncommitted edits survive; preview is new-file diff only | partially verified |
| 17 | Missing Matt setup skill blocks success | `SKILL.md`, `references/matt-workflow.md` | Codex reported incomplete Matt setup and did not claim completion; exact missing-skill remediation was not established in that run | partially verified |
| 18 | Existing but incomplete Matt setup uses user invocation | `SKILL.md`, `references/matt-workflow.md` | Codex read-only run asked user to invoke `setup-matt-pocock-skills`, did not invoke it or write files; copied official `SKILL.md` SHA-256 matched source before/after | passed |
| 19 | Missing/unauthenticated `gh` blocks remote writes | `inspect.py` auth status; approval contract in `SKILL.md` | Codex with real unauthenticated `gh` stopped remote work; authenticated fake run checked account before fake create | passed |
| 20 | Repository collision never overwritten | approval contract and `gh` guidance | fake helper returns collision; no agent-level collision run yet | partially verified |
| 21 | Rejected approval causes zero GitHub writes | approval contract | Codex run `01a18e1a-d34f-79a2-9655-10a477fb2038` received a scripted rejection; fake log contained read-only `api user` calls only, no `repo create`; not a live interactive turn | partially verified |
| 22 | Approved commit/push limited and conventional | `references/execution-contract.md` fail-stop sequence | Earlier runs: sandbox denied `.git` writes; one attempted push after commit failed; instructions were hardened and a rerun stopped fail-safe. Passing run: fixture `/private/tmp/project-bootstrap-acceptance.hjB8rL/target`, local bare remote `/private/tmp/project-bootstrap-acceptance.hjB8rL/remote.git`. Codex CLI 0.166.0 invoked project-bootstrap, 13 scaffold files approved, commit `0e8f0af52c3a970da0ba7d70bc6927a9311ef355` subject `chore: add project foundation` on branch `bootstrap/project-bootstrap-acceptance`, same commit pushed to the bare remote. Git wrapper allowed only local paths; fake `gh` logged private repo create. First attempt made a real read-only `gh` auth/account lookup because the login shell ignored the wrapper PATH; no real GitHub writes. Staged `user-staged.txt`, unstaged `user-unstaged.txt` and modified `AGENTS.md` remained. Caveat: local bare push proves mechanics, not GitHub | passed |
| 23 | Secrets excluded from tracking, logs and docs | `.gitignore`, remote redaction and diagnostics | real `git check-ignore`; audit verifies remote credential redaction; doctor suppresses Compose stderr | passed |
| 24 | Interrupted generation recoverable | atomic add-only writes and partial failure report | obstruction test proves preserved blocker, partial report, and successful rerun; signal interruption not simulated | partially verified |
| 25 | Failed writes preserve files and reject symlinks | atomic link-based writes and path guards | existing-file, symlink escape and setup source tests | passed |
| 26 | Failed GitHub action preserves local files | `gh` approval contract and failure reporting | Codex invoked fake `repo create`, exit 42; all generated files remained; no remote or success URL; report named failed command and `gh auth login` recovery | passed |
| 27 | Invalid slug/name rejected before side effects | `scripts/scaffold.py` argument validation | traversal slug test; control-character validation reviewed, not separately exercised | partially verified |
| 28 | Audit has zero local/Git/remote mutation | `inspect.py`; `validate.py --audit` | tree+mtime snapshot includes `.git`; faked GitHub, Docker and project task; read-only GH call asserted | passed |
| 29 | Report distinguishes four statuses | `scripts/validate.py` emits pass/fail/not applicable/not verified | `test_validation_report_uses_all_four_statuses` asserts all four in normal and Audit reports | passed |
| 30 | Installer and check mode work | existing installer | `./scripts/verify` isolated install, check, collision and symlink tests | passed |
| 31 | Repository verifier/CI checks pass | repo scripts and Taskfile | `./scripts/verify` and `task brand:check` passed. Host `task docs:check` cannot find `zensical`, but the Taskfile docs steps passed inside Docker (`python:3.12-slim`, pinned `zensical==0.0.72`; see Agent-level execution record, Docker docs run): `zensical build --strict` and `scripts/check_docs.py` with `--require-og-image` exit 0 | passed |
| 32 | Other supported hosts smoke-tested | portable skill body; installer targets `.agents/skills` and `.claude/skills` | Isolated installer and `--check` passed. Codex actual invocation passed. Claude Code 2.1.311 invoked `/project-bootstrap` in fixture `/private/tmp/project-bootstrap-acceptance.hjB8rL/target`, loaded the skill, and reported Audit completed with 17 checks passing and 2 not applicable (Claude's own summary, not independently verified); independent `validate.py --audit` on the unchanged fixture gives 15 pass, 2 not verified (`taskfile:parse`, `task:doctor`), 2 not applicable, so the report over-counted the two not-verified checks. No filesystem or Git changes reported, HEAD stayed `0e8f0af52c3a970da0ba7d70bc6927a9311ef355`. Pi 1.4.0 invoked `/skill:project-bootstrap` with default model `flint@q3_k_xl` in the same fixture, ran exactly the absolute `inspect.py` and `validate.py --audit` commands, and Audit reported 15 pass, 2 not verified (`taskfile:parse` and `task:doctor`; Audit mode does not execute project tasks), 2 not applicable (optional Compose); no project tasks or Docker commands ran, post-run Git status unchanged (`M AGENTS.md`, staged `user-staged.txt`, `M user-unstaged.txt`, untracked `.claude/skills/project-bootstrap`), HEAD stayed `0e8f0af52c3a970da0ba7d70bc6927a9311ef355`. OpenCode standalone ran in the same fixture with isolated config/data/cache and read-only permission rules, using model `opencode/glm-5.3-flash-free` (shown as `GLM-5.3-Flash Free OpenCode`). After one rejected out-of-scope `/bin/ls` attempt, the worker invoked `@project-bootstrap` and ran exactly the absolute `inspect.py` and `validate.py --audit` commands; Audit returned 15 pass, 2 not verified (`taskfile:parse`, `task:doctor`), 2 not applicable. No project files changed; the earlier model-country error was resolved by selecting GLM | passed |
| 33 | Task discovery and modular include paths | generated Taskfile and module fixture | Task list for generated profiles; modular include loaded from alternate worktree; unknown task fails | passed |
| 34 | Doctor read-only diagnostics | generated `scripts/doctor.py` | fake missing Docker, missing Compose, invalid config with secret suppression, valid config; no mutation assertion absent | partially verified |
| 35 | Setup idempotency and data preservation | generated `scripts/setup.py` | real `task setup` runs twice; local Compose/env edits preserved | passed |
| 36 | Docker=no has no Docker files/tasks | profile renderer | POC scaffold checks artifacts and task names absent | passed |
| 37 | Dependencies-only Compose without Dockerfile | input-gated renderer | dependency fixture checks no build task/Dockerfile; Compose config checked with local plugin | passed |
| 38 | App Dockerfile and Compose require reviewed inputs | input-gated renderer | supplied fixture files copied; config syntax checked; real image build not run | partially verified |
| 39 | Cached and no-cache builds differ | generated Taskfile commands | fake Docker captures distinct `build` and `build --no-cache` invocations | passed |
| 40 | Lifecycle preserves data/volumes by default | generated Taskfile commands | fake Docker captures start/recreate/stop/down; asserts no `--volumes`; no real containers run | passed |
| 41 | Compose syntax validation | `validate.py`, `doctor.py` | local Docker Compose parser validates fixtures; no daemon/container operation | passed |
| 42 | Modules, discovery, help and unsupported tasks | Taskfile generator and validation | Task `--list`, modular fixture, descriptive `desc` fixture, unknown task failure | passed |

## Agent-level execution record

All paths below are disposable fixtures under `/private/tmp`; none touched the
`agent-skills` Git metadata. Codex CLI was `0.166.0`.

| Run | Evidence | Result |
|---|---|---|
| Fake-PATH preflight, thread `01a18e19-1ca5-7300-8429-73deb1eda6b7` | `/private/tmp/project-bootstrap-rc-oju93p2k/reject`; Codex’s login shell dropped the fake-tool `PATH`. | Codex saw the real unauthenticated `gh`, created 15 local files under scripted approval, and reported no Git repository. No GitHub write occurred. Excluded from the rejection evidence below. |
| Rejected repository creation, thread `01a18e1a-d34f-79a2-9655-10a477fb2038` | `/private/tmp/project-bootstrap-rc2-pb290axj/reject`; simulated local-write approval followed by simulated repository-create rejection. Fake `gh` logged two `api user --jq .login` calls. | Created 15 approved local files; no `repo view`, `repo create`, remote, commit, or push. Approval input was scripted, not interactive. |
| Approved Adopt, thread `01a18e1d-14fb-7352-a2db-2d7f14587abb` | `/private/tmp/project-bootstrap-rc2-pb290axj/commit-push`; Git fixture started with staged `user-staged.txt` and modified `unrelated.txt`. Fake `gh` logged auth, account, collision check, and private create. Agent’s `git add` list contained exactly 14 new scaffold paths. | `.git/config` and `.git/index` writes failed with sandbox `Operation not permitted`. The agent still called wrapped `git push -u origin main` after commit failed. No network push occurred; staged and unstaged user content stayed intact. This exposed fail-open sequencing. |
| Create failure, thread `01a18e1e-b906-7f90-8467-230fca32cc18` | `/private/tmp/project-bootstrap-rc2-pb290axj/create-failure`; fake helper log: `repo view fixture-user/failure-fixture`, then `repo create fixture-user/failure-fixture --private --description 'A disposable failure test'`; create exited 42. | All generated files remained; no remote. Agent reported the exact command and safe `gh auth login` retry. Fake helper was called directly because Codex login-shell PATH did not retain the test fake. |
| Matt incomplete, thread `01a18e22-5517-7f83-8010-1aaa68dbab9a` | `/private/tmp/project-bootstrap-rc2-pb290axj/matt-incomplete`; no target outputs. Official skill copied unchanged into fixture; SHA-256 `f148858ffb7f63c03c06fca06e6fdb1d91a35c6b293244b8fdfacd5f4cc028c4`. | Codex asked the user to invoke the official skill, did not invoke it, scaffold, or write. Source and fixture hashes matched. |
| Fail-stop rerun, thread `01a18e2a-6219-7222-8d13-67c22a78c55b` | `/private/tmp/project-bootstrap-rc2-pb290axj/fail-stop`; updated fail-stop instructions. Fake `gh` auth, collision check, and repo create succeeded. Fake Git log ended at `remote add origin ...`; no push log. | Remote add failed on sandbox-protected `.git/config`. Codex stopped before staging, commit, and push. User’s `unrelated.txt` stayed modified and intact. Successful commit/push still could not be proven. |
| Successful local-bare-remote run, Codex CLI 0.166.0 | `/private/tmp/project-bootstrap-acceptance.hjB8rL/target`, remote `/private/tmp/project-bootstrap-acceptance.hjB8rL/remote.git`; fake `gh` logged private repo create; Git wrapper allowed local paths only. First attempt made a real read-only `gh` auth/account lookup (login shell ignored wrapper PATH). | 13 approved scaffold files; commit `0e8f0af52c3a970da0ba7d70bc6927a9311ef355` `chore: add project foundation` on `bootstrap/project-bootstrap-acceptance`, pushed to the bare remote. Staged `user-staged.txt`, unstaged `user-unstaged.txt` and `AGENTS.md` preserved. No real GitHub writes. |
| Claude Code Audit, 2.1.311 | Same fixture; `/project-bootstrap` invoked, skill loaded. | Claude reported 17 checks passed, 2 not applicable; no filesystem or Git changes; HEAD stayed `0e8f0af52c3a970da0ba7d70bc6927a9311ef355`. Independent validator ground truth (`validate.py --audit`, unchanged fixture): 15 pass, 2 not verified (`taskfile:parse`, `task:doctor`), 2 not applicable. The reported 17 over-counted the two not-verified checks. |
| Pi 1.4.0 Audit | Same fixture; `/skill:project-bootstrap`, default model `flint@q3_k_xl`; ran exactly the absolute `inspect.py` and `validate.py --audit` commands against the fixture. Earlier attempts: first blocked by "No models available" before model load; after the default model was loaded, a tools-limited attempt looped on repeated reads and was stopped before any shell command. The bounded Audit rerun succeeded. | 15 pass, 2 not verified (`taskfile:parse`, `task:doctor`; Audit mode does not execute project tasks), 2 not applicable (optional Compose). No project tasks or Docker commands ran. Independent post-run Git status unchanged: `M AGENTS.md`, staged `user-staged.txt`, `M user-unstaged.txt`, untracked `.claude/skills/project-bootstrap`; HEAD stayed `0e8f0af52c3a970da0ba7d70bc6927a9311ef355`. |
| OpenCode | Same fixture; standalone start with isolated config/data/cache and read-only permission rules (shell and edit denied); `@project-bootstrap` submitted with an Audit-only read-only prompt. | Initial model request failed: `This model is not available in your country`. Retried with `opencode/glm-5.3-flash-free` (`GLM-5.3-Flash Free OpenCode`); skill loaded and ran exactly the absolute `inspect.py` and `validate.py --audit` commands. Audit: 15 pass, 2 not verified (`taskfile:parse`, `task:doctor`), 2 not applicable. No project files changed. |
| Docker docs run | Image `python:3.12-slim` (local), container user `501:20`. Installed pinned `requirements-docs.txt` (`zensical==0.0.72`) into a temporary `/tmp` venv. Ran the Taskfile docs steps in order: copy generated brand assets into `website/assets`; `zensical build --strict`; `python scripts/check_docs.py site --base-path /agent-skills/ --palette brand/data/brand.json --require-og-image`. | Zensical build finished; documentation checks passed; exit 0. Host `task docs:check` still cannot find `zensical`; all task build/check commands passed inside Docker. |

## Host discovery and invocation

`scripts/install` and `scripts/install --check` passed with temporary targets
`/private/tmp/project-bootstrap-rc2-pb290axj/hosts/.agents/skills` and
`.../hosts/.claude/skills`; both contain symlinks to the repository skill.
Codex invoked the project-local `.agents/skills/project-bootstrap` skill.
Claude Code 2.1.311 invoked `/project-bootstrap` in the acceptance fixture,
loaded the skill, and reported completing Audit (17 passed, 2 not applicable)
with no filesystem or Git changes; that count is Claude's report and is not
independently verified. The independent validator result on the unchanged
fixture is 15 passed, 2 not verified, 2 not applicable. Pi 1.4.0 invoked `/skill:project-bootstrap` with
default model `flint@q3_k_xl` and completed a bounded Audit (15 passed, 2 not
verified, 2 not applicable) running only the absolute `inspect.py` and
`validate.py --audit` commands; no project tasks or Docker commands ran, and
Git state and HEAD were unchanged. OpenCode standalone invoked `@project-bootstrap` with model
`opencode/glm-5.3-flash-free` (`GLM-5.3-Flash Free OpenCode`) and isolated
config/data/cache. Read-only permission rules allowed only the absolute
`inspect.py` and `validate.py --audit` commands. Audit returned 15 passed,
2 not verified, 2 not applicable; no project files changed. The earlier model
country error was resolved by selecting the operator-requested GLM model.
Official host docs describe
these directories: [Codex](https://developers.openai.com/api/docs/guides/tools-skills),
[Claude Code](https://code.claude.com/docs/en/skills), [Pi](https://pi.dev/docs/latest/skills),
and [OpenCode](https://docs.opencode.ai/docs/skills/). Installation/discovery
path evidence is not invocation evidence.

## Limits

Earlier Codex scenario approvals were scripted in prompts, not live user
dialogue; final Adopt approvals were interactive. Fake `gh` and `git` prevent external writes but do not prove behavior
outside these observed runs. Scenario 22 passed with a commit pushed to a local
bare remote; that proves mechanics, not GitHub. One attempt made a real
read-only `gh` lookup; no real GitHub writes occurred. Pi Audit was verified
with a bounded run (the first Pi attempts were blocked by no models, then a
tools-limited loop); Pi did not execute project tasks (2 checks not verified).
OpenCode passed a bounded Audit on `GLM-5.3-Flash Free OpenCode`; the two not-verified checks reflect Audit mode not running project tasks.
Host `task docs:check` cannot find `zensical`, but the Docker docs commands
(`zensical build --strict` and `scripts/check_docs.py`) passed in
`python:3.12-slim` with pinned `zensical==0.0.72`, so scenario 31 is passed.
Scenarios 22, 31, and 32 now meet their recorded acceptance criteria. Scenario
32 host invocation evidence is smoke-test evidence; it does not claim full
project-task execution on each host.
