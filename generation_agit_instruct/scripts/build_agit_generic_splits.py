#!/usr/bin/env python3
"""Repo-holdout stratified train/val/test AFTER generic intents exist.

Rules:
  - Keep pairs with n_sections > 0 and n_with_intent > 0
  - Repo-level holdout (no repo appears in >1 split)
  - Build TEST first: category-stratified quotas (default k=25 per AGIT category),
    prefer high-coverage files; union of selected repos
  - Remaining repos → train/val (~85/15) with light format stratification on val

Writes exports/agit_instruct_generic_splits/:
  generic_instruct_{train,val,test}.json
  split_meta.json
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from build_manual_section_study import ORDER

ROOT = Path(__file__).resolve().parent


def load_json(path: str | Path):
    with open(path) as f:
        return json.load(f)


def categories_of(generic_row: dict) -> list[str]:
    cats = generic_row.get("categories_present")
    if cats:
        return list(cats)
    out = []
    for s in generic_row.get("sections") or []:
        if s.get("generic_intent") and s.get("category"):
            out.append(s["category"])
    return out


def build_eligible(pairs: list[dict], generic_files: list[dict]) -> list[dict]:
    if len(pairs) != len(generic_files):
        # align by idx when lengths differ (should not happen for full pipeline)
        g_by_idx = {g["idx"]: g for g in generic_files}
        aligned = []
        for i, p in enumerate(pairs):
            g = g_by_idx.get(i)
            if g is None:
                continue
            aligned.append((p, g))
    else:
        aligned = list(zip(pairs, generic_files))

    eligible: list[dict] = []
    for pair, g in aligned:
        n_sec = int(g.get("n_sections") or 0)
        n_intent = int(g.get("n_with_intent") or 0)
        if n_sec <= 0 or n_intent <= 0:
            continue
        if pair["repo"] != g["repo"]:
            raise RuntimeError(
                f"repo mismatch at idx={g.get('idx')}: {pair['repo']} vs {g['repo']}"
            )
        cats = categories_of(g)
        eligible.append(
            {
                "repo": pair["repo"],
                "format": pair["format"],
                "language": pair.get("language") or g.get("language"),
                "tier": pair.get("tier") or g.get("tier"),
                "input": pair["input"],
                "output": g["generic_output"],
                "categories_present": cats,
                "n_categories": len(set(cats)),
                "n_sections": n_sec,
                "n_with_intent": n_intent,
                "src_idx": g.get("idx"),
                "coverage_score": pair.get("coverage_score", n_intent),
            }
        )
    return eligible


def select_test_files(
    eligible: list[dict],
    k: int,
    seed: int,
) -> tuple[list[dict], set[str], dict[str, int]]:
    """Category-stratified test via union of per-category quotas (k files each).

    For each AGIT category, pick up to k high-coverage files (prefer new repos).
    Test rows = union of those selections. Repos touched are holdouts; other files
    from those repos are dropped (not train/val) to avoid mega-repo inflation.
    """
    rng = random.Random(seed)
    for i, row in enumerate(eligible):
        row["_row_id"] = i

    selected_rows: dict[int, dict] = {}
    repos_used: set[str] = set()

    def file_key(row: dict) -> tuple:
        return (
            row["n_with_intent"],
            row["n_categories"],
            row.get("coverage_score") or 0,
            -(row.get("src_idx") or 0),
        )

    def jitter(rows: list[dict]) -> list[dict]:
        if not rows:
            return rows
        ranked = sorted(rows, key=file_key, reverse=True)
        out: list[dict] = []
        i = 0
        while i < len(ranked):
            j = i + 1
            while j < len(ranked) and file_key(ranked[j]) == file_key(ranked[i]):
                j += 1
            block = ranked[i:j]
            rng.shuffle(block)
            out.extend(block)
            i = j
        return out

    def cat_count(cat: str) -> int:
        return sum(1 for r in selected_rows.values() if cat in r["categories_present"])

    for cat in ORDER:
        if cat_count(cat) >= k:
            continue
        primary = [
            r
            for r in eligible
            if cat in r["categories_present"] and r["repo"] not in repos_used
        ]
        secondary = [
            r
            for r in eligible
            if cat in r["categories_present"]
            and r["_row_id"] not in selected_rows
            and r["repo"] in repos_used
        ]
        for row in jitter(primary) + jitter(secondary):
            if cat_count(cat) >= k:
                break
            rid = row["_row_id"]
            if rid in selected_rows:
                continue
            selected_rows[rid] = row
            repos_used.add(row["repo"])

    final_counts: Counter = Counter()
    for row in selected_rows.values():
        for c in set(row["categories_present"]):
            final_counts[c] += 1

    test_rows = sorted(
        selected_rows.values(),
        key=lambda r: (r["repo"], r.get("src_idx") or 0, r["_row_id"]),
    )
    return test_rows, repos_used, dict(final_counts)


def stratified_val_repos(
    remaining_repos: list[str],
    by_repo: dict[str, list[dict]],
    val_fraction: float,
    seed: int,
) -> set[str]:
    """Light format stratification: sample ~val_fraction repos per format bucket."""
    rng = random.Random(seed)
    # dominant format per repo
    fmt_buckets: dict[str, list[str]] = defaultdict(list)
    for repo in remaining_repos:
        formats = Counter(r["format"] for r in by_repo[repo])
        dom = formats.most_common(1)[0][0]
        fmt_buckets[dom].append(repo)

    val_repos: set[str] = set()
    for fmt, repos in fmt_buckets.items():
        repos = list(repos)
        rng.shuffle(repos)
        n_val = int(round(len(repos) * val_fraction))
        # keep at least 1 val repo when bucket is large enough and fraction > 0
        if val_fraction > 0 and len(repos) >= 4:
            n_val = max(1, n_val)
        n_val = min(n_val, max(0, len(repos) - 1))  # leave something for train
        val_repos.update(repos[:n_val])
    return val_repos


def export_split(rows: list[dict]) -> list[dict]:
    keep = (
        "repo",
        "format",
        "language",
        "tier",
        "input",
        "output",
        "categories_present",
        "n_categories",
    )
    return [{k: r[k] for k in keep} for r in rows]


def build_splits(args: argparse.Namespace) -> dict:
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pairs = load_json(args.pairs_file)
    generic = load_json(args.generic_files)
    eligible = build_eligible(pairs, generic)

    by_repo: dict[str, list[dict]] = defaultdict(list)
    for row in eligible:
        by_repo[row["repo"]].append(row)

    test_rows, test_repos, test_cat_counts = select_test_files(
        eligible, k=args.k_per_category, seed=args.seed
    )
    test_ids = {r["_row_id"] for r in test_rows}
    # Drop non-selected files from test holdout repos (prevents mega-repo inflation)
    n_dropped_holdout = sum(
        1
        for row in eligible
        if row["repo"] in test_repos and row["_row_id"] not in test_ids
    )

    remaining = sorted(r for r in by_repo if r not in test_repos)
    val_repos = stratified_val_repos(
        remaining, by_repo, val_fraction=args.val_fraction, seed=args.seed + 1
    )
    train_repos = set(remaining) - val_repos

    def rows_for(repos: set[str]) -> list[dict]:
        out = []
        for repo in sorted(repos):
            files = sorted(
                by_repo[repo],
                key=lambda r: (-r["n_with_intent"], -r["n_categories"], r["src_idx"] or 0),
            )
            out.extend(files)
        return out

    train_rows = rows_for(train_repos)
    val_rows = rows_for(val_repos)

    for name, rows in (("train", train_rows), ("val", val_rows), ("test", test_rows)):
        path = out_dir / f"generic_instruct_{name}.json"
        path.write_text(json.dumps(export_split(rows), ensure_ascii=False, indent=2))
        print(f"{name}: {len(rows)} pairs / {len({r['repo'] for r in rows})} repos -> {path}")

    meta = {
        "seed": args.seed,
        "k_per_category": args.k_per_category,
        "val_fraction": args.val_fraction,
        "filter": "n_sections > 0 and n_with_intent > 0",
        "holdout": "repo-level",
        "test_policy": (
            "union of up to k high-coverage files per AGIT category; "
            "other files from test repos dropped"
        ),
        "n_eligible_pairs": len(eligible),
        "n_eligible_repos": len(by_repo),
        "n_dropped_holdout_files": n_dropped_holdout,
        "n_train": len(train_rows),
        "n_val": len(val_rows),
        "n_test": len(test_rows),
        "n_train_repos": len(train_repos),
        "n_val_repos": len(val_repos),
        "n_test_repos": len(test_repos),
        "test_category_counts": {c: test_cat_counts.get(c, 0) for c in ORDER},
        "test_category_ge_k": {
            c: test_cat_counts.get(c, 0) >= args.k_per_category for c in ORDER
        },
        "source_pairs": str(args.pairs_file),
        "source_generic": str(args.generic_files),
    }
    (out_dir / "split_meta.json").write_text(json.dumps(meta, indent=2))
    readme = out_dir / "README.md"
    if not readme.exists():
        readme.write_text(
            "# AGIT generic-intent splits\n\n"
            "Built AFTER README summaries + full-corpus section genericization.\n\n"
            "- `generic_instruct_{train,val,test}.json` — repo-holdout splits\n"
            "- `split_meta.json` — counts, per-category test coverage, seed\n"
            "- Inputs include `## Repository summary` blocks\n"
            "- Outputs are generic intent Markdown (`generic_output`)\n"
        )
    print(json.dumps(meta, indent=2))
    return meta


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pairs_file",
        default=str(ROOT / "exports" / "agit_instruct_with_summary.json"),
    )
    parser.add_argument(
        "--generic_files",
        default=str(ROOT / "exports" / "generic_intent_full" / "generic_files.json"),
    )
    parser.add_argument(
        "--output_dir",
        default=str(ROOT / "exports" / "agit_instruct_generic_splits"),
    )
    parser.add_argument("--k_per_category", type=int, default=25)
    parser.add_argument(
        "--val_fraction",
        type=float,
        default=0.15,
        help="Fraction of remaining repos for val (default 0.15 → ~85/15)",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    build_splits(args)


if __name__ == "__main__":
    main()
