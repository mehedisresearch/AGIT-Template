# Generic Intent Full Test — 4-Format Filter

Existing fulltest predictions filtered to RQ2 four formats (AGENTS / CLAUDE / Copilot / Cursor) via `format_name_bucket` from `build_agit_instruct_4fmt.py`. No re-generation.

- Original n: **77**
- Removed (non-4fmt): **15**
- Kept: **62**
- Removed formats: `{'SKILL.md': 14, 'GEMINI.md': 1}`
- Kept by rq2_type: `{'CLAUDE': 21, 'Copilot': 15, 'AGENTS': 26}`
- Model: `gpt-4o-mini`
- Embed model: `all-MiniLM-L6-v2` (normalize_embeddings=True)

## Why not (repo, format) ∩ 4fmt test split?

Intersecting with `agit_instruct_4fmt_splits/generic_instruct_test.json` keeps only **61** / 77 files — the 4fmt split is a new category-stratified repo-holdout, not a subset of the original 77. Format-rule filtering is used instead.

## Full-file metrics (macro mean)

| Approach | R1-P | R1-R | R1-F | R2-F | RL-P | RL-R | RL-F | BLEU | METEOR | BERTScore F1 | Emb Cosine | n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 0.5218 | 0.3683 | 0.4225 | 0.0824 | 0.1958 | 0.1408 | 0.1597 | 0.0347 | 0.2144 | 0.1992 | 0.6806 | 62 |
| rag | 0.5080 | 0.4363 | 0.4585 | 0.1006 | 0.1984 | 0.1733 | 0.1803 | 0.0537 | 0.2450 | 0.2473 | 0.6830 | 62 |

## Overlap-section metrics (gold ∩ pred, macro mean)

| Approach | R1-P | R1-R | R1-F | R2-F | RL-P | RL-R | RL-F | BLEU | METEOR | BERTScore F1 | Emb Cosine | n_scored |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 0.6064 | 0.2867 | 0.3863 | 0.0802 | 0.2813 | 0.1335 | 0.1796 | 0.0235 | 0.1734 | 0.2371 | 0.7097 | 61 |
| rag | 0.5729 | 0.3714 | 0.4325 | 0.0977 | 0.2591 | 0.1734 | 0.1966 | 0.0464 | 0.2091 | 0.2543 | 0.7081 | 62 |

## Per-category metrics (section pair, gold ∩ pred for that category)

Means over filtered files where the category appears in **both** gold and prediction. `n_gold` / `n_pred` / `n_intersection` count files with the category on each side.

### zero_shot

| Category | n_gold | n_pred | n_∩ | R1-F | RL-F | Emb Cosine |
|---|---:|---:|---:|---:|---:|---:|
| Project overview / purpose | 43 | 62 | 43 | 0.4084 | 0.3015 | 0.6426 |
| Repository structure | 43 | 34 | 32 | 0.2408 | 0.1741 | 0.5926 |
| Build / run / install | 57 | 56 | 53 | 0.3303 | 0.2071 | 0.5861 |
| Test / CI commands | 50 | 59 | 50 | 0.2686 | 0.1839 | 0.5838 |
| Code style / formatting | 48 | 51 | 45 | 0.2346 | 0.1532 | 0.5260 |
| Architecture / design constraints | 38 | 48 | 37 | 0.1436 | 0.1035 | 0.4656 |
| Domain models / key abstractions | 30 | 19 | 12 | 0.2477 | 0.1824 | 0.4927 |
| API / interface contracts | 33 | 48 | 32 | 0.2289 | 0.1672 | 0.5203 |
| Do / Don't rules | 43 | 53 | 40 | 0.1611 | 0.1050 | 0.4346 |
| Git / PR / commit conventions | 32 | 59 | 31 | 0.2224 | 0.1555 | 0.5857 |
| Tooling-specific agent config | 36 | 52 | 36 | 0.2406 | 0.1608 | 0.4836 |
| Examples / few-shot snippets | 24 | 38 | 21 | 0.2697 | 0.1909 | 0.5113 |
| Security / secrets | 30 | 61 | 29 | 0.2154 | 0.1531 | 0.5374 |
| Performance | 25 | 61 | 24 | 0.1660 | 0.1318 | 0.5234 |
| Ownership / contacts | 6 | 0 | 0 | n/a | n/a | n/a |
| Maintenance / when to update | 18 | 61 | 18 | 0.2050 | 0.1432 | 0.4140 |

**Top 3 by RL-F:** Project overview / purpose (0.3015, n=43); Build / run / install (0.2071, n=53); Examples / few-shot snippets (0.1909, n=21)
**Bottom 3 by RL-F:** Performance (0.1318, n=24); Do / Don't rules (0.1050, n=40); Architecture / design constraints (0.1035, n=37)

### rag

| Category | n_gold | n_pred | n_∩ | R1-F | RL-F | Emb Cosine |
|---|---:|---:|---:|---:|---:|---:|
| Project overview / purpose | 43 | 60 | 41 | 0.4675 | 0.3502 | 0.6487 |
| Repository structure | 43 | 34 | 32 | 0.3372 | 0.2338 | 0.6474 |
| Build / run / install | 57 | 51 | 48 | 0.3605 | 0.2215 | 0.5611 |
| Test / CI commands | 50 | 56 | 47 | 0.3096 | 0.2091 | 0.5854 |
| Code style / formatting | 48 | 49 | 43 | 0.2842 | 0.1733 | 0.5449 |
| Architecture / design constraints | 38 | 42 | 33 | 0.1691 | 0.1190 | 0.4493 |
| Domain models / key abstractions | 30 | 19 | 12 | 0.2500 | 0.1846 | 0.4969 |
| API / interface contracts | 33 | 45 | 29 | 0.2620 | 0.1805 | 0.5224 |
| Do / Don't rules | 43 | 51 | 39 | 0.1680 | 0.1062 | 0.4301 |
| Git / PR / commit conventions | 32 | 56 | 30 | 0.2696 | 0.1762 | 0.5943 |
| Tooling-specific agent config | 36 | 44 | 29 | 0.2740 | 0.1778 | 0.5425 |
| Examples / few-shot snippets | 24 | 38 | 21 | 0.3280 | 0.2252 | 0.5115 |
| Security / secrets | 30 | 60 | 28 | 0.2333 | 0.1528 | 0.5512 |
| Performance | 25 | 60 | 23 | 0.1828 | 0.1313 | 0.5258 |
| Ownership / contacts | 6 | 0 | 0 | n/a | n/a | n/a |
| Maintenance / when to update | 18 | 53 | 17 | 0.2412 | 0.1600 | 0.4458 |

**Top 3 by RL-F:** Project overview / purpose (0.3502, n=41); Repository structure (0.2338, n=32); Examples / few-shot snippets (0.2252, n=21)
**Bottom 3 by RL-F:** Performance (0.1313, n=23); Architecture / design constraints (0.1190, n=33); Do / Don't rules (0.1062, n=39)

## RAG per-category ranking (RL-F)

| Rank | Category | RL-F | R1-F | Emb | n_∩ |
|---:|---|---:|---:|---:|---:|
| 1 | Project overview / purpose | 0.3502 | 0.4675 | 0.6487 | 41 |
| 2 | Repository structure | 0.2338 | 0.3372 | 0.6474 | 32 |
| 3 | Examples / few-shot snippets | 0.2252 | 0.3280 | 0.5115 | 21 |
| 4 | Build / run / install | 0.2215 | 0.3605 | 0.5611 | 48 |
| 5 | Test / CI commands | 0.2091 | 0.3096 | 0.5854 | 47 |
| 6 | Domain models / key abstractions | 0.1846 | 0.2500 | 0.4969 | 12 |
| 7 | API / interface contracts | 0.1805 | 0.2620 | 0.5224 | 29 |
| 8 | Tooling-specific agent config | 0.1778 | 0.2740 | 0.5425 | 29 |
| 9 | Git / PR / commit conventions | 0.1762 | 0.2696 | 0.5943 | 30 |
| 10 | Code style / formatting | 0.1733 | 0.2842 | 0.5449 | 43 |
| 11 | Maintenance / when to update | 0.1600 | 0.2412 | 0.4458 | 17 |
| 12 | Security / secrets | 0.1528 | 0.2333 | 0.5512 | 28 |
| 13 | Performance | 0.1313 | 0.1828 | 0.5258 | 23 |
| 14 | Architecture / design constraints | 0.1190 | 0.1691 | 0.4493 | 33 |
| 15 | Do / Don't rules | 0.1062 | 0.1680 | 0.4301 | 39 |

## Paths

- Output: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest_4fmt`
- Filtered preds: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest_4fmt/filtered_predictions`
- Kept files: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest_4fmt/kept_files.json`
- Full metrics: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest_4fmt/metrics_full.json`
- Overlap metrics: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest_4fmt/metrics_overlap.json`
- Per-category: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest_4fmt/metrics_per_category.json`
