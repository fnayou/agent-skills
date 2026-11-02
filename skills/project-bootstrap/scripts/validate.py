#!/usr/bin/env python3
"""Read-only checks for a project-bootstrap baseline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess


def validate(root: Path, audit: bool = False) -> list[dict[str, str]]:
    results = []
    required = ["AGENTS.md", "README.md", "Taskfile.yml", ".editorconfig", ".gitignore", ".gitattributes", "CODE_OF_CONDUCT.md", "CONTRIBUTING.md", "SECURITY.md", "SUPPORT.md", ".github/PULL_REQUEST_TEMPLATE.md", ".github/ISSUE_TEMPLATE/config.yml", ".github/ISSUE_TEMPLATE/bug_report.yml", ".github/ISSUE_TEMPLATE/feature_request.yml"]
    for name in required:
        path = root / name
        exists = path.is_file()
        safe = exists and path.resolve(strict=False).is_relative_to(root)
        status = "pass" if safe else "fail"
        detail = "present" if safe else "escapes target root through symlink" if exists else "missing"
        results.append({"check": f"file:{name}", "status": status, "detail": detail})
    ignore_path = root / ".gitignore"
    ignore_safe = ignore_path.is_file() and ignore_path.resolve(strict=False).is_relative_to(root)
    ignore = ignore_path.read_text(encoding="utf-8") if ignore_safe else ""
    ignores_secrets = all(line in ignore.splitlines() for line in (".env", ".env.*", "!.env.example", "*.pem", "*.key"))
    results.append({"check": "gitignore:secrets", "status": "pass" if ignores_secrets else "fail", "detail": "common environment and key files are excluded" if ignores_secrets else "missing required secret exclusions"})
    task = shutil.which("task")
    taskfile_path = root / "Taskfile.yml"
    taskfile_safe = taskfile_path.is_file() and taskfile_path.resolve(strict=False).is_relative_to(root)
    doctor_path = root / "scripts" / "doctor.py"
    doctor_safe = doctor_path.is_file() and doctor_path.resolve(strict=False).is_relative_to(root)
    if audit:
        results.append({"check": "taskfile:parse", "status": "not verified", "detail": "Audit mode does not execute project task definitions"})
        results.append({"check": "task:doctor", "status": "not verified", "detail": "Audit mode does not execute project task definitions"})
    elif not task:
        results.append({"check": "taskfile:parse", "status": "not verified", "detail": "Task CLI missing"})
        results.append({"check": "task:doctor", "status": "not verified", "detail": "Task CLI missing"})
    elif not taskfile_safe:
        results.append({"check": "taskfile:parse", "status": "fail", "detail": "Taskfile is missing or escapes target root through symlink"})
        results.append({"check": "task:doctor", "status": "not verified", "detail": "Unsafe Taskfile was not executed"})
    else:
        listed = subprocess.run([task, "--list"], cwd=root, capture_output=True, text=True, check=False)
        results.append({"check": "taskfile:parse", "status": "pass" if listed.returncode == 0 else "fail", "detail": "task --list succeeded" if listed.returncode == 0 else "Taskfile parse failed; inspect task --list locally"})
        if listed.returncode == 0:
            if not doctor_safe:
                results.append({"check": "task:doctor", "status": "not verified", "detail": "Project doctor script is missing or escapes target root through symlink"})
            else:
                doctor = subprocess.run([task, "doctor"], cwd=root, capture_output=True, text=True, check=False)
                results.append({"check": "task:doctor", "status": "pass" if doctor.returncode == 0 else "fail", "detail": "task doctor succeeded" if doctor.returncode == 0 else "task doctor failed; rerun locally to inspect its diagnostic"})
        else:
            results.append({"check": "task:doctor", "status": "not verified", "detail": "Taskfile could not be loaded"})
    taskfile_text = taskfile_path.read_text(encoding="utf-8") if taskfile_safe else ""
    docker_selected = any((root / name).exists() for name in (".dockerignore", "Dockerfile", "compose.example.yaml", "compose.yaml")) or "docker:" in taskfile_text
    compose_files = [("compose:config", "compose.example.yaml", docker_selected), ("compose:local", "compose.yaml", False)]
    docker = shutil.which("docker")
    version = None
    if docker and not audit:
        version = subprocess.run([docker, "compose", "version"], cwd=root, capture_output=True, text=True, check=False)
    for check_name, file_name, required_compose in compose_files:
        path = root / file_name
        if path.exists() and not path.resolve(strict=False).is_relative_to(root):
            status, detail = "fail", "Compose path escapes target root through symlink"
        elif not path.is_file():
            status = "not applicable" if not required_compose else "fail"
            detail = "local Compose file is optional" if not required_compose else "Compose example missing"
        elif audit:
            status, detail = "not verified", "Audit mode does not invoke Docker Compose"
        elif not docker:
            status, detail = "not verified", "Docker CLI missing"
        elif version is None or version.returncode:
            status, detail = "not verified", "Docker Compose plugin missing"
        else:
            config = subprocess.run([docker, "compose", "-f", file_name, "config", "--quiet"], cwd=root, capture_output=True, text=True, check=False)
            status = "pass" if config.returncode == 0 else "fail"
            detail = "Compose file is valid" if status == "pass" else "Compose validation failed; review the YAML and interpolation inputs"
        results.append({"check": check_name, "status": status, "detail": detail})
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--audit", action="store_true", help="do not execute Task or Docker Compose commands")
    args = parser.parse_args()
    root = Path(args.root).resolve(strict=True)
    results = validate(root, audit=args.audit)
    print(json.dumps(results, indent=2))
    return int(any(item["status"] == "fail" for item in results))


if __name__ == "__main__":
    raise SystemExit(main())
