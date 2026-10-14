# AGIT-Instruct — RQ2 four-format filter

## Inclusion criteria

Keep only RQ2’s four instruction formats (same path rules as RQ2 labeling):

| RQ2 type | Path / name rule |
|---|---|
| **AGENTS** | basename `AGENTS.md` / `agents.md` |
| **CLAUDE** | basename `CLAUDE.md` / `claude.md` |
| **Copilot** | `copilot-instructions.md`, other `*.instructions.md`, or under `/.github/instructions/` |
| **Cursor** | `.cursorrules` or under `/.cursor/rules/` (includes `RULE.md` and other rule basenames) |

**Excluded:** `SKILL.md`, `GEMINI.md`, standalone `README.md`, and any other non-RQ2 format. (A file named `README.md` under `.cursor/rules/` is kept as **Cursor**, matching RQ2 path rules.)

**Section filter:** keep files with **≥ 2 sections** (enough structure for section-level supervision and the 16-category template). The combined instruct pairs already applied this filter; the four-format subset does not drop further on section count.

Pairs are aligned to RQ2 path-classified files via `(repo, source_format, n_sections)`.

## Counts

| Stage | Repos | Files / pairs |
|---|---:|---:|
| Combined instruct corpus (pre–format filter; already ≥2 sections) | 557 | 3889 |
| After RQ2 four-format filter | 552 | 2853 |
| After ≥2 sections (no extra drop) | **552** | **2853** |

**AGIT-Instruct (paper):** **552 repos, 2853 files/pairs**

### Per-format (after four-format + ≥2 sections)

| Format | Files |
|---|---:|
| AGENTS | 1565 |
| CLAUDE | 819 |
| Copilot | 447 |
| Cursor | 22 |

RQ2 labeled **3387** four-format files (AGENTS 1677 / CLAUDE 1107 / Copilot 538 / Cursor 65) under the 16-category scheme. Cursor’s listed-path count (65) is larger than the parseable Cursor subset retained here (22 with ≥2 sections).

## Generic-intent splits (rebuilt)

Category-stratified **repo-holdout** split (`k=25` per AGIT category, seed=42), re-run on the four-format eligible pairs only.

| Split | Pairs | Repos |
|---|---:|---:|
| train | 1432 | 404 |
| val | 321 | 66 |
| test | 75 | 64 |
| eligible (n_sections>0 & n_with_intent>0) | 2568 | 534 |

## Outputs

| File | Description |
|---|---|
| `train.json` / `val.json` / `test.json` | **Official** repo-holdout stratified splits (aliases of `generic_instruct_*`) |
| `test_eval_62.json` | Four-system scored eval subset (not the official test definition) |
| `BENCHMARK.md` | Paper-facing official numbers + filtration steps |
| `provenance/agit_instruct_4fmt_with_summary.json` | Filtered pairs (inputs include repo summary) |
| `provenance/generic_files_4fmt.json` | Matching generic-intent files |
| `split_meta.json` | Split sizes, per-category test coverage |
| `filter_meta.json` | Machine-readable filter stats |
| `PAPER_NARRATIVE.md` | Paper-ready construction paragraph |

## Rebuild

```bash
cd ~/agit_model
python3 build_agit_instruct_4fmt.py
```
