# Upgrade and uninstall (for agents)

## Upgrade

1. The first line of `sdd/README.md` gives the `<source>` and the deployed tag; without a URL there, the source is
   `https://github.com/GrIc/sdd-fabrik`. `git ls-remote --tags --refs <source>` gives the latest `vX.Y.Z`.
2. `git clone <source> <tmp>`; `git -C <tmp> diff <old> <new> -- template/ ':!template/sdd/bin/'` shows what changed
   besides the scripts, which you replace without reading. Then `git -C <tmp> checkout -q <new>`.
3. Coming from a version without `sdd/bin/fabrik/`, check first that the human has Python 3.10 or later
   (`python3 --version`, or `python`, or `py -3`); if not, tell them how to install it for their system, and stop.
   Replace `sdd/WORKFLOW.md`, `sdd/guide/` and `sdd/bin/` with the new tag's, deleting what it no longer has, such as
   `sdd/bin/cockpit.py`. Keep the project's changes to `NOT_CODE` (`sdd/bin/fabrik/size.py`), `AGENT_EMAILS`
   (`git.py`) and `REVIEW_WAIT_HOURS` (`brief.py`). `sdd/config.yml` is the project's and stays; coming from a version
   without it, copy the new tag's, and write a project's change to `MAX_LINES` in it as `batch-lines`. Replace the
   block between `<!-- sdd-fabrik -->` and `<!-- /sdd-fabrik -->` in `AGENTS.md`. Apply the other template changes the
   diff shows with the human. A CI change goes only to the repo's forge: `.github/workflows/sdd.yml` on GitHub, the
   `sdd-audit` job of `.gitlab-ci.yml` on GitLab. A GitLab repo without that job gets it as the deploy adds it, and
   loses `.github/workflows/sdd.yml`, which GitLab never runs. Put the new tag on the first line of `sdd/README.md`.
   Delete `<tmp>`, then run `bash sdd/bin/sdd install-hook`: a new version may add a hook.
4. Tell the human what changed and propose a commit message without `Agent-Assisted` or an agent's `Co-Authored-By`:
   the files come from the kit.

## Uninstall

Remove `sdd/bin/`, `sdd/guide/`, `sdd/WORKFLOW.md`, `sdd/config.yml`, the `commit-msg`, `post-commit` and `pre-push`
hooks that hold `# sdd-fabrik` (or the `sdd/bin/` lines added to other hooks), the `sdd/bin/*` line of
`.gitattributes`, the `/QUIZ.md` line of `.git/info/exclude`, the folders `$(git rev-parse --git-common-dir)/sdd/` and,
in each worktree, `$(git rev-parse --git-path sdd)` (what the harness keeps on this machine, the quiz journal among
it), the refs `refs/notes/sdd-ledger` and `refs/notes/sdd-ledger-remote` (and on the remote, with the human), the
block between the markers in `AGENTS.md`, the `@AGENTS.md` line of `CLAUDE.md`, the `.github/workflows/sdd.yml` step
or the `sdd-audit` job of `.gitlab-ci.yml`, and the deny rules added to your tool.
Ask the human before removing the project's own knowledge: `sdd/README.md`, `coding-style.md`, `modules/`,
`decisions.md` and the other topic files.
