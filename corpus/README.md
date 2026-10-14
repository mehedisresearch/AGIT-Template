# Study corpus (N ≈ 1,000 repos)

Canonical 1,000-repo AGIT study universe: **500 top + 500 bottom** by stars.

Provenance: `Agents Instruction/ai_agent_instruction_files/` (inventories + instruction-file extracts).  
`corpus_meta.json` records counts (expect **1000** repos, **582** adopters).

## Files

| Path | Role | Approx size |
|---|---|---|
| `repo_list_1000.csv` | One row per repo (metadata + format flags; no file trees) | ~80 KB |
| `top_500_projects_instruction_files.csv` | Top cohort inventory; `files` = instruction paths only | ~160 KB |
| `bottom_500_projects_instruction_files.csv` | Bottom cohort inventory; same schema | ~100 KB |
| `instruction_file_inventory.csv` | Flat list of instruction paths from inventories | ~250 KB |
| `instruction_extracts/` | Per-repo **instruction-file extracts** (not full git clones) | ~35 MB |
| `instruction_extracts.tar.gz` | Portable archive of the same extracts | ~10 MB |
| `labeled_unified_files.tar.gz` | Section-labeled corpus (595 repos / 4468 files incl. SKILL etc.) | ~10 MB |
| `corpus_meta.json` | Counts + provenance | |

## What is *not* shipped

| Artifact | Why omitted |
|---|---|
| Full `top_500_projects_with_files.csv` / `bottom_500_…` (~228 MB) | Contain entire repo file trees; RQ1 only needs instruction paths (shipped above) |
| Full `.git` clones of 1000 repos | Multi-GB; extracts already contain the instruction files used by RQ1–RQ2 |
| Empty placeholder `.git` dirs | Stripped from extracts |

To refresh extracts from GitHub (optional; slow), see `../scripts/fetch_instruction_extracts.sh`.

## Layout of extracts

```
instruction_extracts/
  top_repos/<owner_repo>/{AGENTS.md,CLAUDE.md,.cursor/rules/*,.github/instructions/*,…}
  bottom_repos/<owner_repo>/…
```

These are the inputs walked by `rq2_taxonomy/analysis/analyze_rq2_taxonomy.py` (paper **N = 3,387** four-format files).
