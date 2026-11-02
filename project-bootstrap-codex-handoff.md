# Codex Implementation Handoff — `project-bootstrap` V1

## Mission and execution context

You are **Codex CLI already launched from the root of the user's existing local checkout** of `https://github.com/fnayou/agent-skills`.

Implement a new, opinionated, portable Agent Skill at **`skills/project-bootstrap/`**. This is a contribution **to the existing `agent-skills` repository**, NOT an invocation of the new skill to bootstrap this repository.

**Non-negotiable boundaries:**
- Work in the present checkout and respect its current branch, worktree, and uncommitted changes. Do not reclone, `git init`, create a new repository or remote, or rewrite Git history.
- Read the local `AGENTS.md`, relevant nested instructions, `README.md`, existing skill examples, installer, verifier, Taskfile, CI and documentation conventions *before* writing code. The local checkout is authoritative; this handoff specifies product requirements. Report conflicts explicitly and preserve repository invariants.
- Use **`gh` CLI exclusively** for any GitHub interaction. No GitHub web UI/API client or manual HTTP GitHub writes.
- Do not create/push a branch, commit, open a PR, or mutate GitHub without the user's explicit approval. If authorized, use logical atomic **Conventional Commits** and stage only changes related to this task. Never commit unrelated changes.
- Do not create a separate `project-bootstrap` repository or a new package-management/installer framework. Reuse the existing `agent-skills` tooling.
- Build and validate the implementation in this session, not just a design proposal. If something is unavailable, report precisely what you could verify and what remains blocked; do not claim success prematurely.

## Objective

Create an **opinionated, fixed-convention project bootstrap skill** that Codex can invoke from *any future project's directory* to **Create**, **Adopt** or **Audit** an AI-ready GitHub project. Codex is its primary host; follow the portable Agent Skills spec so Pi Agent, Claude Code, OpenCode and other hosts can use the transferable parts where supported.

The skill is meant for POCs, quick CLI utilities, libraries, and applications. It standardizes engineering foundations, not the application domain. It must remain lightweight for a small POC, without creating nonfunctional placeholder commands or arbitrary business code.

### Fixed conventions

- Agent Skills specification: `https://agentskills.io/specification`; canonical skill entry `SKILL.md` with valid YAML frontmatter and useful trigger description. Apply progressive disclosure through `references/`, `assets/` and `scripts/` rather than an enormous `SKILL.md`. Optional `agents/openai.yaml` only if supported and aligned with existing repository patterns.
- Root **`AGENTS.md`** is the primary generated project instruction file; include project context, build/test commands, constraints, security rules, Git conventions and references to Matt workflow documents. Don't blindly replicate global rules or overwrite existing instruction files. Detect compatible other-agent instructions and report conflicts.
- **`gh` CLI exclusively** for GitHub operations; **Conventional Commits**, logically atomic commits with configured machine Git author, no unrelated staged files.
- Always include `.editorconfig`, `.gitignore`, `.gitattributes` when suitable, and a meaningful `README.md` using the explicitly confirmed repository display name. Include applicable GitHub Community Standards: `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`, license only after selection, GitHub issue forms, and PR template. No fake contacts, non-working URLs or placeholder claims. Security reporting can point to GitHub private vulnerability reporting only if verified enabled; otherwise obtain a suitable address/channel or report unresolved.
- Generate **GitHub issue YAML forms** for bug and feature requests (and `config.yml`), with problem/outcome, reproduction or acceptance criteria as appropriate; align any labels with Matt setup rather than inventing incompatible label names.
- Generate a **`.github/PULL_REQUEST_TEMPLATE.md`** following GitHub's standard location, informed by the locally installed Matt Pocock PR guidance if available: summary, linked issue, validation/evidence, impact/risk/rollback, concise checklist. Do not assume Matt's exact template contents; inspect installed skills.
- **Matt Pocock's repository setup workflow is required**. Locate/check the installed setup skill (e.g. `setup-matt-pocock-skills`) and relevant skill-creation / PR / issue-writing skills by actual local discovery. Do not invent exact names or assume they are installed. Respect user-invoked skill semantics: if the setup skill cannot be invoked by another skill automatically, explicitly request the user's invocation and validate its output. If required skills are missing, report and **block declaring full bootstrap success**; independent safe inspection can still run. Don't counterfeit Matt's workflow files. Prefer installed skill-creation guidance (`skill-creator`, `writing-for-agents` or whatever is actually present) while writing this new skill; report missing tools.
- Fixed standards are not a long questionnaire. Ask only project-specific facts, propose sensible detected defaults and confirm where required.

## Interaction and approval contract

On invocation in a future project:
1. **Inspect** the current directory, Git status, parent/nested Git boundaries, symlinks, existing files, `gh` presence/authenticated account, existing remotes, available project tooling, and installed Matt skills. Inspect safely before mutation.
2. Determine `create` / `adopt` / `audit`. Detect likely project profile (POC / CLI / library / application) and confirm. For Create, propose slug from directory but **explicitly ask/confirm both display name and slug**, repository owner (authenticated user or organization), description, and GitHub visibility (**private by default**). **Ask for a license for every project**, including an explicit “no license” option. POC: no release/versioning convention by default; other profiles: ask (e.g. SemVer, CalVer, none).
3. **Always generate a functioning `Taskfile.yml`** in Create; Adopt only through an approved patch. **Explicitly ask whether Docker support is desired**. Do NOT silently enable Docker, even though the skill supports it. If yes, clarify whether application image, development dependencies, or both are needed, and generate only meaningful configurations. If no, do not generate Docker/Compose artifacts or Docker tasks.
4. Present planned files, any changes to existing files, warnings and validation limits; request explicit approval before substantive writes. Never overwrite an existing file without review and permission. In Adopt, show a minimal diff. In Audit, do not modify the project or remotely hosted resources under any circumstance.
5. Generate scaffold, guide/perform the permitted Matt workflow setup, validate, then **propose** GitHub repository creation and initial commit/push. Require explicit approval for each remote mutation and for commits/pushes. Do not assume user approval because a plan was accepted. If the remote already exists, handle it as a conflict rather than overwriting.
6. Finish with an actionable result: what changed, remaining blockers, exact validation statuses (**pass / fail / not applicable / not verified**), GitHub URL only if confirmed, and suggested next step.

### Three modes

- **Create**: initialize the *current* working directory; if it is non-empty or Git-initialized, inspect and avoid any destructive reinitialization; reject unsafe context or offer Adopt when appropriate. Generate appropriate baseline and, only after approval, use `gh` to publish.
- **Adopt**: inspect existing repo, generate diff/plan, preserve Git history, existing `AGENTS.md`, `.gitignore`, worktree state and user modifications; apply only approved minimal changes. No implicit initial commit or push. Idempotent on reruns.
- **Audit**: strictly **read-only** for local files/Git configuration and GitHub. No scaffolding, setup, installs, cache files inside the target or other mutations. Return granular compliance report. Use read-only inspection commands. Audit should still work when some optional tools are absent, reporting limitations.

## Taskfile design (drawn from user's Ansible Taskfiles)

Use the user's established philosophy, but **do not copy Ansible-specific or SOPS-specific behavior**:
- Root `Taskfile.yml` is the **single command interface**; `task` lists tasks (`default` with `task --list` or repo-compatible equivalent). All tasks have useful `desc` and predictable namespaces.
- Use **`.taskfiles/` modular includes** (`docker.yml`, `dev.yml`, `quality.yml`, etc.) **only when justified by real complexity**. Tiny POCs may keep all tasks in root file. Paths resolve, even in alternative worktrees.
- **Always provide `task doctor`** as non-mutating prerequisites/readiness diagnostics with actionable error messages, and **`task setup`** as an idempotent initializer for missing local config that never overwrites existing data. Avoid secrets in output. Doctor must distinguish missing tooling, invalid config and 'not checked'.
- Where *actually usable*, use `task dev`, `run`, `build`, `test`, `lint`, `format`, `check`. Do not generate fake tasks or claimed validation for unknown stacks. `check` can aggregate available static/tests; optional commands should be omitted rather than padded with no-ops.
- If Docker selected, standardized names: **`docker:build`**, **`docker:build-nocache`**, `docker:start`, `docker:recreate`, `docker:stop`, `docker:down`, `docker:logs`, `docker:ps`, `docker:config`; optional other tasks only where useful. Keep normal cached and no-cache build distinct; `start` must not silently force recreation, `recreate` intentionally reapplies config, `stop` stops, `down` preserves volumes by default. No destructive `docker:default`, `docker:kill`, `docker:clean`, `down --volumes` or implicit host resource deletion. If a destructive task is ever introduced, require a separate clearly named operation and explicit approval.
- Compose operations should share a single command definition or helper when necessary, to avoid bypassing prerequisites. Do not auto-start containers during bootstrap. Taskfiles must be safe for noninteractive/CI invocation where relevant (don't force `-t` on CI commands).
- Generated scripts performing sensitive writes should check preconditions and use atomic temp-file+rename where appropriate. Guard destructive operations and never blindly swallow failures.
- `Taskfile.yml` inside newly generated projects is distinct from the existing root `Taskfile.yml` used to maintain `agent-skills`; reuse/extend the latter only where it helps skill development.

## Docker / Compose policy

**Docker is an explicit yes/no bootstrap choice, not a globally mandatory generated dependency. Taskfile remains mandatory.**

When Docker is selected:
- Generate `.dockerignore`, a real suitable `Dockerfile` **if there is a containerizable application/build**, and a version-controlled **`compose.example.yaml`** as the canonical example; initialize local **`compose.yaml`** from it without overwriting an existing file, then **gitignore `/compose.yaml` and `/compose.yml`**. Prefer `.example` over `.dist`, and the `.yaml` extension; include `.env.example` when meaningful, ignore `.env` and private local variants while keeping the example tracked.
- If the selected Docker role is *dependencies only*, do not invent a Dockerfile for an app that isn't containerized. A usable Compose example and local copy are sufficient.
- `task setup` must safely copy the example when missing, never overwrite existing local `compose.yaml`; no implicit auto-reconciliation after template changes.
- Use modern `docker compose` semantics; produce portable Compose where possible, mindful of Podman compatibility, but don't assert untested parity. Validate `docker compose -f compose.example.yaml config` or equivalent with appropriate test environment; check `compose.yaml` only when it exists.
- Prefer project-scoped resources; avoid unprotected ports, hardcoded secrets, privileged flags, destructive mounts, global container names and unsafe defaults. Avoid embedding real user credentials.
- If Docker/Compose/Task executables are absent during creation, generate valid configurations where possible, label runtime validation **not verified**, and provide actionable instructions. Do not automatically install tools. In Audit, missing tools must not cause writes.
- Never claim a Dockerfile actually builds if the application stack is not sufficiently defined; ask for the missing essential information or report the incomplete branch.

## Project profile and generated content policies

- Support `POC`, `CLI`, `library`, `application` with auto-detection and explicit confirmation.
- V1 is a **generic, language-agnostic engineering foundation**. Produce stack-specific source code, CI or starter boilerplate **only when requested and enough stack details are known**. Do not ship a huge catalog of Rust/Node/Python/Go/PHP starters; these may be V2.
- Generate GitHub Actions CI only for known stacks with real executable checks. Otherwise report CI as not applicable/not yet configured, not a generic fake workflow.
- Avoid empty meaningless directories/files (`src/`, `tests/`, `docs/adr/`, `CHANGELOG.md`, `Dockerfile`, etc.) unless useful to the selected profile. Docker selection is the exception for meaningful Compose config; never create nonfunctional placeholders.
- Maintain a coherent minimal README that documents local setup, Task commands, selected Docker workflow, tests, contributing/security pointers and project purpose **only where verified**. Remove template markers, TODO contacts and invented claims.
- No universal network publishing or package manager bootstrapping as a side effect.

## Proposed layout (adjust to repository conventions; justify deviations)

```text
skills/project-bootstrap/
  SKILL.md
  agents/openai.yaml                # optional, if supported/useful
  references/
    execution-contract.md
    project-profiles.md
    github-standards.md
    matt-workflow.md
    acceptance-tests.md
  assets/templates/
    base/
    github/
    profiles/
    taskfile/
    docker/
  scripts/
    inspect.py
    scaffold.py
    validate.py
  tests/
    fixtures/
    test_inspect.py
    test_scaffold.py
    test_validate.py
```

**Prefer coherent, minimal structure over matching filenames mechanically.** The three script roles are:
- `inspect.py`: read-only deterministic state detection; machine-readable output appropriate for orchestration.
- `scaffold.py`: reviewable, approved, conflict-aware file generation and optional template rendering; safe reruns, no out-of-root writes.
- `validate.py`: read-only validations and structured diagnostics; separate `pass`, `fail`, `not_applicable`, `not_verified`.

Use **Python 3 standard library only** for the deterministic engine and tests where feasible (`unittest`, `tempfile`, `pathlib`, `subprocess`, etc.). If standard-library-only constraints prevent reliable parsing of complex YAML, avoid implementing a fragile homegrown YAML parser: validate with installed supported tools when available and clearly mark not verified otherwise. Use subprocess invocation with argument arrays rather than unsanitized shell interpolation. No arbitrary command execution from untrusted names/slugs. Validate and confine target paths, including symlink escapes.

## Test-driven implementation requirements

Before declaring V1 ready, implement meaningful tests in **isolated temp directories**. Prefer mocked `gh`, Docker/Compose and Task binaries for default CI; optionally perform an *approved* disposable private GitHub smoke test. Do not use the user's actual projects as destructive test fixtures. Include unit, local integration, and agent-behavior tests or reproducible manual test scripts where behavioral automation is unavailable.

Minimum acceptance matrix (each applicable scenario must have evidence):

### A. Skill compliance / discovery
1. `SKILL.md` correct frontmatter and valid Agent Skills structure (`skills-ref validate` if available).
2. Existing installer exposes new skill to Codex without breaking current installation scheme.
3. Skill trigger/usage guidance is specific enough for bootstrap tasks and does not claim unrelated tasks.
4. Existing skills continue to pass repository verification.

### B. Inspection / path safety
5. Empty directory correctly identified.
6. Existing Git branch/remote/status/untracked files detected.
7. Nested Git/worktree boundaries handled safely.
8. Existing `AGENTS.md` and `.gitignore` preserved and conflicts reported.
9. Symlink escape, traversal, absolute-outside-target paths rejected.

### C. Scaffold / local adoption
10. Generic POC foundation succeeds without bogus release/CI/source files.
11. CLI profile gets applicable validated foundation; no invented runtime.
12. README consistently uses the confirmed display name/slug where appropriate.
13. Editor/Git hygiene files are valid and required exclusions work.
14. GitHub community docs/forms/PR template contain meaningful, consistent content.
15. Repeated Create/setup runs are idempotent and preserve local customization.
16. Adopt generates an accurate minimal patch, protects existing files/history/unrelated changes.

### D. Matt workflow / GitHub
17. Missing Matt setup skill blocks full success with remediation.
18. Present but unconfigured Matt setup is distinguished from completed setup and user invocation respected.
19. Missing/unauthenticated `gh` stops GitHub mutation and gives actionable errors.
20. Existing remote/name collision never overwrites a GitHub repository.
21. Rejected authorization leads to zero GitHub mutations.
22. Approved staged commit/push touches only intended files, with Conventional Commit format (can be mocked).

### E. Secrets / interruption
23. `.env`/credentials/private keys excluded from tracking, logs and generated docs.
24. Interrupted generation leaves recoverable and correctly reported state.
25. Failed writes never truncate existing files or follow dangerous symlinks.
26. Failed GitHub action preserves local files and reports incomplete publication.
27. Bad slug/path/name input rejected before side effects.

### F. Audit / repo integration
28. Audit causes **zero mutation** (files, Git metadata, remote).
29. Structured compliance report accurately distinguishes four statuses.
30. Existing `scripts/install` and its check mode work after integration.
31. Existing `scripts/verify` / CI verification passes.
32. Smoke-check compatible hosts when installed; never pretend untested support is verified.

### G. Taskfile / Docker/Compose additions
33. `task --list` works; modular includes resolve for both simple and modular fixture projects.
34. `task doctor` is read-only and gives actionable missing-prerequisite statuses.
35. `task setup` is idempotent and never overwrites existing local Compose or `.env`.
36. Docker=No produces Taskfile but no Docker artifacts/tasks.
37. Docker=Yes/dependencies-only produces working Compose example without unnecessary Dockerfile.
38. Docker=Yes/app produces suitable Dockerfile, Compose example and excluded local Compose when sufficient stack information exists.
39. `docker:build` and `docker:build-nocache` differ as intended; build/validate are not claimed when prerequisites absent.
40. Docker `start` vs `recreate` vs `stop` vs `down` have distinct correct semantics; regular lifecycle tasks cannot remove named volumes/data.
41. Compose example syntax validates with available tooling; if unavailable, report not verified.
42. Taskfile module naming, command discovery, descriptive help, and unsupported commands are handled correctly.

Add targeted negative/edge cases as necessary. Not all 42 need to be 42 separate test functions; trace each requirement to an executed test/manual verification record.

## Implementation sequence

1. **Repository reconnaissance**: inspect instructions, layouts, existing scripts/tests/Task conventions, installed skills; produce a concise plan and incompatibility report. Check Git status and don't touch unrelated edits.
2. **Skill creation**: use the available skill-authoring guidance; write a concise `SKILL.md` plus progressive references and any host metadata consistent with repo patterns.
3. **Read-only core first**: implement inspection and validation with unit tests.
4. **Safe generation**: implement templates and Create/Adopt paths with atomic writing, path confinement, dry-run/preview, idempotency and fixtures. Audit must call only read-only components.
5. **Generated project foundation**: AGENTS, editor/Git files, README, license selection, community standards, Matt workflow integration contract, release/profile policies.
6. **Taskfile and optional Docker**: implement user's Taskfile architecture, doctor/setup, module decomposition, optional Compose example + ignored local Compose, build/no-cache and safe lifecycle tasks.
7. **GitHub orchestration**: skill instructions use `gh` exclusively, isolate remote operations behind approvals; test with mock/stubbed tooling. Do not create a live repo without authorization.
8. **Integration/docs**: reuse existing installer, verifier, Taskfile and website/docs; do not introduce duplicate pipeline infrastructure. Check compatibility of old skills.
9. **Review and validation**: run existing repo checks plus new suite; inspect diff for sensitive data, unexplained files and unintended changes. Report failures and limits. Do not commit/push without approval.

## Definition of done and reporting

An acceptable V1 implementation:
- Follows local repo policies and current Agent Skills spec, discoverable through existing installation conventions.
- Offers reliable Create/Adopt/Audit semantics with explicit approval gates; Audit remains strictly read-only.
- Creates meaningful governance and AI instruction files, and correctly coordinates Matt's installed setup workflow.
- Generates functional Taskfile commands and asks for Docker at bootstrap; Docker-selected projects receive the agreed example/local Compose convention and exact `docker:build-nocache` spelling.
- Passes applicable security/idempotency/negative tests; any unverified Docker/GitHub/host functionality is clearly reported.
- Does not change unrelated repository files, install arbitrary dependencies, publish, commit or create remotes unapproved.
- Updates project docs consistent with repo conventions.

In your final response to the user, report: changed files, architecture choices, test commands and results, which of the 42 acceptance scenarios were covered/blocked, discovered Matt skill names and invocation constraints, any gaps/risks, and *specific* next steps. If a decision is truly blocking, state the precise question; otherwise use documented defaults and finish the best safe implementation.

## Standards to consult when useful

- Agent Skills: https://agentskills.io/specification
- Project repository: https://github.com/fnayou/agent-skills (local checkout wins)
- Matt Pocock skills: https://github.com/mattpocock/skills (installed local set wins)
- GitHub issue forms: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/configuring-issue-templates-for-your-repository
- GitHub PR template: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
- Compose file reference: https://docs.docker.com/compose/compose-file/
- Task documentation: https://taskfile.dev/

**Start by inspecting this checkout and installed skill inventory. Then implement. Do not use this repository as a bootstrap target.**
