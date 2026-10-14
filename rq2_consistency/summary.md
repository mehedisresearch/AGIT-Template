# RQ2 instruction consistency — summary

Coding column: **`manual_label`**.

## Distribution

| Label | n=150 | % | n=386 | % |
|---|---:|---:|---:|---:|
| Equivalent | 48 | 32.0% | 126 | 32.6% |
| Complementary | 79 | 52.7% | 198 | 51.3% |
| Divergent | 23 | 15.3% | 62 | 16.1% |
| Contradictory | 0 | 0.0% | 0 | 0.0% |
| **Total** | **150** | 100% | **386** | 100% |

## Agreement with auto labels

| Metric | n=150 | n=386 |
|---|---|---|
| Agreement | 88/150 (58.7%) | 233/386 (60.4%) |
| Cohen κ | 0.430 | 0.452 |

## n=386 sample definition

Similarity-stratified expansion of the n=150 sample: keep all 150 pairs; top up to 128 / 128 / 130 in low (<0.5) / mid (0.5–0.85) / high (≥0.85) bins (seed 42). See `rq2_consistency_sample_definition_n386.json`.
