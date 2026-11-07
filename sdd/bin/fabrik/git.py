"""git calls, and what git tells about who made a commit."""
import os
import re
import subprocess
import sys

# Co-author addresses that mark an agent batch, as a regex that git's -E reads too. Names are not enough: Claude is
# also a first name. Any agent can mark its batch with Agent-Assisted: yes.
AGENT_EMAILS = r"noreply@anthropic\.com|noreply@openai\.com|aider@aider\.chat"

AGENT = re.compile(rf"^(Agent-Assisted:[^\S\n]*yes[^\S\n]*$|Co-Authored-By:.*<({AGENT_EMAILS})>)", re.I | re.M)


def git(*args, **options):
    """Its output, or the exit with git's status when it fails."""
    result = run(args, **options)
    if result.returncode:
        sys.exit(result.returncode)
    return result.stdout.decode(errors="replace").rstrip("\n")


def try_git(*args, **options):
    """Its output, or None when it fails, without its error."""
    result = run(args, quiet=True, **options)
    return None if result.returncode else result.stdout.decode(errors="replace").rstrip("\n")


def run(args, cwd=None, env=None, input=None, quiet=False):
    # Paths with accents print as they are, not as quoted octal escapes.
    return subprocess.run(["git", "-c", "core.quotePath=false", *args], cwd=cwd, env=env and {**os.environ, **env},
                          input=None if input is None else input.encode(), stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL if quiet else None)


def lines(text):
    return text.split("\n") if text else []


def exists(revision):
    return try_git("cat-file", "-e", revision) is not None


def commit_or(revision, fallback):
    return try_git("rev-parse", "-q", "--verify", revision) or fallback


def empty_tree():
    return git("hash-object", "-t", "tree", "--stdin", input="")


def shared_path(name):
    """A file of the harness on this machine, shared by the clone's worktrees."""
    return os.path.join(git("rev-parse", "--git-common-dir"), "sdd", name)


def is_agent(message):
    return bool(AGENT.search(message))


def agent_log(*args, cwd=None, env=None):
    """git log of the agent commits, marked as the hook marks them; none before the first commit."""
    if try_git("rev-parse", "-q", "--verify", "HEAD", cwd=cwd) is None:
        return ""
    return git("log", "--no-merges", "-i", "-E", "--grep=^Agent-Assisted:[[:space:]]*yes[[:space:]]*$",
               f"--grep=^Co-Authored-By:.*<({AGENT_EMAILS})>", *args, cwd=cwd, env=env)


def me(cwd=None, strict=False):
    """The address git would commit with, through the mailmap as %aE is; None without one, or git's exit if strict."""
    ident = git("var", "GIT_AUTHOR_IDENT", cwd=cwd) if strict else try_git("var", "GIT_AUTHOR_IDENT", cwd=cwd)
    if ident is None:
        return None
    mapped = git("check-mailmap", ident[: ident.index(">") + 1], cwd=cwd)
    return re.sub(r".*<(.*)>", r"\1", mapped)
