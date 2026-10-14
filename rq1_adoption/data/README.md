# RQ1 data inputs

| File | Role | n |
|---|---|---:|
| `top_500_projects_instruction_files.csv` | Top-500 inventory (instruction paths in `files`) | 500 |
| `bottom_500_projects_instruction_files.csv` | Bottom-500 inventory | 500 |

Same files live under `../../corpus/` (hard-linked). Combined with `../../corpus/repo_list_1000.csv` they define the **N=1000** study universe (**582** adopters).

## Re-run

```bash
export AGIT_STUDY_ROOT="$(pwd)"   # these slim CSVs are enough for RQ1
export AGIT_RQ_OUT="$(pwd)/.."
python3 ../analysis/analyze_rq1_adoption.py
```

`analyze_rq1_adoption.py` looks for `*_500_projects_instruction_files.csv` first, then falls back to the original full-tree names.
