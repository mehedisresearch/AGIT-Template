# RQ2 — Taxonomy summary (from packaged tables)

- Files: **3387** (expect 3387)
- Files per type: {'CLAUDE.md': 1107, 'Cursor rules': 65, 'Copilot instructions': 538, 'AGENTS.md': 1677}
- Category coding note: Manual coding labels (16-category taxonomy; paper presentation)

## File stats

| type                 |   n_files |   median_chars |   mean_chars |   median_headings |   vocab_heads |   mean_categories |
|:---------------------|----------:|---------------:|-------------:|------------------:|--------------:|------------------:|
| AGENTS.md            |      1677 |           5043 |         7496 |                 9 |         13529 |              9.56 |
| CLAUDE.md            |      1107 |           3903 |         6010 |                 8 |          7669 |              8.59 |
| Cursor rules         |        65 |           1677 |         3022 |                 6 |           591 |              6.46 |
| Copilot instructions |       538 |           3262 |         5986 |                 8 |          5881 |              8.38 |

## Heading Jaccard (vocabulary)

| type_a       | type_b               |   jaccard_headings |   jaccard_categories |   intersect_headings |   union_headings |   |A|_heads |   |B|_heads |
|:-------------|:---------------------|-------------------:|---------------------:|---------------------:|-----------------:|------------:|------------:|
| AGENTS.md    | CLAUDE.md            |             0.2329 |                    1 |                 4005 |            17193 |       13529 |        7669 |
| AGENTS.md    | Cursor rules         |             0.0071 |                    1 |                   99 |            14021 |       13529 |         591 |
| AGENTS.md    | Copilot instructions |             0.0539 |                    1 |                  993 |            18417 |       13529 |        5881 |
| CLAUDE.md    | Cursor rules         |             0.0109 |                    1 |                   89 |             8171 |        7669 |         591 |
| CLAUDE.md    | Copilot instructions |             0.0503 |                    1 |                  649 |            12901 |        7669 |        5881 |
| Cursor rules | Copilot instructions |             0.0138 |                    1 |                   88 |             6384 |         591 |        5881 |

Within-repo pair rows: **358**

## Category prevalence (pct of files)

| category                             |   AGENTS.md |   CLAUDE.md |   Cursor rules |   Copilot instructions |   n_types_ge5pct |
|:-------------------------------------|------------:|------------:|---------------:|-----------------------:|-----------------:|
| 1. Project overview / purpose        |        48.6 |        39.5 |           23.1 |                   42.8 |                4 |
| 2. Repository structure              |        77.5 |        68.3 |           69.2 |                   67.8 |                4 |
| 3. Build / run / install             |        87.1 |        71.2 |           55.4 |                   70.1 |                4 |
| 4. Test / CI commands                |        79.5 |        62.1 |           36.9 |                   57.8 |                4 |
| 5. Code style / formatting           |        51.9 |        49   |           50.8 |                   58.9 |                4 |
| 6. Architecture / design constraints |        60.7 |        58.3 |           44.6 |                   55   |                4 |
| 7. Domain models / key abstractions  |        69.5 |        64   |           50.8 |                   59.9 |                4 |
| 8. API / interface contracts         |        64.3 |        55.6 |           52.3 |                   51.9 |                4 |
| 9. Do / Don't rules                  |        80.1 |        69.8 |           84.6 |                   90.5 |                4 |
| 10. Security / secrets               |        36.3 |        29.9 |           21.5 |                   32   |                4 |
| 11. Performance                      |        32.7 |        39.2 |           26.2 |                   36.2 |                4 |
| 12. Git / PR / commit conventions    |        58.1 |        48.8 |           15.4 |                   52.8 |                4 |
| 13. Tooling-specific agent config    |        76.3 |        81.8 |           36.9 |                   61.9 |                4 |
| 14. Examples / few-shot snippets     |        71.7 |        64.1 |           60   |                   57.4 |                4 |
| 15. Ownership / contacts             |        25.6 |        17.9 |           15.4 |                   16.2 |                4 |
| 16. Maintenance / when to update     |        36.6 |        39.7 |            3.1 |                   26.8 |                3 |
