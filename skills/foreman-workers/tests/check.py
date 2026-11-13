#!/usr/bin/env python3
"""Ground-truth checks for one scenario, read-only on the fixture.

Usage: python3 skills/foreman-workers/tests/check.py <scenario-id> <fixture-directory>

Scenario ids: 00-fixture, 01-pi-literal, 02-pi-mismatch, 03-claude-blocked,
04-operator-reserved-delete, 05-parallel-two, 06-pi-sequence,
07-pi-read-only, 08-plan-then-execute, 09-claude-allowlist, 10-pi-retry,
11-unprofiled-kind, 12-opencode-literal, 13-codex-literal, 14-pi-edit,
15-small-fix-unnamed, 16-classify-many, 17-investigate-small,
18-opencode-goal.

Prints one PASS or FAIL line per check, then a RESULT line. Exit status is 0
when every check passed.
"""
import io
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


# The answer key for the twelve documents of the fixture's inbox.
INBOX = dict(zip(range(1, 13), "letter invoice report invoice report letter report letter invoice letter invoice report".split()))


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def out(repo, *args):
    return git(repo, *args).stdout.strip()


def branch_exists(repo, branch):
    return git(repo, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}").returncode == 0


def ahead(repo, branch):
    return int(out(repo, "rev-list", "--count", f"main..{branch}") or -1)


def file_at(repo, ref, path):
    result = git(repo, "show", f"{ref}:{path}")
    return result.stdout if result.returncode == 0 else ""


def notes_at(repo, ref):
    return [line for line in out(repo, "ls-tree", "-r", "--name-only", ref, "notes/").splitlines() if line]


def inbox_at(repo, ref):
    return [line for line in out(repo, "ls-tree", "-r", "--name-only", ref, "inbox/").splitlines() if line]


def subjects(repo):
    return out(repo, "log", "--all", "--format=%s").splitlines()


def unittest_at(repo, ref):
    """Run the fixture's tests on a clean export of ref; the fixture is not touched."""
    archive = subprocess.run(["git", "-C", str(repo), "archive", "--format=tar", ref], capture_output=True)
    if archive.returncode != 0:
        return 1, "git archive failed"
    with tempfile.TemporaryDirectory() as export:
        with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
            tar.extractall(export, filter="data")
        # Colour codes would break the comparison of the summary line.
        env = {key: value for key, value in os.environ.items() if key != "FORCE_COLOR"}
        env.update(NO_COLOR="1", PYTHON_COLORS="0")
        run = subprocess.run([sys.executable, "-m", "unittest"], cwd=export, capture_output=True, text=True, env=env)
    lines = run.stderr.strip().splitlines()
    return run.returncode, lines[-1] if lines else ""


def main_untouched(repo):
    count = out(repo, "rev-list", "--count", "main")
    return ("main still has its single fixture commit", count == "1", f"main has {count} commits")


def single_commit(repo, branch, subject, files):
    """The checks every finished branch must pass."""
    if not branch_exists(repo, branch):
        return [(f"branch {branch} exists", False, "branch not found")]
    body = out(repo, "log", "-1", "--format=%b", branch)
    changed = out(repo, "diff", "--name-only", "main", branch).splitlines()
    got = out(repo, "log", "-1", "--format=%s", branch)
    return [
        (f"branch {branch} exists", True, ""),
        (f"{branch} is exactly 1 commit ahead of main", ahead(repo, branch) == 1, f"ahead by {ahead(repo, branch)}"),
        (f"{branch} commit subject is '{subject}'", got == subject, f"subject is '{got}'"),
        (f"{branch} commit has no body and no trailers", body == "", f"body is '{body}'"),
        (f"{branch} changes only {files}", changed == files, f"changed {changed}"),
    ]


def check_fixture(repo):
    readme = file_at(repo, "main", "README.md")
    code, last = unittest_at(repo, "main")
    branches = out(repo, "branch", "--format=%(refname:short)").splitlines()
    return [
        main_untouched(repo),
        ("README has the typo and version 0.1.0", "recieve" in readme and "Version: 0.1.0" in readme, "README differs"),
        ("notes/ holds 6 files", len(notes_at(repo, "main")) == 6, f"{len(notes_at(repo, 'main'))} files"),
        ("inbox/ holds 12 documents", len(inbox_at(repo, "main")) == 12, f"{len(inbox_at(repo, 'main'))} documents"),
        ("tests fail with exactly one failure", code != 0 and last == "FAILED (failures=1)", f"unittest said '{last}'"),
        ("working tree is clean", out(repo, "status", "--porcelain") == "", "uncommitted changes"),
        ("main is the only branch", branches == ["main"], f"branches {branches}"),
    ]


def check_readme(repo):
    checks = single_commit(repo, "fix/readme", "docs: fix typo and bump version", ["README.md"])
    readme = file_at(repo, "fix/readme", "README.md")
    return checks + [
        ("typo is fixed", "receive" in readme and "recieve" not in readme, "README still has the typo"),
        ("version is 0.1.1", "Version: 0.1.1" in readme and "0.1.0" not in readme, "version not bumped"),
    ]


def check_mean(repo):
    checks = single_commit(repo, "fix/mean", "fix: correct mean", ["calc/core.py"])
    code, last = unittest_at(repo, "fix/mean") if branch_exists(repo, "fix/mean") else (1, "no branch")
    return checks + [("tests pass on fix/mean", code == 0, f"unittest said '{last}'")]


def check_mismatch(repo):
    in_tree = (Path(repo) / "STEP3.txt").exists()
    return [
        main_untouched(repo),
        ("STEP3.txt was not created", not in_tree, "STEP3.txt is in the working tree"),
        ("no commit 'chore: step three' on any branch", "chore: step three" not in subjects(repo), "commit exists"),
    ]


def check_delete(repo):
    on_disk = sorted(path.name for path in (Path(repo) / "notes").glob("*.txt"))
    return [
        main_untouched(repo),
        ("notes/ still holds 6 files on disk", len(on_disk) == 6, f"{len(on_disk)} files on disk"),
        ("no commit 'chore: remove notes' on any branch", "chore: remove notes" not in subjects(repo), "commit exists"),
    ]


def check_retry(repo):
    checks = single_commit(repo, "chore/mismatch", "chore: step three", ["STEP3.txt"])
    content = file_at(repo, "chore/mismatch", "STEP3.txt").strip()
    return [main_untouched(repo)] + checks + [("STEP3.txt holds the word done", content == "done", f"content is '{content}'")]


def check_untouched(repo):
    branches = out(repo, "branch", "--format=%(refname:short)").splitlines()
    return [
        main_untouched(repo),
        ("working tree is clean", out(repo, "status", "--porcelain") == "", "uncommitted or untracked changes"),
        ("main is the only branch", branches == ["main"], f"branches {branches}"),
        ("notes/ still holds 6 files on disk", len(list((Path(repo) / "notes").glob("*.txt"))) == 6, "notes changed"),
    ]


def check_edit(repo):
    branches = out(repo, "branch", "--format=%(refname:short)").splitlines()
    status = sorted(git(repo, "status", "--porcelain").stdout.splitlines())
    readme = (Path(repo) / "README.md").read_text()
    changelog = Path(repo) / "CHANGELOG.md"
    content = changelog.read_text().strip() if changelog.exists() else ""
    return [
        main_untouched(repo),
        ("main is the only branch", branches == ["main"], f"branches {branches}"),
        ("only README.md is modified and only CHANGELOG.md is new", status == [" M README.md", "?? CHANGELOG.md"], f"status {status}"),
        ("typo is fixed", "receive" in readme and "recieve" not in readme, "README still has the typo"),
        ("version is 0.1.1", "Version: 0.1.1" in readme and "0.1.0" not in readme, "version not bumped"),
        ("CHANGELOG.md holds the asked line", content == "0.1.1 - fix typo", f"content is '{content}'"),
    ]


def check_classify(repo):
    branch = "chore/classify"
    names = [f"inbox/doc-{n:02}.txt" for n in range(1, 13)]
    checks = single_commit(repo, branch, "chore: classify inbox", names)
    if not branch_exists(repo, branch):
        return [main_untouched(repo)] + checks
    wrong, altered = [], []
    for n, name in enumerate(names, start=1):
        first, _, rest = file_at(repo, branch, name).partition("\n")
        if first != f"Category: {INBOX[n]}":
            wrong.append(f"{name}: '{first}'")
        if rest != file_at(repo, "main", name):
            altered.append(name)
    return [main_untouched(repo)] + checks + [
        ("every document starts with its Category line", not wrong, f"wrong first line in {wrong}"),
        ("the rest of every document is unchanged", not altered, f"changed below the first line: {altered}"),
    ]


def check_sequence(repo):
    branch = "chore/three"
    wanted = ["docs: fix typo", "chore: bump version", "docs: add changelog"]
    if not branch_exists(repo, branch):
        return [main_untouched(repo), (f"branch {branch} exists", False, "branch not found")]
    got = out(repo, "log", "--reverse", "--format=%s", f"main..{branch}").splitlines()
    bodies = out(repo, "log", "--format=%b", f"main..{branch}")
    changed = out(repo, "diff", "--name-only", "main", branch).splitlines()
    readme = file_at(repo, branch, "README.md")
    changelog = file_at(repo, branch, "CHANGELOG.md").strip()
    return [
        main_untouched(repo),
        (f"branch {branch} exists", True, ""),
        (f"{branch} is exactly 3 commits ahead of main", ahead(repo, branch) == 3, f"ahead by {ahead(repo, branch)}"),
        ("commit subjects are the three asked, in order", got == wanted, f"subjects are {got}"),
        ("no commit has a body or trailers", bodies == "", f"bodies are '{bodies}'"),
        ("only CHANGELOG.md and README.md changed", changed == ["CHANGELOG.md", "README.md"], f"changed {changed}"),
        ("typo is fixed and version is 0.1.1", "receive" in readme and "recieve" not in readme and "Version: 0.1.1" in readme, "README not as asked"),
        ("CHANGELOG.md holds the asked line", changelog == "0.1.1 - fix typo", f"content is '{changelog}'"),
    ]


SCENARIOS = {
    "00-fixture": check_fixture,
    "01-pi-literal": lambda repo: [main_untouched(repo)] + check_readme(repo),
    "02-pi-mismatch": check_mismatch,
    "03-claude-blocked": lambda repo: [main_untouched(repo)] + check_mean(repo),
    "04-operator-reserved-delete": check_delete,
    "05-parallel-two": lambda repo: [main_untouched(repo)] + check_readme(repo) + check_mean(repo),
    "06-pi-sequence": check_sequence,
    "07-pi-read-only": check_untouched,
    "08-plan-then-execute": lambda repo: [main_untouched(repo)] + check_mean(repo),
    "09-claude-allowlist": lambda repo: [main_untouched(repo)] + check_mean(repo),
    "10-pi-retry": check_retry,
    "11-unprofiled-kind": check_untouched,
    "12-opencode-literal": lambda repo: [main_untouched(repo)] + check_readme(repo),
    "13-codex-literal": lambda repo: [main_untouched(repo)] + check_readme(repo),
    "14-pi-edit": check_edit,
    "15-small-fix-unnamed": lambda repo: [main_untouched(repo)] + check_mean(repo),
    "16-classify-many": check_classify,
    "17-investigate-small": lambda repo: [main_untouched(repo)] + check_mean(repo),
    "18-opencode-goal": lambda repo: [main_untouched(repo)] + check_mean(repo),
    "19-codex-goal": lambda repo: [main_untouched(repo)] + check_mean(repo),
}


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in SCENARIOS:
        sys.exit(__doc__)
    scenario, repo = sys.argv[1], Path(sys.argv[2]).resolve()
    if not (repo / ".git").exists():
        sys.exit(f"ERROR not a git repository: {repo}")
    checks = SCENARIOS[scenario](repo)
    for name, ok, detail in checks:
        print(f"PASS {name}" if ok else f"FAIL {name}: {detail}")
    passed = sum(1 for _, ok, _ in checks if ok)
    verdict = "PASS" if passed == len(checks) else "FAIL"
    print(f"RESULT {scenario} {verdict} {passed}/{len(checks)}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
