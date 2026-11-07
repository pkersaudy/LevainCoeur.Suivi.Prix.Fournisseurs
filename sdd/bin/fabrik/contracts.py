"""What a contract says: the paths it governs, its settings, its links to tests."""
import posixpath
import re
import sys

from fabrik.git import git, lines, try_git


def governs(revision):
    """The paths a contract governs, at a revision path such as HEAD:sdd/modules/search.md. YAML writes them as a list
    in brackets that may wrap, as "- path" lines below the key, or as one path; the next key ends them, comments are
    no paths. An absolute path or one outside the repo stops the command, since git would refuse every diff."""
    value, inside = [], False
    for line in front_matter(re.sub("[\"']", "", git("show", revision))):
        # A YAML comment starts with a "#" at the start of the line or after a space.
        line = re.sub(r"(^|\s)#.*", "", line)
        if not line.strip():
            continue
        # A line flush with the keys, other than a "- path" one, starts the next key.
        if re.match(r"[^\s-]", line):
            inside = line.startswith("governs:")
        if inside:
            value.append(re.sub(r"^(governs:|\s*-\s)", " ", line))
    paths = re.sub(r"[][,]", " ", " ".join(value)).split()
    for path in paths:
        if path.startswith("/") or resolve("", path) is None:
            sys.exit(f"ERROR {revision.split(':', 1)[1]}: governs {path}, outside the repo. Write each path from the"
                     f" repo root.")
    return paths


def front_matter(text):
    """The lines between the first two --- lines."""
    found, fence = [], 0
    for line in text.replace("\r", "").split("\n"):
        if re.match(r"---\s*$", line):
            fence += 1
        elif fence == 1:
            found.append(line)
    return found


RISKS = ("low", "intent", "normal", "high")


def risk(tree, contract, checked):
    """The risk of a contract in a tree: its own, else that of sdd/config.yml in the same tree, else normal; the repo's
    alone without a contract, None when the contract is not there. Another value stops the command when checked (the
    tree), and counts as normal otherwise (the base), so that the commit fixing it passes."""
    own = None
    if contract:
        text = try_git("show", f"{tree}:{contract}")
        if text is None:
            return None
        own = value(front_matter(text), "risk")
    found = own or config(tree, "risk") or "normal"
    if found in RISKS:
        return found
    if checked:
        sys.exit(f"ERROR {contract if own else 'sdd/config.yml'}: risk is {found}. Write low, intent, normal or high.")
    return "normal"


def highest(risks):
    return max(risks, key=RISKS.index)


def own_setting(revision, key):
    """A setting the contract at a revision path states itself, None when it does not or is not there."""
    return value(front_matter(try_git("show", revision) or ""), key)


def config(tree, key):
    """A setting of the repo in sdd/config.yml of the tree, None without one."""
    return value(lines(try_git("show", f"{tree}:sdd/config.yml") or ""), key)


def value(text_lines, key):
    """The value of a flat key: value line, without its quotes or its comment."""
    for line in text_lines:
        found = re.match(rf"{re.escape(key)}:(.*)", re.sub(r"(^|\s)#.*", "", line))
        if found:
            return found.group(1).strip().strip("\"'")
    return None


# The files that steer the project or the harness, when sdd/config.yml lists none.
SENSITIVE = ["sdd/bin/", "sdd/WORKFLOW.md", "sdd/guide/", "sdd/config.yml", "/(?i)(^|/)(agents|claude)\\.md$/",
             "sdd/architecture.md", "sdd/coding-style.md", "sdd/product.md", "sdd/modules/", ".github/workflows/",
             ".gitlab-ci.yml", ".claude/", "opencode.json", "kilo.jsonc", ".vscode/settings.json"]


def sensitive(tree, checked):
    """The sensitive entries of a tree: those of sdd/config.yml, else the kit's, and those of every contract. A wrong
    entry stops the command when checked (the tree), and is left out otherwise (the base), so that the commit fixing it
    passes."""
    found = entries(lines(try_git("show", f"{tree}:sdd/config.yml") or ""), "sdd/config.yml", checked)
    found = list(SENSITIVE) if found is None else found
    for contract in contracts(tree):
        found += entries(front_matter(git("show", f"{tree}:{contract}")), contract, checked) or []
    return found


def entries(text_lines, where, checked):
    """The entries a file lists under sensitive, one on the key's line or one per "- " line below it, never split;
    None when the key is not there."""
    found, inside = None, False
    for line in text_lines:
        line = re.sub(r"(^|\s)#.*", "", line)
        if re.match(r"[^\s-]", line):
            inside = line.startswith("sensitive:")
            entry = line[len("sensitive:"):] if inside else ""
            found = [] if inside else found
        else:
            item = re.match(r"\s*-\s(.*)", line)
            entry = item.group(1) if inside and item else ""
        entry = entry.strip().strip("\"'")
        if entry in ("", "[]"):
            continue
        if entry.startswith("["):
            if checked:
                example = entry[1:].split(",")[0].strip(" ]") or "sdd/architecture.md"
                sys.exit(f'ERROR {where}: sensitive is {entry}. Write one entry per line below the key, as'
                         f' "  - {example}".')
            continue
        if re.fullmatch("/.+/", entry):
            try:
                re.compile(entry[1:-1])
            except re.error as error:
                if checked:
                    sys.exit(f"ERROR {where}: sensitive lists {entry}, a regular expression that does not compile"
                             f" ({error}). Fix it, or write a path.")
                continue
        found.append(entry)
    return found


def matches(entry, path):
    """Whether a sensitive entry matches a path: a regular expression between slashes where it is found, a folder
    every path under it, else the path itself."""
    if re.fullmatch("/.+/", entry):
        return re.search(entry[1:-1], path) is not None
    if entry.endswith("/") and not entry.startswith("/"):
        return path.startswith(entry)
    return path == entry


def contracts(tree):
    return [path for path in lines(git("ls-tree", "-r", "--name-only", tree, "sdd/modules/")) if path.endswith(".md")]


def module(contract):
    return posixpath.basename(contract)[: -len(".md")]


def modules(tree):
    """The modules of a tree, for a message."""
    names = lines(git("ls-tree", "--name-only", tree, "sdd/modules/"))
    return ", ".join(module(name) for name in names if name.endswith(".md"))


def links(tree, contract):
    """The files a contract links to in a tree, other than Markdown and folders, and the drift between the contract and
    them: a linked file the tree lacks, or a name the file lacks."""
    files, found = [], []
    text = re.sub(" +", " ", re.sub("[\r\n]", " ", git("show", f"{tree}:{contract}")))
    for link in re.findall(r"\[[^]]*\]\([^)]*\)", text):
        name, target = link[1:].split("](", 1)
        target = target[:-1].split("#")[0]
        if not target or ":" in target or target.endswith((".md", "/")):
            continue
        # A target starts at the repo root or is relative to the contract. Resolved here, not by git -C: in a
        # worktree's hook, git -C takes the contract's folder for the work tree.
        path = target[1:] if target.startswith("/") else resolve(posixpath.dirname(contract), target)
        file = path and try_git("ls-tree", "--name-only", tree, "--", path)
        if not file:
            found.append(f'DRIFT {contract}: links "{name}" to {target}, a file the commit does not have.')
        elif git("cat-file", "-t", f"{tree}:{file}") == "blob":
            files.append(file)
            # The name as whole words, as grep -w finds it.
            if name not in (posixpath.basename(file), file) and not re.search(rf"(?<!\w){re.escape(name)}(?!\w)",
                                                                              git("show", f"{tree}:{file}")):
                found.append(f'DRIFT {contract}: links "{name}", not found in {file}.')
    return files, found


def resolve(folder, target):
    """The path of target from folder, or None when it climbs out of the repo."""
    kept = []
    for part in f"{folder}/{target}".split("/"):
        if part == "..":
            if not kept:
                return None
            kept.pop()
        elif part not in (".", ""):
            kept.append(part)
    return "/".join(kept)
