#!/usr/bin/env python3
"""Submit / poll / aggregate gpt-4o Batch LLM-judge for the n=386 sample.

Uses the same SYSTEM prompt + JSON schema as the n=150 judge (MRcd.py).

Usage:
  python3 run_batch_judge_n386.py submit
  python3 run_batch_judge_n386.py poll
  python3 run_batch_judge_n386.py aggregate   # after batch completes
  python3 run_batch_judge_n386.py all         # submit + poll + aggregate
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent.parent
LABELS = ["Equivalent", "Complementary", "Divergent", "Contradictory"]
BATCH_JSONL = OUT / "batch_requests_gpt4o.jsonl"
SAMPLE_CSV = OUT / "sample_n386.csv"
META_PATH = OUT / "batch_meta.json"


def load_api_key() -> str:
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"].strip().strip('"').strip("'")
    for path in [
        ROOT / ".env",
        Path("/gpuhome/shanto1/CrossLangVul/.env"),
        Path("/gpuhome/shanto1/BugFix/agentic_experiment/.env"),
    ]:
        if path.exists():
            for line in path.read_text().splitlines():
                if line.startswith("OPENAI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("OPENAI_API_KEY not found")


def make_client():
    from openai import OpenAI

    kwargs = {"api_key": load_api_key()}
    base = os.environ.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE")
    if base:
        kwargs["base_url"] = base
    # Optional proxy via standard env: HTTPS_PROXY / HTTP_PROXY / ALL_PROXY
    return OpenAI(**kwargs)


def submit() -> dict:
    client = make_client()
    print(f"Uploading {BATCH_JSONL} ...")
    with BATCH_JSONL.open("rb") as f:
        up = client.files.create(file=f, purpose="batch")
    print(f"file_id={up.id}")
    batch = client.batches.create(
        input_file_id=up.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"job": "agit_interchangeability_llm_judge_n386", "model": "gpt-4o"},
    )
    meta = {
        "file_id": up.id,
        "batch_id": batch.id,
        "status": batch.status,
        "endpoint": "/v1/chat/completions",
        "model": "gpt-4o",
        "n_requests": sum(1 for _ in BATCH_JSONL.open()),
        "base_url": os.environ.get("OPENAI_BASE_URL")
        or os.environ.get("OPENAI_API_BASE")
        or "https://api.openai.com/v1",
        "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    META_PATH.write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta, indent=2))
    return meta


def poll(max_wait_sec: int = 6 * 3600, interval: int = 30) -> dict:
    client = make_client()
    meta = json.loads(META_PATH.read_text())
    bid = meta["batch_id"]
    t0 = time.time()
    while True:
        b = client.batches.retrieve(bid)
        meta["status"] = b.status
        meta["request_counts"] = getattr(b, "request_counts", None)
        if hasattr(meta["request_counts"], "model_dump"):
            meta["request_counts"] = meta["request_counts"].model_dump()
        elif hasattr(meta["request_counts"], "__dict__"):
            meta["request_counts"] = dict(meta["request_counts"])
        meta["output_file_id"] = getattr(b, "output_file_id", None)
        meta["error_file_id"] = getattr(b, "error_file_id", None)
        META_PATH.write_text(json.dumps(meta, indent=2, default=str))
        print(
            f"[{time.strftime('%H:%M:%S')}] status={b.status} "
            f"counts={meta.get('request_counts')}"
        )
        if b.status in ("completed", "failed", "expired", "cancelled"):
            break
        if time.time() - t0 > max_wait_sec:
            meta["poll_timeout"] = True
            META_PATH.write_text(json.dumps(meta, indent=2, default=str))
            raise TimeoutError(f"Batch {bid} not done after {max_wait_sec}s")
        time.sleep(interval)
    if b.status != "completed":
        raise RuntimeError(f"Batch ended with status={b.status}")
    # download
    out_id = b.output_file_id
    content = client.files.content(out_id)
    raw_path = OUT / "batch_output.jsonl"
    text = content.text if hasattr(content, "text") else content.read().decode()
    raw_path.write_text(text)
    meta["output_path"] = str(raw_path)
    META_PATH.write_text(json.dumps(meta, indent=2, default=str))
    print(f"Wrote {raw_path}")
    return meta


def parse_label(content: str) -> tuple[str, str]:
    content = (content or "").strip()
    try:
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content)
        data = json.loads(content)
        label = str(data.get("label", "")).strip()
        rationale = str(data.get("rationale", "")).strip()
    except Exception:
        label, rationale = "", content[:200]
        m = re.search(
            r"\b(Equivalent|Complementary|Divergent|Contradictory)\b", content, re.I
        )
        if m:
            label = m.group(1)
    for lab in LABELS:
        if label.lower() == lab.lower():
            return lab, rationale
    return "INVALID", rationale or content[:200]


def aggregate() -> dict:
    from sklearn.metrics import (
        accuracy_score,
        classification_report,
        cohen_kappa_score,
        confusion_matrix,
    )

    raw_path = OUT / "batch_output.jsonl"
    if not raw_path.exists():
        raise FileNotFoundError(raw_path)

    by_id: dict[int, dict] = {}
    for line in raw_path.read_text().splitlines():
        if not line.strip():
            continue
        o = json.loads(line)
        cid = o.get("custom_id", "")
        m = re.search(r"n386_(\d+)", cid)
        if not m:
            continue
        rid = int(m.group(1))
        resp = o.get("response") or {}
        body = resp.get("body") or {}
        choices = body.get("choices") or []
        content = ""
        if choices:
            content = (choices[0].get("message") or {}).get("content") or ""
        label, rationale = parse_label(content)
        err = o.get("error")
        if err and label == "INVALID":
            label = "ERROR"
            rationale = str(err)[:300]
        by_id[rid] = {
            "id": rid,
            "llm_label": label,
            "llm_rationale": rationale,
            "raw": content,
        }

    with SAMPLE_CSV.open() as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        rid = int(r["id"])
        j = by_id.get(rid, {})
        r["llm_label"] = j.get("llm_label", "MISSING")
        r["llm_rationale"] = j.get("llm_rationale", "")

    out_csv = OUT / "sample_n386_llm_judge.csv"
    fields = list(rows[0].keys())
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    raw_judge = OUT / "llm_judge_raw.jsonl"
    with raw_judge.open("w", encoding="utf-8") as f:
        for i in sorted(by_id):
            f.write(json.dumps(by_id[i], ensure_ascii=False) + "\n")

    valid = [r for r in rows if r["llm_label"] in LABELS]
    y_llm = [r["llm_label"] for r in valid]
    y_auto = [r["auto_label"] for r in valid]
    llm_counts = Counter(y_llm)
    auto_counts = Counter(y_auto)
    agree = sum(1 for a, b in zip(y_llm, y_auto) if a == b)
    acc = float(accuracy_score(y_llm, y_auto)) if valid else 0.0
    kappa = float(cohen_kappa_score(y_llm, y_auto)) if valid else 0.0
    report = classification_report(
        y_llm, y_auto, labels=LABELS, digits=3, zero_division=0, output_dict=True
    )
    cm = confusion_matrix(y_llm, y_auto, labels=LABELS)

    def bin_of(sim: float) -> str:
        if sim < 0.5:
            return "low_<0.5"
        if sim < 0.85:
            return "mid_0.5-0.85"
        return "high_>=0.85"

    by_bin: dict[str, dict] = {}
    for bname in ("low_<0.5", "mid_0.5-0.85", "high_>=0.85"):
        g = [r for r in valid if bin_of(float(r["embedding_similarity"])) == bname]
        if not g:
            continue
        by_bin[bname] = {
            "n": len(g),
            "agreement": round(
                sum(1 for r in g if r["llm_label"] == r["auto_label"]) / len(g), 3
            ),
            "llm_dist": dict(Counter(r["llm_label"] for r in g)),
            "auto_dist": dict(Counter(r["auto_label"] for r in g)),
        }

    auto_con = [r["auto_label"] == "Contradictory" for r in valid]
    llm_con = [r["llm_label"] == "Contradictory" for r in valid]
    tp = sum(1 for a, b in zip(auto_con, llm_con) if a and b)
    fp = sum(1 for a, b in zip(auto_con, llm_con) if a and not b)
    fn = sum(1 for a, b in zip(auto_con, llm_con) if (not a) and b)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0

    n150 = [r for r in valid if str(r.get("from_n150", "")).lower() in ("true", "1")]
    n150_llm = Counter(r["llm_label"] for r in n150)

    metrics = {
        "model": "gpt-4o",
        "n_sample": len(rows),
        "n_valid_llm": len(valid),
        "n_invalid_or_error": len(rows) - len(valid),
        "llm_label_counts": dict(llm_counts),
        "llm_label_rates_pct": {
            lab: round(100 * llm_counts.get(lab, 0) / len(valid), 1) if valid else 0
            for lab in LABELS
        },
        "auto_label_counts": dict(auto_counts),
        "agreement_count": agree,
        "agreement_rate": round(agree / len(valid), 4) if valid else 0,
        "accuracy_auto_vs_llm": round(acc, 4),
        "cohen_kappa_auto_vs_llm": round(kappa, 4),
        "classification_report": report,
        "confusion_matrix_labels": LABELS,
        "confusion_matrix_llm_rows_auto_cols": cm.tolist(),
        "by_similarity_bin": by_bin,
        "contradictory_detection": {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "tp": tp,
            "fp": fp,
            "fn": fn,
        },
        "n150_subset_llm_counts": dict(n150_llm),
        "n150_reference_llm_counts": {
            "Equivalent": 48,
            "Complementary": 79,
            "Divergent": 23,
            "Contradictory": 0,
        },
        "outputs": {"csv": str(out_csv), "raw": str(raw_judge)},
    }
    (OUT / "llm_judge_metrics.json").write_text(json.dumps(metrics, indent=2))

    # markdown summary
    def row(lab: str) -> str:
        c = llm_counts.get(lab, 0)
        pct = 100 * c / len(valid) if valid else 0
        c150 = {"Equivalent": 48, "Complementary": 79, "Divergent": 23, "Contradictory": 0}[
            lab
        ]
        pct150 = 100 * c150 / 150
        return f"| {lab} | {c} | {pct:.1f}% | {c150} | {pct150:.1f}% |"

    md = f"""# LLM judge n=386 (gpt-4o Batch)

## Sample definition

No project artifact defines a population of exactly **386**. Closest nearby totals:
- Test / CI commands pairs: **381**
- Multi-format repos (this rebuild): **314** (summary.json lists 290)

**Choice:** expand the existing similarity-stratified consistency check from n=150 → n=386.
- Keep all **150** original pairs
- Top up to **128 / 128 / 130** in low (&lt;0.5) / mid (0.5–0.85) / high (≥0.85) bins
- Seed **42**; texts truncated to **800** chars (same as n=150 judge)
- Prompt/schema identical to `MRcd.py`

## LLM label distribution (gpt-4o)

| Label | n=386 | % | n=150 ref | % |
|---|---:|---:|---:|---:|
{chr(10).join(row(l) for l in LABELS)}
| **Total** | **{len(valid)}** | 100% | **150** | 100% |

## Agreement with auto labels

| Metric | n=386 | n=150 |
|---|---:|---:|
| Agreement | {agree}/{len(valid)} ({100*metrics['agreement_rate']:.1f}%) | 88/150 (58.7%) |
| Cohen κ | {kappa:.3f} | 0.430 |

## Auto labels on the n=386 sample (offline)

| Label | n | % |
|---|---:|---:|
| Equivalent | {auto_counts.get('Equivalent',0)} | {100*auto_counts.get('Equivalent',0)/len(rows):.1f}% |
| Complementary | {auto_counts.get('Complementary',0)} | {100*auto_counts.get('Complementary',0)/len(rows):.1f}% |
| Divergent | {auto_counts.get('Divergent',0)} | {100*auto_counts.get('Divergent',0)/len(rows):.1f}% |
| Contradictory | {auto_counts.get('Contradictory',0)} | {100*auto_counts.get('Contradictory',0)/len(rows):.1f}% |
"""
    (OUT / "summary.md").write_text(md)
    print(md)
    print(f"Saved metrics → {OUT / 'llm_judge_metrics.json'}")
    return metrics


def probe() -> None:
    """Quick connectivity check before submitting a large batch."""
    import urllib.request

    client = make_client()
    print("base_url:", getattr(client, "base_url", None))
    try:
        models = client.models.list()
        print("models.list OK, n=", len(getattr(models, "data", []) or []))
    except Exception as e:
        print("models.list FAILED:", type(e).__name__, e)
        raise


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "cmd",
        choices=["submit", "poll", "aggregate", "all", "probe"],
    )
    ap.add_argument("--interval", type=int, default=30)
    ap.add_argument("--max-wait", type=int, default=6 * 3600)
    args = ap.parse_args()
    os.environ["OPENAI_API_KEY"] = load_api_key()
    if args.cmd == "probe":
        probe()
    elif args.cmd == "submit":
        submit()
    elif args.cmd == "poll":
        poll(max_wait_sec=args.max_wait, interval=args.interval)
    elif args.cmd == "aggregate":
        aggregate()
    elif args.cmd == "all":
        submit()
        poll(max_wait_sec=args.max_wait, interval=args.interval)
        aggregate()


if __name__ == "__main__":
    main()
