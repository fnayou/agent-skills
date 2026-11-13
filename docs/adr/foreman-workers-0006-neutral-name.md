# The skill is named foreman-workers

The skill was named `herdr-workers` after the only multiplexer it drove. Since [0005](foreman-workers-0005-multiplexer-neutral-core.md) it drives herdr and Rex side by side, so the name now says **foreman** and **worker**, the two roles it defines, and no multiplexer. The rename was made on 2026-11-13, before any real run of Rex support was counted, so that the runs ending its preview use the final name and paths.

The rename moved, in one change: the skill directory, its `name`, the operator's configuration directory (`~/.config/herdr-workers/` to `~/.config/foreman-workers/`), the website page, and these ADRs' prefix. The description still names herdr and Rex, so an operator who asks for "herdr workers" or "Rex workers" still gets the skill.

## Considered Options

- **Keep `herdr-workers` while herdr is supported**, as 0005 planned. Rejected: Rex is used from now on beside herdr, and a name that names one of two multiplexers misleads.
- **`foreman`.** Rejected: shorter, but it names one side of the delegation only.

## Consequences

- An operator moves the configuration directory and the installed skill link once, by hand.
- The old website page stays as a short page that points to the new one, since external links to it may exist.
- The private archive of earlier runs keeps its name, `herdr-workers-archive`.
