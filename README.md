# AGIT-Template

Replication package for the AGIT paper (empirical study + **AGIT-Instruct** generation benchmark). Artifacts are separated by research question. **Generation uses the 2,853 four-format files only** (AGENTS / CLAUDE / Copilot / Cursor; ≥2 sections). SKILL, GEMINI, mixed 3,889/557 corpus, pilots, and sample3 are excluded.

> ### Access the AGIT-Instruct benchmark
>
> **Directory:** [`generation_agit_instruct/`](generation_agit_instruct/)
>
> | What you need | Path |
> |---|---|
> | Official train / val / test splits | [`generation_agit_instruct/data/`](generation_agit_instruct/data/) (`train.json`, `val.json`, `test.json`) |
> | Benchmark definition & paper-ready numbers | [`generation_agit_instruct/data/BENCHMARK.md`](generation_agit_instruct/data/BENCHMARK.md) |
> | Split metadata | [`generation_agit_instruct/data/split_meta.json`](generation_agit_instruct/data/split_meta.json) |
> | Prompts, results, scoring scripts | `generation_agit_instruct/{prompts,results,scripts}/` |
>
> Start at [`generation_agit_instruct/README.md`](generation_agit_instruct/README.md), then read `data/BENCHMARK.md` for the authoritative split (**1,432 / 321 / 62**).

This repository root **is** the replication package (formerly `agit_model/replication_package/`).

## Canonical paper N (verify against folders)

| Slice | Primary N | Folder |
|---|---|---|
| **Corpus** | **1,000** repos (500 top + 500 bottom); instruction extracts for adopters | `corpus/` |
| **RQ1 — Adoption** | **1,000** repos; **582** with ≥1 of 4 formats (**66.2%** top / **50.2%** bottom; overall **58.2%**) | `rq1_adoption/` |
| **RQ2 — Content** | **3,387** files labeled with **16** categories (4 formats); instruction consistency **n=150** / **n=386** (population **3154**) | `rq2_taxonomy/`, `rq2_consistency/` |
| **RQ3 — Maintenance** | **5,396** heading-level edit events; **448** unique files; **283** repos; **943** PRs; five per-file metrics | `rq3_maintenance/` |
| **AGIT-Instruct Benchmark** | **552** repos / **2,853** files; official splits **1,432 / 321 / 62**; see `generation_agit_instruct/data/BENCHMARK.md` | [`generation_agit_instruct/`](generation_agit_instruct/) |

## Raw data layout

```
corpus/                         # N=1000 universe + instruction extracts (~56 MB)
  repo_list_1000.csv
  {top,bottom}_500_projects_instruction_files.csv
  instruction_extracts/         # ~35 MB (also .tar.gz ~10 MB)
  labeled_unified_files.tar.gz  # 595 repos / 4468 labeled files
rq1_adoption/data/              # slim inventories (inputs for analyze_rq1)
rq2_taxonomy/data/              # extracts symlinks + rq2_file_records.jsonl (3387)
rq2_consistency/data/           # section_pairs_population_3154.jsonl + samples
rq3_maintenance/data/           # events + slim aidev_cache/ (~39 MB)
generation_agit_instruct/data/  # official train/val/test + test_eval_62 + BENCHMARK.md
scripts/                        # fetch helpers for omitted large artifacts
```

## Folder → paper mapping

### `corpus/`

Defines the **exact 1000-repo corpus**: metadata, instruction-path inventories, and per-repo instruction-file extracts (not full git clones). See `corpus/README.md`.

### `rq1_adoption/`

- `rq1_results.json` — prevalence, multi-format, language, star-bin, logit summaries (`n_total=1000`).
- `rq1_project_format_matrix.csv` — one row per repo (n=1000) with `has_any` and per-format flags (`has_any` sum = 582).
- `rq1_language_format.csv` — language × format aggregates.
- **`data/`** — slim inventories used to (re)build the above.
- **`analysis/`** — `analyze_rq1_adoption.py`, `summarize_rq1.py`, `METHODOLOGY.md`, study notebook.

### `rq2_taxonomy/`

- Aggregate CSVs/JSON (`n_files=3387`) + `summary.md`.
- **`data/`** — `top_repos`/`bottom_repos` extracts, `rq2_file_records.jsonl` (3387), labeled `unified_files` tarball/JSONL.
- **`analysis/`** — `analyze_rq2_taxonomy.py`, `summarize_rq2.py`, `METHODOLOGY.md`, study notebook.

### `rq2_consistency/`

- Samples n=150 / n=386 + metrics + scope audit.
- **`data/`** — full **3154**-pair population + sample copies.
- **`analysis/`** — judge/scope notes from interchangeability pipeline.

### `rq3_maintenance/`

| Artifact | N | Meaning |
|---|---:|---|
| `rq3_category_durability_all16.csv` Σ `total_edits` | **5,396** | Heading-level add/delete events across 16 categories |
| `rq3_instruction_events.csv` | **2,146** | Instruction-file touch events in agentic PRs |
| Unique files / repos / PRs | **448 / 283 / 943** | From events + `rq3_file_lifecycle.csv` |

**`data/aidev_cache/`** ships all AIDev-pop tables except full `pr_commit_details.parquet` (~463 MB; fetch via `scripts/fetch_aidev_cache.sh`). Instruction-only detail rows (n=2146) are included.

### `generation_agit_instruct/` — AGIT-Instruct Benchmark

```
generation_agit_instruct/
  data/       # official train/val/test + test_eval_62 + BENCHMARK.md (+ provenance/)
  prompts/    # system + ZS + RAG templates + 16-category AGIT template
  results/    # 4-system metrics + filtered predictions (n=62)
  scripts/    # scoring / build / prompt / category helpers
```

| File | N / role |
|---|---|
| `data/BENCHMARK.md` | **Official** numbers, filtration steps, paper-ready text |
| `data/train.json` / `val.json` / `test.json` | **1,432 / 321 / 75** (repo-holdout, category-stratified) |
| `data/test_eval_62.json` | **62**-file four-system scored eval subset |
| `data/provenance/` | Full **2,853**-pair construction corpora |

**Official test = 62** (four-format eval set; mixed fulltest **n=77** → drop SKILL/GEMINI → **62**). See `generation_agit_instruct/data/BENCHMARK.md`.

## How to cite paths in the paper

Paths are relative to this repository root:

- Corpus: `corpus/repo_list_1000.csv`
- RQ1: `rq1_adoption/rq1_results.json`
- RQ2 taxonomy: `rq2_taxonomy/rq2_results.json` (records: `rq2_taxonomy/data/rq2_file_records.jsonl`)
- RQ2 consistency: `rq2_consistency/data/section_pairs_population_3154.jsonl`
- RQ3 heading edits: `rq3_maintenance/rq3_category_durability_all16.csv` (sum `total_edits` = 5,396)
- RQ3 file lifecycle: `rq3_maintenance/rq3_file_lifecycle.csv` (n=448)
- **AGIT-Instruct** official splits: `generation_agit_instruct/data/{train,val,test}.json` (see `generation_agit_instruct/data/BENCHMARK.md`)

See `DATA_MANIFEST.md` for every included file, role, size, and count.

## Re-run analysis

```bash
# Package-only summaries (no external data):
python3 rq1_adoption/analysis/summarize_rq1.py
python3 rq2_taxonomy/analysis/summarize_rq2.py
python3 rq3_maintenance/analysis/summarize_rq3.py

# Full re-derivation from packaged data/:
python3 rq1_adoption/analysis/analyze_rq1_adoption.py
python3 rq2_taxonomy/analysis/analyze_rq2_taxonomy.py
# RQ3 full re-derive needs full pr_commit_details (~463MB):
./scripts/fetch_aidev_cache.sh
python3 rq3_maintenance/analysis/analyze_rq3_maintenance.py
```

