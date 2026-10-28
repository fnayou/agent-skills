# Skills

## worktree-lanes

Treat each Git worktree as an operational lane. Before the first
repository-affecting action, the skill reads the repository's instructions and
produces a lane census that names:

- the current lane and the primary lane;
- the integration branch;
- other linked lanes and the state of the current tree;
- shared resources and who owns them;
- the repository's lane contract, or that none was found.

It also covers handing off a shared resource and closing a lane, with a rule
that work is preserved before anything is removed. The canonical vocabulary is
in the skill's
[terminology reference](https://github.com/fnayou/agent-skills/blob/main/skills/worktree-lanes/references/terminology.md).

## project-presentation

Gives a repository a coherent, reviewable visual identity. It has two
independent tracks.

- **Brand:** a Catppuccin Macchiato base with a per-project accent, canonical
  SVG artwork, a generator and a freshness check.
- **Documentation:** a Zensical site in `website/`, an offline site checker,
  and GitHub Pages deployment through GitHub Actions.

This site and its artwork are produced with the skill itself.

## agent-browser

Gives agents a browser that is never the user's own. The skill picks the
narrowest of three MCP servers:

- **`playwright`:** headless, with an in-memory profile that disappears when
  the browser closes. The default, and safe for many agents at once.
- **`playwright-auth`:** a visible browser on a persistent, agent-only
  profile, for sites the user signs in to. The user types credentials in the
  browser window, one agent uses it at a time, and the agent confirms before
  any irreversible action.
- **`safari-mcp`:** Safari's built-in MCP server, for Safari compatibility
  checks.

A single launcher holds the package pin and browser binary for every client.
A read-only check reports which clients declare each server and whether the
browser, profile, and output directories are ready. The
[setup reference](https://github.com/fnayou/agent-skills/blob/main/skills/agent-browser/references/setup.md)
covers Claude Code, Codex, OpenCode, and Pi.

### Signing in with playwright-auth

Use `playwright-auth` only for sites that need a login. The agent never types
the password or the code.

1. The agent opens the site. A browser window opens on the agent-only profile
   and shows the login page.
2. The agent stops and asks you to sign in. You enter your credentials in that
   window, including any 2FA code, passkey, or CAPTCHA.
3. You confirm, and the agent continues.

- **Persistence:** the login stays in the agent profile. Later sessions reuse
   it, even after the browser is fully quit, until the site expires it. The
   agent then asks you to sign in again.
- **Isolation:** `playwright` never carries a login. A site that needs one
  opens on its login page there.
- **One agent at a time:** the profile admits a single browser. A second
  `playwright-auth` client fails with `Browser is already in use`, and the
  read-only check reports `profile.lock`.
- **Private data:** snapshots and screenshots of a logged-in page hold your
  private data. The agent keeps replies to what the task needs and confirms
  before any irreversible action: submit, pay, delete, send, publish.
