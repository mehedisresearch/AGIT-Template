"""RQ2 four-format path / basename classifiers (no raw clones required)."""

from __future__ import annotations

from pathlib import Path


def classify_path(path: str) -> set[str]:
    """Map repo-relative path to zero or more of AGENTS / CLAUDE / Copilot / Cursor."""
    p = path.replace("\\", "/")
    pl = p.lower()
    name = Path(pl).name
    found: set[str] = set()
    if name == "agents.md":
        found.add("AGENTS")
    if name == "claude.md":
        found.add("CLAUDE")
    if name == ".cursorrules" or "/.cursor/rules/" in pl or pl.endswith("/.cursor/rules"):
        found.add("Cursor")
    if (
        name == "copilot-instructions.md"
        or name.endswith(".instructions.md")
        or "/.github/instructions/" in pl
    ):
        found.add("Copilot")
    return found


def primary_type(types: set[str]) -> str | None:
    for t in ("AGENTS", "CLAUDE", "Copilot", "Cursor"):
        if t in types:
            return t
    return None


def format_name_bucket(fmt: str) -> str | None:
    """Fallback when path is unavailable (should rarely be needed)."""
    fl = (fmt or "").lower()
    if fl == "agents.md":
        return "AGENTS"
    if fl == "claude.md":
        return "CLAUDE"
    if fl == "copilot-instructions.md" or fl.endswith(".instructions.md"):
        return "Copilot"
    if fl == "rule.md":
        return "Cursor"
    return None
