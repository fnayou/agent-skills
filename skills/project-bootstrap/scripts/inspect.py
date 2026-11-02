#!/usr/bin/env python3
"""Read-only inventory for project-bootstrap."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit, urlunsplit


def run(args: list[str], cwd: Path) -> str | None:
    try:
        env = None
        if args[0] == "git":
            env = os.environ.copy()
            env["GIT_OPTIONAL_LOCKS"] = "0"
        result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=False)
    except OSError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def inspect(root: Path) -> dict[str, object]:
    root = root.resolve(strict=True)
    git_root = run(["git", "rev-parse", "--show-toplevel"], root)
    status = run(["git", "status", "--short", "--branch"], root) if git_root else None
    branch = run(["git", "branch", "--show-current"], root) if git_root else None
    remotes = run(["git", "remote", "-v"], root) if git_root else None
    safe_remotes = []
    if remotes:
        for line in remotes.splitlines():
            match = re.match(r"^(\S+)\s+(\S+)\s+\((fetch|push)\)$", line)
            if match:
                name, url, direction = match.groups()
                if "://" in url:
                    parts = urlsplit(url)
                    netloc = parts.netloc.rsplit("@", 1)
                    safe_netloc = f"REDACTED@{netloc[-1]}" if len(netloc) == 2 else parts.netloc
                    url = urlunsplit((parts.scheme, safe_netloc, parts.path, "", ""))
                safe_remotes.append({"name": name, "url": url, "direction": direction})
    paths = []
    for path in sorted(root.iterdir()):
        info: dict[str, object] = {"name": path.name, "symlink": path.is_symlink()}
        if path.is_symlink():
            info["target"] = os.readlink(path)
            try:
                info["escapes_root"] = not path.resolve(strict=False).is_relative_to(root)
            except (OSError, RuntimeError):
                info["escapes_root"] = True
        info["kind"] = "directory" if path.is_dir() else "file" if path.is_file() else "other"
        paths.append(info)
    symlinks = []
    for base, dirs, names in os.walk(root, followlinks=False):
        for name in [*dirs, *names]:
            path = Path(base) / name
            if path.is_symlink():
                try:
                    escapes = not path.resolve(strict=False).is_relative_to(root)
                except (OSError, RuntimeError):
                    escapes = True
                symlinks.append({"path": str(path.relative_to(root)), "target": os.readlink(path), "escapes_root": escapes})
        dirs[:] = [name for name in dirs if name != ".git"]
    nested = []
    for base, dirs, _files in os.walk(root):
        if ".git" in dirs or ".git" in _files:
            relative = Path(base).relative_to(root)
            if str(relative) != ".":
                nested.append(str(relative))
        dirs[:] = [d for d in dirs if d != ".git"]
    tool_paths = {name: run(["sh", "-c", "command -v \"$1\"", "sh", name], root) for name in ("gh", "task", "docker", "python3")}
    gh_account = run(["gh", "api", "user", "--jq", ".login"], root)
    gh_auth = "authenticated" if gh_account else "not authenticated" if tool_paths["gh"] else "missing"
    return {
        "root": str(root),
        "git_root": git_root,
        "branch": branch,
        "status": status,
        "remotes": safe_remotes,
        "nested_git_boundaries": sorted(set(nested)),
        "entries": paths,
        "symlinks": sorted(symlinks, key=lambda item: item["path"]),
        "tools": tool_paths,
        "gh_account": gh_account,
        "gh_auth": gh_auth,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root)
    try:
        print(json.dumps(inspect(root), indent=2))
    except (OSError, RuntimeError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
