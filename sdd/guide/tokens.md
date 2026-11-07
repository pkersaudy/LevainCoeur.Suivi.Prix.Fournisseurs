# Tokens: what agents spend

`sdd/bin/ledger` keeps what agents spent on each module, by month, in the git notes `sdd-ledger`: the cost of the
product's features, with no commit, author or date. The hooks `install-hook` writes note it at each commit and share it
at each push, unless the dev sets `git config sdd.ledger false` (`--global` for every repo). The tokens come from
`sdd/bin/cockpit`, which reads the agents' logs on this machine, Claude Code's and opencode's.
`bash sdd/bin/cockpit report "$PWD"`, from any folder of the repo, shows a dev where their own tokens went;
`bash sdd/bin/cockpit hints` says what to cut, or which module's quizzes the dev flagged, once in 10 batches at most.
To audit a clone, `git fetch origin refs/notes/sdd-ledger:refs/notes/sdd-ledger`, then `bash sdd/bin/ledger report`:
the tokens by month, module, role and model, then per month the batches noted against the agent commits.
