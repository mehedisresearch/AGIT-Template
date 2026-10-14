#!/usr/bin/env python3
"""RQ3 — Map heading add/delete counts onto the full 16 RQ2 categories.

Produces `rq3_category_durability_all16.csv` (paper Σ total_edits = 5,396).

Requires AIDev-pop `pr_commit_details.parquet` under AGIT_STUDY_ROOT/aidev_cache
(same source as `analyze_rq3_maintenance.py`). Writes into AGIT_RQ_OUT (this RQ folder).
"""
from __future__ import annotations

import os
import re
from collections import Counter
from pathlib import Path

import pandas as pd

STUDY = Path(
    os.environ.get(
        "AGIT_STUDY_ROOT",
        "/gpuhome/shanto1/Agents Instruction/ai_agent_instruction_files",
    )
)
OUT = Path(os.environ.get("AGIT_RQ_OUT", str(Path(__file__).resolve().parents[1])))
CACHE = STUDY / "aidev_cache"

FILE_TYPES = ["AGENTS.md", "CLAUDE.md", "Cursor rules", "Copilot instructions"]

# Same 16 labels as RQ2 taxonomy / paper tables.
CATEGORIES = [
    "Project overview / purpose",
    "Repository structure",
    "Build / run / install",
    "Test / CI commands",
    "Code style / formatting",
    "Architecture / design constraints",
    "Domain models / key abstractions",
    "API / interface contracts",
    "Do / Don't rules",
    "Security / secrets",
    "Performance",
    "Git / PR / commit conventions",
    "Tooling-specific agent config",
    "Examples / few-shot snippets",
    "Ownership / contacts",
    "Maintenance / when to update",
]

CAT_KW = {
    "Project overview / purpose": [r"overview", r"purpose", r"about", r"introduction", r"mission"],
    "Repository structure": [r"structure", r"directory", r"folder", r"layout", r"monorepo"],
    "Build / run / install": [r"command", r"build", r"install", r"setup", r"getting started", r"docker"],
    "Test / CI commands": [r"\btest\b", r"\bci\b", r"lint", r"verif", r"pytest", r"jest"],
    "Code style / formatting": [r"style", r"format", r"prettier", r"eslint", r"convention", r"naming"],
    "Architecture / design constraints": [r"architecture", r"design", r"constraint", r"pattern", r"modular"],
    "Domain models / key abstractions": [r"\bmodel\b", r"domain", r"entity", r"abstraction", r"schema"],
    "API / interface contracts": [r"\bapi\b", r"endpoint", r"interface", r"contract", r"openapi", r"route"],
    "Do / Don't rules": [r"\brule", r"do not", r"don't", r"guideline", r"\bnever\b", r"\balways\b"],
    "Security / secrets": [r"secur", r"secret", r"credential", r"token", r"auth", r"owasp"],
    "Performance": [r"perform", r"latency", r"optim", r"throughput", r"benchmark"],
    "Git / PR / commit conventions": [r"commit", r"pull request", r"\bpr\b", r"branch", r"changelog"],
    "Tooling-specific agent config": [r"agent", r"claude", r"cursor", r"copilot", r"mcp", r"skill", r"hook"],
    "Examples / few-shot snippets": [r"example", r"snippet", r"sample", r"few[- ]shot"],
    "Ownership / contacts": [r"owner", r"contact", r"maintainer", r"codeowner", r"slack"],
    "Maintenance / when to update": [r"maintain", r"stale", r"outdated", r"when to update", r"drift", r"sync"],
}


def classify_path(path: str) -> set[str]:
    if not isinstance(path, str) or not path:
        return set()
    p = path.replace("\\", "/")
    pl = p.lower()
    name = Path(pl).name
    found: set[str] = set()
    if name == "agents.md":
        found.add("AGENTS.md")
    if name == "claude.md":
        found.add("CLAUDE.md")
    if name == ".cursorrules" or "/.cursor/rules/" in pl or pl.endswith("/.cursor/rules"):
        found.add("Cursor rules")
    if (
        name == "copilot-instructions.md"
        or name.endswith(".instructions.md")
        or "/.github/instructions/" in pl
    ):
        found.add("Copilot instructions")
    return found


def norm_h(h: str) -> str:
    h = h.lower().strip()
    h = re.sub(r"[^a-z0-9 /+_.-]+", " ", h)
    return re.sub(r"\s+", " ", h).strip()


def main() -> None:
    details = pd.read_parquet(
        CACHE / "pr_commit_details.parquet",
        columns=["filename", "patch"],
    )
    mask = details["filename"].fillna("").map(lambda p: bool(classify_path(p)))
    inst = details.loc[mask]

    head_add = re.compile(r"^\+\s*#{1,3}\s+(.+)$", re.M)
    head_del = re.compile(r"^\-\s*#{1,3}\s+(.+)$", re.M)
    added_heads: Counter[str] = Counter()
    deleted_heads: Counter[str] = Counter()
    for patch in inst["patch"]:
        if not isinstance(patch, str):
            continue
        for m in head_add.finditer(patch):
            h = norm_h(m.group(1))
            if h:
                added_heads[h] += 1
        for m in head_del.finditer(patch):
            h = norm_h(m.group(1))
            if h:
                deleted_heads[h] += 1

    rows = []
    for cat in CATEGORIES:
        pats = [re.compile(k, re.I) for k in CAT_KW[cat]]
        a = sum(c for h, c in added_heads.items() if any(p.search(h) for p in pats))
        d = sum(c for h, c in deleted_heads.items() if any(p.search(h) for p in pats))
        total = a + d
        rate = round(a / total, 3) if total else None
        rows.append(
            {
                "category": cat,
                "heading_adds": a,
                "heading_dels": d,
                "total_edits": total,
                "survive_rate": rate,
            }
        )

    df = pd.DataFrame(rows).sort_values("total_edits", ascending=False)
    out = OUT / "rq3_category_durability_all16.csv"
    df.to_csv(out, index=False)
    print(f"Wrote {out}  Σ total_edits={int(df['total_edits'].sum())}")


if __name__ == "__main__":
    main()
