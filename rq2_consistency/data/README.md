# RQ2 consistency data inputs

| File | Role | n |
|---|---|---:|
| `section_pairs_population_3154.jsonl` | Full cross-format section-pair population | **3154** |
| `population_summary.json` | Population label rates / similarity | |
| `command_conflicts.json` | Build/test command-conflict audit | |
| `rq2_consistency_n150.csv` | Stratified coding sample | 150 |
| `rq2_consistency_n386.csv` | Expanded stratified sample | 386 |
| `rq2_consistency_scope_audit_n386.csv` | Path-scope audit | 386 |
| `rq2_consistency_sample_definition_n386.json` | Sampling recipe (seed 42) | |
| `rq2_consistency_metrics_{n150,n386}.json` | Agreement / κ vs auto labels | |

Coding column on samples: **`manual_label`**.

Provenance: `agit_model/interchangeability/` (population + LLM-judge / sample artifacts).
