# SDD-Fabrik workflow

How a change is made in this repo. This file and `guide/` belong to [SDD-Fabrik](https://github.com/GrIc/sdd-fabrik)
and are replaced on upgrade: project rules go in [coding-style.md](coding-style.md) or in `AGENTS.md` outside the kit
block.

Read a guide only when its case comes:

- a new project, or existing code to adopt, as the first batch: [guide/start.md](guide/start.md);
- work of several batches: [guide/plan.md](guide/plan.md);
- what agents spend, by module and for each dev: [guide/tokens.md](guide/tokens.md);
- upgrading or removing the kit: [guide/upgrade.md](guide/upgrade.md).

## Where things live

A file is created when first needed.

| Topic | Home |
|---|---|
| The project's map: system, modules | `sdd/README.md` |
| Why, for whom, success, non-goals | `sdd/product.md` |
| Look, accessibility, voice | `sdd/design.md` |
| Code, tests, docs and commit conventions, project commands | `sdd/coding-style.md` |
| The repo's settings: batch size, risk | `sdd/config.yml`, shipped with the defaults as comments |
| System design, data, deployment | `sdd/architecture.md` |
| Decisions, with what was rejected | `sdd/decisions.md` |
| Order of the work, someday | `sdd/roadmap.md`: one line and link per change, and nowhere else |
| A piece of work in several batches | `sdd/changes/<slug>.md`, deleted once delivered |
| What a module must do, its acceptance | `sdd/modules/<module>.md`, linked to the tests that prove it |
| Bugs and ideas caught in passing | `sdd/issues/<slug>.md` |
| Implementation facts | code and tests |

## COMPILE: one batch

1. Read the intent, the contract, its tests and the code. Ask the open intent questions. When behavior depends on real
   input, measure it with a throwaway script first, and stop at the approach that covers 95 to 98% of real cases.
   Run `bash sdd/bin/sdd brief <module>`. When it shows what waits, a quiz in another worktree or a branch waiting for
   a review, propose to finish that before producing more. When it says this is the dev's first batch there, offer a
   discovery mode and apply it only on a yes: sum up the contract and its decisions, ask the dev how they would go
   about it, keep the batch small, tell the reviewer so that its quiz asks why rather than which line, and suggest
   pairing with one of the devs it names.
2. Build the smallest coherent change, with the tests it deserves ([coding style](coding-style.md#tests)). Run the
   project's checks. Never cut a user text, a test or a name to fit the size limit: split the batch, or ask the human
   for `Large-Batch`.
3. Update the contract if the intent changed. An intent that goes against `sdd/decisions.md`, even at the human's
   request, comes with a new decision that supersedes the old one. A batch from a plan moves its criteria into its
   module's contract, in place of what they restate, and deletes its section; a batch without a module drops them.
   Otherwise propose `Spec-Unchanged(<module>): <reason>`.
4. Read the whole diff against the coding style and delete what does not earn its place. From here,
   `bash sdd/bin/sdd next` says which step is left, from the state of the batch in git.
5. Stage the batch, write the proposed message with `Agent-Assisted: yes` to `.git/sdd/message`, and run
   `bash sdd/bin/sdd audit --message .git/sdd/message`.
6. Review: spawn a fresh reviewer, a new context that did not write the batch, and tell it the language the human writes
   to you in. It reads the staged diff, the contract and the coding style, and reports findings with their evidence. A
   finding that adds a check, an error path or a fallback names an input the code really receives and gets wrong;
   without one, you leave it out and list it in the handoff. Once you have fixed or listed the findings, it writes the
   quiz, then runs the audit of step 5 again, which checks the quiz. Give it a smaller model than the writer's unless
   the batch is large or touches security or data. After a fix, send the same reviewer the change: it checks that its
   quiz still holds for a fraction of a fresh one.
7. Hand off: purpose, the decisions you took alone, evidence, limits and a short "understand this" for the human, and at
   high risk the advice to have a second human read the diff. The human reads the diff, answers `QUIZ.md` and commits
   with `git commit -F .git/sdd/message`. Start the next batch in a fresh session: a long one reads its whole history
   again with every call. Then run `bash sdd/bin/cockpit hints`: it prints a line only when this dev's costs show
   something new to cut, or their quiz answers in a module were flagged twice. Put each to the human as a question,
   with the change you would make (turn off a plugin or an MCP server, fold an output, write a rule in the contract, the
   coding style or the quiz instructions), and make it only on a yes, in a batch of its own.

Wherever a fresh reviewer is asked for (plan, batch, module), a tool that cannot spawn one does its part itself and
says so; one that cannot pick a model or resume a sub-agent skips that.

## Quiz

A quiz has one to three questions, as many as what the batch changes calls for. A batch is judged at the highest risk
of the modules it changes, in the parent or in the batch; code outside every module takes the repo's. At `low` it
needs no quiz; at `intent`, only when it adds, deletes or changes the contract of a module at `intent`, which also
holds its `governs` and `depends`. A batch that changes or deletes a sensitive file (see Contracts), in the parent's
list or its own, asks one to three questions even at `low` or `intent`. A batch whose changed files are all Markdown,
`.gitignore`, `.gitattributes` or `.gitkeep` that no contract is, no module governs and no `sensitive` list matches
needs none either (one written is still graded). A batch of tests alone is judged one step lower (`high` gives
`normal`, `normal` gives `intent`, `intent` gives `low`): it changes files a contract links to, and beside them only
Markdown and those git files that no module governs and no `sensitive` list matches. A batch that changes or deletes
a module at `risk: high` (an API contract, security, personal data, money) has three or more, and its `See` lines cite
every hunk of code: `audit` fails until they do, the hook never checks it. The handoff then recommends a second
human's reading; nothing requires one, so a dev alone uses the whole harness.

`bash sdd/bin/sdd fingerprint` prints the batch fingerprint and the two paths to write. The reviewer writes:

- `QUIZ.md` at the repo root (kept out of git): questions that make the human predict, not recognize. Ask what this
  code does, never the technology: from what it does to how, then why. What does this return for that input, which
  line enforces this rule, what breaks if this line goes, why this option over that one. Each question has a `See`
  line citing one to three places of the batch, `file:line` or `file:line-line`, separated by `, `, and 2 to 4 boxes;
  the right box changes place. Everything the human reads is in their language: the title and the line under it,
  questions, boxes, hints; the marks `## `, `See` and `- [ ]` stay as shown.

  ```markdown
  # Quiz for this batch

  Tick one box per question, save, then commit.

  ## 1. What does parse_duration return for "2 hours 30"?

  See src/durations.py:14

  - [ ] 150 minutes
  - [ ] 2 hours
  - [ ] an error
  ```

- the key, at the printed path: the fingerprint, then one line per question with the right letter (A for the first
  box) and a hint for a wrong answer: where to look, never which box. No question asks for a computation nobody does
  when reading code. For a human who does not write in English, eight more lines word the block the hook writes under
  a wrong answer: wrong, hint, the call to type *quiz feedback*, the question why, the three reasons (code not
  understood, question unclear, code not what they wanted) in that order, and other, ending with `:`.

  ```
  3f2a9c...
  A "30" after hours counts as minutes.
  ```

The commit fails until every answer is right. Under each wrong question, the hook writes a quoted block in
`QUIZ.md`, once: the hint, a call to type *quiz feedback*, and optional boxes for the dev to say why (not understood,
question unclear, the code does not do what they wanted). The boxes never change the grade. If the batch changed
since the quiz was written, the hook only warns: ask for a new quiz when the changes touch what it asks. A human with
a reason to skip the quiz writes `Bypass-Quiz: <reason>` in the message; the history keeps it.

The trailer says how much of the batch the quiz covers: `Quiz: 3/3, covers 5/7` counts the hunks of
`git diff --cached -U0` outside Markdown, those git files and lock files that a `See` range meets. A new file is one
hunk; a hunk that only deletes is met at the line before it or the one after, so a deleted file at its line 1. Without
a hunk of code, the trailer is `Quiz: 3/3`. It is a fact about the code, never about the dev.

Once the commit of a passed quiz exists, each question the dev flagged or commented goes to
`$(git rev-parse --git-common-dir)/sdd/quiz-journal`, on this machine only and shared by the clone's worktrees: one
tab-separated line, `v2`, the time in epoch seconds, the batch's modules (joined by `,`, or `-`), the boxes ticked
(`not-understood`, `unclear`, `not-wanted`, joined by `,`, or `-`), the question's title and the dev's own words (or
`-`). The cockpit reads it.

## Contracts

```markdown
---
governs: [src/search.py, src/templates/search/, tests/test_search.py]
depends: [tags]
risk: high
---
# search

Intent, constraints and non-goals, then the criteria.

- A misspelled term of 4 letters or more is corrected to the closest name:
  [test_corrects_a_misspelled_term](../../tests/test_search.py).
```

Govern the code that carries the intent: leave CI, dependency and build files out unless the module is about them.
At most 50 lines. Intent, never facts that a refactor keeping the behavior would change (SQL shapes, file layouts,
JSON formats). A criterion is a plain sentence, then links to the tests that prove it: a test name, a group, or the
whole file with its name or path as the link text, relative to the contract or from the repo root. Several criteria
may share a test; a criterion without a link is checked by hand, as its sentence says. No checkboxes, no status.
`depends` names the modules this one builds on; check their tests pass before you do. `risk` is `low` (no quiz on
code), `intent` (a quiz only when the contract moves, with its `governs` and `depends`), `normal` (the default) or
`high`, for a module where a mistake costs much (an API contract, security, personal data, money): a stricter quiz.
`sdd/config.yml` sets the repo's `risk` and `batch-lines` (200 lines of code and tests by default), as flat
`key: value` lines with comments allowed; a contract's own `risk` wins, so `risk: normal` keeps its module at normal
risk in a repo at `risk: high`. A contract's `batch-lines` replaces the repo's for a batch that changes its module's
code, higher or lower. A batch that changes a `batch-lines` is judged on its new value, with a note for the human, and
SIZE says where the limit is set. `sensitive` lists the files that steer the project or the harness, which ask a quiz
at any risk: one entry on the key's line or one per `- ` line below it, never split, as a path from the repo root, a
folder ending with `/`, or a regular expression between slashes, found anywhere in the path. Unset in
`sdd/config.yml`, it is the kit's list, shown there; set, it replaces it, and `sensitive: []` lists none. A contract's
list adds to the repo's, for any file of a batch. A contract states a setting only where it differs from the repo's.

## Decisions

`sdd/decisions.md`, numbered. Each entry gives the choice, its evidence, and a `Rejected:` line with the alternatives
and why. Numbers never change and no entry is deleted: a superseded entry shrinks to `n. Superseded by m.`, and git
keeps its text.

## Commit trailers

| Trailer | Written by | Effect |
|---|---|---|
| `Agent-Assisted: yes` | the agent, in its proposed message | drift and size block, the quiz is required |
| `Spec-Unchanged(<module>): <reason>` | the author | spares that module from the drift check and the one-module limit |
| `Large-Batch: <reason>` | the human | lifts the size limits (`batch-lines` in `sdd/config.yml`, one module) |
| `Bypass-Quiz: <reason>` | the human, never the agent | the hook asks no quiz; drift and size still apply |
| `Quiz: 3/3, covers 5/7` | the hook | records the passed quiz, its questions and the hunks of code they cite |

A co-author address listed in `AGENT_EMAILS` (in `sdd/bin/fabrik/git.py`) counts as `Agent-Assisted: yes`; any other
commit is the human's own. The script prints ERROR when every commit must stop; DRIFT (code against its contract, or a
contract link to a missing test or file) and SIZE (more than 5% over `batch-lines`, or a second module), which refuse an
agent batch and only warn on the human's own; and NOTE, guidance that never refuses. CI replays drift and size on every
pushed commit, never the quiz. Everything here can be bypassed: it is there to help, not to lock.

The hook compares the batch with HEAD: to amend an agent batch that changes files, run `git reset --soft HEAD^` and
commit again. It checks nothing when it finishes a merge or a cherry-pick. Merge pull requests with a merge commit or
a rebase: a squash adds the batches up, so the size check fails on the default branch, or it drops their trailers.
