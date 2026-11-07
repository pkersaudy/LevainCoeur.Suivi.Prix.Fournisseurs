"""What waits for the dev before a batch, and the step left in one. It names authors to coordinate, never to measure,
and never fetches."""
import itertools
import os
import re
import time
from collections import Counter

from fabrik import quiz
from fabrik.checks import check, quiz_form
from fabrik.contracts import governs
from fabrik.git import commit_or, empty_tree, exists, git, lines, me, try_git
from fabrik.journal import committed

# A pushed branch waits for a review once its last commit is this old.
REVIEW_WAIT_HOURS = 4


def brief(module):
    """Before a batch, in a module if given."""
    address = me(strict=True)
    for line in itertools.islice(waiting(address), 3):
        print(line)
    if module:
        for line in newcomer(address, module):
            print(line)


def waiting(address):
    """A quiz in another worktree of the clone, then the remote branches not merged by another dev, oldest first."""
    top = git("rev-parse", "--show-toplevel")
    for line in lines(git("worktree", "list", "--porcelain")):
        path = line[len("worktree "):]
        if line.startswith("worktree ") and os.path.isfile(f"{path}/QUIZ.md") and not os.path.samefile(path, top):
            yield f"A quiz waits for your answers in {path}."
    if try_git("rev-parse", "-q", "--verify", "refs/remotes/origin/HEAD") is None:
        return
    refs = git("for-each-ref", "--no-merged=origin/HEAD", "--sort=committerdate", "--format=%(refname)",
               "refs/remotes/origin")
    for ref in lines(refs):
        when, email, name = git("log", "-1", "--format=%ct%x09%aE%x09%aN", ref).split("\t", 2)
        hours = (int(time.time()) - int(when)) // 3600
        if hours >= REVIEW_WAIT_HOURS and email.lower() != address.lower():
            age = f"{hours} hours" if hours < 48 else f"{hours // 24} days"
            yield f"{ref[len('refs/remotes/'):]} waits for a review for {age}, see {name}."


def newcomer(address, module):
    """When it is the dev's first batch in a module, says so and who delivered there most, by name, to know whom to
    ask. Says nothing in a module the dev knows, or one not committed yet."""
    contract = f"sdd/modules/{module}.md"
    if not exists(f"HEAD:{contract}"):
        return []
    authors = Counter()
    log = git("log", "--no-merges", "--format=%aE%x09%aN", "--", contract, *governs(f"HEAD:{contract}"))
    for email, name in (line.split("\t") for line in lines(log)):
        if email.lower() == address.lower():
            return []
        authors[name] += 1
    if not authors:
        return []
    most = sorted(authors.items(), key=lambda author: (-author[1], author[0].casefold()))[:3]
    return [f"First batch of yours in {module}.", f"Who delivered there most: {', '.join(name for name, _ in most)}."]


def next_step():
    """The step of COMPILE left for the batch, read from its state in git, then the untracked files, which never
    block."""
    committed()
    print(step_left())
    untracked = lines(git("ls-files", "--others", "--exclude-standard"))
    if untracked:
        print(f"Untracked, stage those of the batch: {', '.join(untracked)}.")


def step_left():
    unstaged = lines(git("diff", "--name-only"))
    if not unstaged and not git("diff", "--cached", "--name-only"):
        return "Nothing to propose: no tracked file changed."
    if unstaged:
        return f"step 5: stage the batch, these files changed and are not staged: {', '.join(unstaged)}."
    path = git("rev-parse", "--git-path", "sdd/message")
    last_commit = try_git("log", "-1", "--format=%ct")
    if not os.path.isfile(path) or (last_commit and os.path.getmtime(path) < int(last_commit)):
        return f"step 5: write the proposed message, with Agent-Assisted: yes, to {path}."
    with open(path, encoding="utf-8", errors="replace", newline="") as file:
        message = file.read()
    batch = check(commit_or("HEAD", empty_tree()), git("write-tree"), message)
    found = batch.errors + batch.findings
    if found:
        number = 3 if re.search(r"^DRIFT", found, re.M) else 5
        return f"step {number}: fix what the audit finds.\n{found.rstrip()}"
    bypass = re.search(r"^Bypass-Quiz:[^\S\n]*\S", message, re.M)
    if bypass or (batch.level == "low" and not os.path.isfile(quiz.QUIZ)):
        return f"step 7: hand off, then the human commits with git commit -F {path}."
    if not os.path.isfile(quiz.QUIZ):
        return "step 6: a fresh reviewer reads the staged diff, reports its findings, then writes QUIZ.md and its key."
    key = quiz.key_path()
    if os.path.isfile(key) and quiz.read_lines(key)[:1] != [quiz.staged()]:
        return ("step 6: the batch changed since the quiz: send the change to the same reviewer, which checks its quiz"
                " still holds and writes the new fingerprint in the key.")
    try:
        quiz_form(batch)
    except SystemExit as refused:
        return f"step 6: the reviewer fixes its quiz. {refused.code}"
    return f"step 7: hand off, then the human answers QUIZ.md and commits with git commit -F {path}."
