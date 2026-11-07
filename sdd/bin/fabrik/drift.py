"""Drift between the contracts and their code, and the modules a commit touches."""
import re
import sys

from fabrik.contracts import contracts, governs, highest, links, module, modules, risk
from fabrik.git import commit_or, empty_tree, exists, git, lines


def drift(batch, base, tree, message):
    """Notes in batch the modules whose code or contract changed from base to tree (hit), the risk of each (risks),
    the contracts whose code changed (coded), the changed paths they govern (governed), the files the contracts of the
    tree link to (linked), and how many changed code that no Spec-Unchanged spares (touched)."""
    for line in re.findall(r"^Spec-Unchanged\(([^)\n]*)\):", message, re.M):
        for name in line.split():
            if not exists(f"{tree}:sdd/modules/{name}.md"):
                batch.errors += f"ERROR Spec-Unchanged({name}): no such module. Modules: {modules(tree)}.\n"
    # The base's contracts too: a batch that deletes a contract is judged at its risk.
    for contract in dict.fromkeys(contracts(tree) + contracts(base)):
        name, path = module(contract), None
        if exists(f"{tree}:{contract}"):
            paths = governs(f"{tree}:{contract}")
            if not paths:
                batch.errors += f"ERROR {contract}: governs is empty. List the paths this module owns.\n"
                continue
            linked, broken = links(tree, contract)
            batch.linked.update(linked)
            if broken:
                batch.findings += "\n".join(broken) + "\n      Fix the link, or the name of the test it points to.\n"
            governed = lines(git("diff", "--name-only", "--no-renames", base, tree, "--", *paths))
            batch.governed.update(governed)
            path = next(iter(governed), None)
        if path:
            batch.coded.append(contract)
        if path or contract in batch.changed:
            batch.hit.append(name)
            # The batch that lowers a module's risk is still judged at the risk it had.
            batch.risks[name] = highest(found for found in (risk(tree, contract, True), risk(base, contract, False))
                                        if found)
        if not path or re.search(rf"^Spec-Unchanged\({re.escape(name)}\):[^\S\n]*\S", message, re.M):
            continue
        batch.touched += 1
        if contract not in batch.changed:
            batch.findings += (
                f"DRIFT {contract}: {path} changed, its contract did not.\n"
                "      Update the contract if the code is right, fix the code if it betrays the intent,\n"
                f"      or add 'Spec-Unchanged({name}): <reason>' to the message if the behavior is unchanged.\n")


def touched(commit):
    """The modules whose code or contract a commit changes, each with its changed lines."""
    if commit_or(commit, None) is None:
        sys.exit(f"No commit {commit} here: commit first, or name a commit.")
    parent = commit_or(f"{commit}^", empty_tree())
    found = []
    for contract in contracts(commit):
        stats = git("diff", "--numstat", "--no-renames", parent, commit, "--", contract,
                    *governs(f"{commit}:{contract}"))
        changed = sum(int(row[0]) + int(row[1]) for row in (line.split("\t") for line in lines(stats)) if row[0] != "-")
        if changed:
            found.append((module(contract), changed))
    return found
