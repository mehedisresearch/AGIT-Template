# LLM judge n=386 (gpt-4o Batch)

## Sample definition

No project artifact defines a population of exactly **386**. Closest nearby totals:
- Test / CI commands pairs: **381**
- Multi-format repos (this rebuild): **314** (summary.json lists 290)

**Choice:** expand the existing similarity-stratified consistency check from n=150 → n=386.
- Keep all **150** original pairs
- Top up to **128 / 128 / 130** in low (&lt;0.5) / mid (0.5–0.85) / high (≥0.85) bins
- Seed **42**; texts truncated to **800** chars (same as n=150 judge)
- Prompt/schema identical to `MRcd.py`

## LLM label distribution (gpt-4o)

| Label | n=386 | % | n=150 ref | % |
|---|---:|---:|---:|---:|
| Equivalent | 126 | 32.6% | 48 | 32.0% |
| Complementary | 198 | 51.3% | 79 | 52.7% |
| Divergent | 62 | 16.1% | 23 | 15.3% |
| Contradictory | 0 | 0.0% | 0 | 0.0% |
| **Total** | **386** | 100% | **150** | 100% |

## Agreement with auto labels

| Metric | n=386 | n=150 |
|---|---:|---:|
| Agreement | 233/386 (60.4%) | 88/150 (58.7%) |
| Cohen κ | 0.452 | 0.430 |

## Auto labels on the n=386 sample (offline)

| Label | n | % |
|---|---:|---:|
| Equivalent | 129 | 33.4% |
| Complementary | 76 | 19.7% |
| Divergent | 160 | 41.5% |
| Contradictory | 21 | 5.4% |

## By similarity bin (LLM)

| Bin | n | Agree(auto) | Eq | Comp | Div | Con |
|---|---:|---:|---:|---:|---:|---:|
| high_>=0.85 | 130 | 91% | 119 | 7 | 4 | 0 |
| low_<0.5 | 128 | 33% | 0 | 81 | 47 | 0 |
| mid_0.5-0.85 | 128 | 57% | 7 | 110 | 11 | 0 |

## Confusion matrix (rows=LLM, cols=auto)

|  | Equivalent | Complementary | Divergent | Contradictory |
|---|---:|---:|---:|---:|
| Equivalent | 118 | 5 | 1 | 2 |
| Complementary | 7 | 67 | 111 | 13 |
| Divergent | 4 | 4 | 48 | 6 |
| Contradictory | 0 | 0 | 0 | 0 |

## Batch

- batch_id: `batch_6aced6017d148190b8df257f2c329981`
- status: `completed`
- requests: {'completed': 386, 'failed': 0, 'total': 386}

## n=150 subset re-judge stability

Re-judged labels match prior n=150 run on **143/150** (95.3%) pairs.
