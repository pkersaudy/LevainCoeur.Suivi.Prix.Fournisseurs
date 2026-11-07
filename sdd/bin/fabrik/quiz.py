"""The quiz: its form, its grade, the block under a wrong answer, and how much of the batch it covers."""
import os
import re
import sys
from types import SimpleNamespace

from fabrik.git import commit_or, git, lines
from fabrik.size import NOT_CODE

QUIZ = "QUIZ.md"

# The block's words when the key does not give them in the dev's language.
WORDS = ["Wrong.", "Hint:", "Type *quiz feedback* to your agent to talk it through.",
         "Optional, why? (stays on this machine)", "I had not understood the code", "The question is unclear",
         "The code does not do what I wanted", "Other:"]


def grade(batch):
    """Checks the boxes ticked in QUIZ.md against the reviewer's key, and writes a block under each wrong answer."""
    if not os.path.isfile(QUIZ):
        sys.exit("No quiz for this agent-assisted batch: ask the fresh reviewer for QUIZ.md (see sdd/WORKFLOW.md).")
    form(batch)
    wrong = {}
    for question in batch.questions:
        if question.ticks != 1:
            sys.exit(f"Tick exactly one box for question {question.number} in QUIZ.md, save, then commit again.")
        if question.pick != question.right:
            wrong[question.number] = question.hint
            print(f"Question {question.number} is wrong: a hint is in QUIZ.md.", file=sys.stderr)
    if wrong:
        feedback(wrong, batch.count)
        sys.exit(f"{batch.count - len(wrong)}/{batch.count}. Fix your answers in QUIZ.md, save, then commit again.")


def form(batch):
    """The reviewer's part: QUIZ.md and its key fit the staged batch. Notes in batch its questions, the right letters in
    order (ranks) and its coverage. Needs batch.changed and batch.level, set by the checks."""
    key = key_path()
    if not os.path.isfile(key):
        sys.exit(f"QUIZ.md has no key: the reviewer writes it at {key} (see sdd/WORKFLOW.md).")
    if read_lines(key)[:1] != [staged()]:
        print("NOTE The batch changed since the quiz was written. If your changes touch what it asks, ask for a new"
              " one.", file=sys.stderr)
    batch.count = sum(line.startswith("## ") for line in read_lines(QUIZ))
    if batch.level == "high" and batch.count < 3:
        sys.exit('QUIZ.md needs 3 questions or more, each under a "## " heading.')
    if batch.level != "high" and not 1 <= batch.count <= 3:
        sys.exit('QUIZ.md needs 1 to 3 questions, each under a "## " heading.')
    batch.questions, batch.ranks, cites = questions(), "", []
    for question in batch.questions:
        places = question.see.split(", ")
        too_many = sum(1 for place in places if place) > 3
        for place in places:
            file, _, span = place.rpartition(":")
            if too_many or not re.fullmatch(r"[0-9]+(-[0-9]+)?", span) or file not in batch.changed:
                sys.exit(f"Question {question.number} needs a See line citing one to three places of this batch, as"
                         " 'See a.py:4, b.py:10-12'.")
            first, _, last = span.partition("-")
            cites.append((file, int(first), int(last or first)))
        if not 2 <= question.boxes <= 4:
            sys.exit(f"Question {question.number} needs 2 to 4 boxes.")
        if question.right == "-":
            sys.exit(f"Question {question.number} has no right box in the key: line {question.number + 1} starts with"
                     " its letter, A for the first box.")
        batch.ranks += question.right
    batch.coverage = cover(cites)


def key_path():
    return git("rev-parse", "--git-path", "sdd/quiz-key")


def read_lines(path):
    """A file's lines, without the CR a Windows editor adds."""
    with open(path, encoding="utf-8", errors="replace", newline="") as file:
        text = file.read().replace("\r", "")
    return text.split("\n")[:-1] if text.endswith("\n") else text.split("\n")


def staged():
    return fingerprint(git("write-tree"), commit_or("HEAD", "none"))


def fingerprint(tree, parent):
    """The batch a quiz is for: a tree on top of a commit, "none" for a first commit."""
    return git("hash-object", "--stdin", input=f"{tree} {parent}")


def questions():
    """Each question of QUIZ.md: its number, boxes, ticked boxes, the ticked letter, what its See cites, the key's
    letter for it (- when the key has none among the boxes) and the key's hint. The one reader of the key's answers."""
    key = read_lines(key_path())
    found = []
    for line in read_lines(QUIZ):
        if line.startswith("## "):
            found.append(SimpleNamespace(number=len(found) + 1, boxes=0, ticks=0, pick="-", see="-"))
        elif found and line.startswith("See "):
            found[-1].see = line[4:].lstrip(" ") or "-"
        elif found and re.match(r"- \[[ xX]\]", line):
            found[-1].boxes += 1
            if re.match(r"- \[[xX]\]", line):
                found[-1].ticks += 1
                # Past the fourth box, no letter: the form refuses it.
                found[-1].pick = "ABCD"[found[-1].boxes - 1: found[-1].boxes]
    for question in found:
        answer = key[question.number] if question.number < len(key) else ""
        right, _, hint = answer.partition(" ")
        question.right = right if len(right) == 1 and right in "ABCD"[: question.boxes] else "-"
        question.hint = hint.lstrip(" ").replace("\t", " ")
        question.see = question.see.replace("\t", " ")
    return found


def cover(cites):
    """How much of the staged code the cited places meet: covered hunks, all hunks, and the missed ones as file:line.
    cites holds (file, first, last). A hunk that only deletes is met at the line before it or the one after, so a
    deleted file at its line 1."""
    covered, total, missed = 0, 0, []
    # Plain a/ and b/ paths and one hunk per change, whatever the dev's diff settings.
    diff = git("diff", "--cached", "-U0", "--inter-hunk-context=0", "--no-renames", "--no-color", "--no-ext-diff",
               "--src-prefix=a/", "--dst-prefix=b/")
    head, code, path = False, False, ""
    for line in lines(diff):
        if line.startswith("diff --git "):
            head, code = True, False
        elif head and line.startswith("--- "):
            path = line[6:]
        elif head and line.startswith("+++ "):
            if line != "+++ /dev/null":
                path = line[6:]
            path = path.removesuffix("\t")
            code, head = not NOT_CODE.search(path), False
        elif code and line.startswith("@@ "):
            start, _, length = line.split(" ")[2][1:].partition(",")
            low = high = int(start)
            if length:
                high = low + int(length) - 1 if length != "0" else low + 1
            total += 1
            if any(file == path and first <= high and last >= low for file, first, last in cites):
                covered += 1
            else:
                missed.append(f"{path}:{low}")
    return covered, total, missed


def feedback(wrong, count):
    """Writes under each wrong question of QUIZ.md that has none yet a quoted block, which the parser skips: the key's
    hint, the call to type *quiz feedback*, and optional boxes for the dev to say why. A block already there stays as
    the dev left it. wrong maps a question's number to its hint. Its words are the eight lines the key may hold after
    its answers, in the dev's language."""
    key = read_lines(key_path())
    words = key[count + 1: count + 9] if len(key) >= count + 9 else WORDS
    parts = [[]]
    for line in read_lines(QUIZ):
        if line.startswith("## "):
            parts.append([])
        parts[-1].append(line)
    rows = []
    for number, part in enumerate(parts):
        if number not in wrong or any(line.startswith(">") for line in part):
            rows += part
            continue
        while part and part[-1] == "":
            part.pop()
        said = f"> {words[0]} {words[1]} {wrong[number]}" if wrong[number] else f"> {words[0]}"
        rows += part + ["", said, f"> {words[2]}", ">", f"> {words[3]}"]
        rows += [f"> - [ ] {word}" for word in words[4:7]] + [f"> - {words[7]}"]
        if number < len(parts) - 1:
            rows.append("")
    write_lines(QUIZ, rows)


def write_lines(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as file:
        file.writelines(row + "\n" for row in rows)
