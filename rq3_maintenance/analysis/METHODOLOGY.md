# RQ3 methodology (maintenance dynamics)

**RQ.** How do agent instruction files evolve — durable vs ephemeral content, and what triggers updates?

## Data

AIDev-pop tables (`pr_commit_details`, `pull_request`, `repository`, `pr_task_type`, `pr_reviews`) filtered to instruction paths. Event time = PR `merged_at` (fallback `created_at`).

Corpus: **2,146** touches · **448** files · **283** repos · **943** PRs.

## Analysis

1. Per-file lifecycle: touches, authors, owner share, churn, span → patterns (abandoned / sparse / burst-taper / continuous).
2. Kruskal–Wallis + Cliff’s δ across formats on five metrics.
3. Trigger heuristics (reactive / proactive / proactive co-change).
4. Heading add/delete survive rates from patches; category durability (12-cat pilot + **all-16** remap for paper 5,396).

## Outputs

See parent folder. Package-only narrative: `../summary.md`.
