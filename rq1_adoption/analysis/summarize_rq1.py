#!/usr/bin/env python3
"""Recompute RQ1 summary tables from packaged CSVs/JSON (no external data)."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    matrix = pd.read_csv(ROOT / "rq1_project_format_matrix.csv")
    lang = pd.read_csv(ROOT / "rq1_language_format.csv")
    results = json.loads((ROOT / "rq1_results.json").read_text())

    n = len(matrix)
    has_any = int(matrix["has_any"].sum())
    lines = [
        "# RQ1 — Adoption summary (from packaged tables)",
        "",
        f"- Repos: **{n}** (expect 1000)",
        f"- Any of 4 formats: **{has_any}** ({100 * has_any / n:.1f}%)",
    ]
    for cohort, g in matrix.groupby("cohort"):
        lines.append(
            f"- {cohort}: **{int(g.has_any.sum())}/{len(g)}** "
            f"({100 * g.has_any.mean():.1f}%)"
        )
    lines += [
        "",
        "## Prevalence (from rq1_results.json)",
        "",
        "| Cohort | n | any % | AGENTS | CLAUDE | Copilot | Cursor |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for p in results["prevalence"]:
        lines.append(
            f"| {p['cohort']} | {p['n']} | {p['any_pct']} | "
            f"{p['AGENTS.md_pct']} | {p['CLAUDE.md_pct']} | "
            f"{p['Copilot instructions_pct']} | {p['Cursor rules_pct']} |"
        )
    lines += [
        "",
        f"Multi-format %: {results.get('multi_pct')}",
        f"Top co-occurring pairs: {results.get('pairs', [])[:3]}",
        "",
        f"Language×format rows in `rq1_language_format.csv`: {len(lang)}",
        "",
    ]
    out = ROOT / "summary.md"
    out.write_text("\n".join(lines))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
