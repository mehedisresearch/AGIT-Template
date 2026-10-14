# RQ2 taxonomy analysis

## What produced the shipped tables

| Script | Writes |
|---|---|
| `analyze_rq2_taxonomy.py` | `../rq2_results.json`, `../rq2_category_prevalence.csv`, `../rq2_file_stats.csv`, `../rq2_heading_jaccard.csv`, `../rq2_within_repo_jaccard.csv` |
| `summarize_rq2.py` | `../summary.md` from packaged tables |

Walks `{top,bottom}_repos` under `AGIT_STUDY_ROOT` (defaults to packaged `../data/` symlinks), extracts headings, and applies the 16-category keyword pilot.

## Re-run full analysis

```bash
python3 analyze_rq2_taxonomy.py
python3 summarize_rq2.py
```

Per-file records without re-walk: `../data/rq2_file_records.jsonl` (n=3387).

## Package-only check

```bash
python3 summarize_rq2.py
```
