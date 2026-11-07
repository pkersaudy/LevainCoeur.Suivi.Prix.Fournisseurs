"""opencode keeps every message in one SQLite base; a sub-agent runs in a child session."""
import json
import os
import sqlite3

from fabrik.logs import REVIEW


def usage(repo, start, end):
    share = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    base = os.path.join(share, "opencode", "opencode.db")
    if not os.path.exists(base):
        return
    db = sqlite3.connect(f"file:{base}?mode=ro", uri=True)
    for data, parent, title in db.execute(
        "select m.data, s.parent_id, s.title from message m join session s on s.id = m.session_id"
        " where s.directory = ? and m.time_created > ? and m.time_created <= ?", (repo, start * 1000, end * 1000)
    ):
        message = json.loads(data)
        if message.get("role") != "assistant":
            continue
        tokens = message.get("tokens", {})
        yield role(parent, title, message), message["modelID"], {
            "input": tokens.get("input", 0),
            # Claude Code counts thinking in its output, opencode apart: output includes reasoning in both.
            "output": tokens.get("output", 0) + tokens.get("reasoning", 0),
            "cache_read": tokens.get("cache", {}).get("read", 0),
            "cache_write": tokens.get("cache", {}).get("write", 0),
        }


def role(parent, title, message):
    if not parent:
        return "writer"
    return "reviewer" if REVIEW.search(title or "") else "agent:" + message["agent"]
