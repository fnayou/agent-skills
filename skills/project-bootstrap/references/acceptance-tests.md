# V1 acceptance traceability

Validation record for the `project-bootstrap-codex-handoff.md` 42 scenarios.
Automated evidence comes from `tests/test_project_bootstrap.py` (25 tests),
`./scripts/verify`, isolated installer checks, and pinned `skills-ref`.
Agent-level evidence comes from five scenario Codex CLI runs and one discarded
PATH preflight, using scripted answers and isolated fake GitHub/Git commands.
Those answers were supplied in prompts;
they were not interactive approval turns. No real GitHub writes, pushes, or
container lifecycle ran. Claude, Pi, and OpenCode invocations could not run.

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
| 22 | Approved commit/push limited and conventional | `references/execution-contract.md` fail-stop sequence | Codex selected the exact 14 approved paths and preserved staged/unstaged user edits. Sandbox denied remote/add/index writes. It then attempted push after commit failed. Instructions were hardened; rerun stopped after remote-add failure, before stage/commit/push. Successful commit/push remains unverified; first run exposed a failure | failed |
| 23 | Secrets excluded from tracking, logs and docs | `.gitignore`, remote redaction and diagnostics | real `git check-ignore`; audit verifies remote credential redaction; doctor suppresses Compose stderr | passed |
| 24 | Interrupted generation recoverable | atomic add-only writes and partial failure report | obstruction test proves preserved blocker, partial report, and successful rerun; signal interruption not simulated | partially verified |
| 25 | Failed writes preserve files and reject symlinks | atomic link-based writes and path guards | existing-file, symlink escape and setup source tests | passed |
| 26 | Failed GitHub action preserves local files | `gh` approval contract and failure reporting | Codex invoked fake `repo create`, exit 42; all generated files remained; no remote or success URL; report named failed command and `gh auth login` recovery | passed |
| 27 | Invalid slug/name rejected before side effects | `scripts/scaffold.py` argument validation | traversal slug test; control-character validation reviewed, not separately exercised | partially verified |
| 28 | Audit has zero local/Git/remote mutation | `inspect.py`; `validate.py --audit` | tree+mtime snapshot includes `.git`; faked GitHub, Docker and project task; read-only GH call asserted | passed |
| 29 | Report distinguishes four statuses | `scripts/validate.py` emits pass/fail/not applicable/not verified | `test_validation_report_uses_all_four_statuses` asserts all four in normal and Audit reports | passed |
| 30 | Installer and check mode work | existing installer | `./scripts/verify` isolated install, check, collision and symlink tests | passed |
| 31 | Repository verifier/CI checks pass | repo scripts and Taskfile | `./scripts/verify`, `task brand:check`, `task docs:check` | passed |
| 32 | Other supported hosts smoke-tested | portable skill body; installer targets `.agents/skills` and `.claude/skills` | Isolated installer and `--check` passed. Codex actual invocation passed. Claude returned `Not logged in · Please run /login`; Pi auth check returned `not_ready`; OpenCode could not start under sandbox (`EPERM` spawning `ps`). Their invocations remain unverified | partially verified |
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

## Host discovery and invocation

`scripts/install` and `scripts/install --check` passed with temporary targets
`/private/tmp/project-bootstrap-rc2-pb290axj/hosts/.agents/skills` and
`.../hosts/.claude/skills`; both contain symlinks to the repository skill.
Codex invoked the project-local `.agents/skills/project-bootstrap` skill.
Claude’s project `.claude/skills` link was installed, but invocation failed
before a model turn because the isolated Claude home was not logged in. Pi’s
isolated auth check was `not_ready`. OpenCode help ran with temporary XDG paths,
but its server could not start inside the sandbox. Official host docs describe
these directories: [Codex](https://developers.openai.com/api/docs/guides/tools-skills),
[Claude Code](https://code.claude.com/docs/en/skills), [Pi](https://pi.dev/docs/latest/skills),
and [OpenCode](https://docs.opencode.ai/docs/skills/). Installation/discovery
path evidence is not invocation evidence.

## Limits

The Codex approval turns were explicitly scripted in prompts, not live user
dialogue. Fake `gh` and `git` prevent external writes but do not prove behavior
outside these observed runs. Commit/push did not complete because Codex’s
sandbox denied `.git` writes. Claude, Pi, and OpenCode invocations remain
unverified. Do not declare the Definition of Done met while scenario 22 fails
and cross-host invocation remains unverified.
