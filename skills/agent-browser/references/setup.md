# Agent browser setup

Every client runs the same launcher. `LAUNCHER` below is the launcher's
absolute path through the installed skill link, for example
`$HOME/.agents/skills/agent-browser/scripts/agent-browser-mcp` with `$HOME`
written out. Claude Code, Codex, and OpenCode pass `command` to the operating
system without a shell, so write the path expanded, not with `~` or `$HOME`.

## Machine settings

The launcher reads an optional file,
`${XDG_CONFIG_HOME:-~/.config}/agent-browser/config` (or the path in
`AGENT_BROWSER_CONFIG`). It is parsed as `KEY=VALUE` lines, never sourced, and
a leading `~` in a value expands to the home directory. MCP clients do not
start servers from the user's shell, so this file, not a shell profile, is
where settings reach the launcher.

| Key | Default | Meaning |
| --- | --- | --- |
| `AGENT_BROWSER_PACKAGE` | `@playwright/mcp@latest` | npm package spec. Pin an exact version so every client runs the same one. |
| `AGENT_BROWSER_EXECUTABLE` | empty | Chromium-family browser binary to launch instead of a Playwright channel. |
| `AGENT_BROWSER_CHANNEL` | empty (Playwright's `chrome`) | Playwright `--browser` value when no executable is set, for example `chromium`, which needs `npx playwright install chromium`. |
| `AGENT_BROWSER_PROFILE` | macOS `~/Library/Application Support/agent-browser/profiles/ai-agent`; elsewhere `${XDG_DATA_HOME:-~/.local/share}/agent-browser/profiles/ai-agent` | Persistent profile used by `playwright-auth`. |
| `AGENT_BROWSER_OUTPUT` | macOS `~/Library/Caches/agent-browser`; elsewhere `${XDG_CACHE_HOME:-~/.cache}/agent-browser` | Snapshots and screenshots, in `playwright/` and `playwright-auth/` subdirectories. |

The profile must be a directory of its own, never a profile inside the user's
personal browser data: browsers lock the whole data directory, and the agent
must not reach the user's own sessions. The launcher creates the profile and
output directories with owner-only permissions.

`agent-browser-mcp --print-config` prints the resolved values.

## Client entries

Back up each file first and keep every unrelated entry.

Claude Code, user scope:

```sh
claude mcp add -s user playwright -- LAUNCHER
claude mcp add -s user playwright-auth -- LAUNCHER auth
claude mcp add -s user safari-mcp -- /usr/bin/safaridriver --mcp
```

Codex, `${CODEX_HOME:-~/.codex}/config.toml`:

```toml
[mcp_servers.playwright]
command = "LAUNCHER"
startup_timeout_sec = 30

[mcp_servers.playwright-auth]
command = "LAUNCHER"
args = ["auth"]
startup_timeout_sec = 30

[mcp_servers.safari-mcp]
command = "/usr/bin/safaridriver"
args = ["--mcp"]
```

OpenCode 2.x, `~/.config/opencode/opencode.jsonc`, merged into any existing
`mcp` object:

```jsonc
"mcp": {
  "servers": {
    "playwright": { "type": "local", "command": ["LAUNCHER"], "timeout": { "startup": 30000 } },
    "playwright-auth": { "type": "local", "command": ["LAUNCHER", "auth"], "timeout": { "startup": 30000 } },
    "safari-mcp": { "type": "local", "command": ["/usr/bin/safaridriver", "--mcp"] }
  }
}
```

Pi, `${PI_CODING_AGENT_DIR:-~/.pi/agent}/mcp.json`:

```json
{
  "mcpServers": {
    "playwright": { "command": "LAUNCHER" },
    "playwright-auth": { "command": "LAUNCHER", "args": ["auth"] },
    "safari-mcp": { "command": "/usr/bin/safaridriver", "args": ["--mcp"] }
  }
}
```

## Verify the clients

- Claude Code: `claude mcp list` connects each server and prints its state.
- Codex: `codex mcp list` shows declared servers without connecting. A
  non-interactive `codex exec` refuses MCP calls unless approvals are
  routed, for example with `--approve-for-me`.
- OpenCode: `opencode mcp list` may print "No MCP servers configured" even
  when servers load; `opencode debug config` shows the parsed entries, and
  the log records `mcp connected` with a tool count when a session starts.
- Pi: `pi mcp list` connects each server and lists its tools. Pi exposes MCP
  tools through code mode by default.

Then run `scripts/check`.

## First login

1. Ask the agent to open the site with `playwright-auth`. A browser window
   opens on the agent profile.
2. The user signs in, including any 2FA, in that window.
3. Later `playwright-auth` sessions reuse the stored login until the site
   expires it.
