# RQ1 methodology (prevalence & adoption)

**RQ.** How prevalent are agent instruction files across repository domains, and what types of repositories use which formats?

## Data

- Inventories: `top_500_projects_with_files.csv` + `bottom_500_projects_with_files.csv` (n=1,000).
- Formats: `AGENTS.md`, `CLAUDE.md`, Copilot instructions (`.github/…/copilot-instructions.md` / `*.instructions.md`), Cursor rules (`.cursorrules` / `.cursor/rules/`).

## Analysis (`analyze_rq1_adoption.py`)

1. Classify each repo’s file paths into the four formats.
2. Prevalence by cohort; multi-format counts; pairwise co-occurrence.
3. Language × format rates (languages with ≥15 repos).
4. Star-quartile bins.
5. Logistic regression (sklearn) for `has_any` and per-format outcomes on log(stars), log(forks), cohort, language dummies.

## Outputs

See parent folder CSVs/JSON. Package-only narrative: `../summary.md`.
