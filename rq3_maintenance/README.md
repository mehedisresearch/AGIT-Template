# RQ3 — Maintenance

| Quantity | N | Source |
|---|---:|---|
| Heading-level edit events | **5,396** | Σ `total_edits` in `rq3_category_durability_all16.csv` |
| Instruction-file touch events | 2,146 | `rq3_instruction_events.csv` / `rq3_results.json` |
| Unique files | **448** | events + `rq3_file_lifecycle.csv` |
| Repositories | **283** | |
| Pull requests | **943** | |

**Five metrics per file** (`rq3_file_lifecycle.csv`): `n_touches`, `n_authors`, `owner_top_share`, `churn_ratio`, `span_days`.

Also: durability / ephemeral heading lists, KW and Cliffs tables, `rq3_results.json`, `summary.md`.

## Raw inputs (`data/`)

Derived event/lifecycle CSVs (hard-linked from parent) plus slim `aidev_cache/` parquet (all tables except full `pr_commit_details.parquet` ~463 MB). Instruction-only detail rows (n=2146) are included. See `data/README.md` and `../scripts/fetch_aidev_cache.sh`.

## Analysis

See **`analysis/`**:

- `analyze_rq3_maintenance.py` — lifecycle, KW/Cliffs, triggers, heading durability
- `analyze_rq3_durability_all16.py` — all-16 category remap (paper 5,396)
- `summarize_rq3.py` — rebuild `summary.md` from packaged tables
- `METHODOLOGY.md` + study notebook

```bash
cd analysis && python3 summarize_rq3.py
```
