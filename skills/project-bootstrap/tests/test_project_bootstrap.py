from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SKILL = Path(__file__).resolve().parents[1]
INSPECT = SKILL / "scripts" / "inspect.py"
SCAFFOLD = SKILL / "scripts" / "scaffold.py"
VALIDATE = SKILL / "scripts" / "validate.py"
FAKE_GH = SKILL / "tests" / "fixtures" / "fake-gh"


class ProjectBootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_script(self, script: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-I", str(script), *args], cwd=self.root, env=env, text=True, capture_output=True)

    def snapshot_tree(self) -> dict[str, tuple[object, ...]]:
        snapshot = {}
        for path in sorted(self.root.rglob("*")):
            rel = str(path.relative_to(self.root))
            stat = path.lstat()
            if path.is_symlink():
                content: object = os.readlink(path)
            elif path.is_file():
                content = path.read_bytes()
            else:
                content = None
            snapshot[rel] = (stat.st_mode, stat.st_mtime_ns, content)
        return snapshot

    def options(self, *extra: str) -> tuple[str, ...]:
        return ("--root", str(self.root), "--display-name", "Sample Project", "--slug", "sample-project", "--description", "A confirmed project.", "--profile", "POC", "--license", "none", "--docker-role", "no", *extra)

    def test_inspection_is_read_only_and_reports_empty_directory(self) -> None:
        before = set(self.root.iterdir())
        result = self.run_script(INSPECT, str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["entries"], [])
        self.assertEqual(set(self.root.iterdir()), before)

    def test_inspection_distinguishes_missing_and_unauthenticated_gh(self) -> None:
        fake_bin = self.root.parent / f"{self.root.name}-bin"
        fake_bin.mkdir()
        for name in ("sh", "git", "task", "docker", "python3"):
            executable = shutil.which(name)
            if executable:
                (fake_bin / name).symlink_to(executable)
        env = os.environ.copy()
        env["PATH"] = str(fake_bin)
        try:
            missing = self.run_script(INSPECT, str(self.root), env=env)
            self.assertEqual(missing.returncode, 0, missing.stderr)
            self.assertEqual(json.loads(missing.stdout)["gh_auth"], "missing")

            gh_log = self.root.parent / f"{self.root.name}-gh-log"
            fake_gh = fake_bin / "gh"
            fake_gh.write_text("#!/bin/sh\nprintf '%s\\n' \"$*\" >> \"$GH_LOG\"\nexit 1\n")
            fake_gh.chmod(0o755)
            env["GH_LOG"] = str(gh_log)
            unauthenticated = self.run_script(INSPECT, str(self.root), env=env)
            self.assertEqual(unauthenticated.returncode, 0, unauthenticated.stderr)
            report = json.loads(unauthenticated.stdout)
            self.assertEqual(report["gh_auth"], "not authenticated")
            self.assertIsNone(report["gh_account"])
            self.assertEqual(gh_log.read_text().splitlines(), ["api user --jq .login"])
        finally:
            (fake_bin / "gh").unlink(missing_ok=True)
            for path in fake_bin.iterdir():
                path.unlink()
            fake_bin.rmdir()
            (self.root.parent / f"{self.root.name}-gh-log").unlink(missing_ok=True)

    def test_fake_gh_fixture_models_collision_and_create_failure(self) -> None:
        log = self.root / "gh-calls.jsonl"
        env = os.environ.copy()
        env["GH_CALL_LOG"] = str(log)
        env["GH_AUTHENTICATED"] = "1"
        account = subprocess.run([str(FAKE_GH), "api", "user", "--jq", ".login"], cwd=self.root, env=env, text=True, capture_output=True)
        self.assertEqual(account.returncode, 0, account.stderr)
        self.assertEqual(account.stdout.strip(), "fixture-user")
        auth = subprocess.run([str(FAKE_GH), "auth", "status"], cwd=self.root, env=env, text=True, capture_output=True)
        self.assertEqual(auth.returncode, 0, auth.stderr)
        env["GH_AUTHENTICATED"] = "0"
        unauthenticated = subprocess.run([str(FAKE_GH), "api", "user", "--jq", ".login"], cwd=self.root, env=env, text=True, capture_output=True)
        self.assertNotEqual(unauthenticated.returncode, 0)
        env["GH_REPO_EXISTS"] = "0"
        missing = subprocess.run([str(FAKE_GH), "repo", "view", "owner/slug"], cwd=self.root, env=env, text=True, capture_output=True)
        self.assertEqual(missing.returncode, 1)
        env["GH_REPO_EXISTS"] = "1"
        collision = subprocess.run([str(FAKE_GH), "repo", "view", "owner/slug"], cwd=self.root, env=env, text=True, capture_output=True)
        self.assertEqual(collision.returncode, 0)
        env["GH_CREATE_FAIL"] = "1"
        failure = subprocess.run([str(FAKE_GH), "repo", "create", "owner/slug", "--private"], cwd=self.root, env=env, text=True, capture_output=True)
        self.assertEqual(failure.returncode, 42)
        self.assertEqual([json.loads(line) for line in log.read_text().splitlines()], [
            ["api", "user", "--jq", ".login"],
            ["auth", "status"],
            ["api", "user", "--jq", ".login"],
            ["repo", "view", "owner/slug"],
            ["repo", "view", "owner/slug"],
            ["repo", "create", "owner/slug", "--private"],
        ])

    def test_inspection_reports_git_boundaries_and_redacts_remote_credentials(self) -> None:
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "remote", "add", "origin", "https://user:secret@example.test/owner/repo.git?token=also-secret"], cwd=self.root, check=True)
        nested = self.root / "nested"
        nested.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=nested, check=True)
        result = self.run_script(INSPECT, str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["branch"] in {"main", "master"})
        self.assertEqual(report["nested_git_boundaries"], ["nested"])
        remote = report["remotes"][0]["url"]
        self.assertNotIn("secret", remote)
        self.assertNotIn("token", remote)

    def test_inspection_lists_nested_symlink_escape(self) -> None:
        outside = self.root.parent / f"{self.root.name}-outside"
        outside.mkdir()
        try:
            (self.root / "nested").mkdir()
            (self.root / "nested" / "escape").symlink_to(outside, target_is_directory=True)
            result = self.run_script(INSPECT, str(self.root))
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            link = next(item for item in report["symlinks"] if item["path"] == "nested/escape")
            self.assertTrue(link["escapes_root"])
        finally:
            outside.rmdir()

    def test_invalid_slug_fails_before_writing(self) -> None:
        args = list(self.options())
        args[args.index("sample-project")] = "../escape"
        result = self.run_script(SCAFFOLD, *args)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_baseline_tracks_security_exclusions_and_no_docker_without_opt_in(self) -> None:
        result = self.run_script(SCAFFOLD, *self.options("--apply", "--approved"))
        self.assertEqual(result.returncode, 0, result.stderr)
        ignored = (self.root / ".gitignore").read_text().splitlines()
        for pattern in (".env", ".env.*", "!.env.example", "*.pem", "*.key"):
            self.assertIn(pattern, ignored)
        self.assertIn("* text=auto", (self.root / ".gitattributes").read_text())
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        for name in (".env", ".env.local", "service.pem", "private.key"):
            (self.root / name).write_text("private fixture\n")
            self.assertEqual(subprocess.run(["git", "check-ignore", "--no-index", "-q", name], cwd=self.root).returncode, 0, name)
        (self.root / ".env.example").write_text("SAFE=value\n")
        self.assertEqual(subprocess.run(["git", "check-ignore", "--no-index", "-q", ".env.example"], cwd=self.root).returncode, 1)
        taskfile = (self.root / "Taskfile.yml").read_text()
        self.assertNotIn("docker:", taskfile)
        for path in ("Dockerfile", ".dockerignore", "compose.example.yaml", "compose.yaml"):
            self.assertFalse((self.root / path).exists(), path)
        validation = self.run_script(VALIDATE, str(self.root), "--audit")
        self.assertEqual(validation.returncode, 0, validation.stderr)
        statuses = {item["status"] for item in json.loads(validation.stdout)}
        self.assertTrue({"pass", "not verified", "not applicable"} <= statuses)
        self.assertEqual({item["status"] for item in json.loads(validation.stdout)}, {"pass", "not verified", "not applicable"})

    def test_cli_profile_stays_language_agnostic_without_placeholder_tasks(self) -> None:
        args = list(self.options("--apply", "--approved"))
        args[args.index("POC")] = "CLI"
        result = self.run_script(SCAFFOLD, *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("profile: CLI", (self.root / "AGENTS.md").read_text())
        self.assertIn("a CLI foundation", (self.root / "README.md").read_text())
        taskfile = (self.root / "Taskfile.yml").read_text()
        self.assertIn("doctor:", taskfile)
        self.assertIn("setup:", taskfile)
        for task in ("run:", "build:", "test:", "lint:", "format:", "check:"):
            self.assertNotIn(task, taskfile)
        for path in ("src", "tests", ".github/workflows", "CHANGELOG.md"):
            self.assertFalse((self.root / path).exists(), path)
        if shutil.which("task"):
            listed = subprocess.run(["task", "--list"], cwd=self.root, text=True, capture_output=True)
            self.assertEqual(listed.returncode, 0, listed.stderr)

    def test_plan_does_not_write_and_apply_requires_approval(self) -> None:
        result = self.run_script(SCAFFOLD, *self.options("--plan", "--diff"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Plan only", result.stdout)
        self.assertIn("+++ README.md", result.stdout)
        self.assertIn("# Sample Project", result.stdout)
        self.assertEqual(list(self.root.iterdir()), [])
        rejected = self.run_script(SCAFFOLD, *self.options("--apply"))
        self.assertNotEqual(rejected.returncode, 0)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_apply_creates_baseline_and_rerun_preserves_customization(self) -> None:
        agents = self.root / "AGENTS.md"
        ignore = self.root / ".gitignore"
        agents.write_text("existing project rules\n")
        ignore.write_text("existing ignore rules\n")
        first = self.run_script(SCAFFOLD, *self.options("--apply", "--approved"))
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(agents.read_text(), "existing project rules\n")
        self.assertEqual(ignore.read_text(), "existing ignore rules\n")
        readme = self.root / "README.md"
        readme.write_text(readme.read_text() + "\nlocal edit\n")
        second = self.run_script(SCAFFOLD, *self.options("--apply", "--approved"))
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertTrue(readme.read_text().endswith("local edit\n"))
        self.assertIn("PRESERVE existing file: README.md", second.stdout)
        self.assertFalse((self.root / "Dockerfile").exists())
        self.assertFalse((self.root / "LICENSE").exists())
        self.assertFalse((self.root / ".dockerignore").exists())
        self.assertFalse((self.root / "compose.example.yaml").exists())
        self.assertNotIn("docker:", (self.root / "Taskfile.yml").read_text())
        self.assertIn("Sample Project", readme.read_text())
        self.assertIn("Reproduction", (self.root / ".github/ISSUE_TEMPLATE/bug_report.yml").read_text())
        self.assertIn("Acceptance criteria", (self.root / ".github/ISSUE_TEMPLATE/feature_request.yml").read_text())
        self.assertIn("## Impact, risk, and rollback", (self.root / ".github/PULL_REQUEST_TEMPLATE.md").read_text())
        self.assertTrue((self.root / "CODE_OF_CONDUCT.md").is_file())
        self.assertTrue((self.root / "CONTRIBUTING.md").is_file())
        self.assertTrue((self.root / "SECURITY.md").is_file())
        self.assertTrue((self.root / "SUPPORT.md").is_file())
        if shutil.which("ruby"):
            yaml_files = [
                self.root / ".github/ISSUE_TEMPLATE/bug_report.yml",
                self.root / ".github/ISSUE_TEMPLATE/feature_request.yml",
                self.root / ".github/ISSUE_TEMPLATE/config.yml",
            ]
            parse = subprocess.run(
                [shutil.which("ruby"), "-e", "require 'yaml'; require 'json'; puts JSON.generate(ARGV.map { |path| YAML.load_file(path) })", *map(str, yaml_files)],
                cwd=self.root,
                text=True,
                capture_output=True,
            )
            self.assertEqual(parse.returncode, 0, parse.stderr)
            forms = json.loads(parse.stdout)
            self.assertEqual([form["name"] for form in forms[:2]], ["Bug report", "Feature request"])
            self.assertFalse(forms[2]["blank_issues_enabled"])
            self.assertEqual(len(forms[0]["body"]), 2)
            self.assertEqual(len(forms[1]["body"]), 2)
        pr_template = (self.root / ".github/PULL_REQUEST_TEMPLATE.md").read_text()
        for section in ("## Summary", "## Linked issue", "## Validation and evidence", "## Impact, risk, and rollback", "## Checklist"):
            self.assertIn(section, pr_template)
        if shutil.which("task"):
            listed = subprocess.run(["task", "--list"], cwd=self.root, text=True, capture_output=True)
            self.assertEqual(listed.returncode, 0, listed.stderr)
            doctor = subprocess.run(["task", "doctor"], cwd=self.root, text=True, capture_output=True)
            self.assertEqual(doctor.returncode, 0, doctor.stderr)
            setup = subprocess.run(["task", "setup"], cwd=self.root, text=True, capture_output=True)
            self.assertEqual(setup.returncode, 0, setup.stderr)

    def test_adopt_preserves_history_staged_files_and_uncommitted_edits(self) -> None:
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.test"], cwd=self.root, check=True)
        subprocess.run(["git", "remote", "add", "origin", "https://example.test/acme/sample.git"], cwd=self.root, check=True)
        agents = self.root / "AGENTS.md"
        readme = self.root / "README.md"
        ignore = self.root / ".gitignore"
        agents.write_text("existing agent instructions\n")
        readme.write_text("committed README\n")
        ignore.write_text("committed ignore rules\n")
        subprocess.run(["git", "add", "AGENTS.md", "README.md", ".gitignore"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture"], cwd=self.root, check=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()
        readme.write_text("user's uncommitted README edit\n")
        ignore.write_text("user's uncommitted ignore edit\n")
        scratch = self.root / "scratch.txt"
        scratch.write_text("untracked user file\n")
        before_status = subprocess.check_output(["git", "status", "--short"], cwd=self.root, text=True)
        staged_before = subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=self.root, text=True)

        result = self.run_script(SCAFFOLD, *self.options("--apply", "--approved"))

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PRESERVE existing file: AGENTS.md", result.stdout)
        self.assertIn("PRESERVE existing file: README.md", result.stdout)
        self.assertIn("PRESERVE existing file: .gitignore", result.stdout)
        self.assertEqual(agents.read_text(), "existing agent instructions\n")
        self.assertEqual(readme.read_text(), "user's uncommitted README edit\n")
        self.assertEqual(ignore.read_text(), "user's uncommitted ignore edit\n")
        self.assertEqual(scratch.read_text(), "untracked user file\n")
        self.assertEqual(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip(), head)
        self.assertEqual(subprocess.check_output(["git", "remote", "-v"], cwd=self.root, text=True).splitlines()[0].split()[0], "origin")
        self.assertEqual(subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=self.root, text=True), staged_before)
        after_status = subprocess.check_output(["git", "status", "--short"], cwd=self.root, text=True)
        self.assertEqual(after_status.splitlines()[:2], before_status.splitlines()[:2])
        self.assertIn("?? scratch.txt", after_status)

    @unittest.skipUnless(shutil.which("task"), "Task CLI unavailable")
    def test_taskfile_modules_resolve_from_alternative_project_directory(self) -> None:
        (self.root / ".taskfiles").mkdir()
        (self.root / "Taskfile.yml").write_text(
            "version: '3'\nincludes:\n  quality:\n    taskfile: .taskfiles/quality.yml\n"
            "tasks:\n  default:\n    cmds: ['task --list']\n"
        )
        (self.root / ".taskfiles/quality.yml").write_text(
            "version: '3'\ntasks:\n  check:\n    desc: Check project quality\n    cmds: ['echo checked']\n"
        )
        project_in_another_lane = self.root / "alternate-worktree"
        project_in_another_lane.mkdir()
        for name in ("Taskfile.yml", ".taskfiles"):
            source = self.root / name
            target = project_in_another_lane / name
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
        task = shutil.which("task")
        listed = subprocess.run([task, "--dir", str(project_in_another_lane), "--list"], cwd=self.root, text=True, capture_output=True)
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertIn("quality:check", listed.stdout)
        unsupported = subprocess.run([task, "--dir", str(project_in_another_lane), "quality:missing"], cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(unsupported.returncode, 0)
        self.assertIn("task", (unsupported.stdout + unsupported.stderr).lower())

    def test_symlink_escape_is_rejected(self) -> None:
        outside = self.root.parent / f"{self.root.name}-outside"
        outside.mkdir()
        try:
            (self.root / ".github").symlink_to(outside, target_is_directory=True)
            result = self.run_script(SCAFFOLD, *self.options())
            self.assertEqual(result.returncode, 2)
            self.assertEqual(list(outside.iterdir()), [])
            self.assertEqual(sorted(path.name for path in self.root.iterdir()), [".github"])
        finally:
            outside.rmdir()

    def test_partial_generation_reports_progress_and_can_resume(self) -> None:
        obstruction = self.root / ".github"
        obstruction.write_text("preserve obstruction\n")
        failed = self.run_script(SCAFFOLD, *self.options("--apply", "--approved"))
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("PARTIAL", failed.stdout)
        self.assertIn(".editorconfig", failed.stdout)
        self.assertEqual(obstruction.read_text(), "preserve obstruction\n")
        editor = self.root / ".editorconfig"
        self.assertTrue(editor.is_file())
        self.assertIn("root = true", editor.read_text())

        obstruction.unlink()
        resumed = self.run_script(SCAFFOLD, *self.options("--apply", "--approved"))
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertIn("PRESERVE existing file: .editorconfig", resumed.stdout)
        self.assertTrue((self.root / ".github/ISSUE_TEMPLATE/bug_report.yml").is_file())
        self.assertTrue((self.root / "README.md").is_file())

    def test_license_and_application_docker_require_specific_inputs(self) -> None:
        license_result = self.run_script(SCAFFOLD, "--root", str(self.root), "--display-name", "Sample", "--slug", "sample", "--description", "Description", "--profile", "POC", "--license", "MIT", "--docker-role", "no")
        self.assertEqual(license_result.returncode, 2)
        app_result = self.run_script(SCAFFOLD, *self.options("--docker-role", "application"))
        self.assertEqual(app_result.returncode, 2)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_confirmed_license_and_dependency_compose_sources_are_copied(self) -> None:
        license_source = self.root / "mit.txt"
        license_source.write_text("Canonical license text\n")
        result = self.run_script(SCAFFOLD, "--root", str(self.root), "--display-name", "Sample", "--slug", "sample", "--description", "Description", "--profile", "POC", "--license", "MIT", "--docker-role", "no", "--license-text", str(license_source), "--apply", "--approved")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Canonical license text", (self.root / "LICENSE").read_text())

    def test_docker_setup_copies_example_once_and_preserves_local_file(self) -> None:
        compose_source = self.root / "sample-compose.yaml"
        compose_source.write_text("services:\n  db:\n    image: postgres:18\n")
        env_source = self.root / "sample.env"
        env_source.write_text("DB_NAME=sample\n")
        options = ("--root", str(self.root), "--display-name", "Sample", "--slug", "sample", "--description", "Description", "--profile", "POC", "--license", "none", "--docker-role", "dependencies", "--compose-example", str(compose_source), "--env-example", str(env_source))
        result = self.run_script(SCAFFOLD, *options, "--apply", "--approved")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("docker:start", (self.root / "Taskfile.yml").read_text())
        docker = shutil.which("docker")
        if docker:
            compose_version = subprocess.run([docker, "compose", "version"], cwd=self.root, text=True, capture_output=True)
            if compose_version.returncode == 0:
                config = subprocess.run([docker, "compose", "-f", "compose.example.yaml", "config", "--quiet"], cwd=self.root, text=True, capture_output=True)
                self.assertEqual(config.returncode, 0, config.stderr)
        if shutil.which("task"):
            listed = subprocess.run(["task", "--list"], cwd=self.root, text=True, capture_output=True)
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertIn("docker:start", listed.stdout)
            self.assertNotIn("docker:build", listed.stdout)
        self.assertNotIn("--volumes", (self.root / "Taskfile.yml").read_text())
        setup = subprocess.run(["task", "setup"] if shutil.which("task") else [sys.executable, str(self.root / "scripts/setup.py")], cwd=self.root, text=True, capture_output=True)
        self.assertEqual(setup.returncode, 0, setup.stderr)
        local = self.root / "compose.yaml"
        self.assertEqual(local.read_text(), compose_source.read_text())
        local_env = self.root / ".env"
        self.assertEqual(local_env.read_text(), env_source.read_text())
        local.write_text("local override\n")
        local_env.write_text("LOCAL_SECRET=preserve\n")
        setup = subprocess.run(["task", "setup"] if shutil.which("task") else [sys.executable, str(self.root / "scripts/setup.py")], cwd=self.root, text=True, capture_output=True)
        self.assertEqual(setup.returncode, 0, setup.stderr)
        self.assertEqual(local.read_text(), "local override\n")
        self.assertEqual(local_env.read_text(), "LOCAL_SECRET=preserve\n")

    def test_docker_setup_refuses_symlinked_templates_outside_target(self) -> None:
        compose_source = self.root / "services.yaml"
        compose_source.write_text("services:\n  db:\n    image: postgres:18\n")
        options = ("--root", str(self.root), "--display-name", "Sample", "--slug", "sample", "--description", "Description", "--profile", "POC", "--license", "none", "--docker-role", "dependencies", "--compose-example", str(compose_source))
        generated = self.run_script(SCAFFOLD, *options, "--apply", "--approved")
        self.assertEqual(generated.returncode, 0, generated.stderr)
        outside = self.root.parent / f"{self.root.name}-outside.yaml"
        outside.write_text("services:\n  private:\n    image: secret\n")
        try:
            example = self.root / "compose.example.yaml"
            example.unlink()
            example.symlink_to(outside)
            setup = subprocess.run([sys.executable, str(self.root / "scripts/setup.py")], cwd=self.root, text=True, capture_output=True)
            self.assertNotEqual(setup.returncode, 0)
            self.assertIn("out-of-project template", setup.stderr)
            self.assertFalse((self.root / "compose.yaml").exists())
            self.assertEqual(outside.read_text(), "services:\n  private:\n    image: secret\n")
        finally:
            outside.unlink(missing_ok=True)

    def test_docker_doctor_reports_missing_plugin_and_invalid_config_without_secrets(self) -> None:
        compose_source = self.root / "services.yaml"
        compose_source.write_text("services:\n  db:\n    image: postgres:18\n")
        options = ("--root", str(self.root), "--display-name", "Sample", "--slug", "sample", "--description", "Description", "--profile", "POC", "--license", "none", "--docker-role", "dependencies", "--compose-example", str(compose_source))
        generated = self.run_script(SCAFFOLD, *options, "--apply", "--approved")
        self.assertEqual(generated.returncode, 0, generated.stderr)

        fake_bin = self.root.parent / f"{self.root.name}-bin"
        fake_bin.mkdir()
        for name in ("git", "python3"):
            (fake_bin / name).symlink_to(shutil.which(name))
        fake_docker = fake_bin / "docker"
        fake_docker_script = (
            "#!/bin/sh\n"
            "if [ \"$1 $2\" = 'compose version' ]; then exit \"${FAKE_COMPOSE_VERSION_STATUS:-0}\"; fi\n"
            "if [ \"${FAKE_CONFIG_STATUS:-0}\" -ne 0 ]; then echo 'TOKEN=must-not-leak' >&2; fi\n"
            "exit \"${FAKE_CONFIG_STATUS:-0}\"\n"
        )
        fake_docker.write_text(fake_docker_script)
        fake_docker.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = str(fake_bin)
        try:
            fake_docker.unlink()
            missing_docker = subprocess.run([sys.executable, str(self.root / "scripts/doctor.py")], cwd=self.root, env=env, text=True, capture_output=True)
            self.assertNotEqual(missing_docker.returncode, 0)
            self.assertIn("NOT CHECKED: Compose config; Docker CLI is missing", missing_docker.stdout)
            fake_docker.write_text(fake_docker_script)
            fake_docker.chmod(0o755)
            env["FAKE_COMPOSE_VERSION_STATUS"] = "1"
            missing_plugin = subprocess.run([sys.executable, str(self.root / "scripts/doctor.py")], cwd=self.root, env=env, text=True, capture_output=True)
            self.assertNotEqual(missing_plugin.returncode, 0)
            self.assertIn("NOT CHECKED: Compose config; Docker Compose plugin is missing", missing_plugin.stdout)
            env["FAKE_COMPOSE_VERSION_STATUS"] = "0"
            env["FAKE_CONFIG_STATUS"] = "7"
            invalid = subprocess.run([sys.executable, str(self.root / "scripts/doctor.py")], cwd=self.root, env=env, text=True, capture_output=True)
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("INVALID: Compose config", invalid.stdout)
            self.assertNotIn("must-not-leak", invalid.stdout + invalid.stderr)
            env["FAKE_CONFIG_STATUS"] = "0"
            valid = subprocess.run([sys.executable, str(self.root / "scripts/doctor.py")], cwd=self.root, env=env, text=True, capture_output=True)
            self.assertEqual(valid.returncode, 0, valid.stderr)
            self.assertIn("OK: Compose config", valid.stdout)
        finally:
            fake_docker.unlink(missing_ok=True)
            for name in ("git", "python3"):
                (fake_bin / name).unlink(missing_ok=True)
            fake_bin.rmdir()

    def test_application_docker_requires_and_uses_reviewed_stack_files(self) -> None:
        compose_source = self.root / "app-compose.yaml"
        compose_source.write_text("services:\n  app:\n    build: .\n")
        dockerfile_source = self.root / "Dockerfile.source"
        dockerfile_source.write_text("FROM busybox:stable\nCMD [\"true\"]\n")
        options = ("--root", str(self.root), "--display-name", "Sample", "--slug", "sample", "--description", "Description", "--profile", "application", "--license", "none", "--docker-role", "application", "--compose-example", str(compose_source), "--dockerfile", str(dockerfile_source))
        result = self.run_script(SCAFFOLD, *options, "--apply", "--approved")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / "Dockerfile").read_text(), dockerfile_source.read_text())
        taskfile = (self.root / "Taskfile.yml").read_text()
        self.assertIn("docker compose up -d --no-recreate", taskfile)
        self.assertIn("docker compose up -d --force-recreate", taskfile)
        self.assertIn("docker compose down\n", taskfile)
        self.assertIn("docker:build-nocache:", taskfile)
        self.assertIn("docker compose build --no-cache", taskfile)
        docker = shutil.which("docker")
        if docker and subprocess.run([docker, "compose", "version"], capture_output=True).returncode == 0:
            config = subprocess.run([docker, "compose", "-f", "compose.example.yaml", "config", "--quiet"], cwd=self.root, text=True, capture_output=True)
            self.assertEqual(config.returncode, 0, config.stderr)

    @unittest.skipUnless(shutil.which("task"), "Task CLI unavailable")
    def test_docker_tasks_dispatch_safe_lifecycle_and_distinct_build_commands(self) -> None:
        compose_source = self.root / "app-compose.yaml"
        compose_source.write_text("services:\n  app:\n    build: .\n")
        dockerfile_source = self.root / "Dockerfile.source"
        dockerfile_source.write_text("FROM busybox:stable\nCMD [\"true\"]\n")
        options = ("--root", str(self.root), "--display-name", "Sample", "--slug", "sample", "--description", "Description", "--profile", "application", "--license", "none", "--docker-role", "application", "--compose-example", str(compose_source), "--dockerfile", str(dockerfile_source))
        generated = self.run_script(SCAFFOLD, *options, "--apply", "--approved")
        self.assertEqual(generated.returncode, 0, generated.stderr)
        fake_bin = self.root.parent / f"{self.root.name}-bin"
        fake_bin.mkdir()
        log = self.root.parent / f"{self.root.name}-docker-log"
        fake_docker = fake_bin / "docker"
        fake_docker.write_text("#!/bin/sh\nprintf '%s\\n' \"$*\" >> \"$DOCKER_LOG\"\nexit 0\n")
        fake_docker.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = str(fake_bin) + os.pathsep + env.get("PATH", "")
        env["DOCKER_LOG"] = str(log)
        task = shutil.which("task")
        commands = ("config", "start", "recreate", "stop", "down", "build", "build-nocache")
        try:
            for command in commands:
                result = subprocess.run([task, f"docker:{command}"], cwd=self.root, env=env, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")
            calls = log.read_text().splitlines()
            self.assertEqual(calls, [
                "compose -f compose.example.yaml config --quiet",
                "compose up -d --no-recreate",
                "compose up -d --force-recreate",
                "compose stop",
                "compose down",
                "compose build",
                "compose build --no-cache",
            ])
            self.assertTrue(all("--volumes" not in call for call in calls))
        finally:
            fake_docker.unlink(missing_ok=True)
            fake_bin.rmdir()
            log.unlink(missing_ok=True)

    def test_validate_distinguishes_missing_files_and_optional_compose(self) -> None:
        result = self.run_script(VALIDATE, str(self.root))
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertTrue(any(item["status"] == "fail" for item in report))
        compose = next(item for item in report if item["check"] == "compose:config")
        self.assertEqual(compose["status"], "not applicable")

    def test_validation_report_uses_all_four_statuses(self) -> None:
        compose_source = self.root / "services.yaml"
        compose_source.write_text("services:\n  db:\n    image: postgres:18\n")
        options = ("--root", str(self.root), "--display-name", "Sample", "--slug", "sample", "--description", "Description", "--profile", "POC", "--license", "none", "--docker-role", "dependencies", "--compose-example", str(compose_source))
        generated = self.run_script(SCAFFOLD, *options, "--apply", "--approved")
        self.assertEqual(generated.returncode, 0, generated.stderr)
        (self.root / "SUPPORT.md").unlink()

        fake_bin = self.root.parent / f"{self.root.name}-bin"
        fake_bin.mkdir()
        docker = fake_bin / "docker"
        docker.write_text("#!/bin/sh\nexit 0\n")
        docker.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = str(fake_bin) + os.pathsep + env.get("PATH", "")
        try:
            regular = subprocess.run([sys.executable, "-I", str(VALIDATE), str(self.root)], cwd=self.root, env=env, text=True, capture_output=True)
            audit = subprocess.run([sys.executable, "-I", str(VALIDATE), str(self.root), "--audit"], cwd=self.root, env=env, text=True, capture_output=True)
            self.assertEqual(regular.returncode, 1)
            self.assertEqual(audit.returncode, 1)
            statuses = {item["status"] for item in (*json.loads(regular.stdout), *json.loads(audit.stdout))}
            self.assertEqual(statuses, {"pass", "fail", "not applicable", "not verified"})
        finally:
            docker.unlink(missing_ok=True)
            fake_bin.rmdir()

    def test_audit_validation_never_executes_project_commands(self) -> None:
        marker = self.root / "audit-wrote-this"
        (self.root / "Taskfile.yml").write_text(f"version: '3'\ntasks:\n  doctor:\n    cmds: ['touch {marker}']\n")
        result = self.run_script(VALIDATE, str(self.root), "--audit")
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        task = next(item for item in report if item["check"] == "taskfile:parse")
        self.assertEqual(task["status"], "not verified")
        self.assertFalse(marker.exists())

    def test_audit_preserves_git_files_and_never_calls_remote_writes(self) -> None:
        scaffold = self.run_script(SCAFFOLD, *self.options("--apply", "--approved"))
        self.assertEqual(scaffold.returncode, 0, scaffold.stderr)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.test"], cwd=self.root, check=True)
        subprocess.run(["git", "remote", "add", "origin", "https://user:secret@example.test/acme/sample.git"], cwd=self.root, check=True)
        (self.root / "Taskfile.yml").write_text("version: '3'\ntasks:\n  doctor:\n    cmds: ['touch audit-marker']\n")
        (self.root / ".dockerignore").write_text(".env\n")
        (self.root / "compose.example.yaml").write_text("services: {}\n")
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture"], cwd=self.root, check=True)
        (self.root / "README.md").write_text("uncommitted edit\n")
        (self.root / ".env").write_text("TOKEN=private-value\n")
        (self.root / "scratch.md").write_text("untracked\n")

        fake_bin = self.root.parent / f"{self.root.name}-bin"
        fake_bin.mkdir()
        call_log = self.root.parent / f"{self.root.name}-gh-calls"
        fake_gh = fake_bin / "gh"
        fake_gh.write_text("#!/bin/sh\nprintf '%s\\n' \"$*\" >> \"$GH_CALL_LOG\"\nif [ \"$1 $2\" = 'api user' ]; then printf 'fixture-user\\n'; exit 0; fi\nexit 78\n")
        fake_gh.chmod(0o755)
        fake_docker = fake_bin / "docker"
        fake_docker.write_text("#!/bin/sh\nprintf '%s\\n' \"$*\" >> \"$DOCKER_CALL_LOG\"\nexit 78\n")
        fake_docker.chmod(0o755)
        env = os.environ.copy()
        env["PATH"] = str(fake_bin) + os.pathsep + env.get("PATH", "")
        env["GH_CALL_LOG"] = str(call_log)
        env["DOCKER_CALL_LOG"] = str(self.root.parent / f"{self.root.name}-docker-calls")
        before = self.snapshot_tree()
        try:
            inspected = self.run_script(INSPECT, str(self.root), env=env)
            audited = self.run_script(VALIDATE, str(self.root), "--audit", env=env)
            self.assertEqual(inspected.returncode, 0, inspected.stderr)
            self.assertEqual(audited.returncode, 0, audited.stderr)
            report = json.loads(inspected.stdout)
            self.assertIn("README.md", report["status"])
            self.assertIn("scratch.md", report["status"])
            self.assertTrue(any(item["name"] == ".env" for item in report["entries"]))
            self.assertNotIn("secret", inspected.stdout)
            after = self.snapshot_tree()
            changed = [name for name in before if before[name] != after.get(name)]
            self.assertEqual(changed, [], f"Audit changed target paths: {changed}")
            self.assertFalse((self.root / "audit-marker").exists())
            self.assertEqual(call_log.read_text().splitlines(), ["api user --jq .login"])
            self.assertFalse(Path(env["DOCKER_CALL_LOG"]).exists())
        finally:
            for path in (call_log, Path(env["DOCKER_CALL_LOG"])):
                path.unlink(missing_ok=True)
            fake_gh.unlink(missing_ok=True)
            fake_docker.unlink(missing_ok=True)
            fake_bin.rmdir()


if __name__ == "__main__":
    unittest.main()
