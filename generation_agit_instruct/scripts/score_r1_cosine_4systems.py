#!/usr/bin/env python3
"""ROUGE-1 F1 + MiniLM cosine for 4 with-template systems on n=62 4fmt.

A/B: reuse published gpt-4o-mini + CodeLlama R1 (and CL overlap cosine);
      compute only the missing CodeLlama full-file embedding_cosine.
C:  reuse gpt-4o-mini per-category from metrics_per_category.json;
      score CodeLlama per-category with LEGACY Ownership probes (published
      content pipeline; fixed Ownership used only in presence tables).
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
from rouge_score import rouge_scorer as rouge_lib
from sentence_transformers import SentenceTransformer

SCRIPTS = Path(__file__).resolve().parent
PKG_GEN = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

from agit_categories import ORDER, CATEGORY_PROBES, match_category  # noqa: E402
import agit_categories as ac  # noqa: E402

OUT = PKG_GEN / "results"
PRED = OUT / "filtered_predictions"
CL_BASE_PRED = PRED / "codellama13b_base.json"
CL_LORA_PRED = PRED / "codellama13b_qlora.json"
CL_BASE_CMP = OUT / "systems" / "codellama13b_base_metrics_comparison.json"
EMBED_MODEL = "all-MiniLM-L6-v2"

# Published content pipeline Ownership/Maintenance probes (pre-fix).
LEGACY_OWNERSHIP = [
    r"\bowner\b",
    r"\bcontact\b",
    r"\bmaintainer\b",
    r"\bcodeowner",
]
LEGACY_MAINTENANCE = [
    r"\bmaintain",
    r"\bstale\b",
    r"\bwhen to update\b",
    r"\bsync\b",
]

SYSTEMS = [
    ("gpt4o_mini_zero_shot", "gpt-4o-mini zero_shot"),
    ("gpt4o_mini_rag", "gpt-4o-mini RAG"),
    ("codellama13b_base", "CodeLlama-13B base"),
    ("codellama13b_qlora", "CodeLlama-13B QLoRA"),
]


def fmt(v, nd=4):
    if v is None:
        return "n/a"
    return f"{float(v):.{nd}f}"


def round4(x):
    if x is None:
        return None
    return round(float(x), 4)


def use_legacy_ownership_probes():
    """Match published content metrics (Ownership often n_∩=0 for template headings)."""
    CATEGORY_PROBES["Ownership / contacts"] = list(LEGACY_OWNERSHIP)
    CATEGORY_PROBES["Maintenance / when to update"] = list(LEGACY_MAINTENANCE)
    # Rebuild dict order: Ownership before Maintenance still via ORDER usage in match.
    # match_category iterates CATEGORY_PROBES insertion order — ensure Ownership first.
    items = list(CATEGORY_PROBES.items())
    # already Ownership before Maintenance in source; just overwrite values.


def sections_from_markdown(text: str):
    return ac.sections_from_markdown(text)


def load_refs():
    refs = json.loads((OUT / "filtered_predictions" / "test_refs.json").read_text())
    assert len(refs) == 62
    return refs


def hyp_map(path: Path, refs) -> dict[str, str]:
    raw = json.loads(path.read_text())
    return {str(r["idx"]): (raw.get(str(r["idx"]), "") or "") for r in refs}


def full_file_r1_cosine(refs, hyp_map_, embedder):
    scorer = rouge_lib.RougeScorer(["rouge1"], use_stemmer=True)
    golds = [r["output"] for r in refs]
    hyps = [hyp_map_.get(str(r["idx"]), "") or "" for r in refs]
    g_emb = embedder.encode(
        golds, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
    )
    h_emb = embedder.encode(
        hyps, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
    )
    cosines = (g_emb * h_emb).sum(axis=1)
    r1s = [float(scorer.score(g, h)["rouge1"].fmeasure) for g, h in zip(golds, hyps)]
    return {
        "n": len(refs),
        "rouge1_f": round4(statistics.mean(r1s)),
        "rouge1_f_std": round4(statistics.stdev(r1s) if len(r1s) > 1 else 0.0),
        "embedding_cosine": round4(float(np.mean(cosines))),
        "embedding_cosine_std": round4(float(np.std(cosines, ddof=1)) if len(cosines) > 1 else 0.0),
    }


def score_per_category(refs, hyp_map_, embedder):
    scorer = rouge_lib.RougeScorer(["rouge1"], use_stemmer=True)
    by_cat = {cat: {"golds": [], "hyps": []} for cat in ORDER}
    n_gold, n_pred, n_inter = Counter(), Counter(), Counter()

    for ref in refs:
        idx = str(ref["idx"])
        gold_secs = sections_from_markdown(ref["output"])
        pred_secs = sections_from_markdown(hyp_map_.get(idx, "") or "")
        for cat in ORDER:
            in_g, in_p = cat in gold_secs, cat in pred_secs
            if in_g:
                n_gold[cat] += 1
            if in_p:
                n_pred[cat] += 1
            if in_g and in_p:
                n_inter[cat] += 1
                g, p = gold_secs[cat], pred_secs[cat]
                g_h = (g.get("heading") or cat).strip()
                p_h = (p.get("heading") or cat).strip()
                by_cat[cat]["golds"].append(f"## {g_h}\n\n{g['content'].strip()}")
                by_cat[cat]["hyps"].append(f"## {p_h}\n\n{p['content'].strip()}")

    out = {}
    for cat in ORDER:
        golds, hyps = by_cat[cat]["golds"], by_cat[cat]["hyps"]
        entry = {
            "n_gold": int(n_gold[cat]),
            "n_pred": int(n_pred[cat]),
            "n_intersection": int(n_inter[cat]),
            "n_scored": len(golds),
            "rouge1_f": None,
            "embedding_cosine": None,
        }
        if golds:
            g_emb = embedder.encode(
                golds, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
            )
            h_emb = embedder.encode(
                hyps, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
            )
            cos = (g_emb * h_emb).sum(axis=1)
            r1s = [
                float(scorer.score(g, h)["rouge1"].fmeasure) for g, h in zip(golds, hyps)
            ]
            entry["rouge1_f"] = round4(statistics.mean(r1s))
            entry["embedding_cosine"] = round4(float(np.mean(cos)))
        out[cat] = entry
    return out


def compact_per_cat(by_cat: dict) -> dict:
    out = {}
    for cat in ORDER:
        e = by_cat.get(cat) or {}
        out[cat] = {
            "n_gold": e.get("n_gold"),
            "n_pred": e.get("n_pred"),
            "n_intersection": e.get("n_intersection"),
            "n_scored": e.get("n_scored"),
            "rouge1_f": e.get("rouge1_f"),
            "embedding_cosine": e.get("embedding_cosine"),
        }
    return out


def write_md(payload: dict, path: Path) -> None:
    full, ov, per = payload["full_file"], payload["overlap_sections"], payload["per_category"]
    lines = [
        "# ROUGE-1 F1 + embedding cosine — 4 with-template systems (n=62)",
        "",
        "Four-format filter sample (n=62; original fulltest n=77 → drop SKILL/GEMINI).",
        "No re-generation. Embed model: `all-MiniLM-L6-v2` (normalize_embeddings=True).",
        "Content metrics use the **published** section pipeline (legacy Ownership probes).",
        "Fixed Ownership probes are used only in presence/coverage tables elsewhere.",
        "",
        "## A) Full-file metrics (macro mean)",
        "",
        "| System | rouge1_f | embedding_cosine | n |",
        "|---|---:|---:|---:|",
    ]
    for key, label in SYSTEMS:
        s = full[key]
        lines.append(
            f"| {label} | {fmt(s['rouge1_f'])} | {fmt(s['embedding_cosine'])} | {s.get('n', '')} |"
        )

    lines.extend(
        [
            "",
            "## B) Overlapped-sections metrics (gold ∩ pred, macro mean)",
            "",
            "Empty intersection files skipped (excluded from macro-average).",
            "",
            "| System | rouge1_f | embedding_cosine | n_scored | n_skipped |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for key, label in SYSTEMS:
        s = ov[key]
        lines.append(
            f"| {label} | {fmt(s['rouge1_f'])} | {fmt(s['embedding_cosine'])} | "
            f"{s.get('n_scored', '')} | {s.get('n_skipped_empty_intersection', '')} |"
        )

    lines.extend(
        [
            "",
            "## C) Per-category (section-pair on gold ∩ pred for that category)",
            "",
            "Means over files where the category appears in **both** gold and prediction.",
            "",
            "### C1 — Per-category rouge1_f",
            "",
            "| Category | gpt-4o-mini zero_shot | gpt-4o-mini RAG | CodeLlama-13B base | CodeLlama-13B QLoRA | n_∩ (ZS / RAG / base / QLoRA) |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for cat in ORDER:
        cells, ns = [], []
        for key, _ in SYSTEMS:
            e = per[key][cat]
            cells.append(fmt(e.get("rouge1_f")))
            ns.append(str(e.get("n_scored") if e.get("n_scored") is not None else 0))
        lines.append(
            f"| {cat} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} | {' / '.join(ns)} |"
        )

    lines.extend(
        [
            "",
            "### C2 — Per-category embedding_cosine",
            "",
            "| Category | gpt-4o-mini zero_shot | gpt-4o-mini RAG | CodeLlama-13B base | CodeLlama-13B QLoRA | n_∩ (ZS / RAG / base / QLoRA) |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for cat in ORDER:
        cells, ns = [], []
        for key, _ in SYSTEMS:
            e = per[key][cat]
            cells.append(fmt(e.get("embedding_cosine")))
            ns.append(str(e.get("n_scored") if e.get("n_scored") is not None else 0))
        lines.append(
            f"| {cat} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} | {' / '.join(ns)} |"
        )

    lines.extend(
        [
            "",
            "## Sources / notes",
            "",
            "- gpt-4o-mini full / overlap / per-category: reused from "
            "`results/metrics_full.json`, `metrics_overlap.json`, `metrics_per_category.json`.",
            "- CodeLlama overlap R1 + cosine: reused from "
            "`results/systems/codellama13b_base_metrics_comparison.json` → `overlap_sections_4fmt`.",
            "- CodeLlama full-file R1: reused from `full_file_4fmt`; "
            "**embedding_cosine newly computed** (was missing from comparison export).",
            "- CodeLlama preds: `results/filtered_predictions/codellama13b_{base,qlora}.json`.",
            "- CodeLlama per-category: scored with legacy Ownership probes "
            "(published content pipeline).",
            f"- Embed model: `{payload['embed_model']}`",
            f"- Elapsed: {payload.get('elapsed_sec', 'n/a')}s",
            "",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {path}")


def main():
    t0 = time.time()
    use_legacy_ownership_probes()
    refs = load_refs()

    gpt_full = json.loads((OUT / "metrics_full.json").read_text())["summary"]
    gpt_ov = json.loads((OUT / "metrics_overlap.json").read_text())["summary"]
    gpt_per = json.loads((OUT / "metrics_per_category.json").read_text())["by_approach"]
    cmp = json.loads(CL_BASE_CMP.read_text())

    full_out = {
        "gpt4o_mini_zero_shot": {
            "n": gpt_full["zero_shot"]["n"],
            "rouge1_f": gpt_full["zero_shot"]["rouge1_f"],
            "rouge1_f_std": gpt_full["zero_shot"].get("rouge1_f_std"),
            "embedding_cosine": gpt_full["zero_shot"]["embedding_cosine"],
            "embedding_cosine_std": gpt_full["zero_shot"].get("embedding_cosine_std"),
            "source": "metrics_full.json",
        },
        "gpt4o_mini_rag": {
            "n": gpt_full["rag"]["n"],
            "rouge1_f": gpt_full["rag"]["rouge1_f"],
            "rouge1_f_std": gpt_full["rag"].get("rouge1_f_std"),
            "embedding_cosine": gpt_full["rag"]["embedding_cosine"],
            "embedding_cosine_std": gpt_full["rag"].get("embedding_cosine_std"),
            "source": "metrics_full.json",
        },
    }
    ov_out = {
        "gpt4o_mini_zero_shot": {
            "n_scored": gpt_ov["zero_shot"]["n_scored"],
            "n_skipped_empty_intersection": gpt_ov["zero_shot"]["n_skipped_empty_intersection"],
            "n_total": gpt_ov["zero_shot"].get("n_total", 62),
            "rouge1_f": gpt_ov["zero_shot"]["rouge1_f"],
            "rouge1_f_std": gpt_ov["zero_shot"].get("rouge1_f_std"),
            "embedding_cosine": gpt_ov["zero_shot"]["embedding_cosine"],
            "embedding_cosine_std": gpt_ov["zero_shot"].get("embedding_cosine_std"),
            "source": "metrics_overlap.json",
        },
        "gpt4o_mini_rag": {
            "n_scored": gpt_ov["rag"]["n_scored"],
            "n_skipped_empty_intersection": gpt_ov["rag"]["n_skipped_empty_intersection"],
            "n_total": gpt_ov["rag"].get("n_total", 62),
            "rouge1_f": gpt_ov["rag"]["rouge1_f"],
            "rouge1_f_std": gpt_ov["rag"].get("rouge1_f_std"),
            "embedding_cosine": gpt_ov["rag"]["embedding_cosine"],
            "embedding_cosine_std": gpt_ov["rag"].get("embedding_cosine_std"),
            "source": "metrics_overlap.json",
        },
    }
    per_out = {
        "gpt4o_mini_zero_shot": compact_per_cat(gpt_per["zero_shot"]),
        "gpt4o_mini_rag": compact_per_cat(gpt_per["rag"]),
    }

    print(f"Loading embedder {EMBED_MODEL}...")
    embedder = SentenceTransformer(EMBED_MODEL)

    for key, pred_path in (
        ("codellama13b_base", CL_BASE_PRED),
        ("codellama13b_qlora", CL_LORA_PRED),
    ):
        hm = hyp_map(pred_path, refs)
        print(f"Full-file R1+cosine for {key}...")
        scored = full_file_r1_cosine(refs, hm, embedder)
        pub = (cmp.get("full_file_4fmt") or {}).get(key) or {}
        # Prefer published R1 if present (pipeline parity); keep newly computed cosine.
        full_out[key] = {
            "n": scored["n"],
            "rouge1_f": pub.get("rouge1_f", scored["rouge1_f"]),
            "rouge1_f_std": scored.get("rouge1_f_std"),
            "rouge1_f_recomputed": scored["rouge1_f"],
            "embedding_cosine": scored["embedding_cosine"],
            "embedding_cosine_std": scored["embedding_cosine_std"],
            "source": "full_file_4fmt R1 + newly computed MiniLM cosine",
        }
        print(
            f"  R1 pub={full_out[key]['rouge1_f']} recomputed={scored['rouge1_f']} "
            f"cos={scored['embedding_cosine']}"
        )

        pub_o = (cmp.get("overlap_sections_4fmt") or {}).get(key) or {}
        ov_out[key] = {
            "n_scored": pub_o.get("n_scored"),
            "n_skipped_empty_intersection": pub_o.get("n_skipped_empty_intersection"),
            "n_total": 62,
            "rouge1_f": pub_o.get("rouge1_f"),
            "embedding_cosine": pub_o.get("embedding_cosine"),
            "source": "metrics_comparison.json overlap_sections_4fmt",
        }

        print(f"Per-category for {key}...")
        per_out[key] = score_per_category(refs, hm, embedder)

    elapsed = round(time.time() - t0, 1)
    payload = {
        "description": (
            "ROUGE-1 F1 + MiniLM embedding cosine for 4 with-template systems "
            "on n=62 four-format fulltest."
        ),
        "n_test": 62,
        "embed_model": EMBED_MODEL,
        "embed_normalize": True,
        "ownership_detector_for_content": "legacy (published pipeline)",
        "systems": [{"key": k, "label": lab} for k, lab in SYSTEMS],
        "full_file": full_out,
        "overlap_sections": ov_out,
        "per_category": per_out,
        "category_order": list(ORDER),
        "elapsed_sec": elapsed,
    }
    json_path = OUT / "metrics_r1_cosine_4systems.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {json_path}")
    write_md(payload, OUT / "metrics_r1_cosine_4systems.md")
    print(f"Done in {elapsed}s")


if __name__ == "__main__":
    main()
