#!/usr/bin/env python3
"""Three-tier metrics: Required(10), Gap(4), Recommended(2) on fulltest_4fmt n=62."""

from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

from rouge_score import rouge_scorer as rouge_lib
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "replication_package" / "generation_agit_instruct" / "scripts"))
from agit_categories import ORDER, sections_from_markdown  # noqa: E402

OUT = ROOT / "exports" / "generic_intent_fulltest_4fmt"
PRED_DIR = OUT / "filtered_predictions"
REFS_PATH = PRED_DIR / "test_refs.json"
EMBED_MODEL = "all-MiniLM-L6-v2"
APPROACHES = ("zero_shot", "rag")

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
# CORRECTED Gap(4): Security, Git/PR, Ownership, Maintenance
GAP = [
    "Security / secrets",
    "Git / PR / commit conventions",
    "Ownership / contacts",
    "Maintenance / when to update",
]
# CORRECTED Recommended(2): Project overview + Performance
RECOMMENDED = [
    "Project overview / purpose",
    "Performance",
]
BUCKETS = {"REQUIRED": REQUIRED, "GAP": GAP, "RECOMMENDED": RECOMMENDED}

EXPECTED_REQUIRED = {
    "zero_shot": {
        "rouge1_f": 0.359,
        "embedding_cosine": 0.687,
        "coverage": 0.739,
        "mean_count": 7.39,
        "ref_recall": 0.875,
    },
    "rag": {
        "rouge1_f": 0.396,
        "embedding_cosine": 0.692,
        "coverage": 0.692,
        "mean_count": 6.92,
        "ref_recall": 0.839,
    },
}


def round_half_up(x: float, nd: int = 3) -> float:
    """Round half up (paper-style); avoid banker's rounding of 0.3585→0.358."""
    from decimal import Decimal, ROUND_HALF_UP

    q = Decimal("1").scaleb(-nd)
    return float(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP))


def round_dict(d: dict, nd: int = 4) -> dict:
    out = {}
    for k, v in d.items():
        if isinstance(v, float):
            out[k] = round(v, nd)
        elif isinstance(v, dict):
            out[k] = round_dict(v, nd)
        else:
            out[k] = v
    return out

def mean_std(vals: list[float]) -> tuple[float, float]:
    if not vals:
        return 0.0, 0.0
    m = float(statistics.mean(vals))
    s = float(statistics.stdev(vals)) if len(vals) > 1 else 0.0
    return m, s


def rouge_prf(reference: str, hypothesis: str) -> dict:
    scorer = rouge_lib.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)
    scores = scorer.score(reference, hypothesis or "")
    out = {}
    for key, val in scores.items():
        out[f"{key}_p"] = float(val.precision)
        out[f"{key}_r"] = float(val.recall)
        out[f"{key}_f"] = float(val.fmeasure)
    return out


def aligned_overlap_in_set(
    gold_secs: dict, pred_secs: dict, cat_set: set[str]
) -> tuple[str, str, list[str]]:
    inter = [c for c in ORDER if c in cat_set and c in gold_secs and c in pred_secs]
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


def score_bucket(refs, hyp_map, cat_list, embedder) -> dict:
    cat_set = set(cat_list)
    rows = []
    n_skip = 0
    for ref in refs:
        idx = str(ref["idx"])
        gold_secs = sections_from_markdown(ref["output"])
        pred_secs = sections_from_markdown(hyp_map.get(idx, "") or "")
        gold_o, pred_o, inter = aligned_overlap_in_set(gold_secs, pred_secs, cat_set)
        if not inter:
            n_skip += 1
            continue
        rows.append(
            {
                "idx": ref["idx"],
                "n_intersection": len(inter),
                "overlap_categories": inter,
                "gold_overlap": gold_o,
                "pred_overlap": pred_o,
            }
        )
    if not rows:
        return {"summary": {"n_scored": 0, "n_skipped_empty_intersection": n_skip}}

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
        scored.append(
            {
                "idx": r["idx"],
                "n_intersection": r["n_intersection"],
                "overlap_categories": r["overlap_categories"],
                "rouge1_f": rouge["rouge1_f"],
                "rougeL_f": rouge["rougeL_f"],
                "embedding_cosine": float(cosines[i]),
            }
        )

    def col(key: str) -> list[float]:
        return [float(s[key]) for s in scored]

    agg = {
        "n_scored": len(scored),
        "n_skipped_empty_intersection": n_skip,
        "n_total": len(refs),
        "mean_n_intersection": statistics.mean(col("n_intersection")),
    }
    for key in ("rouge1_f", "rougeL_f", "embedding_cosine"):
        m, s = mean_std(col(key))
        agg[key] = m
        agg[f"{key}_std"] = s
    return {"summary": round_dict(agg)}


def compliance_for_bucket(refs, hyp_map, cats) -> dict:
    cat_set = set(cats)
    n_bucket = len(cats)
    coverages = []
    counts = []
    recalls = []
    for ref in refs:
        idx = str(ref["idx"])
        gold_secs = sections_from_markdown(ref["output"])
        pred_secs = sections_from_markdown(hyp_map.get(idx, "") or "")
        gold_in = {c for c in cat_set if c in gold_secs}
        pred_in = {c for c in cat_set if c in pred_secs}
        n_pred = len(pred_in)
        counts.append(n_pred)
        coverages.append(n_pred / n_bucket)
        if gold_in:
            recalls.append(len(gold_in & pred_in) / len(gold_in))
    return round_dict(
        {
            "coverage_mean": statistics.mean(coverages),
            "mean_count": statistics.mean(counts),
            "ref_recall_mean": statistics.mean(recalls) if recalls else None,
            "n_files": len(refs),
            "n_files_with_gold": sum(
                1
                for ref in refs
                if any(c in sections_from_markdown(ref["output"]) for c in cat_set)
            ),
        }
    )


def main() -> None:
    t0 = time.time()
    refs = json.loads(REFS_PATH.read_text(encoding="utf-8"))
    preds = {
        mode: json.loads((PRED_DIR / f"{mode}.json").read_text(encoding="utf-8"))
        for mode in APPROACHES
    }
    assert len(refs) == 62
    assert set(REQUIRED) | set(GAP) | set(RECOMMENDED) == set(ORDER)
    assert len(REQUIRED) == 10 and len(GAP) == 4 and len(RECOMMENDED) == 2
    assert not (
        set(REQUIRED) & set(GAP)
        or set(REQUIRED) & set(RECOMMENDED)
        or set(GAP) & set(RECOMMENDED)
    )

    print(f"Loading embedder ({EMBED_MODEL})...")
    embedder = SentenceTransformer(EMBED_MODEL)

    overlap_by: dict = {}
    compliance_by: dict = {}
    for mode in APPROACHES:
        print(f"\n=== {mode} ===")
        hyp_map = preds[mode]
        overlap_by[mode] = {}
        compliance_by[mode] = {}
        for name, cats in BUCKETS.items():
            print(f"  scoring {name} ({len(cats)})...")
            result = score_bucket(refs, hyp_map, cats, embedder)
            overlap_by[mode][name] = result
            comp = compliance_for_bucket(refs, hyp_map, cats)
            compliance_by[mode][name] = comp
            s = result["summary"]
            print(
                f"    R1-F={s.get('rouge1_f')} cos={s.get('embedding_cosine')} "
                f"cov={comp['coverage_mean']:.4f} mean={comp['mean_count']:.4f} "
                f"ref.recall={comp['ref_recall_mean']:.4f} n_scored={s.get('n_scored')}"
            )

    def pack_row(tier_label, mode_label, mode_key, bucket):
        s = overlap_by[mode_key][bucket]["summary"]
        c = compliance_by[mode_key][bucket]
        return {
            "tier": tier_label,
            "approach": mode_label,
            "rouge1_f": round_half_up(s["rouge1_f"], 3),
            "embedding_cosine": round_half_up(s["embedding_cosine"], 3),
            "coverage": round_half_up(c["coverage_mean"], 3),
            "mean_count": round_half_up(c["mean_count"], 2),
            "ref_recall": round_half_up(c["ref_recall_mean"], 3),
            "rouge1_f_raw": s["rouge1_f"],
            "embedding_cosine_raw": s["embedding_cosine"],
            "coverage_raw": c["coverage_mean"],
            "mean_count_raw": c["mean_count"],
            "ref_recall_raw": c["ref_recall_mean"],
            "n_scored_overlap": s.get("n_scored"),
            "n_skipped_empty_intersection": s.get("n_skipped_empty_intersection"),
        }

    table_rows = []
    latex_rows = []
    for bucket, label in [
        ("REQUIRED", "Required (10)"),
        ("GAP", "Gap (4)"),
        ("RECOMMENDED", "Recommended (2)"),
    ]:
        for mode_key, mode_label in [("zero_shot", "Zero-shot"), ("rag", "RAG")]:
            r = pack_row(label, mode_label, mode_key, bucket)
            table_rows.append(r)
            latex_rows.append(
                f"{r['tier']} & {r['approach']} & {r['rouge1_f']:.3f} & "
                f"{r['embedding_cosine']:.3f} & {r['coverage']:.3f} & "
                f"{r['mean_count']:.2f} & {r['ref_recall']:.3f} \\\\"
            )

    required_confirmation = {}
    for mode in APPROACHES:
        s = overlap_by[mode]["REQUIRED"]["summary"]
        c = compliance_by[mode]["REQUIRED"]
        got = {
            "rouge1_f": round_half_up(s["rouge1_f"], 3),
            "embedding_cosine": round_half_up(s["embedding_cosine"], 3),
            "coverage": round_half_up(c["coverage_mean"], 3),
            "mean_count": round_half_up(c["mean_count"], 2),
            "ref_recall": round_half_up(c["ref_recall_mean"], 3),
        }
        exp = EXPECTED_REQUIRED[mode]
        required_confirmation[mode] = {
            "expected": exp,
            "got": got,
            "match": all(abs(got[k] - exp[k]) <= 0.002 for k in exp),
        }

    payload = {
        "description": (
            "Three-tier template metrics on generic_intent_fulltest_4fmt (n=62). "
            "Required (10) unchanged from REQUIRED10. Gap (4) = Security / secrets, "
            "Git / PR / commit conventions, Ownership / contacts, Maintenance / when to update. "
            "Recommended (2) = Project overview / purpose + Performance. "
            "R1-F/cosine: overlap-concat within bucket (gold∩pred∩bucket), MiniLM cosine, "
            "macro over files with ≥1 intersection. Coverage = |pred∩bucket|/|bucket|; "
            "mean count = mean |pred∩bucket|; ref.recall = |gold∩bucket∩pred|/|gold∩bucket|."
        ),
        "tier_definitions": {
            "REQUIRED": REQUIRED,
            "GAP": GAP,
            "RECOMMENDED": RECOMMENDED,
            "rationale": {
                "REQUIRED": (
                    "build_generic_instruction_template.REQUIRED10 / "
                    "instruction_linter.REQUIRED_CATEGORIES (unchanged)"
                ),
                "GAP": (
                    "Corrected Gap(4): Security / secrets, Git / PR / commit conventions, "
                    "Ownership / contacts, Maintenance / when to update "
                    "(Performance moved to Recommended; Git/PR into Gap)"
                ),
                "RECOMMENDED": (
                    "Project overview / purpose + Performance; "
                    "with Required+Gap covers all 16 taxonomy categories"
                ),
            },
            "covers_all_16": sorted(set(REQUIRED) | set(GAP) | set(RECOMMENDED))
            == sorted(ORDER),
            "former_GAP5": [
                "Security / secrets",
                "Performance",
                "Maintenance / when to update",
                "Project overview / purpose",
                "Ownership / contacts",
            ],
        },
        "n_test": len(refs),
        "openai_model": "gpt-4o-mini",
        "embed_model": EMBED_MODEL,
        "embed_normalize": True,
        "required_confirmation": required_confirmation,
        "table_rows": table_rows,
        "latex_rows": latex_rows,
        "overlap_by_approach": {
            mode: {bucket: overlap_by[mode][bucket]["summary"] for bucket in BUCKETS}
            for mode in APPROACHES
        },
        "compliance_by_approach": compliance_by,
        "elapsed_sec": round(time.time() - t0, 1),
    }

    out_path = OUT / "metrics_three_tiers.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\nWrote", out_path)
    print("\nRequired confirmation:", json.dumps(required_confirmation, indent=2))
    print("\nLaTeX rows:")
    for line in latex_rows:
        print(line)


if __name__ == "__main__":
    main()
