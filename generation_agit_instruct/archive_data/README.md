# AGIT-Instruct data

**Start here:** [`BENCHMARK.md`](BENCHMARK.md) — official train / val / test numbers and filtration story.

## Official benchmark splits (use these)

| File | Role | N files | N repos | # category sections |
|---|---|---:|---:|---:|
| `train.json` | Train | **1,432** | **404** | **4,178** |
| `val.json` | Validation | **321** | **66** | **1,006** |
| `test.json` | Official test | **75** | **64** | **642** |
| `test_eval_62.json` | Scored four-system eval subset | **62** | **52** | **556** |

`train.json` / `val.json` / `test.json` are hardlinked aliases of `generic_instruct_{train,val,test}.json`.

## Metadata

| File | Role |
|---|---|
| `BENCHMARK.md` | Paper-facing benchmark definition |
| `benchmark_meta.json` | Machine-readable official numbers |
| `filter_meta.json` | Filtration counts |
| `split_meta.json` | Split construction (seed, k, per-category test coverage) |
| `FILTER_README.md` | Format inclusion rules |
| `PAPER_NARRATIVE.md` | Short construction narrative |

## Provenance (not required for scoring)

`provenance/` holds the full filtered **2,853**-pair corpora used to build the splits (`agit_instruct_pairs_2853.json`, `generic_intent_files_2853.json`, and naming aliases). Keep for rebuild / audit; load `train.json` / `val.json` / `test.json` for the established benchmark.
