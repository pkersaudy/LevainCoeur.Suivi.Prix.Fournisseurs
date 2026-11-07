"""The checks of a change, as the hook, audit and CI run them, and the guidance audit adds."""
import os
import sys
from types import SimpleNamespace

from fabrik import quiz
from fabrik.contracts import RISKS, governs, highest, matches, risk, sensitive
from fabrik.drift import drift
from fabrik.git import commit_or, empty_tree, exists, git, is_agent, lines, try_git
from fabrik.journal import committed
from fabrik.size import PROSE_OR_GIT, size


def audit_staged(message_file=None):
    """The staged batch. Without a message file, it is judged as an agent's with no trailers."""
    message = "Agent-Assisted: yes"
    if message_file:
        with open(message_file, encoding="utf-8", errors="replace", newline="") as file:
            message = file.read()
    committed()
    batch = check(commit_or("HEAD", empty_tree()), git("write-tree"), message)
    status = 0 if report(batch, message) else 1
    if batch.high:
        print(f"NOTE {', '.join(batch.high)}: high risk, the quiz cites every hunk of code and a second human's reading"
              " is recommended.", file=sys.stderr)
    # The reviewer checks its quiz here, so that a malformed one never reaches the human.
    if os.path.isfile(quiz.QUIZ):
        try:
            quiz_form(batch)
            if len(batch.ranks) > 1 and batch.ranks == batch.ranks[0] * len(batch.ranks):
                print(f"NOTE QUIZ.md: the right answer is box {batch.ranks[0]} every time, vary it.", file=sys.stderr)
        except SystemExit as refused:
            if isinstance(refused.code, str):
                print(refused.code, file=sys.stderr)
            status = 1
    if status == 0:
        print("OK: the staged batch passes the checks.")
    guidance()
    return status


def audit_range(span):
    """CI: each commit of base..tip, with its own message."""
    base, _, tip = span.partition("..")
    # A base git does not know (a new branch, a force-push) audits the tip only.
    if exists(f"{base}^{{commit}}"):
        commits = lines(git("rev-list", "--reverse", "--no-merges", span))
    else:
        commits = [git("rev-parse", tip)]
    status = 0
    for commit in commits:
        # Commits from before the harness was adopted are not its business.
        if not exists(f"{commit}:sdd/bin/sdd"):
            continue
        message = git("log", "-1", "--format=%B", commit)
        if report(check(commit_or(f"{commit}^", empty_tree()), commit, message), message):
            print("OK   " + git("log", "-1", "--format=%h %s", commit))
        else:
            print("FAIL " + git("log", "-1", "--format=%h %s", commit))
            status = 1
    return status


def check(base, tree, message):
    """Checks the change from base to tree (commits or trees) under a commit message. Returns the batch: its changed
    files, hit, high, level (low, normal or high), errors (fatal for everyone), findings (fatal for agents only) and
    notes."""
    batch = SimpleNamespace(changed=lines(git("diff", "--name-only", "--no-renames", base, tree)), errors="",
                            findings="", notes="", hit=[], risks={}, coded=[], governed=set(), linked=set(), touched=0)
    drift(batch, base, tree, message)
    size(batch, base, tree, message)
    # A file that steers the project or the harness asks a quiz at any risk; the base's list too, so that the batch
    # emptying the list is judged by it.
    listed = sensitive(tree, True) + sensitive(base, False)
    flagged = [path for path in batch.changed if any(matches(entry, path) for entry in listed)]
    # Tests a contract links to, alone or with prose the human reads, ask one step less: they prove the intent and leave
    # what the product does as it was.
    step = 1 if batch.linked.intersection(batch.changed) and all(
        path in batch.linked or (PROSE_OR_GIT.search(path) and path not in batch.governed and path not in flagged)
        for path in batch.changed) else 0
    judged = {name: lower(found, step) for name, found in batch.risks.items()}
    risks = list(judged.values())
    # Code outside every module takes the repo's risk. Markdown and git's own files there ask no quiz: the human reads
    # their diff.
    if any(path not in batch.governed and not PROSE_OR_GIT.search(path) for path in batch.changed):
        risks += [lower(risk(tree, None, True), step), lower(risk(base, None, False), step)]
    level = highest(risks or ["low"])
    # At intent, only a contract that moves asks a quiz. A boundary moves with one: governs and depends are in it, and
    # code of a second module that no Spec-Unchanged spares is drift until its contract changes too.
    if level == "intent":
        moved = any(judged[name] == "intent" and f"sdd/modules/{name}.md" in batch.changed for name in batch.hit)
        level = "normal" if moved else "low"
    if flagged:
        level = highest([level, "normal"])
    batch.level = {"low": "low", "high": "high"}.get(level, "normal")
    batch.high = [name for name in batch.hit if batch.risks[name] == "high"] if batch.level == "high" else []
    return batch


def lower(found, step):
    return RISKS[max(RISKS.index(found) - step, 0)]


def quiz_form(batch):
    """The quiz as audit wants it: its form, and at high risk See lines that cite every hunk of code."""
    quiz.form(batch)
    covered, total, missed = batch.coverage
    if batch.level == "high" and covered != total:
        sys.exit(f"QUIZ.md cites {covered} of {total} hunks of code; at high risk, its See lines cite them all."
                 f" Missed: {', '.join(missed)}.")


def report(batch, message):
    """Prints what the checks found, and whether the commit may go on."""
    sys.stderr.write(batch.notes)
    if batch.errors:
        sys.stderr.write(batch.errors + batch.findings)
        return False
    if not batch.findings:
        return True
    if is_agent(message):
        sys.stderr.write("Refused, agent-assisted batch:\n" + batch.findings)
        return False
    sys.stderr.write("Warnings only, this is your own commit:\n" + batch.findings)
    return True


def guidance():
    """Guidance for the agent, never a refusal: governs paths that match nothing, and the project's markdown against the
    code it governs (WORKFLOW.md and guide/ are the kit's)."""
    paths = []
    for contract in lines(git("ls-files", "sdd/modules/*.md")):
        for path in governs(f":{contract}"):
            paths.append(path)
            if not git("ls-files", "--", path):
                print(f"NOTE {contract}: {path} matches no tracked file, a typo or code still to come.")
    markdown = nonblank("sdd/*.md", "AGENTS.md", ":!sdd/WORKFLOW.md", ":!sdd/guide/")
    if not paths:
        print(f"NOTE {markdown} lines of markdown, no contract yet.")
        return
    code = nonblank(*paths, ":!*.md")
    print(f"NOTE {markdown} lines of markdown for {code} lines of governed code, ratio"
          f" {markdown / code if code else 0:.2f} (guideline: at most 1).")


def nonblank(*paths):
    """The lines that are not blank in the tracked text files of these pathspecs."""
    counts = try_git("grep", "-I", "-h", "-c", "-v", "-e", "^[[:space:]]*$", "--", *paths) or ""
    return sum(int(count) for count in lines(counts))
