#!/usr/bin/env python3
"""Plan or safely create missing project-bootstrap baseline files."""

from __future__ import annotations

import argparse
import difflib
import os
from pathlib import Path
import re
import tempfile


BASE = {
    ".editorconfig": "root = true\n\n[*]\ncharset = utf-8\nend_of_line = lf\ninsert_final_newline = true\nindent_style = space\nindent_size = 2\n\n[*.md]\ntrim_trailing_whitespace = false\n",
    ".gitattributes": "* text=auto\n*.sh text eol=lf\n*.py text eol=lf\n",
    ".gitignore": ".DS_Store\n.env\n.env.*\n!.env.example\n*.pem\n*.key\n",
    "CODE_OF_CONDUCT.md": "# Contributor Covenant Code of Conduct\n\nWe welcome respectful, constructive participation. Harassment, discrimination, and personal attacks are not acceptable. Maintainers will review reports and take fair, proportionate action.\n\nFor concerns, use a verified private channel listed in `SECURITY.md` or contact a maintainer through the repository's verified support channel.\n",
    "CONTRIBUTING.md": "# Contributing\n\nOpen an issue to discuss substantial changes. Keep pull requests focused, explain the change, and include validation evidence. Follow the commands in `Taskfile.yml` that apply to this project. Do not include credentials or unrelated files.\n",
    "SECURITY.md": "# Security policy\n\nDo not report vulnerabilities in public issues. Check whether private vulnerability reporting is enabled in this repository. If it is unavailable, ask the maintainers for a verified private reporting channel before sharing details. Do not include secrets in reports.\n",
    "SUPPORT.md": "# Support\n\nUse GitHub Issues for reproducible bugs and feature requests. For security reports, follow `SECURITY.md`. Include relevant versions and steps to reproduce; remove credentials and private data.\n",
    ".github/ISSUE_TEMPLATE/bug_report.yml": "name: Bug report\ndescription: Report a reproducible problem\ntitle: \"\"\nbody:\n  - type: textarea\n    id: problem\n    attributes:\n      label: Problem and expected outcome\n      description: What happened, and what should happen instead?\n    validations:\n      required: true\n  - type: textarea\n    id: reproduction\n    attributes:\n      label: Reproduction\n      description: Steps, relevant environment, and exact error output. Remove secrets.\n    validations:\n      required: true\n",
    ".github/ISSUE_TEMPLATE/feature_request.yml": "name: Feature request\ndescription: Propose a user outcome or capability\ntitle: \"\"\nbody:\n  - type: textarea\n    id: outcome\n    attributes:\n      label: Problem and desired outcome\n      description: Who needs this, and what outcome should it enable?\n    validations:\n      required: true\n  - type: textarea\n    id: acceptance\n    attributes:\n      label: Acceptance criteria\n      description: List observable conditions that would satisfy the request.\n    validations:\n      required: true\n",
    ".github/ISSUE_TEMPLATE/config.yml": "blank_issues_enabled: false\n",
    ".github/PULL_REQUEST_TEMPLATE.md": "## Summary\n\n## Linked issue\n\nCloses #\n\n## Validation and evidence\n\n## Impact, risk, and rollback\n\n## Checklist\n\n- [ ] Scope is focused and unrelated changes are excluded\n- [ ] Validation results are recorded\n- [ ] Documentation is updated where needed\n",
}


def valid_slug(value: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value))


def build_files(name: str, slug: str, description: str, profile: str, docker_role: str) -> dict[str, str]:
    files = dict(BASE)
    files["AGENTS.md"] = (
        f"# Agent instructions: {name}\n\n"
        f"Project profile: {profile}. {description}\n\n"
        "## Commands\n\nUse `task --list` to see available commands. Run `task setup` once, then `task doctor` before project work.\n\n"
        "## Working rules\n\nPreserve user changes and existing files. Keep credentials out of source control and logs. Use focused changes and Conventional Commits. Check `docs/agents/` for issue-tracker, triage-label, and domain-doc conventions when those files exist.\n"
    )
    files["README.md"] = (
        f"# {name}\n\n{description}\n\n"
        "## Getting started\n\nInstall [Task](https://taskfile.dev/) and run `task setup`, then `task doctor`.\n\n"
        "## Commands\n\nRun `task --list` for available commands.\n\n"
        "## Project profile\n\n"
        f"This repository is initialized as a {profile} foundation. Add verified project-specific build and test instructions as the implementation takes shape.\n\n"
        "## Contributing and security\n\nSee [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [SUPPORT.md](SUPPORT.md).\n"
    )
    if docker_role != "no":
        files["README.md"] += (
            "\n## Docker Compose\n\nRun `task setup` to create ignored `compose.yaml` from the tracked example when it is missing. Edit the local file for machine-specific settings. Run `task docker:config` to validate the example.\n"
        )
    files["Taskfile.yml"] = (
        'version: "3"\n\n'
        "tasks:\n"
        "  default:\n    desc: List available project tasks\n    cmds:\n      - task --list\n\n"
        "  doctor:\n    desc: Check local project prerequisites\n    cmds:\n      - python3 scripts/doctor.py\n\n"
        "  setup:\n    desc: Check whether project-specific local setup is needed\n    cmds:\n      - echo 'No local configuration templates are required.'\n"
    )
    doctor = (
        "import shutil, sys\n"
        "missing = [name for name in ('git', 'python3') if not shutil.which(name)]\n"
        "for name in missing:\n    print(f'MISSING: {name}')\n"
        "if missing:\n    print('Install missing tools and rerun task doctor.')\n"
        "    sys.exit(1)\n"
        "print('OK: local prerequisites found')\n"
    )
    if docker_role != "no":
        files[".gitignore"] += "/compose.yaml\n/compose.yml\n.env.local\n.env.*.local\n"
        files[".dockerignore"] = ".git\n.env\n.env.*\n!.env.example\ncompose.yaml\n"
        files["scripts/setup.py"] = """from pathlib import Path
import os
import tempfile


def copy_if_missing(source_name, target_name):
    source, target = Path(source_name), Path(target_name)
    root = Path.cwd().resolve()
    if not source.is_file() or not source.resolve().is_relative_to(root):
        raise SystemExit(f"Refusing missing or out-of-project template: {source_name}")
    if target.exists() or target.is_symlink():
        print(f"Preserved existing {target_name}")
        return
    fd, name = tempfile.mkstemp(prefix=f".{target_name}.", dir=".")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(source.read_bytes())
            stream.flush()
            os.fsync(stream.fileno())
        os.link(name, target)
    except FileExistsError:
        print(f"Preserved existing {target_name}")
    finally:
        Path(name).unlink(missing_ok=True)


copy_if_missing("compose.example.yaml", "compose.yaml")
if Path(".env.example").is_file():
    copy_if_missing(".env.example", ".env")
"""
        files["Taskfile.yml"] = files["Taskfile.yml"].replace(
            "      - echo 'No local configuration templates are required.'",
            "      - python3 scripts/setup.py",
        )
        files["Taskfile.yml"] = files["Taskfile.yml"].replace(
            "desc: Check whether project-specific local setup is needed",
            "desc: Initialize missing local configuration without overwriting files",
        )
        doctor = doctor.replace("import shutil, sys", "import shutil, subprocess, sys")
        doctor += (
            "docker = shutil.which('docker')\n"
            "if not docker:\n    print('NOT CHECKED: Compose config; Docker CLI is missing.')\n"
            "    sys.exit(1)\n"
            "version = subprocess.run([docker, 'compose', 'version'], capture_output=True, text=True)\n"
            "if version.returncode:\n    print('NOT CHECKED: Compose config; Docker Compose plugin is missing.')\n"
            "    sys.exit(1)\n"
            "result = subprocess.run([docker, 'compose', '-f', 'compose.example.yaml', 'config', '--quiet'], capture_output=True, text=True)\n"
            "if result.returncode:\n    print('INVALID: Compose config; run task setup and review YAML and interpolation values.')\n"
            "    sys.exit(result.returncode)\n"
            "print('OK: Compose config')\n"
        )
        files["Taskfile.yml"] += (
            "\n  docker:config:\n    desc: Validate Compose configuration without printing resolved values\n    cmds:\n      - docker compose -f compose.example.yaml config --quiet\n\n"
            "  docker:start:\n    desc: Start configured services without recreating containers\n    cmds:\n      - docker compose up -d --no-recreate\n\n"
            "  docker:recreate:\n    desc: Recreate services with current configuration\n    cmds:\n      - docker compose up -d --force-recreate\n\n"
            "  docker:stop:\n    desc: Stop services and preserve data\n    cmds:\n      - docker compose stop\n\n"
            "  docker:down:\n    desc: Remove services and networks while preserving volumes\n    cmds:\n      - docker compose down\n\n"
            "  docker:logs:\n    desc: Follow service logs\n    cmds:\n      - docker compose logs -f\n\n"
            "  docker:ps:\n    desc: List project services\n    cmds:\n      - docker compose ps\n"
        )
        if docker_role in {"application", "both"}:
            files["Taskfile.yml"] += (
                "\n  docker:build:\n    desc: Build the application image\n    cmds:\n      - docker compose build\n\n"
                "  docker:build-nocache:\n    desc: Build the application image without cache\n    cmds:\n      - docker compose build --no-cache\n"
            )
    files["scripts/doctor.py"] = doctor
    return files


def confined(root: Path, relative: str) -> Path:
    candidate = root / relative
    if not candidate.resolve(strict=False).is_relative_to(root):
        raise ValueError(f"path escapes target root: {relative}")
    current = root
    for part in Path(relative).parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"refusing symlink target: {relative}")
    return candidate


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temp_name, path)
    finally:
        Path(temp_name).unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--profile", choices=("POC", "CLI", "library", "application"), required=True)
    parser.add_argument("--docker-role", choices=("no", "dependencies", "application", "both"), required=True)
    parser.add_argument("--compose-example", help="approved, project-specific Compose YAML source")
    parser.add_argument("--env-example", help="approved, non-secret example environment file")
    parser.add_argument("--dockerfile", help="approved, stack-specific Dockerfile source for application images")
    parser.add_argument("--license", required=True, help="confirmed SPDX identifier or none")
    parser.add_argument("--license-text", help="canonical license text confirmed by the user")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--plan", action="store_true", help="show additions without writing; default mode")
    action.add_argument("--apply", action="store_true")
    parser.add_argument("--diff", action="store_true", help="show reviewable diffs for generated additions")
    parser.add_argument("--approved", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    text_has_control = any(ord(char) < 32 for value in (args.display_name, args.description) for char in value)
    if not root.is_dir() or not valid_slug(args.slug) or not args.display_name.strip() or not args.description.strip() or text_has_control:
        parser.error("target must be a directory; display name, description, and slug must be valid")
    if args.license != "none" and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*", args.license):
        parser.error("license must be a SPDX-style identifier or none")
    if args.apply and not args.approved:
        parser.error("--apply requires --approved after the user reviews the plan")
    if args.approved and not args.apply:
        parser.error("--approved is valid only with --apply")
    files = build_files(args.display_name.strip(), args.slug, args.description.strip(), args.profile, args.docker_role)
    supplied_files = set()
    if args.license != "none":
        if not args.license_text:
            print(f"BLOCKED license={args.license}: provide user-confirmed canonical license text.")
            return 2
        license_source = Path(args.license_text).resolve(strict=True)
        if not license_source.is_file():
            print("BLOCKED license source must be a regular file.")
            return 2
        files["LICENSE"] = license_source.read_text(encoding="utf-8")
        supplied_files.add("LICENSE")
    if args.docker_role != "no":
        if not args.compose_example:
            print("BLOCKED Docker: provide approved service requirements and a validated Compose example.")
            return 2
        compose_source = Path(args.compose_example).resolve(strict=True)
        if not compose_source.is_file():
            print("BLOCKED Compose source must be a regular file.")
            return 2
        files["compose.example.yaml"] = compose_source.read_text(encoding="utf-8")
        supplied_files.add("compose.example.yaml")
        if args.env_example:
            env_source = Path(args.env_example).resolve(strict=True)
            if not env_source.is_file():
                print("BLOCKED environment example source must be a regular file.")
                return 2
            files[".env.example"] = env_source.read_text(encoding="utf-8")
            supplied_files.add(".env.example")
    if args.docker_role in {"application", "both"}:
        if not args.dockerfile:
            print("BLOCKED application image: confirm stack, build command, runtime, and Dockerfile content.")
            return 2
        dockerfile_source = Path(args.dockerfile).resolve(strict=True)
        if not dockerfile_source.is_file():
            print("BLOCKED Dockerfile source must be a regular file.")
            return 2
        files["Dockerfile"] = dockerfile_source.read_text(encoding="utf-8")
        supplied_files.add("Dockerfile")
    conflicts = []
    for rel in files:
        try:
            path = confined(root, rel)
        except ValueError as error:
            print(f"CONFLICT {error}")
            return 2
        if path.exists():
            conflicts.append(rel)
    for rel in files:
        if rel not in conflicts:
            print(f"{'CREATE' if args.apply else 'WOULD CREATE'} {rel}")
    for rel in conflicts:
        print(f"PRESERVE existing file: {rel}")
    if not args.apply and args.diff:
        for rel, content in files.items():
            if rel in conflicts:
                continue
            if rel in supplied_files:
                print(f"INPUT {rel}: review the supplied source separately; contents omitted.")
                continue
            diff = difflib.unified_diff([], content.splitlines(keepends=True), fromfile="/dev/null", tofile=rel)
            print("".join(diff), end="")
    if args.apply:
        created = []
        for rel, content in files.items():
            if rel not in conflicts:
                try:
                    atomic_write(root / rel, content)
                except OSError as error:
                    reason = error.strerror or error.__class__.__name__
                    print(f"PARTIAL: created {len(created)} file(s); failed at {rel}: {reason}. Fix the obstruction and rerun the same approved plan.")
                    return 1
                created.append(rel)
        print(f"Created {len(files) - len(conflicts)} file(s); preserved {len(conflicts)} conflict(s).")
    else:
        print("Plan only. Review conflicts and obtain approval before applying.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
