# Taskfile and Docker

Every Create includes a functioning Taskfile v3. Keep small projects in one
file; split `.taskfiles/` modules only when real complexity warrants it. The
default lists tasks. `doctor` checks prerequisites without mutation and gives
actionable results. `setup` initializes only missing local configuration and
never overwrites it. Add `dev`, `run`, `build`, `test`, `lint`, `format`, or
`check` only when the known stack supports real commands.

Docker is opt-in. Without it, create no Docker files or tasks. With it, create
`.dockerignore` and `compose.example.yaml`; copy it to ignored `compose.yaml`
only when missing. Keep `.env.example` tracked where useful and copy it to
ignored `.env` only when missing. Ignore private variants and never overwrite
local files. Dependencies-only Compose needs no Dockerfile. Add a Dockerfile
only for a sufficiently defined containerizable app.

Use modern `docker compose` and project-scoped resources. Provide
`docker:build`, `docker:build-nocache`, `docker:start`, `docker:recreate`,
`docker:stop`, `docker:down`, `docker:logs`, `docker:ps`, and `docker:config`
only when their configuration makes them useful. Start uses `up --no-recreate`;
recreate reapplies configuration; down preserves volumes. Never auto-start or
remove volumes. `task doctor` checks Docker availability and validates Compose
quietly, without printing resolved environment values. Otherwise mark runtime
validation `not verified`. Do not claim untested Podman parity. The scaffold
script takes reviewed files through `--compose-example` and optional
`--env-example`; application images also require `--dockerfile`.
