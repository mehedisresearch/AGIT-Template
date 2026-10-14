#!/usr/bin/env python3
"""Category presence + tier coverage for 4 with-template systems on n=62 4fmt.

Uses fixed Ownership probes in agit_categories.sections_from_markdown.
"""

from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
PKG_GEN = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
from agit_categories import ORDER, CATEGORY_PROBES, match_category, sections_from_markdown  # noqa: E402

OUT = PKG_GEN / "results"
PRED_DIR = OUT / "filtered_predictions"
CL_BASE = PRED_DIR / "codellama13b_base.json"
CL_LORA = PRED_DIR / "codellama13b_qlora.json"

REQUIRED = [
    "Do / Don't rules",
    "Build / run / install",
    "Repository structure",
    "Test / CI commands",
    "Code style / formatting",
    "Architecture / design constraints",
    "Domain models / key abstractions",
    "API / interface contracts",
    "Examples / few-shot snippets",
    "Tooling-specific agent config",
]
GAP = [
    "Security / secrets",
    "Git / PR / commit conventions",
    "Ownership / contacts",
    "Maintenance / when to update",
]
RECOMMENDED = [
    "Project overview / purpose",
    "Performance",
]
BUCKETS = {
    "Required (10)": REQUIRED,
    "Gap (4)": GAP,
    "Recommended (2)": RECOMMENDED,
    "All-16": list(ORDER),
}

SYSTEMS = [
    ("gpt4o_mini_zero_shot", "gpt-4o-mini zero_shot", PRED_DIR / "zero_shot.json"),
    ("gpt4o_mini_rag", "gpt-4o-mini RAG", PRED_DIR / "rag.json"),
    ("codellama13b_base", "CodeLlama-13B base", CL_BASE),
    ("codellama13b_qlora", "CodeLlama-13B QLoRA", CL_LORA),
]

# Pre-fix Ownership probes (for before/after only).
OLD_OWNERSHIP_PROBES = [
    r"\bowner\b",
    r"\bcontact\b",
    r"\bmaintainer\b",
    r"\bcodeowner",
]
OLD_MAINTENANCE_PROBES = [
    r"\bmaintain",
    r"\bstale\b",
    r"\bwhen to update\b",
    r"\bsync\b",
]


def round4(x: float) -> float:
    return round(float(x), 4)


def load_hyp_map(path: Path, kept: set[str]) -> dict[str, str]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for k, v in raw.items():
        sk = str(k)
        if sk not in kept:
            continue
        if isinstance(v, str):
            out[sk] = v
        elif isinstance(v, dict):
            out[sk] = v.get("prediction") or v.get("output") or v.get("text") or ""
        else:
            out[sk] = str(v or "")
    return out


def pred_cats(text: str) -> set[str]:
    return set(sections_from_markdown(text or ""))


def match_category_legacy(heading: str) -> str | None:
    """Old Ownership/Maintenance probes; other categories unchanged."""
    h = heading.lower()
    for cat, probes in CATEGORY_PROBES.items():
        if cat == "Ownership / contacts":
            probes = OLD_OWNERSHIP_PROBES
        elif cat == "Maintenance / when to update":
            probes = OLD_MAINTENANCE_PROBES
        if any(re.search(p, h, re.I) for p in probes):
            return cat
    return None


def sections_legacy(text: str) -> dict[str, dict]:
    """Same as sections_from_markdown but with legacy Ownership/Maintenance probes."""
    text = (text or "").strip()
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
        cat = match_category_legacy(heading)
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


def score_system(hyp_map: dict[str, str], idxs: list[str]) -> dict:
    n = len(idxs)
    presence_counts = {c: 0 for c in ORDER}
    tier_coverages = {name: [] for name in BUCKETS}
    tier_counts = {name: [] for name in BUCKETS}
    own_legacy = 0
    own_fixed = 0

    for idx in idxs:
        text = hyp_map.get(idx, "") or ""
        cats = pred_cats(text)
        legacy = set(sections_legacy(text))
        if "Ownership / contacts" in cats:
            own_fixed += 1
        if "Ownership / contacts" in legacy:
            own_legacy += 1
        for c in ORDER:
            if c in cats:
                presence_counts[c] += 1
        for name, bucket in BUCKETS.items():
            inter = cats & set(bucket)
            tier_counts[name].append(len(inter))
            tier_coverages[name].append(len(inter) / len(bucket))

    presence = {c: round4(presence_counts[c] / n) for c in ORDER}
    presence_n = dict(presence_counts)
    tiers = {}
    for name in BUCKETS:
        tiers[name] = {
            "n_categories": len(BUCKETS[name]),
            "coverage_mean": round4(statistics.mean(tier_coverages[name])),
            "mean_count": round4(statistics.mean(tier_counts[name])),
            "coverage_std": round4(
                statistics.stdev(tier_coverages[name]) if n > 1 else 0.0
            ),
            "mean_count_std": round4(
                statistics.stdev(tier_counts[name]) if n > 1 else 0.0
            ),
        }

    return {
        "n": n,
        "presence": presence,
        "presence_n": presence_n,
        "tiers": tiers,
        "ownership_before_after": {
            "before_legacy_probes": round4(own_legacy / n),
            "after_fixed_probes": round4(own_fixed / n),
            "n_before": own_legacy,
            "n_after": own_fixed,
            "delta": round4((own_fixed - own_legacy) / n),
        },
    }


def md_table_presence(by_system: dict, labels: dict[str, str]) -> str:
    keys = [k for k, _, _ in SYSTEMS]
    header = "| Category | " + " | ".join(labels[k] for k in keys) + " |"
    sep = "|---|---:|---:|---:|---:|"
    rows = [header, sep]
    for cat in ORDER:
        cells = [f"{by_system[k]['presence'][cat]:.4f}" for k in keys]
        rows.append(f"| {cat} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def md_table_tiers(by_system: dict, labels: dict[str, str]) -> str:
    keys = [k for k, _, _ in SYSTEMS]
    header = "| Tier | " + " | ".join(labels[k] for k in keys) + " |"
    sep = "|---|---:|---:|---:|---:|"
    rows = [header, sep]
    for tier in BUCKETS:
        cells = [f"{by_system[k]['tiers'][tier]['coverage_mean']:.4f}" for k in keys]
        rows.append(f"| {tier} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def md_table_ownership_ba(by_system: dict, labels: dict[str, str]) -> str:
    keys = [k for k, _, _ in SYSTEMS]
    header = "| System | Before (legacy) | After (fixed) | Δ | n_before | n_after |"
    sep = "|---|---:|---:|---:|---:|---:|"
    rows = [header, sep]
    for k in keys:
        ba = by_system[k]["ownership_before_after"]
        rows.append(
            f"| {labels[k]} | {ba['before_legacy_probes']:.4f} | "
            f"{ba['after_fixed_probes']:.4f} | {ba['delta']:+.4f} | "
            f"{ba['n_before']} | {ba['n_after']} |"
        )
    return "\n".join(rows)


def main() -> None:
    zs = json.loads((PRED_DIR / "zero_shot.json").read_text(encoding="utf-8"))
    kept = sorted(zs.keys(), key=lambda x: int(x))
    kept_set = set(kept)
    assert len(kept) == 62

    # Sanity: fixed detector matches canonical Ownership heading.
    assert match_category("Ownership / contacts") == "Ownership / contacts"
    assert match_category("Maintainers") == "Ownership / contacts"
    assert match_category("Maintenance / when to update") == "Maintenance / when to update"

    by_system = {}
    labels = {}
    for key, label, path in SYSTEMS:
        hyp = load_hyp_map(path, kept_set)
        missing = [i for i in kept if i not in hyp]
        if missing:
            raise SystemExit(f"{key}: missing idxs {missing[:10]} (n={len(missing)})")
        by_system[key] = score_system(hyp, kept)
        labels[key] = label
        ba = by_system[key]["ownership_before_after"]
        print(
            f"{label}: Ownership {ba['before_legacy_probes']:.4f} -> "
            f"{ba['after_fixed_probes']:.4f}  All-16={by_system[key]['tiers']['All-16']['coverage_mean']:.4f}"
        )

    payload = {
        "description": (
            "Category-level presence (Coverage) and tier structural coverage for "
            "with-template generation on generic_intent_fulltest_4fmt n=62. "
            "Presence(c) = fraction of files where category c is detected in "
            "generated markdown via sections_from_markdown (fixed Ownership probes). "
            "Tier coverage = mean over files of |pred ∩ tier| / |tier|."
        ),
        "n_test": 62,
        "idxs": [int(i) for i in kept],
        "ownership_probe_fix": {
            "file": "replication_package/generation_agit_instruct/scripts/agit_categories.py",
            "ownership_probes": CATEGORY_PROBES["Ownership / contacts"],
            "maintenance_probes": CATEGORY_PROBES["Maintenance / when to update"],
            "note": (
                "Broadened Ownership to match ownership/owners/contacts/maintainers/"
                "codeowners. Replaced Maintenance \\bmaintain with \\bmaintenance\\b "
                "so Maintainers maps to Ownership."
            ),
            "legacy_ownership_probes": OLD_OWNERSHIP_PROBES,
            "legacy_maintenance_probes": OLD_MAINTENANCE_PROBES,
        },
        "tier_definitions": {
            "Required (10)": REQUIRED,
            "Gap (4)": GAP,
            "Recommended (2)": RECOMMENDED,
            "All-16": list(ORDER),
        },
        "systems": {
            key: {
                "label": label,
                "prediction_path": str(path),
                **by_system[key],
            }
            for key, label, path in SYSTEMS
        },
        "tables": {
            "presence_16x4": {
                cat: {labels[k]: by_system[k]["presence"][cat] for k in labels}
                for cat in ORDER
            },
            "tier_coverage_4": {
                tier: {
                    labels[k]: by_system[k]["tiers"][tier]["coverage_mean"]
                    for k in labels
                }
                for tier in BUCKETS
            },
            "ownership_before_after": {
                labels[k]: by_system[k]["ownership_before_after"] for k in labels
            },
        },
    }

    json_path = OUT / "metrics_per_category_fixed_ownership.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# Category presence & tier coverage — 4 systems (n=62, with-template)",
        "",
        "Four-format filter sample (n=62; original fulltest n=77 → drop SKILL/GEMINI).",
        "Detector: `sections_from_markdown` / `match_category` with **fixed Ownership probes** "
        "(`agit_categories.py`).",
        "",
        "Presence = Coverage(i,{c}) averaged over files = fraction of generations where "
        "category c is detected (non-empty section body under a matching heading).",
        "",
        "## Ownership detector fix (before → after)",
        "",
        "Legacy probes missed the literal heading `Ownership / contacts` "
        "(`\\bowner\\b` does not match `ownership`; `\\bcontact\\b` does not match `contacts`). "
        "Maintenance used `\\bmaintain`, which incorrectly claimed `Maintainers`.",
        "",
        md_table_ownership_ba(by_system, labels),
        "",
        "## Table 1 — 16 categories × 4 systems (presence rates)",
        "",
        md_table_presence(by_system, labels),
        "",
        "## Table 2 — Tier structural coverage × 4 systems",
        "",
        md_table_tiers(by_system, labels),
        "",
        "### Tier mean counts",
        "",
    ]
    keys = [k for k, _, _ in SYSTEMS]
    md_lines.append(
        "| Tier | " + " | ".join(labels[k] for k in keys) + " |"
    )
    md_lines.append("|---|---:|---:|---:|---:|")
    for tier in BUCKETS:
        cells = [f"{by_system[k]['tiers'][tier]['mean_count']:.2f}" for k in keys]
        md_lines.append(f"| {tier} mean # | " + " | ".join(cells) + " |")

    md_lines += [
        "",
        "## Sources",
        "",
        "- Predictions (all 4): `results/filtered_predictions/"
        "{zero_shot,rag,codellama13b_base,codellama13b_qlora}.json`",
        "- Metrics JSON: `results/metrics_per_category_fixed_ownership.json`",
        "",
    ]
    md_path = OUT / "summary_per_category_4systems.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
