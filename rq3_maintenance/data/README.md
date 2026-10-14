# RQ3 data inputs

## Derived tables (also hard-linked at parent `../`)

| File | Role | n |
|---|---|---:|
| `rq3_instruction_events.csv` | Instruction-file touch events | **2146** |
| `rq3_file_lifecycle.csv` | Five metrics per file | **448** |
| `rq3_category_durability_all16.csv` | Heading edits (paper Σ=5396) | 16 cats |
| `rq3_*.csv` / `rq3_results.json` | KW, Cliffs, durable/ephemeral, summary | |

## AIDev-pop parquet (`aidev_cache/`)

| File | Role | Approx size |
|---|---|---|
| `repository.parquet` | Repos | ~0.2 MB |
| `pull_request.parquet` | PRs | ~17 MB |
| `pr_task_type.parquet` | Task types | ~3 MB |
| `pr_reviews.parquet` | Reviews | ~7.5 MB |
| `pr_commits.parquet` | Commits | ~8 MB |
| `pr_commit_details_instruction_rows.parquet` | Instruction-file rows only (n=2146) | ~2 MB |

**Omitted:** full `pr_commit_details.parquet` (~463 MB) — needed only to re-derive co-change stats from scratch. Fetch with:

```bash
../../scripts/fetch_aidev_cache.sh
export AGIT_STUDY_ROOT="$(pwd)"   # so aidev_cache/ resolves here
export AGIT_RQ_OUT="$(pwd)/.."
python3 ../analysis/analyze_rq3_maintenance.py
```

See `aidev_cache_meta.json` for provenance.
