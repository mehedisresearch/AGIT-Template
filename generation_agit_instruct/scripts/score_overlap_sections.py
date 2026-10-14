#!/usr/bin/env python3
"""Score generic-intent predictions on overlapping AGIT sections only (gold intersect pred)."""

from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

import numpy as np
from nltk.translate.bleu_score import SmoothingFunction, corpus_bleu
from nltk.translate.meteor_score import meteor_score
from rouge_score import rouge_scorer as rouge_lib
from sentence_transformers import SentenceTransformer

from agit_categories import ORDER, sections_from_markdown
from metrics import lexical_and_structure_metrics

ROOT = Path(__file__).resolve().parent.parent  # generation_agit_instruct/
OUT = ROOT / "results"  # package layout; prefer reproduce_score_4fmt.py
REFS_PATH = OUT / "api_batch" / "test_refs.json"
PRED_DIR = OUT / "api_predictions"
FULL_METRICS = OUT / "metrics.json"
FULL_EXTENDED = OUT / "metrics_extended.json"

EMBED_MODEL = "all-MiniLM-L6-v2"
APPROACHES = ("zero_shot", "rag")


def aligned_overlap_texts(
    gold_secs: dict[str, dict], pred_secs: dict[str, dict]
) -> tuple[str, str, list[str]]:
    """Concatenate intersecting categories in ORDER; include ## heading each section."""
    inter = [c for c in ORDER if c in gold_secs and c in pred_secs]
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


def rouge_prf(reference: str, hypothesis: str) -> dict:
    scorer = rouge_lib.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    scores = scorer.score(reference, hypothesis or "")
    out = {}
    for key, val in scores.items():
        out[f"{key}_p"] = float(val.precision)
        out[f"{key}_r"] = float(val.recall)
        out[f"{key}_f"] = float(val.fmeasure)
    return out


def mean_std(vals: list[float]) -> tuple[float, float]:
    if not vals:
        return 0.0, 0.0
    m = float(statistics.mean(vals))
    s = float(statistics.stdev(vals)) if len(vals) > 1 else 0.0
    return m, s


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


def load_fullfile_baselines() -> dict:
    """Pull full-file R1-F, RL-F, emb cosine from prior metric files."""
    base: dict = {}
    if FULL_METRICS.exists():
        m = json.loads(FULL_METRICS.read_text())
        for mode in APPROACHES:
            key = f"gpt-4o-mini_{mode}"
            agg = (m.get("summary") or {}).get(key) or {}
            base[mode] = {
                "rouge1_f": agg.get("rouge1_f"),
                "rougeL_f": agg.get("rougeL_f"),
            }
    if FULL_EXTENDED.exists():
        e = json.loads(FULL_EXTENDED.read_text())
        for mode in APPROACHES:
            key = f"gpt-4o-mini_{mode}"
            agg = (e.get("summary") or {}).get(key) or {}
            base.setdefault(mode, {})
            base[mode]["embedding_cosine"] = agg.get("embedding_cosine_mean")
            base[mode]["bleu"] = agg.get("bleu")
            base[mode]["meteor"] = agg.get("meteor")
            base[mode]["bertscore_f1"] = agg.get("bertscore_f1")
            base[mode]["rouge1_f"] = base[mode].get("rouge1_f") or agg.get(
                "rouge1_f_prior"
            )
            base[mode]["rougeL_f"] = base[mode].get("rougeL_f") or agg.get(
                "rougeL_f_prior"
            )
    return base


def main() -> None:
    t0 = time.time()
    refs = json.loads(REFS_PATH.read_text(encoding="utf-8"))
    preds = {
        mode: json.loads((PRED_DIR / f"{mode}.json").read_text(encoding="utf-8"))
        for mode in APPROACHES
    }

    prepared: dict[str, list[dict]] = {mode: [] for mode in APPROACHES}
    skip_counts: dict[str, int] = {mode: 0 for mode in APPROACHES}

    for ref in refs:
        idx = str(ref["idx"])
        gold_secs = sections_from_markdown(ref["output"])
        for mode in APPROACHES:
            hyp = preds[mode].get(idx, "") or ""
            pred_secs = sections_from_markdown(hyp)
            gold_overlap, pred_overlap, inter = aligned_overlap_texts(
                gold_secs, pred_secs
            )
            n_gold = len(gold_secs)
            n_pred = len(pred_secs)
            n_inter = len(inter)
            if n_inter == 0:
                skip_counts[mode] += 1
                continue
            prepared[mode].append(
                {
                    "idx": ref["idx"],
                    "repo": ref["repo"],
                    "format": ref["format"],
                    "language": ref.get("language"),
                    "overlap_categories": inter,
                    "n_intersection": n_inter,
                    "n_gold_cats": n_gold,
                    "n_pred_cats": n_pred,
                    "gold_overlap": gold_overlap,
                    "pred_overlap": pred_overlap,
                    "gold_overlap_chars": len(gold_overlap),
                    "pred_overlap_chars": len(pred_overlap),
                }
            )

    print("Loading embedder...")
    embedder = SentenceTransformer(EMBED_MODEL)

    try:
        from bert_score import score as bert_score_fn

        bert_ok = True
    except Exception as e:
        print(f"BERTScore unavailable: {e}")
        bert_ok = False

    smoother = SmoothingFunction().method1
    summary: dict = {}
    per_pair: dict = {}

    for mode in APPROACHES:
        rows = prepared[mode]
        print(
            f"{mode}: scoring {len(rows)} files "
            f"(skipped {skip_counts[mode]} empty intersection)"
        )
        if not rows:
            summary[mode] = {
                "n_scored": 0,
                "n_skipped_empty_intersection": skip_counts[mode],
            }
            per_pair[mode] = []
            continue

        golds = [r["gold_overlap"] for r in rows]
        hyps = [r["pred_overlap"] for r in rows]

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

        bert_f1s = None
        if bert_ok:
            print(f"  BERTScore ({mode})...")
            _, _, f1 = bert_score_fn(
                hyps, golds, lang="en", rescale_with_baseline=True, verbose=False
            )
            bert_f1s = f1.numpy() if hasattr(f1, "numpy") else np.asarray(f1)

        scored = []
        for i, r in enumerate(rows):
            rouge = rouge_prf(r["gold_overlap"], r["pred_overlap"])
            try:
                lex = lexical_and_structure_metrics(
                    r["gold_overlap"], r["pred_overlap"]
                )
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

        def col(key: str) -> list[float]:
            return [float(s[key]) for s in scored]

        agg = {
            "n_scored": len(scored),
            "n_skipped_empty_intersection": skip_counts[mode],
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

        summary[mode] = round_dict(agg)
        per_pair[mode] = [round_dict(s) for s in scored]
        print(
            f"  {mode}: R1-F={agg['rouge1_f']:.4f} RL-F={agg['rougeL_f']:.4f} "
            f"emb={agg['embedding_cosine']:.4f} n={agg['n_scored']}"
        )

    full_base = load_fullfile_baselines()
    comparison = {}
    for mode in APPROACHES:
        comparison[mode] = {
            "full_file": full_base.get(mode, {}),
            "overlap_sections": {
                "rouge1_f": summary[mode].get("rouge1_f"),
                "rougeL_f": summary[mode].get("rougeL_f"),
                "embedding_cosine": summary[mode].get("embedding_cosine"),
                "bleu": summary[mode].get("bleu"),
                "meteor": summary[mode].get("meteor"),
                "bertscore_f1": summary[mode].get("bertscore_f1"),
                "n_scored": summary[mode].get("n_scored"),
            },
        }

    elapsed = round(time.time() - t0, 1)
    desc = (
        "Automated metrics on gold∩pred AGIT category sections only. "
        "Per file: parse sections via sections_from_markdown/match_category; "
        "concatenate intersecting categories in ORDER with ## headings; "
        "macro-average over files with >=1 overlapping category "
        "(empty intersection skipped)."
    )
    payload = {
        "description": desc,
        "n_test": len(refs),
        "openai_model": "gpt-4o-mini",
        "embed_model": EMBED_MODEL,
        "embed_normalize": True,
        "category_order": ORDER,
        "empty_intersection_policy": "skip (excluded from macro-average)",
        "skip_counts": skip_counts,
        "bertscore": {
            "computed": bert_ok,
            "rescale_with_baseline": True,
            "lang": "en",
        },
        "summary": summary,
        "comparison_full_vs_overlap": comparison,
        "elapsed_sec": elapsed,
        "per_pair": per_pair,
    }

    json_path = OUT / "metrics_overlap_sections.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Generic Intent Full Test — Overlap Sections Metrics",
        "",
        "Scores use **only categories present in both gold and prediction** "
        "(gold ∩ pred), concatenated in the AGIT `ORDER` with `##` headings.",
        "",
        f"- Test size: **{len(refs)}**",
        "- Model: `gpt-4o-mini`",
        f"- Embed model: `{EMBED_MODEL}` (normalize_embeddings=True)",
        "- Empty ∩ policy: **skip** (excluded from macro-average)",
        f"- Elapsed: {elapsed}s",
        "",
        "## Skip / coverage counts",
        "",
        "| Approach | Scored (>=1 ∩) | Skipped (empty ∩) | Mean |∩| | Mean |gold cats| | Mean |pred cats| |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for mode in APPROACHES:
        s = summary[mode]
        lines.append(
            f"| {mode} | {s.get('n_scored', 0)} | {s.get('n_skipped_empty_intersection', 0)} "
            f"| {s.get('mean_n_intersection', 0):.2f} | {s.get('mean_n_gold_cats', 0):.2f} "
            f"| {s.get('mean_n_pred_cats', 0):.2f} |"
        )

    lines.extend(
        [
            "",
            "## Overlap-section metrics (macro mean)",
            "",
            "| Approach | R1-P | R1-R | R1-F | R2-F | RL-P | RL-R | RL-F | BLEU | METEOR | BERTScore F1 | Emb Cosine |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for mode in APPROACHES:
        s = summary[mode]
        bs = s.get("bertscore_f1")
        bs_s = f"{bs:.4f}" if bs is not None else "n/a"
        lines.append(
            f"| {mode} | {s.get('rouge1_p', 0):.4f} | {s.get('rouge1_r', 0):.4f} | {s.get('rouge1_f', 0):.4f} "
            f"| {s.get('rouge2_f', 0):.4f} | {s.get('rougeL_p', 0):.4f} | {s.get('rougeL_r', 0):.4f} "
            f"| {s.get('rougeL_f', 0):.4f} | {s.get('bleu', 0):.4f} | {s.get('meteor', 0):.4f} "
            f"| {bs_s} | {s.get('embedding_cosine', 0):.4f} |"
        )

    lines.extend(
        [
            "",
            "## Full-file vs overlap (key metrics)",
            "",
            "| Approach | Scope | ROUGE-1 F | ROUGE-L F | Emb Cosine |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for mode in APPROACHES:
        ff = comparison[mode]["full_file"]
        ov = comparison[mode]["overlap_sections"]
        lines.append(
            f"| {mode} | full-file | {ff.get('rouge1_f'):.4f} "
            f"| {ff.get('rougeL_f'):.4f} "
            f"| {ff.get('embedding_cosine'):.4f} |"
        )
        lines.append(
            f"| {mode} | overlap ∩ | {ov.get('rouge1_f'):.4f} "
            f"| {ov.get('rougeL_f'):.4f} "
            f"| {ov.get('embedding_cosine'):.4f} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Section parsing: `sections_from_markdown` / `match_category` from "
            "`build_manual_section_study.py` (same AGIT categories / `ORDER`).",
            "- Aligned strings include each side's original `##` heading plus body for "
            "intersecting categories only, ordered by `ORDER`.",
            "- Macro-average is over files with >=1 overlapping category.",
            "- Full-file baselines from `metrics.json` / `metrics_extended.json`.",
            "",
            "## Paths",
            "",
            f"- Metrics JSON: `{json_path}`",
            f"- Predictions: `{PRED_DIR}`",
            f"- Gold refs: `{REFS_PATH}`",
            "",
        ]
    )
    md_path = OUT / "summary_overlap_sections.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
