"""The token ledger: what agents spent on each module, by month, with no link to a commit or a person.

The tokens come from `sdd/bin/cockpit usage`. With `git config sdd.ledger false`, nothing is noted. The keys are no
objects: `git notes --ref sdd-ledger prune` would delete the whole ledger."""
import os
import pathlib
import subprocess
import sys
import time
from collections import defaultdict

from fabrik.drift import touched
from fabrik.git import agent_log, git, lines, run, try_git

REF = "refs/notes/sdd-ledger"
# With / even on Windows, for the sh that runs the cockpit.
BIN = pathlib.Path(__file__).resolve().parent.parent.as_posix()


def record():
    """Notes the tokens spent since the last commit, split over the modules HEAD changes by their changed lines."""
    if try_git("config", "--bool", "sdd.ledger") == "false":
        return
    state = git("rev-parse", "--git-path", "sdd/ledger-until")
    until = git("log", "-1", "--format=%ct")
    # Each window starts where the last record ended: an amend counts nothing twice, a failure loses nothing.
    if os.path.isfile(state):
        with open(state, encoding="utf-8") as file:
            # Empty after a crash between its two writes: the window starts with the logs.
            since = file.read().strip() or "0"
    else:
        since = try_git("log", "-1", "--format=%ct", "HEAD^") or "0"
    os.makedirs(os.path.dirname(state), exist_ok=True)
    with open(state, "w", newline="") as file:
        file.write(since + "\n")
    # Through the command, which a test can stand in for.
    usage = subprocess.run(["sh", f"{BIN}/cockpit", "usage", git("rev-parse", "--show-toplevel"), since,
                            until], stdout=subprocess.PIPE)
    if usage.returncode:
        sys.exit(usage.returncode)
    with open(state, "w", newline="") as file:
        file.write(until + "\n")
    if not usage.stdout.strip():
        return
    # A batch that changes no module still costs: it goes to "-".
    shares = touched("HEAD") or [("-", 1)]
    weights = [weight for _, weight in shares]
    month = git("log", "-1", "--date=format-local:%Y-%m", "--format=%cd", env={"TZ": "UTC"})
    note = []
    for line in lines(usage.stdout.decode().rstrip("\n")):
        role, model, *counts = line.split("\t")
        rows = {module: [] for module, _ in shares}
        for count in counts:
            for (module, _), part in zip(shares, split(int(count), weights)):
                rows[module].append(str(part))
        for module, row in rows.items():
            note.append("\t".join(["v1", month, module, role, model] + row))
    note = "\n".join(note)
    # A random key: the note hangs on no commit.
    key = git("hash-object", "--stdin", input=f"{note}\n{os.urandom(16).hex()}\n")
    git("notes", "--ref", "sdd-ledger", "add", "-m", note, key, env=neutral(month))


def split(count, weights):
    """Splits count into whole parts in proportion to weights, summing to count: each part its floor, then one more to
    the largest remainders, the first on a tie. A lone call split over two modules still counts once."""
    total = sum(weights)
    parts = [count * weight // total for weight in weights]
    by_remainder = sorted(range(len(weights)), key=lambda i: -(count * weights[i] % total))
    for i in by_remainder[:count - sum(parts)]:
        parts[i] += 1
    return parts


def neutral(month):
    """A ledger commit names neither who wrote it nor when: a neutral author, dated the first of the month."""
    date = f"{month}-01T00:00:00Z"
    return {f"GIT_{who}_{what}": value for who in ("AUTHOR", "COMMITTER")
            for what, value in (("NAME", "sdd-fabrik"), ("EMAIL", "sdd-fabrik@localhost"), ("DATE", date))}


def sync(remote):
    """Merges the remote's ledger into ours, then pushes the merged notes as one commit with no parent: the shared
    history never shows whose notes came in which order. Runs before a push and never stops it. A dev with no ledger
    has nothing to send, so their push stays a single round trip."""
    if try_git("rev-parse", "-q", "--verify", REF) is None:
        return
    month, seen = time.strftime("%Y-%m", time.gmtime()), ""
    if try_git("fetch", "-q", remote, f"+{REF}:{REF}-remote") is not None:
        seen = git("rev-parse", f"{REF}-remote")
        # Two notes on one key keep their lines: the strategy never leaves a merge open for the next sync to trip on.
        if run(["notes", "--ref", "sdd-ledger", "merge", "-q", "-s", "cat_sort_uniq", f"{REF}-remote"],
               env=neutral(month)).returncode:
            print(f"NOTE the token ledger could not merge {remote}'s: the next push retries.", file=sys.stderr)
            return
    flat = git("commit-tree", "-m", "Token ledger", f"{REF}^{{tree}}", env=neutral(month))
    # The lease: a ledger another dev pushed since the fetch is merged at the next push, never overwritten.
    if run(["push", "-q", "--no-verify", f"--force-with-lease={REF}:{seen}", remote, f"{flat}:{REF}"]).returncode:
        print(f"NOTE the token ledger did not reach {remote}: the next push retries.", file=sys.stderr)


def report():
    """The ledger summed by month, module, role and model; then, per month, the batches noted against the agent
    commits, to show what it misses."""
    if try_git("rev-parse", "-q", "--verify", REF) is None:
        sys.exit(f"No token ledger here. Fetch it: git fetch origin {REF}:{REF}")
    sums, batches = defaultdict(lambda: [0] * 5), defaultdict(int)
    for note in notes():
        for month in {fields[1] for fields in note}:
            batches[month] += 1
        for fields in note:
            for i, count in enumerate(fields[5:10]):
                sums[tuple(fields[1:5])][i] += int(count)
    commits = defaultdict(int)
    for month in lines(agent_log("--date=format-local:%Y-%m", "--format=%cd", env={"TZ": "UTC"})):
        commits[month] += 1
    print("\t".join(["month", "module", "role", "model", "calls", "input", "output", "cache_read", "cache_write"]))
    for line in sorted("\t".join(list(key) + [str(count) for count in counts]) for key, counts in sums.items()):
        print(line)
    print()
    print("\t".join(["month", "batches", "agent_commits"]))
    for month in sorted(set(commits) | set(batches)):
        print(f"{month}\t{batches[month]}\t{commits[month]}")


def notes():
    """The ledger's notes, each as its v1 lines split into fields."""
    blobs = [line.split()[2] for line in lines(git("ls-tree", "-r", REF))]
    out = run(["cat-file", "--batch"], input="".join(blob + "\n" for blob in blobs)).stdout
    found = []
    while out:
        header, out = out.split(b"\n", 1)
        size = int(header.split()[2])
        text, out = out[:size].decode(errors="replace"), out[size + 1:]
        found.append([line.split("\t") for line in text.split("\n") if line.startswith("v1\t")])
    return found
