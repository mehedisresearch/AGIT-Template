# Per-system run metadata (CodeLlama)

Small artifacts only (no adapter weights or train dumps).

| File | Role |
|---|---|
| `codellama13b_base_generate_meta.json` | Base generate settings (original n=77) |
| `codellama13b_qlora_generate_meta.json` | QLoRA generate settings (original n=77) |
| `codellama13b_*_metrics_comparison.json` | Published full-file / overlap 4fmt comparison tables |
| `codellama13b_*_summary.md` | Original export summaries |

Filtered n=62 predictions are in `../filtered_predictions/codellama13b_{base,qlora}.json`.
