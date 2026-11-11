# Security policy

## Reporting a vulnerability

Do not open a public issue for a security problem. Use GitHub's private
vulnerability reporting: open the **Security** tab of this repository and
choose **Report a vulnerability**.

Include what you found, how to reproduce it, and which files or scripts are
affected. You can expect an acknowledgement, and a fix or an explanation, as
soon as the maintainer can review it.

## Scope

This repository holds skill instructions, the helper scripts and tests that
ship inside skills, and two repository scripts, `scripts/install` and
`scripts/verify`. Reports about the installer (for example unsafe symlink
handling), about a skill's scripts, or about instructions that would lead an
agent to a destructive action are in scope. For `herdr-workers`, that includes
guidance that would let a foreman or a worker take an action the guard rails
reserve for the operator.

Only the latest commit on `main` is supported.
