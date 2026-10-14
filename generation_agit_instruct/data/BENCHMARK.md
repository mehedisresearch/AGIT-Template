# AGIT-Instruct — Official Benchmark

Canonical four-format generation benchmark after filtration.  
Machine-readable twin: `split_meta.json`.

## Official split (use these numbers in the paper)

| Split | # files | # repos | # category instances |
|---|---:|---:|---:|
| **train** | **1,432** | **404** | **4,178** |
| **val** | **321** | **66** | **1,006** |
| **test** | **62** | **52** | **556** |
| **Total (in splits)** | **1,815** | **522** | **5,740** |

Official files:

- `data/train.json`
- `data/val.json`
- `data/test.json`

**Category instance** = occurrence of a particular taxonomy category in an instruction file (length of `categories_present` / gold AGIT sections with generic intent). Verified on `test.json`: **556**.

Training and validation are **repository-disjoint** from the 62 test files (verified: 0 shared repos).

### Corpus after filtration (before split)

| Quantity | Value |
|---|---:|
| Files / pairs | **2,853** |
| Repositories | **552** |
| AGENTS / CLAUDE / Copilot / Cursor | 1,565 / 819 / 447 / 22 |

## Filtration pipeline (numbered)

1. **Starting universe (combined instruct pairs).** Combined AGIT-Instruct pairs already requiring **≥ 2 sections**: **3,889** files / **557** repos (includes non–RQ2 formats such as SKILL / GEMINI).
2. **RQ2 four formats only.** Keep AGENTS.md / CLAUDE.md / Copilot instructions (`copilot-instructions.md`, `*.instructions.md`, `/.github/instructions/`) / Cursor rules (`.cursorrules`, `/.cursor/rules/`). **Drop** SKILL.md, GEMINI.md, standalone README.md, and other non-RQ2 formats. → **2,853** files / **552** repos.
3. **≥ 2 sections.** Required for section-level / category-level evaluation; already satisfied by the combined instruct corpus → **no further drop** (still **2,853** / **552**).
4. **Generic-intent eligibility.** Keep pairs with `n_sections > 0` and `n_with_intent > 0`. → **2,568** eligible files / **534** repos (**285** ineligible).
5. **Repository-level holdout for train / val.** Seed **42**. From eligible repos, form a category-stratified held-out pool (union of up to **k = 25** high-coverage files per AGIT category); other files from held-out repos are dropped (not used for train/val). Remaining repos → train / val (~85% / 15%). → **1,432** train / **321** val files (**404** / **66** repos).
6. **Official test = 62-file eval set.** The test partition is the four-format evaluation set used for multi-system scoring: mixed-format fulltest **n = 77** → drop SKILL×14 + GEMINI×1 → **n = 62** files / **52** repos / **556** category instances. Train and val contain **no** repositories that appear in these 62 files.

**Final official splits:** **1,432 / 321 / 62** files (train / val / test); **404 / 66 / 52** repos; **4,178 / 1,006 / 556** category instances.

## Paper-ready paragraph

We construct AGIT-Instruct from the four instruction formats analyzed in our empirical study. We retain files containing at least two sections to support category-level evaluation and restrict the corpus to AGENTS.md, CLAUDE.md, Copilot instruction files, and Cursor rules. The eligible corpus comprises 2,853 files from 552 repositories: 1,565 AGENTS.md, 819 CLAUDE.md, 447 Copilot instruction files, and 22 Cursor rule files. We organize instruction sections according to the 16-category taxonomy used to derive our template. After generic-intent filtering and repository-level holdout, we obtain repository-disjoint training and validation partitions of 1,432 and 321 files. The evaluation set contains 62 files with 556 reference category instances. A category instance represents the occurrence of a particular category within an instruction file. The training partition supplies examples for retrieval and model adaptation.

## Paper-ready table

| Split | # files | # repos | # category instances |
|---|---:|---:|---:|
| Train | 1,432 | 404 | 4,178 |
| Validation | 321 | 66 | 1,006 |
| Test | 62 | 52 | 556 |
