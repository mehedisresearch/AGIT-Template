#!/usr/bin/env python3
"""Restrict AGIT-Instruct to RQ2's four formats and rebuild generic splits.

RQ2 formats (path-based, from universal_agent_instruction_study.ipynb):
  - AGENTS: basename agents.md
  - CLAUDE: basename claude.md
  - Copilot: copilot-instructions.md OR *.instructions.md OR /.github/instructions/
  - Cursor: .cursorrules OR /.cursor/rules/

Filters agit_instruct_with_summary + generic_intent_full to those formats,
keeps ≥2 sections (already true for the instruct pairs), then re-runs
category-stratified repo-holdout splits (k=25) into
exports/agit_instruct_4fmt_splits/.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from build_agit_generic_splits import build_splits

ROOT = Path(__file__).resolve().parent
PROC_BASE = (
    Path("/gpuhome/shanto1/Agents Instruction/ai_agent_instruction_files")
    / "parsedAndProcessedDatasetForRQ3"
)


def classify_path(path: str) -> set[str]:
    """RQ2 classify_path — map repo-relative path to zero or more of the four types."""
    p = path.replace("\\", "/")
    pl = p.lower()
    name = Path(pl).name
    found: set[str] = set()
    if name == "agents.md":
        found.add("AGENTS")
    if name == "claude.md":
        found.add("CLAUDE")
    if name == ".cursorrules" or "/.cursor/rules/" in pl or pl.endswith("/.cursor/rules"):
        found.add("Cursor")
    if (
        name == "copilot-instructions.md"
        or name.endswith(".instructions.md")
        or "/.github/instructions/" in pl
    ):
        found.add("Copilot")
    return found


def primary_type(types: set[str]) -> str | None:
    for t in ("AGENTS", "CLAUDE", "Copilot", "Cursor"):
        if t in types:
            return t
    return None


def load_processed_4fmt() -> list[dict]:
    rows: list[dict] = []
    for split in ("top_repos_processed", "bottom_repos_processed"):
        d = PROC_BASE / split
        if not d.exists():
            raise FileNotFoundError(d)
        for jp in sorted(d.glob("*.json")):
            data = json.loads(jp.read_text())
            repo = data.get("folder_name") or jp.stem
            for f in data.get("files", []):
                path = f.get("source_path") or ""
                types = classify_path(path)
                if not types:
                    continue
                rows.append(
                    {
                        "repo": repo,
                        "format": f.get("source_format"),
                        "path": path,
                        "n_sections": len(f.get("sections") or []),
                        "rq2_type": primary_type(types),
                        "rq2_types": sorted(types),
                    }
                )
    return rows


def format_name_bucket(fmt: str) -> str | None:
    """Fallback when path is unavailable (should rarely be needed)."""
    fl = (fmt or "").lower()
    if fl == "agents.md":
        return "AGENTS"
    if fl == "claude.md":
        return "CLAUDE"
    if fl == "copilot-instructions.md" or fl.endswith(".instructions.md"):
        return "Copilot"
    if fl == "rule.md":
        return "Cursor"
    return None


def match_pairs_to_4fmt(
    pairs: list[dict], proc: list[dict]
) -> tuple[list[int], list[str], dict]:
    """Return kept pair indices, rq2_type per kept row, and filter stats."""
    by_rfn: dict[tuple, list[dict]] = defaultdict(list)
    for x in proc:
        by_rfn[(x["repo"], x["format"], x["n_sections"])].append(x)

    used: set[int] = set()
    keep_idx: list[int] = []
    keep_types: list[str] = []

    def take(cands: list[dict]) -> dict | None:
        for x in cands:
            xid = id(x)
            if xid not in used:
                used.add(xid)
                return x
        return None

    for i, p in enumerate(pairs):
        key = (p["repo"], p["format"], p["n_sections"])
        pick = take(by_rfn.get(key, []))
        if pick is None:
            # Ambiguous n_sections: any unused same repo+format
            cands = [
                x
                for x in proc
                if x["repo"] == p["repo"]
                and x["format"] == p["format"]
                and id(x) not in used
            ]
            pick = take(cands)
        if pick is None:
            # Last resort: format-name heuristic (path-classifiable formats only)
            bucket = format_name_bucket(p["format"])
            if bucket is None:
                continue
            keep_idx.append(i)
            keep_types.append(bucket)
            continue
        keep_idx.append(i)
        keep_types.append(pick["rq2_type"])

    stats = {
        "n_processed_4fmt": len(proc),
        "n_processed_4fmt_repos": len({x["repo"] for x in proc}),
        "n_processed_4fmt_ge2": sum(1 for x in proc if x["n_sections"] >= 2),
        "n_processed_4fmt_ge2_repos": len(
            {x["repo"] for x in proc if x["n_sections"] >= 2}
        ),
        "processed_4fmt_by_type": dict(Counter(x["rq2_type"] for x in proc)),
        "processed_4fmt_ge2_by_type": dict(
            Counter(x["rq2_type"] for x in proc if x["n_sections"] >= 2)
        ),
    }
    return keep_idx, keep_types, stats


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
        default=str(ROOT / "exports" / "agit_instruct_4fmt_splits"),
    )
    parser.add_argument("--k_per_category", type=int, default=25)
    parser.add_argument("--val_fraction", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pairs = json.loads(Path(args.pairs_file).read_text())
    generic = json.loads(Path(args.generic_files).read_text())
    if len(pairs) != len(generic):
        raise RuntimeError(
            f"pairs/generic length mismatch: {len(pairs)} vs {len(generic)}"
        )
    for i, (p, g) in enumerate(zip(pairs, generic)):
        if p["repo"] != g["repo"] or p["format"] != g.get("format"):
            raise RuntimeError(f"alignment mismatch at {i}")

    n_before = len(pairs)
    n_repos_before = len({p["repo"] for p in pairs})
    min_sec = min(p["n_sections"] for p in pairs)
    # All instruct pairs already passed ≥2 in build_dataset
    assert min_sec >= 2

    proc = load_processed_4fmt()
    keep_idx, keep_types, proc_stats = match_pairs_to_4fmt(pairs, proc)

    filtered_pairs = []
    filtered_generic = []
    for new_i, (old_i, rq2_type) in enumerate(zip(keep_idx, keep_types)):
        p = dict(pairs[old_i])
        g = dict(generic[old_i])
        p["rq2_format"] = rq2_type
        g["rq2_format"] = rq2_type
        g["idx"] = old_i  # preserve original corpus index for provenance
        filtered_pairs.append(p)
        filtered_generic.append(g)

    # ≥2 already applied on instruct pairs; report intersection with processed ge2
    n_after_fmt = len(filtered_pairs)
    n_repos_after_fmt = len({p["repo"] for p in filtered_pairs})
    ge2_pairs = [p for p in filtered_pairs if p["n_sections"] >= 2]
    n_after_ge2 = len(ge2_pairs)
    n_repos_after_ge2 = len({p["repo"] for p in ge2_pairs})
    by_type = Counter(p["rq2_format"] for p in filtered_pairs)
    by_format_raw = Counter(p["format"] for p in filtered_pairs)

    pairs_out = out_dir / "agit_instruct_4fmt_with_summary.json"
    generic_out = out_dir / "generic_files_4fmt.json"
    pairs_out.write_text(json.dumps(filtered_pairs, ensure_ascii=False, indent=2))
    generic_out.write_text(json.dumps(filtered_generic, ensure_ascii=False, indent=2))

    # Rebuild stratified splits on filtered corpus
    split_args = argparse.Namespace(
        pairs_file=str(pairs_out),
        generic_files=str(generic_out),
        output_dir=str(out_dir),
        k_per_category=args.k_per_category,
        val_fraction=args.val_fraction,
        seed=args.seed,
    )
    split_meta = build_splits(split_args)

    filter_meta = {
        "criteria": {
            "formats": "RQ2 four formats only (AGENTS, CLAUDE, Copilot, Cursor)",
            "format_rules": {
                "AGENTS": "basename agents.md / AGENTS.md",
                "CLAUDE": "basename claude.md / CLAUDE.md",
                "Copilot": (
                    "copilot-instructions.md OR *.instructions.md "
                    "OR path under /.github/instructions/"
                ),
                "Cursor": ".cursorrules OR path under /.cursor/rules/",
            },
            "min_sections": 2,
            "min_sections_reason": (
                "enough structure for section-level supervision / template categories"
            ),
            "excluded": [
                "SKILL.md",
                "GEMINI.md",
                "standalone README.md (not under .cursor/rules/)",
                "other non-RQ2 formats",
            ],
            "alignment": (
                "pairs matched to RQ2 path-classified files in the labeled corpus "
                "via (repo, source_format, n_sections)"
            ),
        },
        "rq2_reference": {
            "n_files_labeled": 3387,
            "files_per_type": {
                "AGENTS.md": 1677,
                "CLAUDE.md": 1107,
                "Copilot instructions": 538,
                "Cursor rules": 65,
            },
            "note": (
                "RQ2 labeled 3387 instruction files across the four formats "
                "(16-category coding). Cursor listed-path count is 65; "
                "22 Cursor files with ≥2 parseable sections appear in AGIT-Instruct."
            ),
        },
        "counts": {
            "before_format_filter": {
                "pairs": n_before,
                "repos": n_repos_before,
                "min_n_sections": min_sec,
                "note": "combined agit_instruct_with_summary (already ≥2 sections)",
            },
            "processed_corpus_4fmt": {
                "files": proc_stats["n_processed_4fmt"],
                "repos": proc_stats["n_processed_4fmt_repos"],
                "by_type": proc_stats["processed_4fmt_by_type"],
            },
            "after_format_filter": {
                "pairs": n_after_fmt,
                "repos": n_repos_after_fmt,
                "by_rq2_type": dict(by_type),
                "by_source_format_top": by_format_raw.most_common(30),
            },
            "after_ge2_sections": {
                "pairs": n_after_ge2,
                "repos": n_repos_after_ge2,
                "by_rq2_type": dict(Counter(p["rq2_format"] for p in ge2_pairs)),
                "note": "instruct pairs already required ≥2 sections; no further drop",
            },
            "processed_4fmt_ge2": {
                "files": proc_stats["n_processed_4fmt_ge2"],
                "repos": proc_stats["n_processed_4fmt_ge2_repos"],
                "by_type": proc_stats["processed_4fmt_ge2_by_type"],
            },
            "agit_instruct": {
                "repos": n_repos_after_ge2,
                "files": n_after_ge2,
            },
        },
        "split_summary": {
            "n_train": split_meta["n_train"],
            "n_val": split_meta["n_val"],
            "n_test": split_meta["n_test"],
            "n_train_repos": split_meta["n_train_repos"],
            "n_val_repos": split_meta["n_val_repos"],
            "n_test_repos": split_meta["n_test_repos"],
            "n_eligible_pairs": split_meta["n_eligible_pairs"],
            "n_eligible_repos": split_meta["n_eligible_repos"],
        },
        "sources": {
            "pairs_file": args.pairs_file,
            "generic_files": args.generic_files,
            "processed_corpus": str(PROC_BASE),
        },
    }
    (out_dir / "filter_meta.json").write_text(json.dumps(filter_meta, indent=2))

    # Enrich split_meta with format filter note
    split_meta = json.loads((out_dir / "split_meta.json").read_text())
    split_meta["format_filter"] = "RQ2 four formats (AGENTS/CLAUDE/Copilot/Cursor)"
    split_meta["n_agit_instruct_pairs"] = n_after_ge2
    split_meta["n_agit_instruct_repos"] = n_repos_after_ge2
    split_meta["per_format_rq2"] = dict(by_type)
    (out_dir / "split_meta.json").write_text(json.dumps(split_meta, indent=2))

    write_filter_readme(out_dir, filter_meta, split_meta)
    write_paper_narrative(out_dir, filter_meta, split_meta)

    print("\n=== AGIT-Instruct (4 formats + ≥2 sections) ===")
    print(f"X repos = {n_repos_after_ge2}")
    print(f"Y files = {n_after_ge2}")
    print(f"per-format: {dict(by_type)}")
    print(
        f"splits: train={split_meta['n_train']} val={split_meta['n_val']} "
        f"test={split_meta['n_test']}"
    )


def write_filter_readme(out_dir: Path, filter_meta: dict, split_meta: dict) -> None:
    c = filter_meta["counts"]
    x = c["agit_instruct"]["repos"]
    y = c["agit_instruct"]["files"]
    by = c["after_ge2_sections"]["by_rq2_type"]
    text = f"""# AGIT-Instruct — RQ2 four-format filter

## Inclusion criteria

Keep only RQ2’s four instruction formats (same path rules as RQ2 labeling):

| RQ2 type | Path / name rule |
|---|---|
| **AGENTS** | basename `AGENTS.md` / `agents.md` |
| **CLAUDE** | basename `CLAUDE.md` / `claude.md` |
| **Copilot** | `copilot-instructions.md`, other `*.instructions.md`, or under `/.github/instructions/` |
| **Cursor** | `.cursorrules` or under `/.cursor/rules/` (includes `RULE.md` and other rule basenames) |

**Excluded:** `SKILL.md`, `GEMINI.md`, standalone `README.md`, and any other non-RQ2 format.
(A file named `README.md` under `.cursor/rules/` is kept as **Cursor**, matching RQ2 path rules.)

**Section filter:** keep files with **≥ 2 sections** (enough structure for section-level supervision and the 16-category template). The combined instruct pairs already applied this filter; the four-format subset does not drop further on section count.

Pairs are aligned to RQ2 path-classified files via `(repo, source_format, n_sections)`.

## Counts

| Stage | Repos | Files / pairs |
|---|---:|---:|
| Combined instruct corpus (pre–format filter; already ≥2 sections) | {c['before_format_filter']['repos']} | {c['before_format_filter']['pairs']} |
| After RQ2 four-format filter | {c['after_format_filter']['repos']} | {c['after_format_filter']['pairs']} |
| After ≥2 sections (no extra drop) | **{x}** | **{y}** |

**AGIT-Instruct (paper):** **{x} repos, {y} files/pairs**

### Per-format (after four-format + ≥2 sections)

| Format | Files |
|---|---:|
| AGENTS | {by.get('AGENTS', 0)} |
| CLAUDE | {by.get('CLAUDE', 0)} |
| Copilot | {by.get('Copilot', 0)} |
| Cursor | {by.get('Cursor', 0)} |

RQ2 labeled **3387** four-format files (AGENTS 1677 / CLAUDE 1107 / Copilot 538 / Cursor 65) under the 16-category scheme. Cursor’s listed-path count (65) is larger than the parseable Cursor subset retained here ({by.get('Cursor', 0)} with ≥2 sections).

## Generic-intent splits (rebuilt)

Category-stratified **repo-holdout** split (`k={split_meta['k_per_category']}` per AGIT category, seed={split_meta['seed']}), re-run on the four-format eligible pairs only.

| Split | Pairs | Repos |
|---|---:|---:|
| train | {split_meta['n_train']} | {split_meta['n_train_repos']} |
| val | {split_meta['n_val']} | {split_meta['n_val_repos']} |
| test | {split_meta['n_test']} | {split_meta['n_test_repos']} |
| eligible (n_sections>0 & n_with_intent>0) | {split_meta['n_eligible_pairs']} | {split_meta['n_eligible_repos']} |

## Outputs

| File | Description |
|---|---|
| `agit_instruct_4fmt_with_summary.json` | Filtered pairs (inputs include repo summary) |
| `generic_files_4fmt.json` | Matching generic-intent files |
| `generic_instruct_{{train,val,test}}.json` | Repo-holdout stratified splits |
| `split_meta.json` | Split sizes, per-category test coverage |
| `filter_meta.json` | Machine-readable filter stats |
| `PAPER_NARRATIVE.md` | Paper-ready construction paragraph |

## Rebuild

```bash
cd ~/agit_model
python3 build_agit_instruct_4fmt.py
```
"""
    (out_dir / "FILTER_README.md").write_text(text)


def write_paper_narrative(out_dir: Path, filter_meta: dict, split_meta: dict) -> None:
    c = filter_meta["counts"]
    x = c["agit_instruct"]["repos"]
    y = c["agit_instruct"]["files"]
    by = c["after_ge2_sections"]["by_rq2_type"]
    narrative = f"""# AGIT-Instruct construction (paper narrative)

We construct **AGIT-Instruct** from agent instruction files in the same four formats studied in RQ2—**AGENTS.md**, **CLAUDE.md**, **GitHub Copilot instructions** (`copilot-instructions.md` and other `*.instructions.md`), and **Cursor rules** (`.cursorrules` / `.cursor/rules/`)—consistent with RQ2’s labeling of **3,387** files under a shared **16-category** taxonomy. We exclude other instruction-like artifacts (e.g., SKILL, GEMINI, and standalone README-style files) so the generation benchmark stays aligned with RQ2’s four-format scope.

Because section-level supervision and template-category coverage require meaningful internal structure, we retain only files with **at least two sections**. After this filter, AGIT-Instruct contains **{x:,} repositories** and **{y:,} instruction files** (AGENTS: {by.get('AGENTS', 0):,}; CLAUDE: {by.get('CLAUDE', 0):,}; Copilot: {by.get('Copilot', 0):,}; Cursor: {by.get('Cursor', 0):,}).

For each retained file we convert gold sections into **generic intents** under the same **16 taxonomy categories**, stripping repository-specific commands, paths, and stack details while preserving instructional meaning. Model inputs include a short repository summary plus the requested section categories; targets are the generic-intent Markdown files.

We then form train/validation/test splits with **repository-level holdout** (no repository appears in more than one split). The **test set** is selected first via **category-stratified quotas** (up to **k = {split_meta['k_per_category']}** high-coverage files per AGIT category; union of selections), so evaluation covers the full template section inventory as far as the corpus allows. Remaining repositories are split into train/validation (approximately 85%/15%). In the four-format release this yields **{split_meta['n_train']:,} / {split_meta['n_val']:,} / {split_meta['n_test']:,}** pairs (train/val/test). **Zero-shot and RAG generation** (and any fine-tuned baselines) are run on this held-out test set.
"""
    (out_dir / "PAPER_NARRATIVE.md").write_text(narrative)


if __name__ == "__main__":
    main()
