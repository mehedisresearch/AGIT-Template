# CodeLlama-13B QLoRA — Generic Intent Full Test

## Setup

- Base model: `/gpuhome/shanto1/models/CodeLlama-13b-Instruct-hf`
- Adapter: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest/codellama13b_lora/outputs/qlora/best`
- Train / val / test: **2066** / **262** / **77**
- Quantization: **4-bit NF4 QLoRA** (fp16 LoRA OOM on V100-32GB; weights alone ~26GB)
- max_length=1536, lr=0.0001, eff_batch≈16, best_val_loss=1.6833675972377982
- n_test predictions: **77**

## Full-file metrics (macro mean over test)

| Approach | R1-P | R1-R | R1-F | R2-F | RL-P | RL-R | RL-F | Token-F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| gpt-4o-mini_zero_shot | 0.5009 | 0.3632 | 0.4104 | 0.0758 | 0.1896 | 0.1400 | 0.1563 | 0.3576 |
| gpt-4o-mini_rag | 0.4833 | 0.4251 | 0.4407 | 0.0933 | 0.1911 | 0.1712 | 0.1755 | 0.3852 |
| codellama13b_qlora | 0.5969 | 0.2104 | 0.2649 | 0.0666 | 0.3280 | 0.1070 | 0.1348 | 0.2404 |

## Overlap-section metrics (gold ∩ pred categories)

| Approach | n_scored | R1-F | R2-F | RL-F | BLEU | METEOR | Emb Cosine | BERTScore F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 76 | 0.3694 | 0.0722 | 0.1735 | 0.0207 | 0.1662 | 0.6916 | 0.2222 |
| rag | 77 | 0.4138 | 0.0897 | 0.1889 | 0.0421 | 0.1986 | 0.6902 | 0.2378 |
| codellama13b_qlora | 66 | 0.3383 | 0.0972 | 0.2050 | 0.0657 | 0.2270 | 0.6326 | 0.2887 |

## Winners

- Full-file ROUGE-L F: **gpt-4o-mini_rag** (0.1755)
- Overlap ROUGE-L F: **codellama13b_qlora** (0.2050)

## Paths

- Adapter: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest/codellama13b_lora/outputs/qlora/best`
- Predictions: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest/codellama13b_lora/predictions.json`
- Metrics: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest/codellama13b_lora/metrics.json`
- This summary: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest/codellama13b_lora/summary.md`
