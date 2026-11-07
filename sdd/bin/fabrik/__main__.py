"""The harness, run by the launchers sdd/bin/sdd, sdd/bin/ledger and sdd/bin/cockpit as `python fabrik <launcher> ...`.
See sdd/WORKFLOW.md."""
import os
import signal
import subprocess
import sys

# Run as a folder, Python puts the folder itself on the path: its parent holds the package.
sys.path[0] = os.path.dirname(os.path.abspath(sys.path[0]))

from fabrik import brief, checks, cockpit, hooks, journal, ledger, quiz
from fabrik.drift import touched


def quiet(command):
    """Runs a command and keeps its output short for the agent: one line when it passes, its last 30 lines when it
    fails."""
    # Through sh, which runs scripts as the dev's shell does, and words its own errors. The script goes through the
    # environment: on Windows, Git Bash's runtime does not give back the escaped quotes Python puts on a command line.
    result = subprocess.run(["sh", "-c", "eval $SDD_QUIET", "sh", *command], env=dict(os.environ, SDD_QUIET='"$@"'),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, status = result.stdout, result.returncode
    if status == 0:
        hidden = out.count(b"\n")
        print(f"ok: {' '.join(command)} ({hidden} lines hidden)")
        return 0
    sys.stdout.flush()
    if out:
        sys.stdout.buffer.write(b"\n".join(out.rstrip(b"\n").split(b"\n")[-30:]) + b"\n")
    print(f"FAIL ({status}): {' '.join(command)}")
    return status


def misuse(text):
    print(text, file=sys.stderr)
    return 2


def sdd_command(args):
    command = args[0] if args else ""
    if command == "hook":
        hooks.hook(args[1])
    elif command == "committed":
        journal.committed()
    elif command == "audit" and args[1:2] == ["--message"]:
        return checks.audit_staged(args[2])
    elif command == "audit" and args[1:2] == ["--range"]:
        return checks.audit_range(args[2])
    elif command == "audit":
        return checks.audit_staged()
    elif command == "fingerprint":
        journal.committed()
        os.makedirs(os.path.dirname(quiz.key_path()), exist_ok=True)
        print(f"fingerprint: {quiz.staged()}")
        print("quiz: QUIZ.md")
        print(f"key: {quiz.key_path()}")
    elif command == "install-hook":
        return hooks.install()
    elif command == "touched":
        for module, lines in touched(args[1] if len(args) > 1 else "HEAD"):
            print(f"{module}\t{lines}")
    elif command == "brief":
        brief.brief(args[1] if len(args) > 1 else "")
    elif command == "next":
        brief.next_step()
    elif command == "quiet":
        return quiet(args[1:])
    else:
        return misuse("usage: bash sdd/bin/sdd hook <message-file> | audit [--message <file> | --range <base>..<tip>]\n"
                      "       bash sdd/bin/sdd fingerprint | install-hook | touched [<commit>] | brief [<module>]\n"
                      "       bash sdd/bin/sdd next | quiet <command>...")


def ledger_command(args):
    if args == ["record"]:
        ledger.record()
    elif args[:1] == ["sync"] and len(args) <= 2:
        ledger.sync(args[1] if len(args) == 2 else "origin")
    elif args == ["report"]:
        ledger.report()
    else:
        return misuse("usage: bash sdd/bin/ledger record | sync [<remote>] | report")


def cockpit_command(args):
    if args[:1] == ["usage"] and len(args) == 4:
        cockpit.usage(args[1], int(args[2]), int(args[3]))
    elif args[:1] == ["report"] and len(args) in (2, 4):
        cockpit.report(args[1], *map(int, args[2:]))
    elif args == ["hints"]:
        cockpit.hints()
    else:
        return misuse("usage: bash sdd/bin/cockpit report <repo> [<since> <until>] | hints"
                      " | usage <repo> <since> <until>")


# Paths with accents and LF line ends, whatever the platform; lines in order when stdout and stderr share a file.
for stream in (sys.stdout, sys.stderr):
    stream.reconfigure(encoding="utf-8", newline="\n", line_buffering=True)
# Piped into head, it stops quietly as the shell tools do. Windows has no SIGPIPE.
if hasattr(signal, "SIGPIPE"):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
launcher, arguments = sys.argv[1], sys.argv[2:]
sys.exit({"sdd": sdd_command, "ledger": ledger_command, "cockpit": cockpit_command}[launcher](arguments))
