#!/usr/bin/env python3
"""Filter generic_intent_fulltest to RQ2 four formats and recompute metrics.

PACKAGE NOTE: In this replication package the filtered predictions and
metrics already live under ../results/. Prefer reproduce_score_4fmt.py to
recompute metrics from those artifacts. This script expects the original
agit_model/exports/generic_intent_fulltest/ layout if re-filtering.

Does NOT re-generate predictions. Keeps files matching format_name_bucket from
build_agit_instruct_4fmt.py (AGENTS / CLAUDE / Copilot / Cursor). The 4fmt test
split is a different repo-holdout, so (repo, format) intersection is not used.
"""

from __future__ import annotations

import json
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from nltk.translate.bleu_score import SmoothingFunction, corpus_bleu
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer as rouge_lib
from sentence_transformers import SentenceTransformer

from format_buckets import format_name_bucket
from agit_categories import ORDER, sections_from_markdown
from metrics import lexical_and_structure_metrics
from score_overlap_sections import aligned_overlap_texts, mean_std, rouge_prf, round_dict

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "exports" / "generic_intent_fulltest"
OUT = ROOT / "exports" / "generic_intent_fulltest_4fmt"
REFS_PATH = SRC / "api_batch" / "test_refs.json"
PRED_DIR = SRC / "api_predictions"
EMBED_MODEL = "all-MiniLM-L6-v2"
APPROACHES = ("zero_shot", "rag")


def fmt(v, nd=4):
    if v is None:
        return "n/a"
    return f"{float(v):.{nd}f}"


def score_full_file(refs, hyp_map, embedder, bert_ok):
    scorer = rouge_lib.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    smoother = SmoothingFunction().method1
    golds = [r["output"] for r in refs]
    hyps = [hyp_map.get(str(r["idx"]), "") or "" for r in refs]

    g_emb = embedder.encode(
        golds, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
    )
    h_emb = embedder.encode(
        hyps, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
    )
    cosines = (g_emb * h_emb).sum(axis=1)

    bert_f1s = None
    if bert_ok:
        from bert_score import score as bert_score_fn

        print("  BERTScore (full-file)...")
        _, _, f1 = bert_score_fn(
            hyps, golds, lang="en", rescale_with_baseline=True, verbose=False
        )
        bert_f1s = f1.numpy() if hasattr(f1, "numpy") else np.asarray(f1)

    scored = []
    for i, r in enumerate(refs):
        hyp = hyps[i]
        scores = scorer.score(r["output"], hyp)
        row = {
            "idx": r["idx"],
            "repo": r["repo"],
            "format": r["format"],
            "rq2_type": r.get("rq2_type"),
        }
        for key, val in scores.items():
            row[f"{key}_p"] = float(val.precision)
            row[f"{key}_r"] = float(val.recall)
            row[f"{key}_f"] = float(val.fmeasure)
        try:
            lex = lexical_and_structure_metrics(r["output"], hyp)
            row["bleu"] = float(lex["bleu"])
            row["meteor"] = float(lex["meteor"])
        except Exception:
            row["bleu"] = float(
                corpus_bleu(
                    [[r["output"].split()]],
                    [hyp.split()],
                    smoothing_function=smoother,
                )
            )
            try:
                row["meteor"] = float(
                    meteor_score([r["output"].split()], hyp.split())
                )
            except Exception:
                row["meteor"] = 0.0
        row["embedding_cosine"] = float(cosines[i])
        if bert_f1s is not None:
            row["bertscore_f1"] = float(bert_f1s[i])
        scored.append(row)

    def col(key):
        return [float(s[key]) for s in scored]

    agg = {"n": len(scored)}
    for key in (
        "rouge1_p",
        "rouge1_r",
        "rouge1_f",
        "rouge2_p",
        "rouge2_r",
        "rouge2_f",
        "rougeL_p",
        "rougeL_r",
        "rougeL_f",
        "bleu",
        "meteor",
        "embedding_cosine",
    ):
        m, s = mean_std(col(key))
        agg[key] = m
        agg[f"{key}_std"] = s
    if bert_f1s is not None:
        m, s = mean_std(col("bertscore_f1"))
        agg["bertscore_f1"] = m
        agg["bertscore_f1_std"] = s
    agg["bleu_corpus"] = float(
        corpus_bleu(
            [[g.split()] for g in golds],
            [h.split() for h in hyps],
            smoothing_function=smoother,
        )
    )
    return round_dict(agg), [round_dict(s) for s in scored]


def score_overlap(refs, hyp_map, embedder, bert_ok):
    prepared = []
    skip = 0
    for ref in refs:
        idx = str(ref["idx"])
        gold_secs = sections_from_markdown(ref["output"])
        pred_secs = sections_from_markdown(hyp_map.get(idx, "") or "")
        gold_overlap, pred_overlap, inter = aligned_overlap_texts(gold_secs, pred_secs)
        if not inter:
            skip += 1
            continue
        prepared.append(
            {
                "idx": ref["idx"],
                "repo": ref["repo"],
                "format": ref["format"],
                "rq2_type": ref.get("rq2_type"),
                "overlap_categories": inter,
                "n_intersection": len(inter),
                "n_gold_cats": len(gold_secs),
                "n_pred_cats": len(pred_secs),
                "gold_overlap": gold_overlap,
                "pred_overlap": pred_overlap,
                "gold_overlap_chars": len(gold_overlap),
                "pred_overlap_chars": len(pred_overlap),
            }
        )

    if not prepared:
        return (
            {"n_scored": 0, "n_skipped_empty_intersection": skip, "n_total": len(refs)},
            [],
            skip,
        )

    golds = [r["gold_overlap"] for r in prepared]
    hyps = [r["pred_overlap"] for r in prepared]
    g_emb = embedder.encode(
        golds, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
    )
    h_emb = embedder.encode(
        hyps, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
    )
    cosines = (g_emb * h_emb).sum(axis=1)

    bert_f1s = None
    if bert_ok:
        from bert_score import score as bert_score_fn

        print("  BERTScore (overlap)...")
        _, _, f1 = bert_score_fn(
            hyps, golds, lang="en", rescale_with_baseline=True, verbose=False
        )
        bert_f1s = f1.numpy() if hasattr(f1, "numpy") else np.asarray(f1)

    smoother = SmoothingFunction().method1
    scored = []
    for i, r in enumerate(prepared):
        rouge = rouge_prf(r["gold_overlap"], r["pred_overlap"])
        try:
            lex = lexical_and_structure_metrics(r["gold_overlap"], r["pred_overlap"])
            bleu = float(lex["bleu"])
            meteor = float(lex["meteor"])
        except Exception:
            bleu = float(
                corpus_bleu(
                    [[r["gold_overlap"].split()]],
                    [r["pred_overlap"].split()],
                    smoothing_function=smoother,
                )
            )
            try:
                meteor = float(
                    meteor_score(
                        [r["gold_overlap"].split()], r["pred_overlap"].split()
                    )
                )
            except Exception:
                meteor = 0.0
        entry = {
            "idx": r["idx"],
            "repo": r["repo"],
            "format": r["format"],
            "rq2_type": r.get("rq2_type"),
            "n_intersection": r["n_intersection"],
            "n_gold_cats": r["n_gold_cats"],
            "n_pred_cats": r["n_pred_cats"],
            "overlap_categories": r["overlap_categories"],
            "gold_overlap_chars": r["gold_overlap_chars"],
            "pred_overlap_chars": r["pred_overlap_chars"],
            **rouge,
            "bleu": bleu,
            "meteor": meteor,
            "embedding_cosine": float(cosines[i]),
        }
        if bert_f1s is not None:
            entry["bertscore_f1"] = float(bert_f1s[i])
        scored.append(entry)

    def col(key):
        return [float(s[key]) for s in scored]

    agg = {
        "n_scored": len(scored),
        "n_skipped_empty_intersection": skip,
        "n_total": len(refs),
        "mean_n_intersection": statistics.mean(col("n_intersection")),
        "mean_n_gold_cats": statistics.mean(col("n_gold_cats")),
        "mean_n_pred_cats": statistics.mean(col("n_pred_cats")),
    }
    for key in (
        "rouge1_p",
        "rouge1_r",
        "rouge1_f",
        "rouge2_p",
        "rouge2_r",
        "rouge2_f",
        "rougeL_p",
        "rougeL_r",
        "rougeL_f",
        "bleu",
        "meteor",
        "embedding_cosine",
    ):
        m, s = mean_std(col(key))
        agg[key] = m
        agg[f"{key}_std"] = s
    if bert_f1s is not None:
        m, s = mean_std(col("bertscore_f1"))
        agg["bertscore_f1"] = m
        agg["bertscore_f1_std"] = s
    agg["bleu_corpus"] = float(
        corpus_bleu(
            [[g.split()] for g in golds],
            [h.split() for h in hyps],
            smoothing_function=smoother,
        )
    )
    return round_dict(agg), [round_dict(s) for s in scored], skip


def score_per_category(refs, hyp_map, embedder):
    """Per-category metrics on section pairs where gold∩pred contain the category."""
    scorer = rouge_lib.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)

    # Collect section texts per category
    by_cat = {
        cat: {"golds": [], "hyps": [], "files": []} for cat in ORDER
    }
    n_gold = Counter()
    n_pred = Counter()
    n_inter = Counter()

    for ref in refs:
        idx = str(ref["idx"])
        gold_secs = sections_from_markdown(ref["output"])
        pred_secs = sections_from_markdown(hyp_map.get(idx, "") or "")
        for cat in ORDER:
            in_g = cat in gold_secs
            in_p = cat in pred_secs
            if in_g:
                n_gold[cat] += 1
            if in_p:
                n_pred[cat] += 1
            if in_g and in_p:
                n_inter[cat] += 1
                g = gold_secs[cat]
                p = pred_secs[cat]
                g_h = (g.get("heading") or cat).strip()
                p_h = (p.get("heading") or cat).strip()
                g_txt = f"## {g_h}\n\n{g['content'].strip()}"
                p_txt = f"## {p_h}\n\n{p['content'].strip()}"
                by_cat[cat]["golds"].append(g_txt)
                by_cat[cat]["hyps"].append(p_txt)
                by_cat[cat]["files"].append(
                    {"idx": ref["idx"], "repo": ref["repo"], "format": ref["format"]}
                )

    out = {}
    for cat in ORDER:
        golds = by_cat[cat]["golds"]
        hyps = by_cat[cat]["hyps"]
        entry = {
            "n_gold": int(n_gold[cat]),
            "n_pred": int(n_pred[cat]),
            "n_intersection": int(n_inter[cat]),
            "n_scored": len(golds),
        }
        if not golds:
            entry.update(
                {
                    "rouge1_f": None,
                    "rougeL_f": None,
                    "embedding_cosine": None,
                }
            )
            out[cat] = entry
            continue

        r1s, rls, cos = [], [], []
        g_emb = embedder.encode(
            golds,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        h_emb = embedder.encode(
            hyps,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        cosines = (g_emb * h_emb).sum(axis=1)
        for i, (g, h) in enumerate(zip(golds, hyps)):
            sc = scorer.score(g, h)
            r1s.append(float(sc["rouge1"].fmeasure))
            rls.append(float(sc["rougeL"].fmeasure))
            cos.append(float(cosines[i]))
        entry["rouge1_f"] = float(statistics.mean(r1s))
        entry["rougeL_f"] = float(statistics.mean(rls))
        entry["embedding_cosine"] = float(statistics.mean(cos))
        entry["rouge1_f_std"] = (
            float(statistics.stdev(r1s)) if len(r1s) > 1 else 0.0
        )
        entry["rougeL_f_std"] = (
            float(statistics.stdev(rls)) if len(rls) > 1 else 0.0
        )
        entry["embedding_cosine_std"] = (
            float(statistics.stdev(cos)) if len(cos) > 1 else 0.0
        )
        out[cat] = round_dict(entry)
    return out


def write_summary(path, filter_meta, full, overlap, per_cat):
    lines = [
        "# Generic Intent Full Test — 4-Format Filter",
        "",
        "Existing fulltest predictions filtered to RQ2 four formats "
        "(AGENTS / CLAUDE / Copilot / Cursor) via `format_name_bucket` "
        "from `build_agit_instruct_4fmt.py`. No re-generation.",
        "",
        f"- Original n: **{filter_meta['n_original']}**",
        f"- Removed (non-4fmt): **{filter_meta['n_removed']}**",
        f"- Kept: **{filter_meta['n_kept']}**",
        f"- Removed formats: `{dict(filter_meta['removed_formats'])}`",
        f"- Kept by rq2_type: `{dict(filter_meta['kept_rq2_types'])}`",
        "- Model: `gpt-4o-mini`",
        f"- Embed model: `{EMBED_MODEL}` (normalize_embeddings=True)",
        "",
        "## Why not (repo, format) ∩ 4fmt test split?",
        "",
        f"Intersecting with `agit_instruct_4fmt_splits/generic_instruct_test.json` "
        f"keeps only **{filter_meta['n_intersect_4fmt_test']}** / "
        f"{filter_meta['n_original']} files — the 4fmt split is a new "
        "category-stratified repo-holdout, not a subset of the original 77. "
        "Format-rule filtering is used instead.",
        "",
        "## Full-file metrics (macro mean)",
        "",
        "| Approach | R1-P | R1-R | R1-F | R2-F | RL-P | RL-R | RL-F | BLEU | METEOR | BERTScore F1 | Emb Cosine | n |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for mode in APPROACHES:
        s = full["summary"][mode]
        lines.append(
            f"| {mode} | {fmt(s.get('rouge1_p'))} | {fmt(s.get('rouge1_r'))} | {fmt(s.get('rouge1_f'))} "
            f"| {fmt(s.get('rouge2_f'))} | {fmt(s.get('rougeL_p'))} | {fmt(s.get('rougeL_r'))} "
            f"| {fmt(s.get('rougeL_f'))} | {fmt(s.get('bleu'))} | {fmt(s.get('meteor'))} "
            f"| {fmt(s.get('bertscore_f1'))} | {fmt(s.get('embedding_cosine'))} | {s.get('n')} |"
        )

    lines.extend(
        [
            "",
            "## Overlap-section metrics (gold ∩ pred, macro mean)",
            "",
            "| Approach | R1-P | R1-R | R1-F | R2-F | RL-P | RL-R | RL-F | BLEU | METEOR | BERTScore F1 | Emb Cosine | n_scored |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for mode in APPROACHES:
        s = overlap["summary"][mode]
        lines.append(
            f"| {mode} | {fmt(s.get('rouge1_p'))} | {fmt(s.get('rouge1_r'))} | {fmt(s.get('rouge1_f'))} "
            f"| {fmt(s.get('rouge2_f'))} | {fmt(s.get('rougeL_p'))} | {fmt(s.get('rougeL_r'))} "
            f"| {fmt(s.get('rougeL_f'))} | {fmt(s.get('bleu'))} | {fmt(s.get('meteor'))} "
            f"| {fmt(s.get('bertscore_f1'))} | {fmt(s.get('embedding_cosine'))} "
            f"| {s.get('n_scored')} |"
        )

    lines.extend(
        [
            "",
            "## Per-category metrics (section pair, gold ∩ pred for that category)",
            "",
            "Means over filtered files where the category appears in **both** gold and prediction. "
            "`n_gold` / `n_pred` / `n_intersection` count files with the category on each side.",
            "",
        ]
    )
    for mode in APPROACHES:
        lines.extend(
            [
                f"### {mode}",
                "",
                "| Category | n_gold | n_pred | n_∩ | R1-F | RL-F | Emb Cosine |",
                "|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        cats = per_cat["by_approach"][mode]
        # sort by RL-F descending for readability, but keep ORDER in table
        for cat in ORDER:
            c = cats[cat]
            lines.append(
                f"| {cat} | {c['n_gold']} | {c['n_pred']} | {c['n_intersection']} "
                f"| {fmt(c.get('rouge1_f'))} | {fmt(c.get('rougeL_f'))} "
                f"| {fmt(c.get('embedding_cosine'))} |"
            )
        scored = [
            (cat, cats[cat])
            for cat in ORDER
            if cats[cat].get("rougeL_f") is not None
        ]
        scored.sort(key=lambda x: x[1]["rougeL_f"], reverse=True)
        lines.append("")
        if scored:
            lines.append(
                f"**Top 3 by RL-F:** "
                + "; ".join(
                    f"{c} ({v['rougeL_f']:.4f}, n={v['n_intersection']})"
                    for c, v in scored[:3]
                )
            )
            lines.append(
                f"**Bottom 3 by RL-F:** "
                + "; ".join(
                    f"{c} ({v['rougeL_f']:.4f}, n={v['n_intersection']})"
                    for c, v in scored[-3:]
                )
            )
        lines.append("")

    # Highlight RAG top/bottom
    rag = per_cat["by_approach"]["rag"]
    scored = [
        (cat, rag[cat]) for cat in ORDER if rag[cat].get("rougeL_f") is not None
    ]
    scored.sort(key=lambda x: x[1]["rougeL_f"], reverse=True)
    lines.extend(
        [
            "## RAG per-category ranking (RL-F)",
            "",
            "| Rank | Category | RL-F | R1-F | Emb | n_∩ |",
            "|---:|---|---:|---:|---:|---:|",
        ]
    )
    for i, (cat, v) in enumerate(scored, 1):
        lines.append(
            f"| {i} | {cat} | {fmt(v['rougeL_f'])} | {fmt(v['rouge1_f'])} "
            f"| {fmt(v['embedding_cosine'])} | {v['n_intersection']} |"
        )

    lines.extend(
        [
            "",
            "## Paths",
            "",
            f"- Output: `{OUT}`",
            f"- Filtered preds: `{OUT / 'filtered_predictions'}`",
            f"- Kept files: `{OUT / 'kept_files.json'}`",
            f"- Full metrics: `{OUT / 'metrics_full.json'}`",
            f"- Overlap metrics: `{OUT / 'metrics_overlap.json'}`",
            f"- Per-category: `{OUT / 'metrics_per_category.json'}`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "filtered_predictions").mkdir(parents=True, exist_ok=True)

    refs_all = json.loads(REFS_PATH.read_text(encoding="utf-8"))
    preds_all = {
        mode: json.loads((PRED_DIR / f"{mode}.json").read_text(encoding="utf-8"))
        for mode in APPROACHES
    }

    # Optional: report 4fmt-test intersection size for documentation
    test4_path = (
        ROOT / "exports" / "agit_instruct_4fmt_splits" / "generic_instruct_test.json"
    )
    n_intersect = 0
    if test4_path.exists():
        test4 = json.loads(test4_path.read_text(encoding="utf-8"))
        keys4 = {(x["repo"], x["format"]) for x in test4}
        n_intersect = sum(1 for r in refs_all if (r["repo"], r["format"]) in keys4)

    kept_refs = []
    removed_refs = []
    for r in refs_all:
        bucket = format_name_bucket(r["format"])
        if bucket:
            kept_refs.append({**r, "rq2_type": bucket})
        else:
            removed_refs.append({**r, "rq2_type": None})

    kept_idxs = {str(r["idx"]) for r in kept_refs}
    filter_meta = {
        "filter": "format_name_bucket (AGENTS/CLAUDE/Copilot/Cursor)",
        "n_original": len(refs_all),
        "n_kept": len(kept_refs),
        "n_removed": len(removed_refs),
        "n_intersect_4fmt_test": n_intersect,
        "removed_formats": dict(Counter(r["format"] for r in removed_refs)),
        "kept_formats": dict(Counter(r["format"] for r in kept_refs)),
        "kept_rq2_types": dict(Counter(r["rq2_type"] for r in kept_refs)),
        "removed_files": [
            {"idx": r["idx"], "repo": r["repo"], "format": r["format"]}
            for r in removed_refs
        ],
        "kept_files": [
            {
                "idx": r["idx"],
                "repo": r["repo"],
                "format": r["format"],
                "rq2_type": r["rq2_type"],
            }
            for r in kept_refs
        ],
    }

    (OUT / "kept_files.json").write_text(
        json.dumps(filter_meta["kept_files"], indent=2), encoding="utf-8"
    )
    (OUT / "removed_files.json").write_text(
        json.dumps(filter_meta["removed_files"], indent=2), encoding="utf-8"
    )
    (OUT / "filter_meta.json").write_text(
        json.dumps(filter_meta, indent=2), encoding="utf-8"
    )

    filtered_preds = {}
    for mode in APPROACHES:
        filtered_preds[mode] = {
            k: v for k, v in preds_all[mode].items() if k in kept_idxs
        }
        (OUT / "filtered_predictions" / f"{mode}.json").write_text(
            json.dumps(filtered_preds[mode], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    (OUT / "filtered_predictions" / "test_refs.json").write_text(
        json.dumps(kept_refs, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(
        f"Filter: kept {len(kept_refs)} / {len(refs_all)} "
        f"(removed {len(removed_refs)}; 4fmt-test ∩ would keep {n_intersect})"
    )
    print("Loading embedder...")
    embedder = SentenceTransformer(EMBED_MODEL)
    try:
        from bert_score import score as _bs  # noqa: F401

        bert_ok = True
    except Exception as e:
        print(f"BERTScore unavailable: {e}")
        bert_ok = False

    full_summary = {}
    full_per = {}
    ov_summary = {}
    ov_per = {}
    per_cat_by = {}

    for mode in APPROACHES:
        print(f"Scoring full-file ({mode})...")
        agg, per = score_full_file(kept_refs, filtered_preds[mode], embedder, bert_ok)
        full_summary[mode] = agg
        full_per[mode] = per
        print(
            f"  {mode} full: R1-F={agg['rouge1_f']:.4f} RL-F={agg['rougeL_f']:.4f} "
            f"emb={agg['embedding_cosine']:.4f}"
        )

        print(f"Scoring overlap ({mode})...")
        oagg, oper, skip = score_overlap(
            kept_refs, filtered_preds[mode], embedder, bert_ok
        )
        ov_summary[mode] = oagg
        ov_per[mode] = oper
        print(
            f"  {mode} overlap: R1-F={oagg.get('rouge1_f', 0):.4f} "
            f"RL-F={oagg.get('rougeL_f', 0):.4f} "
            f"emb={oagg.get('embedding_cosine', 0):.4f} "
            f"n={oagg.get('n_scored')} skip={skip}"
        )

        print(f"Scoring per-category ({mode})...")
        per_cat_by[mode] = score_per_category(
            kept_refs, filtered_preds[mode], embedder
        )

    elapsed = round(time.time() - t0, 1)

    full_payload = {
        "description": (
            "Full-file automated metrics on 4-format-filtered fulltest "
            "(no re-generation)."
        ),
        "filter": filter_meta,
        "n_test": len(kept_refs),
        "openai_model": "gpt-4o-mini",
        "embed_model": EMBED_MODEL,
        "embed_normalize": True,
        "bertscore": {
            "computed": bert_ok,
            "rescale_with_baseline": True,
            "lang": "en",
        },
        "summary": full_summary,
        "elapsed_sec": elapsed,
        "per_pair": full_per,
    }
    (OUT / "metrics_full.json").write_text(
        json.dumps(full_payload, indent=2), encoding="utf-8"
    )

    ov_payload = {
        "description": (
            "Overlap-section (gold∩pred) metrics on 4-format-filtered fulltest."
        ),
        "filter": {
            "n_kept": filter_meta["n_kept"],
            "n_removed": filter_meta["n_removed"],
        },
        "n_test": len(kept_refs),
        "openai_model": "gpt-4o-mini",
        "embed_model": EMBED_MODEL,
        "embed_normalize": True,
        "category_order": ORDER,
        "empty_intersection_policy": "skip (excluded from macro-average)",
        "bertscore": {
            "computed": bert_ok,
            "rescale_with_baseline": True,
            "lang": "en",
        },
        "summary": ov_summary,
        "elapsed_sec": elapsed,
        "per_pair": ov_per,
    }
    (OUT / "metrics_overlap.json").write_text(
        json.dumps(ov_payload, indent=2), encoding="utf-8"
    )

    # Rankings for RAG
    rag_rank = []
    for cat in ORDER:
        c = per_cat_by["rag"][cat]
        if c.get("rougeL_f") is not None:
            rag_rank.append(
                {
                    "category": cat,
                    "rougeL_f": c["rougeL_f"],
                    "rouge1_f": c["rouge1_f"],
                    "embedding_cosine": c["embedding_cosine"],
                    "n_intersection": c["n_intersection"],
                }
            )
    rag_rank.sort(key=lambda x: x["rougeL_f"], reverse=True)

    per_cat_payload = {
        "description": (
            "Per-category section-pair metrics. For each AGIT category, "
            "mean ROUGE-1/L F and MiniLM emb cosine over filtered files where "
            "the category appears in both gold and prediction. "
            "n_gold / n_pred / n_intersection count files with that category present."
        ),
        "n_test": len(kept_refs),
        "categories": ORDER,
        "embed_model": EMBED_MODEL,
        "by_approach": per_cat_by,
        "rag_ranking_by_rougeL_f": rag_rank,
        "elapsed_sec": elapsed,
    }
    (OUT / "metrics_per_category.json").write_text(
        json.dumps(per_cat_payload, indent=2), encoding="utf-8"
    )

    write_summary(
        OUT / "summary.md",
        filter_meta,
        full_payload,
        ov_payload,
        per_cat_payload,
    )

    print(f"\nWrote outputs under {OUT} ({elapsed}s)")
    print(f"Removed {filter_meta['n_removed']}, kept {filter_meta['n_kept']}")
    if rag_rank:
        print("RAG top RL-F:", rag_rank[0]["category"], rag_rank[0]["rougeL_f"])
        print("RAG bottom RL-F:", rag_rank[-1]["category"], rag_rank[-1]["rougeL_f"])


if __name__ == "__main__":
    main()
