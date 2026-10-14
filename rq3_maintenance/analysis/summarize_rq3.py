#!/usr/bin/env python3
"""Recompute RQ3 summary from packaged CSVs/JSON (no parquet needed)."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    results = json.loads((ROOT / "rq3_results.json").read_text())
    life = pd.read_csv(ROOT / "rq3_file_lifecycle.csv")
    events = pd.read_csv(ROOT / "rq3_instruction_events.csv")
    dur16 = pd.read_csv(ROOT / "rq3_category_durability_all16.csv")
    kw = pd.read_csv(ROOT / "rq3_kruskal_wallis.csv")
    cliffs = pd.read_csv(ROOT / "rq3_cliffs_delta.csv")

    lines = [
        "# RQ3 — Maintenance summary (from packaged tables)",
        "",
        f"- Instruction-file touches: **{results['n_instruction_events']}** (CSV rows={len(events)})",
        f"- Unique files: **{results['n_unique_files']}** (lifecycle rows={len(life)})",
        f"- Repos / PRs: **{results['n_repos']} / {results['n_prs']}**",
        f"- Heading edits (all16 Σ total_edits): **{int(dur16['total_edits'].sum())}** (expect 5396)",
        "",
        "## Lifecycle medians by format",
        "",
    ]
    for row in results.get("lifecycle_summary", []):
        lines.append(
            f"- {row['file_type']}: n={row['n_files']}, "
            f"med_touches={row['median_touches']}, "
            f"med_churn={row['median_churn_ratio']}, "
            f"abandoned={row['pct_abandoned']}%"
        )
    lines += [
        "",
        "## Kruskal–Wallis",
        "",
        kw.to_string(index=False),
        "",
        "## Cliffs' δ (first 12 rows)",
        "",
        cliffs.head(12).to_string(index=False),
        "",
        "## Category durability (all 16)",
        "",
        dur16.to_string(index=False),
        "",
        f"Notes: {results.get('notes')}",
        "",
    ]
    out = ROOT / "summary.md"
    out.write_text("\n".join(lines))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
