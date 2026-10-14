# Compliance REQUIRED vs GAP — 4-format fulltest

n=62 kept 4-format files (zs + rag).

## Definition

The codebase has no field literally named `compliance_score`. Closest notions:

- `metrics.py` **coverage** = count of 10 REQUIRED keyword buckets in hyp; **has_gap** = any GAP keyword
- `instruction_linter` / template meta **n_required/10**, **n_gap/5** via heading probes

**Primary (used here): template compliance** — fraction of canonical `REQUIRED10` / `GAP5` categories present as detected `##` sections in the prediction (`sections_from_markdown`), macro-averaged over files.

**Secondary: gold recall compliance** — of gold categories in each bucket, fraction also present in pred (files with ≥1 gold cat in bucket).

## Category lists

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

## Template compliance (primary)

| Approach | REQUIRED mean | mean n/10 | GAP mean | mean n/5 | gap_all_five |
|---|---:|---:|---:|---:|---:|
| zero_shot | 0.7387 | 7.39 | 0.7903 | 3.95 | 0.0000 |
| rag | 0.6919 | 6.92 | 0.7516 | 3.76 | 0.0000 |

## Gold recall compliance (secondary)

| Approach | REQUIRED mean | n_files | GAP mean | n_files |
|---|---:|---:|---:|---:|
| zero_shot | 0.8748 | 62 | 0.8898 | 59 |
| rag | 0.8385 | 62 | 0.8672 | 59 |

## ROUGE / emb from `metrics_required_vs_gap.json` (overlap-concat)

| Approach | Bucket | n_scored | mean n_∩ | R1-F | RL-F | Emb |
|---|---|---:|---:|---:|---:|---:|
| zero_shot | REQUIRED | 61 | 5.8689 | 0.3585 | 0.1703 | 0.6871 |
| zero_shot | GAP | 54 | 2.1111 | 0.3341 | 0.2141 | 0.6307 |
| rag | REQUIRED | 62 | 5.371 | 0.3963 | 0.1855 | 0.6922 |
| rag | GAP | 52 | 2.0962 | 0.3838 | 0.2497 | 0.6476 |

## Legacy keyword metrics (`metrics.py`)

| Approach | required coverage/10 | has_gap rate |
|---|---:|---:|
| zero_shot | 0.8387 | 1.0000 |
| rag | 0.8435 | 1.0000 |

## Paths

- `exports/generic_intent_fulltest_4fmt/compliance_required_vs_gap.json`
- ROUGE source: `exports/generic_intent_fulltest_4fmt/metrics_required_vs_gap.json`
- Predictions: `exports/generic_intent_fulltest_4fmt/filtered_predictions`

