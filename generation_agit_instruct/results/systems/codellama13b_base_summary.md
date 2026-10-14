# CodeLlama-13B Base vs QLoRA — Generic Intent Full Test

## Setup

- Base model: `/gpuhome/shanto1/models/CodeLlama-13b-Instruct-hf`
- Adapter: **none** (Instruct zero-shot)
- Load: **fp16**
- Same test prompts as QLoRA: `exports/generic_intent_fulltest/codellama13b_lora/data/test.jsonl` (`[INST]` + requirements)
- n_test predictions: **77** (4fmt subset: **62**)

## Full-file metrics (n=77, macro mean)

| Approach | R1-P | R1-R | R1-F | R2-F | RL-P | RL-R | RL-F | Token-F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| gpt-4o-mini_zero_shot | 0.5009 | 0.3632 | 0.4104 | 0.0758 | 0.1896 | 0.1400 | 0.1563 | 0.3576 |
| gpt-4o-mini_rag | 0.4833 | 0.4251 | 0.4407 | 0.0933 | 0.1911 | 0.1712 | 0.1755 | 0.3852 |
| codellama13b_base | 0.2749 | 0.3398 | 0.2907 | 0.0386 | 0.1199 | 0.1525 | 0.1280 | 0.2519 |
| codellama13b_qlora | 0.5969 | 0.2104 | 0.2649 | 0.0666 | 0.3280 | 0.1070 | 0.1348 | 0.2404 |

## Overlap-section metrics (n=77 gold ∩ pred categories)

| Approach | n_scored | R1-F | R2-F | RL-F | BLEU | METEOR | Emb Cosine | BERTScore F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| zero_shot | 76 | 0.3694 | 0.0722 | 0.1735 | 0.0207 | 0.1662 | 0.6916 | 0.2222 |
| rag | 77 | 0.4138 | 0.0897 | 0.1889 | 0.0421 | 0.1986 | 0.6902 | 0.2378 |
| codellama13b_base | 67 | 0.2899 | 0.0377 | 0.1442 | 0.0058 | 0.1337 | 0.4250 | -0.0717 |
| codellama13b_qlora | 66 | 0.3383 | 0.0972 | 0.2050 | 0.0657 | 0.2270 | 0.6326 | 0.2887 |

## 4fmt subset (exclude SKILL/GEMINI, n=62)

gpt-4o-mini numbers from `exports/generic_intent_fulltest_4fmt/summary.md`.

### Full-file

| Approach | n | R1-F | R2-F | RL-F | Token-F1 |
|---|---:|---:|---:|---:|---:|
| gpt-4o-mini_zero_shot | 62 | 0.4225 | 0.0824 | 0.1597 | — |
| gpt-4o-mini_rag | 62 | 0.4585 | 0.1006 | 0.1803 | — |
| codellama13b_base | 62 | 0.3044 | 0.0420 | 0.1323 | 0.2632 |
| codellama13b_qlora | 62 | 0.2727 | 0.0735 | 0.1391 | 0.2481 |

### Overlap-section

| Approach | n_scored | R1-F | R2-F | RL-F | Emb Cosine | BERTScore F1 |
|---|---:|---:|---:|---:|---:|---:|
| gpt-4o-mini_zero_shot | 61 | 0.3863 | 0.0802 | 0.1796 | 0.7097 | 0.2371 |
| gpt-4o-mini_rag | 62 | 0.4325 | 0.0977 | 0.1966 | 0.7081 | 0.2543 |
| codellama13b_base | 53 | 0.3090 | 0.0423 | 0.1525 | 0.4341 | -0.0624 |
| codellama13b_qlora | 57 | 0.3465 | 0.1035 | 0.2121 | 0.6468 | 0.2931 |

## Base vs QLoRA (headline)

- Full-file RL-F: base **0.1280** vs QLoRA **0.1348**
- Full-file Token-F1: base **0.2519** vs QLoRA **0.2404**
- Overlap RL-F: base **0.1442** vs QLoRA **0.2050**
- Overlap BERTScore: base **-0.0717** vs QLoRA **0.2887**

## Paths

- Predictions: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest/codellama13b_base/predictions.json`
- Metrics: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest/codellama13b_base/metrics.json`
- Comparison: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest/codellama13b_base/metrics_comparison.json`
- This summary: `/gpuhome/shanto1/agit_model/exports/generic_intent_fulltest/codellama13b_base/comparison.md`
