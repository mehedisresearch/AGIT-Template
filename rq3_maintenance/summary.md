# RQ3 — Maintenance summary (from packaged tables)

- Instruction-file touches: **2146** (CSV rows=2146)
- Unique files: **448** (lifecycle rows=448)
- Repos / PRs: **283 / 943**
- Heading edits (all16 Σ total_edits): **5396** (expect 5396)

## Lifecycle medians by format

- AGENTS.md: n=157, med_touches=2.0, med_churn=0.0, abandoned=38.2%
- CLAUDE.md: n=122, med_touches=2.0, med_churn=0.014, abandoned=34.4%
- Cursor rules: n=20, med_touches=2.0, med_churn=0.399, abandoned=40.0%
- Copilot instructions: n=149, med_touches=2.0, med_churn=0.0, abandoned=47.7%

## Kruskal–Wallis

         metric      H            p
      n_touches  7.468 5.839626e-02
      n_authors 11.777 8.186219e-03
owner_top_share 12.480 5.906079e-03
    churn_ratio 31.017 8.429217e-07
      span_days  1.857 6.026658e-01
     n_modified  5.483 1.396511e-01

## Cliffs' δ (first 12 rows)

         metric         a                    b  delta  n_a  n_b
      n_touches AGENTS.md            CLAUDE.md -0.081  157  122
      n_touches AGENTS.md Copilot instructions  0.098  157  149
      n_touches CLAUDE.md Copilot instructions  0.170  122  149
      n_touches AGENTS.md         Cursor rules  0.119  157   20
      n_authors AGENTS.md            CLAUDE.md -0.086  157  122
      n_authors AGENTS.md Copilot instructions -0.160  157  149
      n_authors CLAUDE.md Copilot instructions -0.069  122  149
      n_authors AGENTS.md         Cursor rules -0.082  157   20
owner_top_share AGENTS.md            CLAUDE.md  0.089  157  122
owner_top_share AGENTS.md Copilot instructions  0.167  157  149
owner_top_share CLAUDE.md Copilot instructions  0.069  122  149
owner_top_share AGENTS.md         Cursor rules  0.088  157   20

## Category durability (all 16)

                         category  heading_adds  heading_dels  total_edits  survive_rate
            Build / run / install           959           239         1198         0.801
                 Do / Don't rules           685           145          830         0.825
    Tooling-specific agent config           383           149          532         0.720
Architecture / design constraints           329            87          416         0.791
             Repository structure           336            78          414         0.812
    Git / PR / commit conventions           309            51          360         0.858
               Test / CI commands           266            58          324         0.821
          Code style / formatting           215            57          272         0.790
       Project overview / purpose           190            66          256         0.742
 Domain models / key abstractions           156            64          220         0.709
        API / interface contracts           135            33          168         0.804
                      Performance           131            34          165         0.794
               Security / secrets           116            18          134         0.866
     Examples / few-shot snippets            73            19           92         0.793
     Maintenance / when to update             7             1            8         0.875
             Ownership / contacts             7             0            7         1.000

Notes: {'source': 'AIDev-pop pr_commit_details filtered to instruction paths', 'timestamps': 'PR merged_at (fallback created_at)', 'trigger_coding': 'Automated heuristic; dual-coder κ pending', 'abandoned_def': 'Exactly one touch in AIDev-pop window'}
