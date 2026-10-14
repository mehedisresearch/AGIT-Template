# RQ2 taxonomy data inputs

| Path | Role | Approx size / n |
|---|---|---|
| `top_repos/`, `bottom_repos/` | Symlinks → `../../corpus/instruction_extracts/` (raw instruction files) | ~35 MB; paper **3387** 4-format files |
| `rq2_file_records.jsonl` | Per-file headings + 16-category keyword labels | **3387** rows |
| `rq2_file_records_meta.json` | Counts vs paper N | |
| `labeled_files_4fmt.jsonl` | Section-labeled 4-format subset from `unified_files` | ~3372 files |
| `labeled_repo_index.json` | Per-repo index over full labeled corpus | 595 repos |
| `labeled_unified_files.tar.gz` | Full labeled JSON corpus (4468 files incl. SKILL/GEMINI/README) | ~10 MB |
| `labeled_corpus_meta.json` | Provenance | |

## What feeds which analysis

- **Jaccard / prevalence / file stats** (`analyze_rq2_taxonomy.py`): walks `top_repos` + `bottom_repos`.
- **Understanding labels without re-walk**: `rq2_file_records.jsonl` (keyword pilot, matches paper N=3387).
- **Section-level labeled content** (categories + section text): `labeled_*.jsonl` / tarball (from `agit_model/unified_files`).

## Re-run

```bash
export AGIT_STUDY_ROOT="$(pwd)"   # expects top_repos/ + bottom_repos/
export AGIT_RQ_OUT="$(pwd)/.."
python3 ../analysis/analyze_rq2_taxonomy.py
```
