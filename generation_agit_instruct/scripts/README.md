# Generation scoring scripts

| Script | Role |
|---|---|
| `score_per_category_presence_4systems.py` | **Primary (4 systems).** Category presence + tier coverage with **fixed Ownership** probes. Writes `../results/metrics_per_category_fixed_ownership.json` + `summary_per_category_4systems.md`. |
| `score_r1_cosine_4systems.py` | **Primary (4 systems).** Full-file + overlap ROUGE-1 F1 / MiniLM cosine. Writes `../results/metrics_r1_cosine_4systems.{json,md}`. |
| `reproduce_score_4fmt.py` | Recompute gpt-4o-mini full-file + overlap from `../results/filtered_predictions/{zero_shot,rag}.json` (n=62). |
| `score_required_vs_gap_4fmt.py` | Template compliance (Required vs Gap); writes `../results/compliance_required_vs_gap.*`. |
| `score_three_tiers_4fmt.py` | Tier coverage (Required / Gap / Recommended); writes `../results/metrics_three_tiers.json`. |
| `build_agit_instruct_4fmt.py` | Build 2,853-pair corpus + `PAPER_NARRATIVE.md` / filter notes (needs source exports). |
| `build_agit_generic_splits.py` | Repo-holdout train/val/test splits (1,432 / 321 / 75). |
| `score_fulltest_4fmt.py` | Original filter+score entrypoint (reference; needs original fulltest layout to re-filter). |
| `score_overlap_sections.py` | Overlap-section helpers. |
| `metrics.py` | Lexical / structure metric helpers. |
| `agit_categories.py` | 16-category `ORDER` + `sections_from_markdown` (no API). |
| `format_buckets.py` | RQ2 four-format basename classifier. |
| `api_prompts.py` | `SYSTEM_PROMPT`, zero-shot / RAG user-prompt builders + MiniLM RAG index. |

## Reproduce

```bash
cd generation_agit_instruct/scripts

# Presence / tiers (all 4 systems)
python3 score_per_category_presence_4systems.py

# R1 + cosine (all 4 systems; needs sentence-transformers)
python3 score_r1_cosine_4systems.py

# gpt-4o-mini full/overlap only
python3 reproduce_score_4fmt.py

# Compliance / tiers (gpt-4o-mini preds; paths may need adjusting to ../results)
python3 score_required_vs_gap_4fmt.py
python3 score_three_tiers_4fmt.py
```

Predictions for all four systems live under `../results/filtered_predictions/`.
CodeLlama comparison tables used by the R1 script: `../results/systems/codellama13b_base_metrics_comparison.json`.
Corpus construction narrative: `../data/PAPER_NARRATIVE.md`, `../data/FILTER_README.md`.
