#!/usr/bin/env python3
"""REQUIRED vs GAP overlap metrics on generic_intent_fulltest_4fmt.

Lists match build_generic_instruction_template.REQUIRED10/GAP5,
instruction_linter.REQUIRED_CATEGORIES/GAP_CATEGORIES, and build_dataset.py.
"""

from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

import numpy as np
from rouge_score import rouge_scorer as rouge_lib
from sentence_transformers import SentenceTransformer

from build_manual_section_study import ORDER, sections_from_markdown
from score_overlap_sections import mean_std, rouge_prf, round_dict

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "exports" / "generic_intent_fulltest_4fmt"
PRED_DIR = OUT / "filtered_predictions"
REFS_PATH = PRED_DIR / "test_refs.json"
PER_CAT_PATH = OUT / "metrics_per_category.json"
EMBED_MODEL = "all-MiniLM-L6-v2"
APPROACHES = ("zero_shot", "rag")

# Official 10 REQUIRED + 5 GAP (Git / PR is in ORDER but neither bucket)
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
    "Performance",
    "Maintenance / when to update",
    "Project overview / purpose",
    "Ownership / contacts",
]
BUCKETS = {"REQUIRED": REQUIRED, "GAP": GAP}


def aligned_overlap_in_set(
    gold_secs: dict, pred_secs: dict, cat_set: set[str]
) -> tuple[str, str, list[str]]:
    """Concatenate gold∩pred categories restricted to cat_set, in ORDER."""
    inter = [
        c for c in ORDER if c in cat_set and c in gold_secs and c in pred_secs
    ]
    gold_parts: list[str] = []
    pred_parts: list[str] = []
    for cat in inter:
        g = gold_secs[cat]
        p = pred_secs[cat]
        g_h = (g.get("heading") or cat).strip()
        p_h = (p.get("heading") or cat).strip()
        gold_parts.append(f"## {g_h}\n\n{g['content'].strip()}")
        pred_parts.append(f"## {p_h}\n\n{p['content'].strip()}")
    return "\n\n".join(gold_parts).strip(), "\n\n".join(pred_parts).strip(), inter


def aggregate_from_per_category(per_cat: dict, cats: list[str]) -> dict:
    """Macro (unweighted over cats) and micro (n_scored-weighted) from section-pair means."""
    scored = []
    for cat in cats:
        entry = per_cat.get(cat) or {}
        n = entry.get("n_scored") or 0
        r1 = entry.get("rouge1_f")
        rl = entry.get("rougeL_f")
        emb = entry.get("embedding_cosine")
        if n > 0 and r1 is not None and rl is not None and emb is not None:
            scored.append(
                {
                    "cat": cat,
                    "n": int(n),
                    "rouge1_f": float(r1),
                    "rougeL_f": float(rl),
                    "embedding_cosine": float(emb),
                }
            )
    if not scored:
        return {
            "n_categories_scored": 0,
            "n_section_pairs": 0,
            "macro": None,
            "micro": None,
            "per_category_n": {c: (per_cat.get(c) or {}).get("n_scored", 0) for c in cats},
        }

    n_pairs = sum(s["n"] for s in scored)
    macro = {
        "rouge1_f": statistics.mean(s["rouge1_f"] for s in scored),
        "rougeL_f": statistics.mean(s["rougeL_f"] for s in scored),
        "embedding_cosine": statistics.mean(s["embedding_cosine"] for s in scored),
    }
    micro = {
        "rouge1_f": sum(s["rouge1_f"] * s["n"] for s in scored) / n_pairs,
        "rougeL_f": sum(s["rougeL_f"] * s["n"] for s in scored) / n_pairs,
        "embedding_cosine": sum(s["embedding_cosine"] * s["n"] for s in scored) / n_pairs,
    }
    return round_dict(
        {
            "n_categories_scored": len(scored),
            "n_section_pairs": n_pairs,
            "macro": macro,
            "micro": micro,
            "per_category_n": {s["cat"]: s["n"] for s in scored},
        }
    )


def score_bucket(
    refs: list[dict],
    hyp_map: dict,
    cat_list: list[str],
    embedder: SentenceTransformer,
) -> dict:
    cat_set = set(cat_list)
    scorer = rouge_lib.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)
    rows = []
    n_skip = 0
    for ref in refs:
        idx = str(ref["idx"])
        gold_secs = sections_from_markdown(ref["output"])
        pred_secs = sections_from_markdown(hyp_map.get(idx, "") or "")
        gold_o, pred_o, inter = aligned_overlap_in_set(gold_secs, pred_secs, cat_set)
        n_gold = sum(1 for c in cat_set if c in gold_secs)
        n_pred = sum(1 for c in cat_set if c in pred_secs)
        if not inter:
            n_skip += 1
            continue
        rows.append(
            {
                "idx": ref["idx"],
                "repo": ref["repo"],
                "format": ref["format"],
                "overlap_categories": inter,
                "n_intersection": len(inter),
                "n_gold_cats_in_bucket": n_gold,
                "n_pred_cats_in_bucket": n_pred,
                "gold_overlap": gold_o,
                "pred_overlap": pred_o,
            }
        )

    if not rows:
        return {
            "n_scored": 0,
            "n_skipped_empty_intersection": n_skip,
            "n_total": len(refs),
        }

    golds = [r["gold_overlap"] for r in rows]
    hyps = [r["pred_overlap"] for r in rows]
    g_emb = embedder.encode(
        golds, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
    )
    h_emb = embedder.encode(
        hyps, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
    )
    cosines = (g_emb * h_emb).sum(axis=1)

    scored = []
    for i, r in enumerate(rows):
        rouge = rouge_prf(r["gold_overlap"], r["pred_overlap"])
        # keep only the keys we care about (+ rouge2 if present)
        entry = {
            "idx": r["idx"],
            "repo": r["repo"],
            "format": r["format"],
            "n_intersection": r["n_intersection"],
            "n_gold_cats_in_bucket": r["n_gold_cats_in_bucket"],
            "n_pred_cats_in_bucket": r["n_pred_cats_in_bucket"],
            "overlap_categories": r["overlap_categories"],
            "rouge1_f": rouge["rouge1_f"],
            "rougeL_f": rouge["rougeL_f"],
            "embedding_cosine": float(cosines[i]),
        }
        # also store P/R for completeness
        for k in ("rouge1_p", "rouge1_r", "rougeL_p", "rougeL_r"):
            entry[k] = rouge[k]
        scored.append(entry)

    def col(key: str) -> list[float]:
        return [float(s[key]) for s in scored]

    agg = {
        "n_scored": len(scored),
        "n_skipped_empty_intersection": n_skip,
        "n_total": len(refs),
        "mean_n_intersection": statistics.mean(col("n_intersection")),
        "mean_n_gold_cats_in_bucket": statistics.mean(col("n_gold_cats_in_bucket")),
        "mean_n_pred_cats_in_bucket": statistics.mean(col("n_pred_cats_in_bucket")),
    }
    for key in (
        "rouge1_p",
        "rouge1_r",
        "rouge1_f",
        "rougeL_p",
        "rougeL_r",
        "rougeL_f",
        "embedding_cosine",
    ):
        m, s = mean_std(col(key))
        agg[key] = m
        agg[f"{key}_std"] = s

    return {
        "summary": round_dict(agg),
        "per_file": [round_dict(s) for s in scored],
    }


def fmt4(v) -> str:
    if v is None:
        return "n/a"
    return f"{float(v):.4f}"


def main() -> None:
    t0 = time.time()
    refs = json.loads(REFS_PATH.read_text(encoding="utf-8"))
    preds = {
        mode: json.loads((PRED_DIR / f"{mode}.json").read_text(encoding="utf-8"))
        for mode in APPROACHES
    }
    per_cat_payload = json.loads(PER_CAT_PATH.read_text(encoding="utf-8"))
    per_cat_by = per_cat_payload.get("by_approach") or {}

    print(f"Loading embedder ({EMBED_MODEL})...")
    embedder = SentenceTransformer(EMBED_MODEL)

    overlap_by: dict = {}
    section_agg_by: dict = {}

    for mode in APPROACHES:
        print(f"\n=== {mode} ===")
        hyp_map = preds[mode]
        overlap_by[mode] = {}
        section_agg_by[mode] = {}
        for bucket_name, cats in BUCKETS.items():
            print(f"  scoring {bucket_name} ({len(cats)} cats)...")
            result = score_bucket(refs, hyp_map, cats, embedder)
            overlap_by[mode][bucket_name] = result
            s = result["summary"]
            print(
                f"    n={s['n_scored']} skip={s['n_skipped_empty_intersection']} "
                f"mean_n∩={s.get('mean_n_intersection', 0):.2f} "
                f"R1-F={s.get('rouge1_f', 0):.4f} RL-F={s.get('rougeL_f', 0):.4f} "
                f"emb={s.get('embedding_cosine', 0):.4f}"
            )
            section_agg_by[mode][bucket_name] = aggregate_from_per_category(
                per_cat_by.get(mode) or {}, cats
            )

    neither = [c for c in ORDER if c not in set(REQUIRED) | set(GAP)]
    elapsed = round(time.time() - t0, 1)

    # Compact table summary for JSON
    table = {}
    for mode in APPROACHES:
        table[mode] = {}
        for bucket_name in BUCKETS:
            s = overlap_by[mode][bucket_name]["summary"]
            micro = (section_agg_by[mode][bucket_name].get("micro") or {})
            macro = (section_agg_by[mode][bucket_name].get("macro") or {})
            table[mode][bucket_name] = {
                "overlap_concat": {
                    "n_scored": s.get("n_scored"),
                    "mean_n_intersection": s.get("mean_n_intersection"),
                    "rouge1_f": s.get("rouge1_f"),
                    "rougeL_f": s.get("rougeL_f"),
                    "embedding_cosine": s.get("embedding_cosine"),
                },
                "section_pair_micro": micro,
                "section_pair_macro": macro,
                "n_section_pairs": section_agg_by[mode][bucket_name].get(
                    "n_section_pairs"
                ),
            }

    payload = {
        "description": (
            "Generation metrics on gold∩pred AGIT sections, scored separately for "
            "REQUIRED vs GAP category sets. Primary: concatenate ∩ within each set "
            "(ORDER), then ROUGE-1/L F + MiniLM emb cosine (macro over files). "
            "Secondary: aggregate existing metrics_per_category.json "
            "(macro over categories; micro = n_scored-weighted over section pairs)."
        ),
        "sources": {
            "REQUIRED": [
                "build_generic_instruction_template.REQUIRED10",
                "instruction_linter.REQUIRED_CATEGORIES",
                "build_dataset.REQUIRED_CATEGORIES",
            ],
            "GAP": [
                "build_generic_instruction_template.GAP5",
                "instruction_linter.GAP_CATEGORIES",
                "build_dataset.GAP_CATEGORIES",
            ],
        },
        "REQUIRED": REQUIRED,
        "GAP": GAP,
        "neither_in_ORDER": neither,
        "n_test": len(refs),
        "openai_model": "gpt-4o-mini",
        "embed_model": EMBED_MODEL,
        "embed_normalize": True,
        "empty_intersection_policy": "skip (excluded from macro-average)",
        "elapsed_sec": elapsed,
        "table": table,
        "overlap_concat_by_approach": {
            mode: {
                bucket: overlap_by[mode][bucket]["summary"] for bucket in BUCKETS
            }
            for mode in APPROACHES
        },
        "section_pair_agg_from_per_category": section_agg_by,
        "per_file": {
            mode: {
                bucket: overlap_by[mode][bucket].get("per_file", [])
                for bucket in BUCKETS
            }
            for mode in APPROACHES
        },
    }

    out_json = OUT / "metrics_required_vs_gap.json"
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {out_json}")

    # Markdown summary
    lines = [
        "# REQUIRED vs GAP metrics — 4-format fulltest",
        "",
        f"n={len(refs)} kept 4-format files; model=`gpt-4o-mini`; "
        f"embed=`{EMBED_MODEL}` (normalize=True).",
        "",
        "## Category lists",
        "",
        "Official lists from `build_generic_instruction_template.REQUIRED10` / `GAP5` "
        "(same as `instruction_linter` and `build_dataset`).",
        "",
        f"**REQUIRED ({len(REQUIRED)}):**",
        "",
    ]
    for c in REQUIRED:
        lines.append(f"- {c}")
    lines.extend(["", f"**GAP ({len(GAP)}):**", ""])
    for c in GAP:
        lines.append(f"- {c}")
    lines.extend(
        [
            "",
            f"**Neither (in ORDER, not scored here):** {', '.join(neither)}",
            "",
            "## Primary: overlap-concat within bucket (gold ∩ pred ∩ set)",
            "",
            "Per file: keep only categories in the bucket that appear in both gold and "
            "pred; concatenate in AGIT `ORDER` with `##` headings; score; macro-average "
            "over files with ≥1 intersecting category in that bucket.",
            "",
            "| Approach | Bucket | n_scored | mean n_∩ | R1-F | RL-F | Emb Cosine |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for mode in APPROACHES:
        for bucket in ("REQUIRED", "GAP"):
            s = overlap_by[mode][bucket]["summary"]
            lines.append(
                f"| {mode} | {bucket} | {s.get('n_scored')} | "
                f"{fmt4(s.get('mean_n_intersection'))} | "
                f"{fmt4(s.get('rouge1_f'))} | {fmt4(s.get('rougeL_f'))} | "
                f"{fmt4(s.get('embedding_cosine'))} |"
            )

    lines.extend(
        [
            "",
            "## Secondary: from `metrics_per_category.json` (section pairs)",
            "",
            "Macro = unweighted mean over categories with n_scored>0. "
            "Micro = n_scored-weighted mean over section-pair instances (preferred).",
            "",
            "| Approach | Bucket | n_pairs | Micro R1-F | Micro RL-F | Micro Emb | Macro R1-F | Macro RL-F | Macro Emb |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for mode in APPROACHES:
        for bucket in ("REQUIRED", "GAP"):
            agg = section_agg_by[mode][bucket]
            mi = agg.get("micro") or {}
            ma = agg.get("macro") or {}
            lines.append(
                f"| {mode} | {bucket} | {agg.get('n_section_pairs')} | "
                f"{fmt4(mi.get('rouge1_f'))} | {fmt4(mi.get('rougeL_f'))} | "
                f"{fmt4(mi.get('embedding_cosine'))} | "
                f"{fmt4(ma.get('rouge1_f'))} | {fmt4(ma.get('rougeL_f'))} | "
                f"{fmt4(ma.get('embedding_cosine'))} |"
            )

    lines.extend(
        [
            "",
            "## Compact table (primary overlap-concat)",
            "",
            "| | Required RL-F | Required R1-F | Required Emb | Gap RL-F | Gap R1-F | Gap Emb |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for mode in APPROACHES:
        zr = overlap_by[mode]["REQUIRED"]["summary"]
        zg = overlap_by[mode]["GAP"]["summary"]
        label = "ZS" if mode == "zero_shot" else "RAG"
        lines.append(
            f"| {label} | {fmt4(zr.get('rougeL_f'))} | {fmt4(zr.get('rouge1_f'))} | "
            f"{fmt4(zr.get('embedding_cosine'))} | {fmt4(zg.get('rougeL_f'))} | "
            f"{fmt4(zg.get('rouge1_f'))} | {fmt4(zg.get('embedding_cosine'))} |"
        )

    lines.extend(
        [
            "",
            "## Paths",
            "",
            f"- Metrics JSON: `{out_json}`",
            f"- Per-category source: `{PER_CAT_PATH}`",
            f"- Predictions: `{PRED_DIR}`",
            "",
        ]
    )

    out_md = OUT / "summary_required_vs_gap.md"
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_md}")

    # Append pointer to main summary.md
    summary_path = OUT / "summary.md"
    summary_text = summary_path.read_text(encoding="utf-8")
    pointer = (
        "\n## REQUIRED vs GAP\n\n"
        "See `summary_required_vs_gap.md` and `metrics_required_vs_gap.json` "
        "for overlap metrics restricted to the official 10 REQUIRED vs 5 GAP "
        "AGIT categories.\n"
    )
    if "REQUIRED vs GAP" not in summary_text:
        summary_path.write_text(summary_text.rstrip() + "\n" + pointer, encoding="utf-8")
        print(f"Updated {summary_path}")


if __name__ == "__main__":
    main()
