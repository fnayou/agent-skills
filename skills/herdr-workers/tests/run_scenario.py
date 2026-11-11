#!/usr/bin/env python3
"""Drive one scenario with a fresh Claude Code foreman in its own herdr pane.

Usage: python3 skills/herdr-workers/tests/run_scenario.py <scenario-id> <fixture-directory> [full|hold|finish] [--kind KIND]

Run it from a session inside herdr. The fixture directory must not exist yet.

  full    (default) build the fixture, start the foreman in it, send the
          scenario's prompt, wait until the foreman and its workers are done,
          then print the check result and what the foreman did.
  hold    the same up to the foreman's first stop, then leave it alive, for a
          scenario in which the foreman asks the operator something first.
  finish  the second half of a held run: wait and report. Give the same
          scenario id and fixture directory.

--kind replaces <KIND> in a prompt that names no kind of its own.

The prompt is the first text block under "## Prompt" in the scenario file.
The foreman's pane is closed when the foreman has finished, and left open
otherwise so that it can be inspected.
"""
import glob
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))
import tokens  # noqa: E402

GIT_WRITES = r"git(?: -C \S+)? (?:add|commit|switch|checkout|worktree add|merge|rebase|reset|push|rm|mv)\b[^\n;|&]*"
WAIT_SECONDS = 1500


def run(*args, timeout=120):
    return subprocess.run(list(args), capture_output=True, text=True, timeout=timeout)


def herdr(*args, timeout=120):
    result = run("herdr", *args, timeout=timeout)
    try:
        return json.loads(result.stdout or result.stderr)
    except ValueError:
        return {"raw": result.stdout + result.stderr}


def status(name):
    return herdr("agent", "get", name).get("result", {}).get("agent", {}).get("agent_status", "gone")


def pane_text(name, lines, source="visible"):
    return run("herdr", "agent", "read", name, "--source", source, "--lines", str(lines)).stdout


def prompt_of(scenario, fixture, kind):
    """The scenario's prompt, with its placeholders filled in."""
    text = (TESTS / "scenarios" / f"{scenario}.md").read_text()
    found = re.search(r"^## Prompt\n.*?```text\n(.*?)\n```", text, flags=re.S | re.M)
    if not found:
        sys.exit(f"ERROR no prompt block in scenario {scenario}")
    prompt = found.group(1).replace("<FIXTURE>", fixture)
    if "<KIND>" in prompt:
        if not kind:
            sys.exit(f"ERROR scenario {scenario} needs --kind")
        prompt = prompt.replace("<KIND>", kind)
    return prompt


def tool_calls(path):
    """Every tool call of one Claude Code session file, in order."""
    for line in open(path):
        content = (json.loads(line).get("message") or {}).get("content")
        for item in content if isinstance(content, list) else []:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                yield item


def session_files(fixture):
    # Claude Code names a session's directory after its working directory,
    # with every character that is not a letter or a digit turned into "-".
    # The trailing wildcard takes in worktrees made beside the fixture.
    slug = re.sub(r"[^A-Za-z0-9]", "-", fixture)
    return sorted(glob.glob(os.path.expanduser(f"~/.claude/projects/{slug}*/*.jsonl")), key=os.path.getmtime)


def report_session(path, fixture):
    calls, skills, commands, changes = 0, [], [], []
    for item in tool_calls(path):
        calls += 1
        command = str(item["input"].get("command", ""))
        commands.append(command)
        if item.get("name") == "Skill":
            skills.append(item["input"].get("skill"))
        if "herdr agent start" in command:
            print("START", command[command.index("herdr agent start"):][:600].splitlines()[0])
        if "herdr agent prompt" in command and "PROMPT=" in command:
            print("BRIEF_CHARS", len(command))
        if command.lstrip().startswith("cd "):
            print("CD_USED", command[:80].splitlines()[0])
        # What the foreman changed itself: file tools aimed at the fixture,
        # and git commands with an effect outside any heredoc it sent.
        target = str(item["input"].get("file_path", ""))
        if item.get("name") in ("Edit", "Write", "NotebookEdit") and target.startswith(fixture):
            changes.append(f"{item['name']} {target[len(fixture):]}")
        bare = re.sub(r"<<-?\s*['\"]?(\w+)['\"]?.*?\n\s*\1\b", "", command, flags=re.S)
        bare = re.sub(r"Bash\([^)]*\)", "", bare)  # allowlist patterns are not commands
        changes.extend(found[:110] for found in re.findall(GIT_WRITES, bare))
    print("SESSION", Path(path).stem[:8], tokens.claude(path), "TOOL_CALLS", calls, "SKILL", skills)
    if skills:
        text = "\n".join(commands)
        print("FOREMAN_CHANGES", len(changes), changes)
        print(
            "COUNTS splits", text.count("herdr pane split"),
            "starts", text.count("herdr agent start"),
            "quits", text.count("/quit") + text.count("/exit"),
            "closes", text.count("herdr pane close"),
            "prompts", text.count("herdr agent prompt"),
        )


def start_foreman(scenario, fixture, agent, kind):
    prompt = prompt_of(scenario, fixture, kind)
    print(run(sys.executable, str(TESTS / "fixture" / "build.py"), fixture).stdout.strip())
    print(run(sys.executable, str(TESTS / "check.py"), "00-fixture", fixture).stdout.strip().splitlines()[-1])

    split = herdr("pane", "split", "--current", "--direction", "right", "--cwd", fixture, "--no-focus")
    pane = split["result"]["pane"]["pane_id"]
    herdr("pane", "rename", pane, f"claude: TEST foreman {Path(fixture).name}")
    print("PANE", pane, agent)
    time.sleep(2)
    herdr("agent", "start", agent, "--kind", "claude", "--pane", pane, "--timeout", "90000")
    # The fixture is a directory Claude Code has not been started in.
    if "Yes, I trust this folder" in pane_text(agent, 30):
        herdr("agent", "send-keys", agent, "down", "enter")
        print("TRUST dialog of the fixture answered yes")
    for _ in range(45):
        time.sleep(2)
        if status(agent) in ("idle", "done"):
            break
    else:
        print("NOT READY\n" + pane_text(agent, 30))
        return None
    herdr("agent", "prompt", agent, prompt, "--wait", "--timeout", str(WAIT_SECONDS * 1000), timeout=WAIT_SECONDS + 60)
    return pane


def main():
    args = sys.argv[1:]
    kind = None
    if "--kind" in args:
        at = args.index("--kind")
        kind = args[at + 1]
        del args[at:at + 2]
    if len(args) not in (2, 3) or (len(args) == 3 and args[2] not in ("full", "hold", "finish")):
        sys.exit(__doc__)
    scenario = args[0]
    mode = args[2] if len(args) == 3 else "full"
    fixture = os.path.realpath(args[1])
    agent = "tf-" + re.sub(r"[^a-z0-9]", "-", Path(fixture).name.lower())
    started = time.time()

    if mode == "finish":
        pane = herdr("agent", "get", agent).get("result", {}).get("agent", {}).get("pane_id")
        if not pane:
            sys.exit(f"ERROR no foreman {agent} to finish")
    else:
        if os.path.exists(fixture):
            sys.exit(f"ERROR fixture directory exists: {fixture}")
        pane = start_foreman(scenario, fixture, agent, kind)
        if pane is None:
            return
        if mode == "hold":
            print("HELD", status(agent), "WALL", int(time.time() - started), "s")
            print(pane_text(agent, 70, "recent-unwrapped"))
            return

    # A foreman that asks the operator a question looks finished to herdr.
    # The run is over only when none of its workers is left.
    def workers_left():
        listed = herdr("agent", "list").get("result", {}).get("agents", [])
        return [a.get("name") for a in listed if a.get("cwd", "").startswith(fixture) and a.get("name") != agent]

    def question_open():
        # A list of choices, or a dialog the foreman has reported as the
        # operator's and not yet followed with its summary.
        text = pane_text(agent, 60)
        return "Enter to select" in text or text.rfind("WAITING FOR OPERATOR") > text.rfind("runs summary")

    while (workers_left() or question_open()) and time.time() - started < WAIT_SECONDS:
        time.sleep(5)
    herdr("agent", "wait", agent, "--until", "idle", "--until", "done", "--timeout", "180000", timeout=200)
    time.sleep(3)
    state = status(agent)
    print("STATUS", state, "WALL", int(time.time() - started), "s")
    print(pane_text(agent, 55, "recent-unwrapped"))
    print(run(sys.executable, str(TESTS / "check.py"), scenario, fixture).stdout.strip())

    for path in session_files(fixture):
        report_session(path, fixture)

    left = [a.get("name") or a.get("pane_id") for a in herdr("agent", "list").get("result", {}).get("agents", [])]
    print("AGENTS_LEFT", left)
    if state in ("idle", "done"):
        herdr("pane", "close", pane)
        print("CLOSED", pane)


if __name__ == "__main__":
    main()
