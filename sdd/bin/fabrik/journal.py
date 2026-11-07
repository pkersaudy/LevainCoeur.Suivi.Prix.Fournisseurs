"""The quiz journal: the questions a dev flagged or commented, kept on this machine and shared by the clone's
worktrees. A line is v2, the time, the batch's modules, the causes, the title and the words, tab-separated; the
cockpit reads it."""
import os
import re
import time
from collections import Counter

from fabrik.drift import touched
from fabrik.git import commit_or, git, shared_path
from fabrik.quiz import QUIZ, fingerprint, key_path, read_lines

CAUSES = ["not-understood", "unclear", "not-wanted"]


def committed():
    """After a commit: its quiz, once the commit exists, goes to the journal if it passed, then away. A later
    commit-msg hook that fails keeps the quiz, and a commit made with --no-verify leaves none behind for the next batch.
    The post-commit hook runs it; the next commit, audit and fingerprint do too, for a clone whose hooks predate it."""
    key = key_path()
    if not (os.path.isfile(QUIZ) and os.path.isfile(key) and commit_or("HEAD", None)):
        return
    tree = git("rev-parse", "HEAD^{tree}")
    # An amend builds on what HEAD was before it, not on HEAD^.
    if read_lines(key)[:1] not in ([fingerprint(tree, commit_or("HEAD^", "none"))],
                                   [fingerprint(tree, commit_or("HEAD@{1}", "none"))]):
        return
    if any(line.startswith("Quiz:") for line in git("log", "-1", "--format=%B").split("\n")):
        write(",".join(module for module, _ in touched("HEAD")))
    os.remove(QUIZ)
    os.remove(key)


def write(modules):
    """Appends a line per question of QUIZ.md the dev flagged or commented. It runs once the commit of a passed quiz
    exists, when the boxes are the dev's last word. The block's boxes are read by their place, so in any language."""
    rows, title, causes, words, box = [], "", [], "", 0

    def close():
        if causes or words:
            fields = ["v2", str(int(time.time())), modules or "-", ",".join(causes) or "-", title, words or "-"]
            rows.append("\t".join(field.replace("\t", " ") for field in fields) + "\n")

    for line in read_lines(QUIZ):
        if line.startswith("## "):
            close()
            title, causes, words, box = re.sub(r"^## ([0-9]+\. )?", "", line), [], "", 0
        elif re.match(r"> - \[[ xX]\]", line):
            box += 1
            if re.match(r"> - \[[xX]\]", line) and box <= len(CAUSES):
                causes.append(CAUSES[box - 1])
        elif re.match(r"> - [^[]", line):
            # The words follow the label and its ":"; a label without one leaves no words.
            label = re.match(r"> - [^:]*:\s*", line)
            words = line[label.end():] if label else ""
    close()
    os.makedirs(os.path.dirname(path()), exist_ok=True)
    with open(path(), "a", encoding="utf-8", newline="") as file:
        file.writelines(rows)


def path():
    return shared_path("quiz-journal")


def flagged(start):
    """Per module, the quiz answers flagged unclear or not wanted since start, once per title and cause: a commit that
    fails after the quiz passed journals it again."""
    flags = set()
    if os.path.exists(path()):
        with open(path(), encoding="utf-8", errors="replace") as file:
            for line in file:
                fields = line.rstrip("\n").split("\t")
                if fields[0] == "v2" and int(fields[1]) > start:
                    flags.update((module, fields[4], cause) for module in fields[2].split(",") if module != "-"
                                 for cause in fields[3].split(",") if cause in ("unclear", "not-wanted"))
    return Counter(module for module, _, _ in flags)
