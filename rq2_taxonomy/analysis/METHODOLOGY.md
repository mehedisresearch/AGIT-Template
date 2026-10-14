# RQ2 methodology (taxonomy & Jaccard)

**RQ.** How similar are agent instruction files in content — shared core, format-specific content, and gaps?

## Data

Raw instruction files under `{top,bottom}_repos` clones (n=3,387 classified files).

## Analysis (`analyze_rq2_taxonomy.py`)

1. Extract `#`/`##`/`###` headings; normalize.
2. Map file text → **16 categories**.
3. Vocabulary Jaccard on headings and on category sets across format pairs.
4. Within-repo Jaccard for multi-format repos.
5. Category prevalence (% of files per format); shared-strong / gap heuristics for template mapping.

## Outputs

`rq2_results.json` plus prevalence / file-stats / Jaccard CSVs. Consistency coding lives in `../rq2_consistency/`.
