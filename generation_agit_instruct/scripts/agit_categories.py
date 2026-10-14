"""AGIT 16-category taxonomy helpers (no API / no secrets).

Extracted for replication scoring: section parsing and category order only.
"""

from __future__ import annotations

import re

ORDER = [
    "Project overview / purpose",
    "Repository structure",
    "Build / run / install",
    "Test / CI commands",
    "Code style / formatting",
    "Architecture / design constraints",
    "Domain models / key abstractions",
    "API / interface contracts",
    "Do / Don't rules",
    "Git / PR / commit conventions",
    "Tooling-specific agent config",
    "Examples / few-shot snippets",
    "Security / secrets",
    "Performance",
    "Ownership / contacts",
    "Maintenance / when to update",
]

CATEGORY_PROBES = {
    "Project overview / purpose": [
        r"\boverview\b",
        r"\bpurpose\b",
        r"\babout\b",
        r"\bintroduction\b",
        r"\bmission\b",
    ],
    "Repository structure": [
        r"\bstructure\b",
        r"\bdirectory\b",
        r"\bfolder\b",
        r"\blayout\b",
        r"\bmonorepo\b",
    ],
    "Build / run / install": [
        r"\bbuild\b",
        r"\binstall\b",
        r"\brun\b",
        r"\bsetup\b",
        r"\bgetting started\b",
    ],
    "Test / CI commands": [
        r"\btest\b",
        r"\bci\b",
        r"\blint\b",
        r"\bcoverage\b",
        r"\bgithub actions\b",
    ],
    "Code style / formatting": [
        r"\bstyle\b",
        r"\bformat\b",
        r"\blinter\b",
        r"\bconvention\b",
        r"\bnaming\b",
    ],
    "Architecture / design constraints": [
        r"\barchitecture\b",
        r"\bdesign\b",
        r"\bconstraint\b",
        r"\bpattern\b",
    ],
    "Domain models / key abstractions": [
        r"\bmodel\b",
        r"\bdomain\b",
        r"\bentity\b",
        r"\babstraction\b",
        r"\bschema\b",
    ],
    "API / interface contracts": [
        r"\bapi\b",
        r"\bendpoint\b",
        r"\binterface\b",
        r"\bcontract\b",
        r"\broute\b",
    ],
    "Do / Don't rules": [
        r"\bdo not\b",
        r"\bdon't\b",
        r"\bnever\b",
        r"\balways\b",
        r"\brules?\b",
        r"\bguidelines?\b",
    ],
    "Git / PR / commit conventions": [
        r"\bgit\b",
        r"\bpull request\b",
        r"\bcommit\b",
        r"\bbranch\b",
        r"\bpr\b",
    ],
    "Tooling-specific agent config": [
        r"\bagent\b",
        r"\bclaude\b",
        r"\bcursor\b",
        r"\bcopilot\b",
        r"\bskill\b",
        r"\bmcp\b",
    ],
    "Examples / few-shot snippets": [
        r"\bexample\b",
        r"\bsnippet\b",
        r"\bsample\b",
        r"\bfew[- ]shot\b",
    ],
    "Security / secrets": [
        r"\bsecurit",
        r"\bsecret\b",
        r"\bcredential\b",
        r"\btoken\b",
        r"\bauth\b",
    ],
    "Performance": [
        r"\bperformance\b",
        r"\blatenc",
        r"\boptimiz",
        r"\bthroughput\b",
        r"\bcach",
    ],
    # Ownership before Maintenance in dict order: claim maintainers/owners/contacts
    # first so Maintenance's maintenance/update probes do not steal them.
    "Ownership / contacts": [
        r"\bownership\b",
        r"\bowners?\b",
        r"\bcontacts?\b",
        r"\bmaintainers?\b",
        r"\bcode[\s_-]*owners?\b",
    ],
    "Maintenance / when to update": [
        # Prefer \bmaintenance\b over \bmaintain so "Maintainers" stays Ownership.
        r"\bmaintenance\b",
        r"\bstale\b",
        r"\bwhen to update\b",
        r"\bsync\b",
    ],
}


def match_category(heading: str) -> str | None:
    h = heading.lower()
    for cat, probes in CATEGORY_PROBES.items():
        if any(re.search(p, h, re.I) for p in probes):
            return cat
    return None


def sections_from_markdown(text: str) -> dict[str, dict]:
    """Parse ## headings into AGIT categories."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:markdown|md)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    lines = text.splitlines()
    blocks: list[tuple[str, list[str]]] = []
    cur_h = None
    cur: list[str] = []
    for line in lines:
        m = re.match(r"^(#{1,3})\s+(.+?)\s*$", line)
        if m and len(m.group(1)) <= 2:
            if cur_h is not None:
                blocks.append((cur_h, cur))
            cur_h = m.group(2).strip()
            cur = []
        else:
            if cur_h is not None:
                cur.append(line)
    if cur_h is not None:
        blocks.append((cur_h, cur))

    out: dict[str, dict] = {}
    for heading, body_lines in blocks:
        cat = match_category(heading)
        if not cat:
            continue
        body = "\n".join(body_lines).strip()
        if not body:
            continue
        if cat not in out:
            out[cat] = {"heading": heading, "content": body}
        else:
            out[cat]["content"] += "\n\n" + body
    return out
