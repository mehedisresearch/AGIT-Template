#!/usr/bin/env python3
"""Recompute 4-format generation metrics from packaged predictions.

Does not call any LLM API. Reads:
  ../results/filtered_predictions/{test_refs,zero_shot,rag}.json

Writes verification metrics under:
  ../results/reproduce_verify/

Dependencies: numpy, nltk, rouge-score, sentence-transformers; optional bert-score.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from score_fulltest_4fmt import (  # noqa: E402
    APPROACHES,
    EMBED_MODEL,
    score_full_file,
    score_overlap,
)

PKG_GEN = SCRIPTS.parent
PRED = PKG_GEN / "results" / "filtered_predictions"
OUT = PKG_GEN / "results" / "reproduce_verify"


def load_json(path: Path):
    with path.open() as f:
        return json.load(f)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    refs = load_json(PRED / "test_refs.json")
    if len(refs) != 62:
        raise SystemExit(f"expected 62 4fmt refs, got {len(refs)}")

    try:
        import bert_score  # noqa: F401

        bert_ok = True
    except Exception:
        bert_ok = False
        print("bert-score not installed; skipping BERTScore")

    embedder = SentenceTransformer(EMBED_MODEL)
    out = {
        "n_refs": len(refs),
        "embed_model": EMBED_MODEL,
        "bertscore": bert_ok,
        "note": "Recomputed from packaged filtered_predictions (4-format only).",
    }

    for approach in APPROACHES:
        hyp_map = load_json(PRED / f"{approach}.json")
        if len(hyp_map) != 62:
            raise SystemExit(f"{approach}: expected 62 preds, got {len(hyp_map)}")
        print(f"Scoring {approach} (full-file)...")
        full_summary, full_rows = score_full_file(refs, hyp_map, embedder, bert_ok)
        print(f"Scoring {approach} (overlap)...")
        overlap_summary, overlap_rows, skip = score_overlap(
            refs, hyp_map, embedder, bert_ok
        )
        out[approach] = {
            "full": full_summary,
            "overlap": overlap_summary,
            "n_overlap_skipped": skip,
        }
        (OUT / f"{approach}_full.json").write_text(
            json.dumps({"summary": full_summary, "per_file": full_rows}, indent=2)
        )
        (OUT / f"{approach}_overlap.json").write_text(
            json.dumps(
                {"summary": overlap_summary, "per_file": overlap_rows, "n_skipped": skip},
                indent=2,
            )
        )

    (OUT / "summary.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({k: v for k, v in out.items() if k in ("n_refs", "zero_shot", "rag")}, indent=2))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
