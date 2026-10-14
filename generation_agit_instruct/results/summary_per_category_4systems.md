# Category presence & tier coverage — 4 systems (n=62, with-template)

Four-format filter sample (n=62; original fulltest n=77 → drop SKILL/GEMINI).
Detector: `sections_from_markdown` / `match_category` with **fixed Ownership probes** (`agit_categories.py`).

Presence = Coverage(i,{c}) averaged over files = fraction of generations where category c is detected (non-empty section body under a matching heading).

## Ownership detector fix (before → after)

Legacy probes missed the literal heading `Ownership / contacts` (`\bowner\b` does not match `ownership`; `\bcontact\b` does not match `contacts`). Maintenance used `\bmaintain`, which incorrectly claimed `Maintainers`.

| System | Before (legacy) | After (fixed) | Δ | n_before | n_after |
|---|---:|---:|---:|---:|---:|
| gpt-4o-mini zero_shot | 0.0000 | 1.0000 | +1.0000 | 0 | 62 |
| gpt-4o-mini RAG | 0.0000 | 0.9677 | +0.9677 | 0 | 60 |
| CodeLlama-13B base | 0.0000 | 0.7258 | +0.7258 | 0 | 45 |
| CodeLlama-13B QLoRA | 0.0000 | 0.0161 | +0.0161 | 0 | 1 |

## Table 1 — 16 categories × 4 systems (presence rates)

| Category | gpt-4o-mini zero_shot | gpt-4o-mini RAG | CodeLlama-13B base | CodeLlama-13B QLoRA |
|---|---:|---:|---:|---:|
| Project overview / purpose | 1.0000 | 0.9677 | 0.7903 | 0.3710 |
| Repository structure | 0.5484 | 0.5484 | 0.4516 | 0.1613 |
| Build / run / install | 0.9032 | 0.8226 | 0.7258 | 0.3065 |
| Test / CI commands | 0.9516 | 0.9032 | 0.7903 | 0.0161 |
| Code style / formatting | 0.8226 | 0.7903 | 0.6452 | 0.3065 |
| Architecture / design constraints | 0.7742 | 0.6774 | 0.5484 | 0.4516 |
| Domain models / key abstractions | 0.3065 | 0.3065 | 0.2097 | 0.0645 |
| API / interface contracts | 0.7742 | 0.7258 | 0.6129 | 0.1290 |
| Do / Don't rules | 0.8548 | 0.8226 | 0.6452 | 0.2419 |
| Git / PR / commit conventions | 0.9516 | 0.9032 | 0.8387 | 0.0323 |
| Tooling-specific agent config | 0.8387 | 0.7097 | 0.7097 | 0.2903 |
| Examples / few-shot snippets | 0.6129 | 0.6129 | 0.4516 | 0.0484 |
| Security / secrets | 0.9839 | 0.9677 | 0.7419 | 0.1290 |
| Performance | 0.9839 | 0.9677 | 0.7258 | 0.0968 |
| Ownership / contacts | 1.0000 | 0.9677 | 0.7258 | 0.0161 |
| Maintenance / when to update | 0.9839 | 0.8871 | 0.7097 | 0.0000 |

## Table 2 — Tier structural coverage × 4 systems

| Tier | gpt-4o-mini zero_shot | gpt-4o-mini RAG | CodeLlama-13B base | CodeLlama-13B QLoRA |
|---|---:|---:|---:|---:|
| Required (10) | 0.7387 | 0.6919 | 0.5790 | 0.2016 |
| Gap (4) | 0.9798 | 0.9315 | 0.7540 | 0.0444 |
| Recommended (2) | 0.9919 | 0.9677 | 0.7581 | 0.2339 |
| All-16 | 0.8306 | 0.7863 | 0.6452 | 0.1663 |

### Tier mean counts

| Tier | gpt-4o-mini zero_shot | gpt-4o-mini RAG | CodeLlama-13B base | CodeLlama-13B QLoRA |
|---|---:|---:|---:|---:|
| Required (10) mean # | 7.39 | 6.92 | 5.79 | 2.02 |
| Gap (4) mean # | 3.92 | 3.73 | 3.02 | 0.18 |
| Recommended (2) mean # | 1.98 | 1.94 | 1.52 | 0.47 |
| All-16 mean # | 13.29 | 12.58 | 10.32 | 2.66 |

## Sources

- Predictions (all 4): `results/filtered_predictions/{zero_shot,rag,codellama13b_base,codellama13b_qlora}.json`
- Metrics JSON: `results/metrics_per_category_fixed_ownership.json`

