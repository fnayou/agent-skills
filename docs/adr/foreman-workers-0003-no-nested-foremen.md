# No nested foremen

A worker never starts workers of its own: one foreman supervises a flat set of workers. Nesting was tested once, with a Claude Code worker running its own pi worker, and every herdr command of the sub-foreman still came up for approval, so supervision was done twice and authority had to be reasoned about at two levels.

## Considered Options

- **Keep nesting** for large work. Rejected: the decomposition it offered is obtained without it. A paid worker on a goal brief investigates and writes the runbook, the foreman reviews it, and a pi worker executes it.

## Consequences

- For several large tasks at once, the foreman supervises every worker itself, planners and executors alike.
- Very large workflows may justify nesting later; this decision would then be revisited.
