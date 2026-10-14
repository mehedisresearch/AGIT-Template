# DATA_MANIFEST

Every file included in the AGIT replication package (extract trees summarized as one row each).

Hard links: `agit_instruct_pairs_2853.json` ↔ `agit_instruct_4fmt_with_summary.json`; `generic_intent_files_2853.json` ↔ `generic_files_4fmt.json`; RQ1/RQ3 `data/` tables ↔ parent CSVs where noted; `corpus/*_instruction_files.csv` ↔ `rq1_adoption/data/` counterparts.

| Path | Role | n | bytes |
|---|---|---:|---:|
| `DATA_MANIFEST.md` | This manifest |  | 13,118 |
| `README.md` | Package overview |  | 6,482 |
| `corpus/README.md` | Corpus readme |  | 1,881 |
| `corpus/bottom_500_projects_instruction_files.csv` | Bottom-500 slim inventory | 500 | 95,675 |
| `corpus/corpus_meta.json` | Corpus counts/provenance |  | 503 |
| `corpus/instruction_extracts.tar.gz` | Instruction extracts archive |  | 10,430,899 |
| `corpus/instruction_extracts/` | Instruction extracts tree (top_repos+bottom_repos) | 4877 | 34,956,207 |
| `corpus/instruction_file_inventory.csv` | Flat instruction-path inventory | 3598 | 311,437 |
| `corpus/labeled_unified_files.tar.gz` | Labeled unified_files archive |  | 10,219,157 |
| `corpus/repo_list_1000.csv` | 1000-repo list | 1000 | 127,278 |
| `corpus/top_500_projects_instruction_files.csv` | Top-500 slim inventory | 500 | 164,322 |
| `generation_agit_instruct/README.md` | Folder readme |  | 3,653 |
| `generation_agit_instruct/data/FILTER_README.md` | AGIT-Instruct data |  | 2,608 |
| `generation_agit_instruct/data/PAPER_NARRATIVE.md` | AGIT-Instruct data |  | 1,875 |
| `generation_agit_instruct/data/agit_instruct_4fmt_with_summary.json` | AGIT-Instruct data | 2853 | 30,386,294 |
| `generation_agit_instruct/data/agit_instruct_pairs_2853.json` | AGIT-Instruct data | 2853 | 30,386,294 |
| `generation_agit_instruct/data/filter_meta.json` | AGIT-Instruct data |  | 4,931 |
| `generation_agit_instruct/data/generic_files_4fmt.json` | AGIT-Instruct data | 2853 | 18,625,331 |
| `generation_agit_instruct/data/generic_instruct_test.json` | AGIT-Instruct data | 75 | 440,407 |
| `generation_agit_instruct/data/generic_instruct_train.json` | AGIT-Instruct data | 1432 | 4,095,941 |
| `generation_agit_instruct/data/generic_instruct_val.json` | AGIT-Instruct data | 321 | 955,315 |
| `generation_agit_instruct/data/generic_intent_files_2853.json` | AGIT-Instruct data | 2853 | 18,625,331 |
| `generation_agit_instruct/data/split_meta.json` | AGIT-Instruct data |  | 2,161 |
| `generation_agit_instruct/prompts/agit_template_16categories.md` | Prompt/template |  | 24,283 |
| `generation_agit_instruct/prompts/agit_template_16categories_slim.md` | Prompt/template |  | 5,417 |
| `generation_agit_instruct/prompts/agit_template_meta.json` | Prompt/template |  | 7,162 |
| `generation_agit_instruct/prompts/rag_user_prompt.md` | Prompt/template |  | 867 |
| `generation_agit_instruct/prompts/system_prompt.txt` | Prompt/template |  | 287 |
| `generation_agit_instruct/prompts/zero_shot_user_prompt.md` | Prompt/template |  | 366 |
| `generation_agit_instruct/results/compliance_required_vs_gap.json` | Benchmark results |  | 168,509 |
| `generation_agit_instruct/results/compliance_required_vs_gap.md` | Benchmark results |  | 2,461 |
| `generation_agit_instruct/results/filter_meta.json` | Benchmark results |  | 9,930 |
| `generation_agit_instruct/results/filtered_predictions/codellama13b_base.json` | Benchmark results |  | 297,666 |
| `generation_agit_instruct/results/filtered_predictions/codellama13b_qlora.json` | Benchmark results |  | 117,821 |
| `generation_agit_instruct/results/filtered_predictions/rag.json` | Benchmark results |  | 217,272 |
| `generation_agit_instruct/results/filtered_predictions/test_refs.json` | Benchmark results | 62 | 260,652 |
| `generation_agit_instruct/results/filtered_predictions/zero_shot.json` | Benchmark results |  | 180,022 |
| `generation_agit_instruct/results/kept_files.json` | Benchmark results | 62 | 7,185 |
| `generation_agit_instruct/results/metrics_full.json` | Benchmark results |  | 75,923 |
| `generation_agit_instruct/results/metrics_overlap.json` | Benchmark results |  | 125,924 |
| `generation_agit_instruct/results/metrics_per_category.json` | Benchmark results |  | 14,087 |
| `generation_agit_instruct/results/metrics_per_category_fixed_ownership.json` | Benchmark results |  | 18,194 |
| `generation_agit_instruct/results/metrics_r1_cosine_4systems.json` | Benchmark results |  | 16,499 |
| `generation_agit_instruct/results/metrics_r1_cosine_4systems.md` | Benchmark results |  | 4,922 |
| `generation_agit_instruct/results/metrics_three_tiers.json` | Benchmark results |  | 9,253 |
| `generation_agit_instruct/results/removed_files.json` | Benchmark results | 15 | 1,249 |
| `generation_agit_instruct/results/summary.md` | Benchmark results |  | 6,653 |
| `generation_agit_instruct/results/summary_per_category_4systems.md` | Benchmark results |  | 3,165 |
| `generation_agit_instruct/results/summary_required_vs_gap.md` | Benchmark results |  | 2,709 |
| `generation_agit_instruct/results/systems/README.md` | Folder readme |  | 546 |
| `generation_agit_instruct/results/systems/codellama13b_base_generate_meta.json` | Benchmark results |  | 476 |
| `generation_agit_instruct/results/systems/codellama13b_base_metrics_comparison.json` | Benchmark results |  | 3,363 |
| `generation_agit_instruct/results/systems/codellama13b_base_summary.md` | Benchmark results |  | 3,042 |
| `generation_agit_instruct/results/systems/codellama13b_qlora_generate_meta.json` | Benchmark results |  | 381 |
| `generation_agit_instruct/results/systems/codellama13b_qlora_metrics_comparison.json` | Benchmark results |  | 818 |
| `generation_agit_instruct/results/systems/codellama13b_qlora_summary.md` | Benchmark results |  | 1,934 |
| `generation_agit_instruct/scripts/README.md` | Folder readme |  | 2,301 |
| `generation_agit_instruct/scripts/agit_categories.py` | Scoring/build script |  | 4,922 |
| `generation_agit_instruct/scripts/api_prompts.py` | Scoring/build script |  | 7,503 |
| `generation_agit_instruct/scripts/build_agit_generic_splits.py` | Scoring/build script |  | 10,922 |
| `generation_agit_instruct/scripts/build_agit_instruct_4fmt.py` | Scoring/build script |  | 18,820 |
| `generation_agit_instruct/scripts/format_buckets.py` | Scoring/build script |  | 1,377 |
| `generation_agit_instruct/scripts/metrics.py` | Scoring/build script |  | 3,463 |
| `generation_agit_instruct/scripts/reproduce_score_4fmt.py` | Scoring/build script |  | 2,770 |
| `generation_agit_instruct/scripts/score_fulltest_4fmt.py` | Scoring/build script |  | 26,189 |
| `generation_agit_instruct/scripts/score_overlap_sections.py` | Scoring/build script |  | 15,710 |
| `generation_agit_instruct/scripts/score_per_category_presence_4systems.py` | Scoring/build script |  | 13,151 |
| `generation_agit_instruct/scripts/score_r1_cosine_4systems.py` | Scoring/build script |  | 15,637 |
| `generation_agit_instruct/scripts/score_required_vs_gap_4fmt.py` | Scoring/build script |  | 16,514 |
| `generation_agit_instruct/scripts/score_three_tiers_4fmt.py` | Scoring/build script |  | 13,498 |
| `manual_review_by_category.xlsx` | Package file |  | 206,705 |
| `rq1_adoption/README.md` | Folder readme |  | 1,028 |
| `rq1_adoption/analysis/METHODOLOGY.md` | Analysis script/notes |  | 910 |
| `rq1_adoption/analysis/README.md` | Folder readme |  | 638 |
| `rq1_adoption/analysis/analyze_rq1_adoption.py` | Analysis script/notes |  | 8,762 |
| `rq1_adoption/analysis/summarize_rq1.py` | Analysis script/notes |  | 1,780 |
| `rq1_adoption/analysis/universal_agent_instruction_study.ipynb` | Analysis script/notes |  | 26,338 |
| `rq1_adoption/data/README.md` | Folder readme |  | 699 |
| `rq1_adoption/data/bottom_500_projects_instruction_files.csv` | Package file | 500 | 95,675 |
| `rq1_adoption/data/top_500_projects_instruction_files.csv` | Package file | 500 | 164,322 |
| `rq1_adoption/rq1_language_format.csv` | RQ1 table | 10 | 531 |
| `rq1_adoption/rq1_project_format_matrix.csv` | RQ1 table | 1000 | 71,730 |
| `rq1_adoption/rq1_results.json` | RQ1 table |  | 12,394 |
| `rq1_adoption/summary.md` | Package file |  | 704 |
| `rq2_consistency/README.md` | Folder readme |  | 908 |
| `rq2_consistency/analysis/llm_judge_n386_summary.md` | Analysis script/notes |  | 2,012 |
| `rq2_consistency/analysis/population_summary.json` | Analysis script/notes |  | 7,352 |
| `rq2_consistency/analysis/rq2_divergent_scope_report.md` | Analysis script/notes |  | 9,564 |
| `rq2_consistency/analysis/run_batch_judge_n386.py` | Analysis script/notes |  | 13,738 |
| `rq2_consistency/analysis/scope_report_n386.md` | Analysis script/notes |  | 12,123 |
| `rq2_consistency/data/README.md` | Folder readme |  | 797 |
| `rq2_consistency/data/command_conflicts.json` | Package file | 92 | 101,932 |
| `rq2_consistency/data/population_summary.json` | Package file |  | 7,352 |
| `rq2_consistency/data/rq2_consistency_metrics_n150.json` | RQ2 table |  | 2,893 |
| `rq2_consistency/data/rq2_consistency_metrics_n386.json` | RQ2 table |  | 3,304 |
| `rq2_consistency/data/rq2_consistency_n150.csv` | RQ2 table | 3816 | 227,252 |
| `rq2_consistency/data/rq2_consistency_n386.csv` | RQ2 table | 10072 | 652,220 |
| `rq2_consistency/data/rq2_consistency_sample_definition_n386.json` | RQ2 table |  | 1,283 |
| `rq2_consistency/data/rq2_consistency_scope_audit_n386.csv` | RQ2 table | 386 | 144,014 |
| `rq2_consistency/data/section_pairs_population_3154.jsonl` | Pair population | 3154 | 2,696,933 |
| `rq2_consistency/rq2_consistency_metrics_n150.json` | RQ2 table |  | 2,893 |
| `rq2_consistency/rq2_consistency_metrics_n386.json` | RQ2 table |  | 3,304 |
| `rq2_consistency/rq2_consistency_n150.csv` | RQ2 table | 3816 | 227,252 |
| `rq2_consistency/rq2_consistency_n386.csv` | RQ2 table | 10072 | 652,220 |
| `rq2_consistency/rq2_consistency_sample_definition_n386.json` | RQ2 table |  | 1,283 |
| `rq2_consistency/rq2_consistency_scope_audit_n386.csv` | RQ2 table | 386 | 144,014 |
| `rq2_consistency/summary.md` | Package file |  | 767 |
| `rq2_taxonomy/README.md` | Folder readme |  | 1,484 |
| `rq2_taxonomy/analysis/METHODOLOGY.md` | Analysis script/notes |  | 726 |
| `rq2_taxonomy/analysis/README.md` | Folder readme |  | 723 |
| `rq2_taxonomy/analysis/analyze_rq2_taxonomy.py` | Analysis script/notes |  | 16,775 |
| `rq2_taxonomy/analysis/summarize_rq2.py` | Analysis script/notes |  | 1,628 |
| `rq2_taxonomy/analysis/universal_agent_instruction_study.ipynb` | Analysis script/notes |  | 26,338 |
| `rq2_taxonomy/data/README.md` | Folder readme |  | 1,257 |
| `rq2_taxonomy/data/bottom_repos/` | Symlink → corpus/instruction_extracts | symlink | 0 |
| `rq2_taxonomy/data/labeled_corpus_meta.json` | Package file |  | 336 |
| `rq2_taxonomy/data/labeled_files_4fmt.jsonl` | Package file | 577 | 34,129,128 |
| `rq2_taxonomy/data/labeled_repo_index.json` | Package file | 595 | 160,978 |
| `rq2_taxonomy/data/labeled_unified_files.tar.gz` | Package file |  | 10,219,157 |
| `rq2_taxonomy/data/rq2_file_records.jsonl` | Per-file RQ2 labels/headings | 3387 | 2,744,415 |
| `rq2_taxonomy/data/rq2_file_records_meta.json` | RQ2 table | 3387 | 538 |
| `rq2_taxonomy/data/top_repos/` | Symlink → corpus/instruction_extracts | symlink | 0 |
| `rq2_taxonomy/rq2_category_prevalence.csv` | RQ2 table | 16 | 877 |
| `rq2_taxonomy/rq2_file_stats.csv` | RQ2 table | 4 | 248 |
| `rq2_taxonomy/rq2_heading_jaccard.csv` | RQ2 table | 6 | 448 |
| `rq2_taxonomy/rq2_results.json` | RQ2 table | 3387 | 37,477 |
| `rq2_taxonomy/rq2_within_repo_jaccard.csv` | RQ2 table | 358 | 30,876 |
| `rq2_taxonomy/summary.md` | Package file |  | 4,721 |
| `rq3_maintenance/README.md` | Folder readme |  | 1,251 |
| `rq3_maintenance/analysis/METHODOLOGY.md` | Analysis script/notes |  | 890 |
| `rq3_maintenance/analysis/README.md` | Folder readme |  | 962 |
| `rq3_maintenance/analysis/analyze_rq3_durability_all16.py` | Analysis script/notes |  | 5,480 |
| `rq3_maintenance/analysis/analyze_rq3_maintenance.py` | Analysis script/notes |  | 16,848 |
| `rq3_maintenance/analysis/summarize_rq3.py` | Analysis script/notes |  | 1,978 |
| `rq3_maintenance/analysis/universal_agent_instruction_study.ipynb` | Analysis script/notes |  | 26,338 |
| `rq3_maintenance/data/README.md` | Folder readme |  | 1,174 |
| `rq3_maintenance/data/aidev_cache/pr_commit_details_instruction_rows.parquet` | AIDev parquet | 2146 | 1,864,591 |
| `rq3_maintenance/data/aidev_cache/pr_commits.parquet` | AIDev parquet | 88576 | 8,314,097 |
| `rq3_maintenance/data/aidev_cache/pr_reviews.parquet` | AIDev parquet | 28875 | 7,517,041 |
| `rq3_maintenance/data/aidev_cache/pr_task_type.parquet` | AIDev parquet | 33596 | 2,993,264 |
| `rq3_maintenance/data/aidev_cache/pull_request.parquet` | AIDev parquet | 33596 | 16,855,612 |
| `rq3_maintenance/data/aidev_cache/repository.parquet` | AIDev parquet | 2807 | 167,251 |
| `rq3_maintenance/data/aidev_cache_meta.json` | Package file |  | 576 |
| `rq3_maintenance/data/rq3_category_durability.csv` | RQ3 table | 12 | 409 |
| `rq3_maintenance/data/rq3_category_durability_all16.csv` | RQ3 table | 16 | 713 |
| `rq3_maintenance/data/rq3_cliffs_delta.csv` | RQ3 table | 24 | 1,270 |
| `rq3_maintenance/data/rq3_durable_headings.csv` | RQ3 table | 40 | 1,415 |
| `rq3_maintenance/data/rq3_ephemeral_headings.csv` | RQ3 table | 40 | 1,785 |
| `rq3_maintenance/data/rq3_file_lifecycle.csv` | RQ3 table | 448 | 87,672 |
| `rq3_maintenance/data/rq3_instruction_events.csv` | RQ3 table | 5536 | 1,344,780 |
| `rq3_maintenance/data/rq3_kruskal_wallis.csv` | RQ3 table | 6 | 241 |
| `rq3_maintenance/data/rq3_results.json` | RQ3 table |  | 23,983 |
| `rq3_maintenance/rq3_category_durability.csv` | RQ3 table | 12 | 409 |
| `rq3_maintenance/rq3_category_durability_all16.csv` | RQ3 table | 16 | 713 |
| `rq3_maintenance/rq3_cliffs_delta.csv` | RQ3 table | 24 | 1,270 |
| `rq3_maintenance/rq3_durable_headings.csv` | RQ3 table | 40 | 1,415 |
| `rq3_maintenance/rq3_ephemeral_headings.csv` | RQ3 table | 40 | 1,785 |
| `rq3_maintenance/rq3_file_lifecycle.csv` | RQ3 table | 448 | 87,672 |
| `rq3_maintenance/rq3_instruction_events.csv` | RQ3 table | 5536 | 1,344,780 |
| `rq3_maintenance/rq3_kruskal_wallis.csv` | RQ3 table | 6 | 241 |
| `rq3_maintenance/rq3_results.json` | RQ3 table |  | 23,983 |
| `rq3_maintenance/summary.md` | Package file |  | 3,505 |
| `scripts/README.md` | Folder readme |  | 532 |
| `scripts/fetch_aidev_cache.sh` | Package file |  | 2,580 |
| `scripts/fetch_instruction_extracts.sh` | Package file |  | 3,264 |

## Verification snapshot

```json
{
  "CORPUS": {
    "n_repos": 1000,
    "adopters": 582,
    "instruction_paths": 3598
  },
  "RQ1": {
    "n_total": 1000,
    "has_any": 582,
    "top_pct": 66.2,
    "bottom_pct": 50.2,
    "overall_pct": 58.2
  },
  "RQ2": {
    "n_files": 3387,
    "file_records": 3387,
    "consistency_population": 3154,
    "consistency_n150": 150,
    "consistency_n386": 386
  },
  "RQ3": {
    "heading_edits_note": "sum total_edits in rq3_category_durability_all16.csv = 5396",
    "file_touches": 2146,
    "files": 448
  },
  "GEN": {
    "pairs": 2853,
    "train_val_test": [
      1432,
      321,
      75
    ],
    "eval_4fmt": 62
  },
  "OMITTED": {
    "full_tree_inventories_MB": 228,
    "full_pr_commit_details_MB": 463,
    "full_git_clones": "multi-GB; use instruction extracts"
  }
}
```

## Analysis files per RQ

- **Corpus** `corpus/` — 1000-repo inventories + instruction extracts
- **RQ1** `rq1_adoption/data/` + `analysis/`
- **RQ2 taxonomy** `rq2_taxonomy/data/` + `analysis/`
- **RQ2 consistency** `rq2_consistency/data/` + `analysis/`
- **RQ3** `rq3_maintenance/data/` + `analysis/`
- **Generation** `generation_agit_instruct/{data,scripts}/`
- **Fetch helpers** `scripts/fetch_*.sh`
