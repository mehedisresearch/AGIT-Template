# ROUGE-1 F1 + embedding cosine — 4 with-template systems (n=62)

Four-format filter sample (n=62; original fulltest n=77 → drop SKILL/GEMINI).
No re-generation. Embed model: `all-MiniLM-L6-v2` (normalize_embeddings=True).
Content metrics use the **published** section pipeline (legacy Ownership probes).
Fixed Ownership probes are used only in presence/coverage tables elsewhere.

## A) Full-file metrics (macro mean)

| System | rouge1_f | embedding_cosine | n |
|---|---:|---:|---:|
| gpt-4o-mini zero_shot | 0.4225 | 0.6806 | 62 |
| gpt-4o-mini RAG | 0.4585 | 0.6830 | 62 |
| CodeLlama-13B base | 0.3044 | 0.3731 | 62 |
| CodeLlama-13B QLoRA | 0.2727 | 0.6075 | 62 |

## B) Overlapped-sections metrics (gold ∩ pred, macro mean)

Empty intersection files skipped (excluded from macro-average).

| System | rouge1_f | embedding_cosine | n_scored | n_skipped |
|---|---:|---:|---:|---:|
| gpt-4o-mini zero_shot | 0.3863 | 0.7097 | 61 | 1 |
| gpt-4o-mini RAG | 0.4325 | 0.7081 | 62 | 0 |
| CodeLlama-13B base | 0.3090 | 0.4341 | 53 | 9 |
| CodeLlama-13B QLoRA | 0.3465 | 0.6468 | 57 | 5 |

## C) Per-category (section-pair on gold ∩ pred for that category)

Means over files where the category appears in **both** gold and prediction.

### C1 — Per-category rouge1_f

| Category | gpt-4o-mini zero_shot | gpt-4o-mini RAG | CodeLlama-13B base | CodeLlama-13B QLoRA | n_∩ (ZS / RAG / base / QLoRA) |
|---|---:|---:|---:|---:|---:|
| Project overview / purpose | 0.4084 | 0.4675 | 0.2382 | 0.5199 | 43 / 41 / 31 / 16 |
| Repository structure | 0.2408 | 0.3372 | 0.2215 | 0.4348 | 32 / 32 / 26 / 9 |
| Build / run / install | 0.3303 | 0.3605 | 0.2271 | 0.4208 | 53 / 48 / 42 / 19 |
| Test / CI commands | 0.2686 | 0.3096 | 0.2330 | 0.3438 | 50 / 47 / 42 / 1 |
| Code style / formatting | 0.2346 | 0.2842 | 0.1973 | 0.2449 | 45 / 43 / 35 / 16 |
| Architecture / design constraints | 0.1436 | 0.1691 | 0.1776 | 0.2136 | 37 / 33 / 26 / 20 |
| Domain models / key abstractions | 0.2477 | 0.2500 | 0.1952 | 0.2423 | 12 / 12 / 8 / 3 |
| API / interface contracts | 0.2289 | 0.2620 | 0.1867 | 0.3343 | 32 / 29 / 25 / 6 |
| Do / Don't rules | 0.1611 | 0.1680 | 0.1580 | 0.2237 | 40 / 39 / 31 / 12 |
| Git / PR / commit conventions | 0.2224 | 0.2696 | 0.1695 | 0.1918 | 31 / 30 / 29 / 1 |
| Tooling-specific agent config | 0.2406 | 0.2740 | 0.2041 | 0.3531 | 36 / 29 / 30 / 15 |
| Examples / few-shot snippets | 0.2697 | 0.3280 | 0.2131 | 0.3748 | 21 / 21 / 17 / 3 |
| Security / secrets | 0.2154 | 0.2333 | 0.1584 | 0.1375 | 29 / 28 / 20 / 7 |
| Performance | 0.1660 | 0.1828 | 0.1578 | 0.2654 | 24 / 23 / 17 / 4 |
| Ownership / contacts | n/a | n/a | n/a | n/a | 0 / 0 / 0 / 0 |
| Maintenance / when to update | 0.2050 | 0.2412 | 0.1909 | n/a | 18 / 17 / 13 / 0 |

### C2 — Per-category embedding_cosine

| Category | gpt-4o-mini zero_shot | gpt-4o-mini RAG | CodeLlama-13B base | CodeLlama-13B QLoRA | n_∩ (ZS / RAG / base / QLoRA) |
|---|---:|---:|---:|---:|---:|
| Project overview / purpose | 0.6426 | 0.6487 | 0.3039 | 0.7869 | 43 / 41 / 31 / 16 |
| Repository structure | 0.5926 | 0.6474 | 0.4788 | 0.7134 | 32 / 32 / 26 / 9 |
| Build / run / install | 0.5861 | 0.5611 | 0.3625 | 0.6474 | 53 / 48 / 42 / 19 |
| Test / CI commands | 0.5838 | 0.5854 | 0.4356 | 0.4341 | 50 / 47 / 42 / 1 |
| Code style / formatting | 0.5260 | 0.5449 | 0.3768 | 0.4987 | 45 / 43 / 35 / 16 |
| Architecture / design constraints | 0.4656 | 0.4493 | 0.3373 | 0.5443 | 37 / 33 / 26 / 20 |
| Domain models / key abstractions | 0.4927 | 0.4969 | 0.3469 | 0.5403 | 12 / 12 / 8 / 3 |
| API / interface contracts | 0.5203 | 0.5224 | 0.3619 | 0.5720 | 32 / 29 / 25 / 6 |
| Do / Don't rules | 0.4346 | 0.4301 | 0.3361 | 0.4724 | 40 / 39 / 31 / 12 |
| Git / PR / commit conventions | 0.5857 | 0.5943 | 0.4813 | 0.2702 | 31 / 30 / 29 / 1 |
| Tooling-specific agent config | 0.4836 | 0.5425 | 0.4624 | 0.5556 | 36 / 29 / 30 / 15 |
| Examples / few-shot snippets | 0.5113 | 0.5115 | 0.3555 | 0.5805 | 21 / 21 / 17 / 3 |
| Security / secrets | 0.5374 | 0.5512 | 0.3802 | 0.5397 | 29 / 28 / 20 / 7 |
| Performance | 0.5234 | 0.5258 | 0.3757 | 0.5819 | 24 / 23 / 17 / 4 |
| Ownership / contacts | n/a | n/a | n/a | n/a | 0 / 0 / 0 / 0 |
| Maintenance / when to update | 0.4140 | 0.4458 | 0.2741 | n/a | 18 / 17 / 13 / 0 |

## Sources / notes

- gpt-4o-mini full / overlap / per-category: reused from `metrics_full.json`, `metrics_overlap.json`, `metrics_per_category.json`.
- CodeLlama overlap R1 + cosine: reused from `systems/codellama13b_base_metrics_comparison.json` → `overlap_sections_4fmt`.
- CodeLlama full-file R1: reused from `full_file_4fmt`; **embedding_cosine newly computed** (was missing from comparison export).
- CodeLlama preds: `filtered_predictions/codellama13b_{base,qlora}.json`.
- CodeLlama per-category: scored with legacy Ownership probes (published content pipeline).
- Embed model: `all-MiniLM-L6-v2`
- Elapsed: 237.2s

