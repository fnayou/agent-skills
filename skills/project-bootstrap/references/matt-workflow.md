# Matt Pocock setup workflow

Discover the installed `setup-matt-pocock-skills` skill by inspecting local
skill directories and its actual metadata. Do not invent a skill name or its
output. First check whether existing `AGENTS.md` / `CLAUDE.md` and
`docs/agents/` files already provide complete, consistent setup. Reuse valid
existing setup. If setup is missing or incomplete and the skill is present,
it is user-invoked (`disable-model-invocation: true`) and cannot be invoked by
this skill. Ask the user to invoke it, then inspect and validate its actual
output. Preserve its choices and resolve conflicts with the user.

If missing, explain that the required workflow is unavailable and give the
user a way to install or provide it. Do not counterfeit its files. Continue
independent safe work, but do not declare full bootstrap success until the
required workflow is completed and validated.
