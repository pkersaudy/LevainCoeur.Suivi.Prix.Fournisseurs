# Start: the first batch

## GENESIS: a new project

Ask the human, one question at a time: the first useful slice, for whom, the non-goals, whose coding conventions to
follow, the qualities that matter here (accessibility, devices, performance, cost, carbon), then the settings of
`config.yml`: the batch size (200 lines of code and tests by default) and the risk (`low`, `intent`, `normal` or
`high`, as its comment says). Write only what the first slice needs: `README.md`, `coding-style.md` with its first
rules and commands, in `config.yml` the settings that differ from its defaults, one contract per module the slice
touches. Scaffold with the stack's
generator, then strip what the slice does not use. The first delivery follows [PLAN](plan.md) or COMPILE in [the
workflow](../WORKFLOW.md).

## ADOPT: existing code

Read the existing instructions, README, tests and entry points. Keep the behavior and the existing checks. Ask the
settings of `config.yml` as GENESIS does and write those that differ. Write the map, a coding style drawn from what the
code already does, and contracts only where the intent is not obvious from code and tests, with `governs` paths checked
by `git ls-files`. Changes you would like to make become issues, not contract text.
