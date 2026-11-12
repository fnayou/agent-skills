#!/usr/bin/env python3
"""Drive one scenario with a fresh Claude Code foreman in its own pane.

Usage: python3 skills/herdr-workers/tests/run_scenario.py <scenario-id> <fixture-directory> [full|hold|finish] [--kind KIND] [--multiplexer herdr|rex]

Run it from a session inside herdr or Rex. The fixture directory must not exist yet.

  full    (default) build the fixture, start the foreman in it, send the
          scenario's prompt, wait until the foreman and its workers are done,
          then print the check result and what the foreman did.
  hold    the same up to the foreman's first stop, then leave it alive, for a
          scenario in which the foreman asks the operator something first.
  finish  the second half of a held run: wait and report. Give the same
          scenario id and fixture directory.

--kind replaces <KIND> in a prompt that names no kind of its own.
--multiplexer chooses where the foreman runs; without it, herdr when
HERDR_ENV=1, otherwise Rex when REX_SESSION is set.

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


def as_json(result):
    try:
        return json.loads(result.stdout or result.stderr)
    except ValueError:
        return {"raw": result.stdout + result.stderr}


def session_label():
    """The label of the driver's Rex session, or None outside Rex."""
    session = os.environ.get("REX_SESSION")
    return session and as_json(run("rex", "session", "inspect", session, "--json")).get("label")


def restore_label(saved):
    # Rex's start-up hook asks every new agent, the foreman under test included, to rename the session.
    now = session_label()
    if saved and now != saved:
        run("rex", "session", "rename", os.environ["REX_SESSION"], saved)
        print("SESSION_RENAMED", now, "restored to", saved)


class Herdr:
    """The foreman as a herdr agent, found by its name."""

    name = "herdr"

    def __init__(self, fixture):
        self.fixture = fixture
        self.agent = "tf-" + re.sub(r"[^a-z0-9]", "-", Path(fixture).name.lower())
        self.pane = None
        # herdr inside a Rex pane: the foreman still gets Rex's start-up hook.
        self.label = session_label()

    def herdr(self, *args, timeout=120):
        return as_json(run("herdr", *args, timeout=timeout))

    def status(self):
        return self.herdr("agent", "get", self.agent).get("result", {}).get("agent", {}).get("agent_status", "gone")

    def text(self, lines, recent=False):
        source = "recent-unwrapped" if recent else "visible"
        return run("herdr", "agent", "read", self.agent, "--source", source, "--lines", str(lines)).stdout

    def start(self, label, prompt):
        split = self.herdr("pane", "split", "--current", "--direction", "right", "--cwd", self.fixture, "--no-focus")
        self.pane = split["result"]["pane"]["pane_id"]
        self.herdr("pane", "rename", self.pane, label)
        print("PANE", self.pane, self.agent)
        time.sleep(2)
        self.herdr("agent", "start", self.agent, "--kind", "claude", "--pane", self.pane, "--timeout", "90000")
        # The fixture is a directory Claude Code has not been started in.
        if "Yes, I trust this folder" in self.text(30):
            self.herdr("agent", "send-keys", self.agent, "down", "enter")
            print("TRUST dialog of the fixture answered yes")
        for _ in range(45):
            time.sleep(2)
            if self.status() in ("idle", "done"):
                break
        else:
            print("NOT READY\n" + self.text(30))
            return False
        self.herdr("agent", "prompt", self.agent, prompt, "--wait", "--timeout", str(WAIT_SECONDS * 1000),
                   timeout=WAIT_SECONDS + 60)
        return True

    def find(self, label):
        self.pane = self.herdr("agent", "get", self.agent).get("result", {}).get("agent", {}).get("pane_id")
        return self.pane

    def workers(self):
        listed = self.herdr("agent", "list").get("result", {}).get("agents", [])
        return [a.get("name") for a in listed if a.get("cwd", "").startswith(self.fixture) and a.get("name") != self.agent]

    def agents_left(self):
        return [a.get("name") or a.get("pane_id") for a in self.herdr("agent", "list").get("result", {}).get("agents", [])]

    def settle(self):
        self.herdr("agent", "wait", self.agent, "--until", "idle", "--until", "done", "--timeout", "180000", timeout=200)

    def close(self):
        self.herdr("pane", "close", self.pane)

    def restore(self):
        restore_label(self.label)


class Rex:
    """The foreman in a Rex pane of the driver's session, found by its label."""

    name = "rex"

    def __init__(self, fixture):
        self.fixture = fixture
        self.session = os.environ["REX_SESSION"]
        self.pane = None
        self.label = session_label()

    def rex(self, *args, timeout=60):
        return run("rex", *args, timeout=timeout)

    def call(self, block, method):
        return as_json(self.rex("block", "call", "-s", self.session, "-b", block, method))

    def state(self, block):
        # The record without an id is the program's own; opencode adds one per session.
        records = [r for r in self.call(block, "program_status").get("records", []) if not r.get("id")]
        return records[0].get("state") if records else None

    def status(self):
        return self.state(self.pane) or "gone"

    def text(self, lines, recent=False):
        out = self.rex("capture", "-s", self.session, "-b", self.pane, "--trim", "--unwrap").stdout
        return "\n".join(out.splitlines()[-lines:])

    def start(self, label, prompt):
        # The prompt goes to claude as one argument: typing it would submit at its first newline.
        split = as_json(self.rex("split", "-s", self.session, "-b", os.environ["REX_BLOCK"], "--split=right",
                                 "--label", label, "--focus=false", "-c", self.fixture, "--json",
                                 "--", "claude", prompt))
        self.pane = split["block_ids"][0]
        print("PANE", self.pane, label)
        trusted = False
        for _ in range(45):
            time.sleep(2)
            # The fixture is a directory Claude Code has not been started in.
            if not trusted and "Yes, I trust this folder" in self.text(30):
                self.rex("send-key", "-s", self.session, "-b", self.pane, "down")
                self.rex("send-key", "-s", self.session, "-b", self.pane, "enter")
                trusted = True
                print("TRUST dialog of the fixture answered yes")
            if self.status() == "working":
                break
        else:
            print("NOT STARTED\n" + self.text(30))
            return False
        while self.status() == "working" and time.time() - self.started < WAIT_SECONDS:
            time.sleep(5)
        return True

    def blocks(self):
        listed = as_json(self.rex("block", "ls", "-s", self.session, "--json")).get("blocks", [])
        return [b for b in listed if b.get("flavor", "").startswith("com.superlogical.terminal")]

    def find(self, label):
        found = [b["block_id"] for b in self.blocks() if b.get("label") == label]
        self.pane = found[0] if found else None
        return self.pane

    def agents(self):
        """Every pane of the session where a program reports a status, with its working directory."""
        for block in self.blocks():
            records = self.call(block["block_id"], "program_status").get("records", [])
            if records:
                cwd = (self.call(block["block_id"], "process").get("foreground") or {}).get("cwd", "")
                yield block, records[0].get("app"), cwd

    def workers(self):
        return [f"{app} {b['block_id']}" for b, app, cwd in self.agents()
                if cwd.startswith(self.fixture) and b["block_id"] != self.pane]

    def agents_left(self):
        return [f"{app} {b.get('label')}" for b, app, cwd in self.agents()]

    def settle(self):
        for _ in range(36):
            if self.status() != "working":
                return
            time.sleep(5)

    def close(self):
        self.rex("block", "close", "-s", self.session, self.pane)

    def restore(self):
        restore_label(self.label)


def multiplexer(args):
    if "--multiplexer" in args:
        at = args.index("--multiplexer")
        chosen = args[at + 1]
        del args[at:at + 2]
    elif os.environ.get("HERDR_ENV") == "1":
        chosen = "herdr"
    elif os.environ.get("REX_SESSION"):
        chosen = "rex"
    else:
        sys.exit("ERROR run this from a session inside herdr or Rex")
    if chosen not in ("herdr", "rex"):
        sys.exit(__doc__)
    return Herdr if chosen == "herdr" else Rex


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


def report_session(path, fixture, driven):
    calls, skills, commands, changes = 0, [], [], []
    for item in tool_calls(path):
        calls += 1
        command = str(item["input"].get("command", ""))
        commands.append(command)
        if item.get("name") == "Skill":
            skills.append(item["input"].get("skill"))
        if "herdr agent start" in command:
            print("START", command[command.index("herdr agent start"):][:600].splitlines()[0])
        if "env -u REX_SESSION" in command:
            print("START", command[command.index("env -u REX_SESSION"):][:600].splitlines()[0])
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
        bare = re.sub(r"rex send [^\n]*", "", bare)  # text typed into a worker's pane is the worker's
        changes.extend(found[:110] for found in re.findall(GIT_WRITES, bare))
    print("SESSION", Path(path).stem[:8], tokens.claude(path), "TOOL_CALLS", calls, "SKILL", skills)
    if skills:
        text = "\n".join(commands)
        print("FOREMAN_CHANGES", len(changes), changes)
        print(
            "COUNTS splits", text.count("herdr pane split") + text.count("rex split"),
            "starts", text.count("herdr agent start") + text.count("env -u REX_SESSION"),
            "quits", text.count("/quit") + text.count("/exit"),
            "closes", text.count("herdr pane close") + text.count("rex block close"),
            "prompts", text.count("herdr agent prompt") + text.count("follow it exactly"),
        )
        # With both multiplexers present, the foreman must drive the one the driver ran it in.
        other = "rex split" if driven == "herdr" else "herdr pane split"
        if other in text:
            print("WRONG_MULTIPLEXER the foreman ran", other, "under", driven)


def main():
    args = sys.argv[1:]
    kind = None
    if "--kind" in args:
        at = args.index("--kind")
        kind = args[at + 1]
        del args[at:at + 2]
    mux = multiplexer(args)
    if len(args) not in (2, 3) or (len(args) == 3 and args[2] not in ("full", "hold", "finish")):
        sys.exit(__doc__)
    scenario = args[0]
    mode = args[2] if len(args) == 3 else "full"
    fixture = os.path.realpath(args[1])
    label = f"claude: TEST foreman {Path(fixture).name}"
    foreman = mux(fixture)
    started = foreman.started = time.time()

    if mode == "finish":
        if not foreman.find(label):
            sys.exit(f"ERROR no foreman {label} to finish")
    else:
        if os.path.exists(fixture):
            sys.exit(f"ERROR fixture directory exists: {fixture}")
        prompt = prompt_of(scenario, fixture, kind)
        if foreman.name == "rex":
            # The prompts name herdr, as an operator inside herdr would.
            prompt = prompt.replace("herdr", "Rex")
        print(run(sys.executable, str(TESTS / "fixture" / "build.py"), fixture).stdout.strip())
        print(run(sys.executable, str(TESTS / "check.py"), "00-fixture", fixture).stdout.strip().splitlines()[-1])
        print("MULTIPLEXER", foreman.name)
        if not foreman.start(label, prompt):
            return
        if mode == "hold":
            print("HELD", foreman.status(), "WALL", int(time.time() - started), "s")
            print(foreman.text(70, recent=True))
            return

    # A foreman that asks the operator a question looks finished to the multiplexer.
    # The run is over only when none of its workers is left.
    def question_open():
        # A list of choices, or a dialog the foreman has reported as the
        # operator's and not yet followed with its summary.
        text = foreman.text(60)
        return "Enter to select" in text or text.rfind("WAITING FOR OPERATOR") > text.rfind("runs summary")

    while (foreman.workers() or question_open()) and time.time() - started < WAIT_SECONDS:
        time.sleep(5)
    foreman.settle()
    time.sleep(3)
    state = foreman.status()
    print("STATUS", state, "WALL", int(time.time() - started), "s")
    print(foreman.text(55, recent=True))
    print(run(sys.executable, str(TESTS / "check.py"), scenario, fixture).stdout.strip())

    for path in session_files(fixture):
        report_session(path, fixture, foreman.name)

    print("AGENTS_LEFT", foreman.agents_left())
    foreman.restore()
    if state in ("idle", "done"):
        foreman.close()
        print("CLOSED", foreman.pane)


if __name__ == "__main__":
    main()
