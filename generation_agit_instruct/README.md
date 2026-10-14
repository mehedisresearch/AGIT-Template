# AGIT-Instruct Benchmark

Four-format instruction-file generation benchmark. **Official split after filtration:** train / val / test = **1,432 / 321 / 62**.

See [`data/BENCHMARK.md`](data/BENCHMARK.md) for the authoritative numbers, filtration steps, and paper-ready text.

## Corpus & splits

| Slice | N |
|---|---:|
| Four-format corpus (AGENTS / CLAUDE / Copilot / Cursor; ≥2 sections) | **2,853** files / **552** repos |
| **Official train / val / test** (repo-disjoint; test = 62-file eval set) | **1,432 / 321 / 62** |
| Official files | `data/train.json`, `data/val.json`, `data/test.json` |
| Category instances (test) | **556** |

**Test definition.** `data/test.json` is the four-format eval set of **62** files (origin: mixed-format fulltest **77** → drop SKILL/GEMINI → **62**). Train / val are repository-disjoint from those 62. Construction dumps and prior aliases live under `archive_data/`.

## Four generation systems

| # | System | Predictions (`results/filtered_predictions/`) |
|---|---|---|
| 1 | **gpt-4o-mini zero_shot** | `zero_shot.json` |
| 2 | **gpt-4o-mini RAG** | `rag.json` |
| 3 | **CodeLlama-13B base** | `codellama13b_base.json` |
| 4 | **CodeLlama-13B QLoRA** | `codellama13b_qlora.json` |

Gold references: `test_refs.json` (aligned with `data/test.json`, n=62). Small CodeLlama run meta under `results/systems/`.

Prompts / template: `prompts/` (system + ZS + RAG + 16-category AGIT template). Prompt builders: `scripts/api_prompts.py`.

## Layout

```
generation_agit_instruct/
  data/          # train.json, val.json, test.json, BENCHMARK.md, split_meta.json
  archive_data/  # provenance dumps, prior aliases, filter notes (not needed to load splits)
  prompts/       # system + ZS + RAG + AGIT 16-category template
  results/       # n=62 metrics + filtered preds for all 4 systems
  scripts/       # scoring / category / prompt helpers (no API keys)
```

| Path | Role |
|---|---|
| `data/BENCHMARK.md` | **Official benchmark definition** |
| `data/train.json` / `val.json` / `test.json` | Official splits (1432 / 321 / 62) |
| `data/split_meta.json` | Split sizes + verified repo-disjoint flag |
| `archive_data/` | 2853-pair provenance, former `test_eval_62`, generic_instruct_* aliases |
| `results/metrics_r1_cosine_4systems.{json,md}` | Full-file + overlap R1 / cosine (4 systems) |
| `results/metrics_per_category_fixed_ownership.json` | Per-category **presence** (fixed Ownership) |
| `results/summary_per_category_4systems.md` | Presence + tier coverage tables |
| `results/metrics_three_tiers.json` | Tier coverage (Required / Gap / Recommended) |
| `results/compliance_required_vs_gap.{json,md}` | Template compliance (ZS + RAG) |
| `results/metrics_{full,overlap,per_category}.json` | Detailed gpt-4o-mini metrics (legacy Ownership for content) |
| `results/summary.md` | gpt-4o-mini-only eval narrative |

## Corpus builders (optional; needs source exports)

```bash
# Build 2853-pair corpus + PAPER_NARRATIVE / filter notes
python3 scripts/build_agit_instruct_4fmt.py

# Repo-holdout train/val; official test is the 62-file eval set
python3 scripts/build_agit_generic_splits.py
```

## Reproduce metrics

From this folder (no LLM API; needs `rouge-score`, `sentence-transformers`, etc.):

```bash
# Presence + tier coverage (all 4 systems; fixed Ownership probes)
python3 scripts/score_per_category_presence_4systems.py

# Full-file + overlap R1 / cosine (all 4; reuses published gpt-4o-mini + CL overlap tables)
python3 scripts/score_r1_cosine_4systems.py

# Recompute gpt-4o-mini full/overlap from packaged preds only
python3 scripts/reproduce_score_4fmt.py
```

Compare outputs to the committed files under `results/`. Presence script is CPU-light; R1/cosine needs MiniLM embeddings.

## Paper pointers

- **Dataset / benchmark numbers:** `data/BENCHMARK.md`
- Headline R1 / cosine: `results/metrics_r1_cosine_4systems.md`
- Category presence (Ownership fixed): `results/summary_per_category_4systems.md`
- Filter story (77→62 test set): `results/summary.md` + `archive_data/FILTER_README.md`
