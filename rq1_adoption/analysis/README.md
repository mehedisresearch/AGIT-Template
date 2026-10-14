# RQ1 analysis

## What produced the shipped tables

| Script | Writes |
|---|---|
| `analyze_rq1_adoption.py` | `../rq1_results.json`, `../rq1_project_format_matrix.csv`, `../rq1_language_format.csv` |
| `summarize_rq1.py` | `../summary.md` from packaged tables (no external data) |

Study notebook (scaffold + methods notes): `universal_agent_instruction_study.ipynb`.

## Re-run full analysis

Defaults to packaged `../data/` slim inventories:

```bash
python3 analyze_rq1_adoption.py
python3 summarize_rq1.py
```

Override with `AGIT_STUDY_ROOT` / `AGIT_RQ_OUT` if needed.

## Package-only check

```bash
python3 summarize_rq1.py
```
