# REQUIRED vs GAP metrics — 4-format fulltest

n=62 kept 4-format files; model=`gpt-4o-mini`; embed=`all-MiniLM-L6-v2` (normalize=True).

## Category lists

Official lists from `build_generic_instruction_template.REQUIRED10` / `GAP5` (same as `instruction_linter` and `build_dataset`).

**REQUIRED (10):**

- Do / Don't rules
- Build / run / install
- Repository structure
- Test / CI commands
- Code style / formatting
- Architecture / design constraints
- Domain models / key abstractions
- API / interface contracts
- Examples / few-shot snippets
- Tooling-specific agent config

**GAP (5):**

- Security / secrets
- Performance
- Maintenance / when to update
- Project overview / purpose
- Ownership / contacts

**Neither (in ORDER, not scored here):** Git / PR / commit conventions

## Primary: overlap-concat within bucket (gold ∩ pred ∩ set)

Per file: keep only categories in the bucket that appear in both gold and pred; concatenate in AGIT `ORDER` with `##` headings; score; macro-average over files with ≥1 intersecting category in that bucket.

| Approach | Bucket | n_scored | mean n_∩ | R1-F | RL-F | Emb Cosine |
|---|---|---:|---:|---:|---:|---:|
| zero_shot | REQUIRED | 61 | 5.8689 | 0.3585 | 0.1703 | 0.6871 |
| zero_shot | GAP | 54 | 2.1111 | 0.3341 | 0.2141 | 0.6307 |
| rag | REQUIRED | 62 | 5.3710 | 0.3963 | 0.1855 | 0.6922 |
| rag | GAP | 52 | 2.0962 | 0.3838 | 0.2497 | 0.6476 |

## Secondary: from `metrics_per_category.json` (section pairs)

Macro = unweighted mean over categories with n_scored>0. Micro = n_scored-weighted mean over section-pair instances (preferred).

| Approach | Bucket | n_pairs | Micro R1-F | Micro RL-F | Micro Emb | Macro R1-F | Macro RL-F | Macro Emb |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | REQUIRED | 358 | 0.2390 | 0.1620 | 0.5257 | 0.2366 | 0.1628 | 0.5197 |
| zero_shot | GAP | 114 | 0.2762 | 0.2030 | 0.5546 | 0.2487 | 0.1824 | 0.5293 |
| rag | REQUIRED | 333 | 0.2776 | 0.1826 | 0.5339 | 0.2743 | 0.1831 | 0.5292 |
| rag | GAP | 109 | 0.3120 | 0.2236 | 0.5661 | 0.2812 | 0.1986 | 0.5429 |

## Compact table (primary overlap-concat)

| | Required RL-F | Required R1-F | Required Emb | Gap RL-F | Gap R1-F | Gap Emb |
|---|---:|---:|---:|---:|---:|---:|
| ZS | 0.1703 | 0.3585 | 0.6871 | 0.2141 | 0.3341 | 0.6307 |
| RAG | 0.1855 | 0.3963 | 0.6922 | 0.2497 | 0.3838 | 0.6476 |

## Paths

- Metrics JSON: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest_4fmt/metrics_required_vs_gap.json`
- Per-category source: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest_4fmt/metrics_per_category.json`
- Predictions: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest_4fmt/filtered_predictions`
