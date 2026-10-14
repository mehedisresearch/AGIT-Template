# RQ3 analysis

## What produced the shipped tables

| Script | Writes |
|---|---|
| `analyze_rq3_maintenance.py` | `../rq3_results.json`, `../rq3_instruction_events.csv`, `../rq3_file_lifecycle.csv`, `../rq3_category_durability.csv`, KW/Cliffs, durable/ephemeral heading lists |
| `analyze_rq3_durability_all16.py` | `../rq3_category_durability_all16.csv` (paper Σ `total_edits` = 5396) |
| `summarize_rq3.py` | `../summary.md` from packaged tables |

Uses AIDev-pop parquet under `AGIT_STUDY_ROOT/aidev_cache/`. Packaged `../data/aidev_cache/` includes all tables except full `pr_commit_details.parquet` (~463 MB). Fetch it first for a full re-derive:

```bash
../../scripts/fetch_aidev_cache.sh
python3 analyze_rq3_maintenance.py
python3 analyze_rq3_durability_all16.py
python3 summarize_rq3.py
```

Shipped `../rq3_instruction_events.csv` (n=2146) is already the derived instruction-touch table.

## Package-only check

```bash
python3 summarize_rq3.py
```
