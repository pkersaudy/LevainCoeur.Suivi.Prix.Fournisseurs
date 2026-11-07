"""One reader per agent tool, each a module here. A new tool is a new module, nothing else.

Every reader has usage(repo, start, end), for the ledger: each reply of the tool in that repo between two epoch seconds,
as (role, model, tokens). The role is writer, reviewer or agent:<type>; the tokens are input, output (reasoning
included), cache_read and cache_write.

A reader that can also weigh its calls, for the cockpit's report and hints, has NAME, PRICES (its provider's price
ratios, in words) and calls(repo, start, end, sent): each reply in the window as a Call, adding to sent what the tool
sends along with them. sent is complete once every call is read."""
import importlib
import pkgutil
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import NamedTuple

# A sub-agent whose description names a review or a quiz is the reviewer. Above READERS: the readers import it.
REVIEW = re.compile(r"review|quiz", re.I)

# The kinds of what is sent along that the hints read apart: a source is a kind and a name, such as (MCP, "docs").
MCP, SKILLS = "MCP instructions", "skill listing"


class Call(NamedTuple):
    """A reply: the context it was sent, in tokens; its cost and that of its cache reads, in input-equivalent tokens at
    the provider's prices. rank counts the replies of its log in the window up to this one; opens says it is the log's
    first."""
    role: str
    model: str
    context: int
    cost: float
    read: float
    opens: bool
    rank: int


@dataclass
class Sent:
    """What a tool sends along with its calls besides the conversation. costs holds each source's cost, estimated from
    its size; plugin_sizes, the largest size each plugin's skills had in the listing."""
    costs: Counter = field(default_factory=Counter)
    servers_called: set = field(default_factory=set)
    plugin_sizes: dict = field(default_factory=dict)
    plugins_called: set = field(default_factory=set)


def label(source):
    kind, name = source
    return f"{kind} {name}" if name else kind


READERS = [importlib.import_module(f"{__name__}.{found.name}") for found in pkgutil.iter_modules(__path__)]
