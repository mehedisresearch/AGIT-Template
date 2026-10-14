#!/usr/bin/env python3
"""Recompute RQ2 taxonomy summary from packaged CSVs/JSON (no clones needed)."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    results = json.loads((ROOT / "rq2_results.json").read_text())
    prev = pd.read_csv(ROOT / "rq2_category_prevalence.csv")
    stats = pd.read_csv(ROOT / "rq2_file_stats.csv")
    hj = pd.read_csv(ROOT / "rq2_heading_jaccard.csv")
    wj = pd.read_csv(ROOT / "rq2_within_repo_jaccard.csv")

    lines = [
        "# RQ2 — Taxonomy summary (from packaged tables)",
        "",
        f"- Files: **{results['n_files']}** (expect 3387)",
        f"- Files per type: {results.get('files_per_type')}",
        f"- Category coding note: {results.get('notes', {}).get('category_coding')}",
        "",
        "## File stats",
        "",
        stats.to_markdown(index=False)
        if hasattr(stats, "to_markdown")
        else stats.to_string(index=False),
        "",
        "## Heading Jaccard (vocabulary)",
        "",
        hj.to_markdown(index=False)
        if hasattr(hj, "to_markdown")
        else hj.to_string(index=False),
        "",
        f"Within-repo pair rows: **{len(wj)}**",
        "",
        "## Category prevalence (pct of files)",
        "",
        prev.to_markdown(index=False)
        if hasattr(prev, "to_markdown")
        else prev.to_string(index=False),
        "",
    ]
    out = ROOT / "summary.md"
    out.write_text("\n".join(str(x) for x in lines))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
