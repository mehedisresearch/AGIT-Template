#!/usr/bin/env python3
"""Build corpus/ + per-RQ data/ inputs for the AGIT replication package."""
from __future__ import annotations

import ast
import csv
import json
import os
import re
import shutil
import tarfile
from collections import Counter
from pathlib import Path

csv.field_size_limit(10**9)

PKG = Path("/gpuhome/shanto1/agit_model/replication_package")
STUDY = Path("/gpuhome/shanto1/Agents Instruction/ai_agent_instruction_files")
AGIT = Path("/gpuhome/shanto1/agit_model")
INTER = AGIT / "interchangeability"

FILE_TYPES = ["AGENTS.md", "CLAUDE.md", "Cursor rules", "Copilot instructions"]
SKIP = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
    "__pycache__",
    ".tox",
    "target",
    "vendor",
    ".next",
    "coverage",
}


def classify_path(path: str) -> set[str]:
    p = path.replace("\\", "/")
    pl = p.lower()
    name = Path(pl).name
    found: set[str] = set()
    if name == "agents.md":
        found.add("AGENTS.md")
    if name == "claude.md":
        found.add("CLAUDE.md")
    if name == ".cursorrules" or "/.cursor/rules/" in pl or pl.endswith("/.cursor/rules"):
        found.add("Cursor rules")
    if (
        name == "copilot-instructions.md"
        or name.endswith(".instructions.md")
        or "/.github/instructions/" in pl
    ):
        found.add("Copilot instructions")
    return found


def ensure(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def copy_file(src: Path, dst: Path) -> int:
    ensure(dst.parent)
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    shutil.copy2(src, dst)
    return dst.stat().st_size


def hardlink_or_copy(src: Path, dst: Path) -> int:
    ensure(dst.parent)
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)
    return dst.stat().st_size


def du(p: Path) -> int:
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


def main() -> None:
    corpus = ensure(PKG / "corpus")
    rq1_data = ensure(PKG / "rq1_adoption" / "data")
    rq2_data = ensure(PKG / "rq2_taxonomy" / "data")
    rq2c_data = ensure(PKG / "rq2_consistency" / "data")
    rq3_data = ensure(PKG / "rq3_maintenance" / "data")

    print("== slim inventories ==")
    repo_rows = []
    instruction_inventory = []

    for cohort, inv_name in [
        ("top", "top_500_projects_with_files.csv"),
        ("bottom", "bottom_500_projects_with_files.csv"),
    ]:
        src = STUDY / inv_name
        out_rows = []
        with open(src, newline="", encoding="utf-8", errors="replace") as f:
            for row in csv.DictReader(f):
                try:
                    files = ast.literal_eval(row["files"]) if row.get("files") else []
                except Exception:
                    files = []
                inst = []
                types: set[str] = set()
                for fp in files:
                    t = classify_path(str(fp))
                    if t:
                        inst.append(str(fp).replace("\\", "/"))
                        types |= t
                out = {
                    "id": row.get("id"),
                    "url": row.get("url"),
                    "full_name": row.get("full_name"),
                    "language": row.get("language") or "Unknown",
                    "license": row.get("license") or "Unknown",
                    "stars": row.get("stars"),
                    "forks": row.get("forks"),
                    "cohort": cohort,
                    "n_instruction_files": len(inst),
                    "has_any": int(len(types) > 0),
                    "files": inst,
                }
                for t in FILE_TYPES:
                    out[f"has_{t}"] = int(t in types)
                out_rows.append(out)
                repo_rows.append(
                    {
                        k: out[k]
                        for k in [
                            "id",
                            "url",
                            "full_name",
                            "language",
                            "license",
                            "stars",
                            "forks",
                            "cohort",
                            "n_instruction_files",
                            "has_any",
                        ]
                        + [f"has_{t}" for t in FILE_TYPES]
                    }
                )
                folder = (row.get("full_name") or "").replace("/", "_")
                for fp in inst:
                    instruction_inventory.append(
                        {
                            "cohort": cohort,
                            "full_name": row.get("full_name"),
                            "repo_folder": folder,
                            "path": fp,
                            "formats": sorted(classify_path(fp)),
                        }
                    )

        slim_name = f"{cohort}_500_projects_instruction_files.csv"
        slim_path = corpus / slim_name
        fieldnames = [
            "id",
            "url",
            "full_name",
            "language",
            "license",
            "stars",
            "forks",
            "cohort",
            "n_instruction_files",
            "has_any",
        ] + [f"has_{t}" for t in FILE_TYPES] + ["files"]
        with open(slim_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in out_rows:
                row = dict(r)
                row["files"] = json.dumps(r["files"])
                w.writerow(row)
        hardlink_or_copy(slim_path, rq1_data / slim_name)
        print(
            f"  {slim_name}: {len(out_rows)} repos, "
            f"{sum(r['n_instruction_files'] for r in out_rows)} inst paths, "
            f"{slim_path.stat().st_size / 1e6:.2f} MB"
        )

    with open(corpus / "repo_list_1000.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(repo_rows[0].keys()))
        w.writeheader()
        w.writerows(repo_rows)

    with open(corpus / "instruction_file_inventory.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f, fieldnames=["cohort", "full_name", "repo_folder", "path", "formats"]
        )
        w.writeheader()
        for r in instruction_inventory:
            row = dict(r)
            row["formats"] = "|".join(r["formats"])
            w.writerow(row)

    meta = {
        "study_root": str(STUDY),
        "n_repos": len(repo_rows),
        "n_top": sum(1 for r in repo_rows if r["cohort"] == "top"),
        "n_bottom": sum(1 for r in repo_rows if r["cohort"] == "bottom"),
        "n_adopters_inventory": sum(int(r["has_any"]) for r in repo_rows),
        "n_instruction_paths_in_inventory": len(instruction_inventory),
        "source_inventories": {
            "top": "top_500_projects_with_files.csv (full tree ~175MB; slimmed)",
            "bottom": "bottom_500_projects_with_files.csv (full tree ~53MB; slimmed)",
        },
        "note": (
            "Slim CSVs keep analyze_rq1_adoption.py-compatible `files` column "
            "with instruction paths only."
        ),
    }
    (corpus / "corpus_meta.json").write_text(json.dumps(meta, indent=2))
    print("  corpus_meta:", meta["n_repos"], "repos;", meta["n_adopters_inventory"], "adopters")

    print("== instruction extracts ==")
    extracts_dir = ensure(corpus / "instruction_extracts")
    for cohort in ["top_repos", "bottom_repos"]:
        src = STUDY / cohort
        dst = extracts_dir / cohort
        if dst.exists():
            shutil.rmtree(dst)

        def ignore(directory, names):
            return [n for n in names if n in {".git", ".DS_Store"}]

        shutil.copytree(src, dst, ignore=ignore)

    tarball = corpus / "instruction_extracts.tar.gz"
    if tarball.exists():
        tarball.unlink()
    with tarfile.open(tarball, "w:gz") as tar:
        tar.add(extracts_dir, arcname="instruction_extracts")
    print(
        f"  extracts={du(extracts_dir)/1e6:.1f}MB "
        f"tarball={tarball.stat().st_size/1e6:.1f}MB "
        f"files={sum(1 for _ in extracts_dir.rglob('*') if _.is_file())}"
    )

    for cohort in ["top_repos", "bottom_repos"]:
        dst = rq2_data / cohort
        if dst.exists() or dst.is_symlink():
            if dst.is_symlink() or dst.is_file():
                dst.unlink()
            else:
                shutil.rmtree(dst)
        os.symlink(os.path.relpath(extracts_dir / cohort, rq2_data), dst)

    print("== RQ2 file records ==")
    src_txt = (PKG / "rq2_taxonomy" / "analysis" / "analyze_rq2_taxonomy.py").read_text()
    ns: dict = {}
    start = src_txt.index("CATEGORIES = {")
    end = src_txt.index("COMPILED =")
    exec(src_txt[start:end], ns)
    CATEGORIES = ns["CATEGORIES"]
    COMPILED = {k: [re.compile(p, re.I) for p in v] for k, v in CATEGORIES.items()}
    HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$", re.M)
    FRONTMATTER_DESC = re.compile(r"^---\s*\n(.*?)\n---", re.S)
    DESC_LINE = re.compile(r"^description:\s*[\'\"]?(.*?)[\'\"]?\s*$", re.M)

    def normalize_heading(h: str) -> str:
        h = h.lower().strip()
        h = re.sub(r"`+", "", h)
        h = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", h)
        h = re.sub(r"[^a-z0-9 /+_.-]+", " ", h)
        h = re.sub(r"\s+", " ", h).strip()
        return h

    def extract_headings(text: str) -> list[str]:
        heads = []
        fm = FRONTMATTER_DESC.match(text)
        if fm:
            for m in DESC_LINE.finditer(fm.group(1)):
                d = normalize_heading(m.group(1))
                if d:
                    heads.append(d)
        for m in HEADING_RE.finditer(text):
            h = normalize_heading(m.group(2))
            if h and h not in ("table of contents", "toc"):
                heads.append(h)
        return heads

    def categorize_text(text: str) -> list[str]:
        sample = text[:50000]
        return sorted(
            cat for cat, pats in COMPILED.items() if any(p.search(sample) for p in pats)
        )

    records = []
    n_err = 0
    for cohort in ["top_repos", "bottom_repos"]:
        root = extracts_dir / cohort
        for repo in sorted(root.iterdir()):
            if not repo.is_dir():
                continue
            for dirpath, dirnames, filenames in os.walk(repo):
                dirnames[:] = [d for d in dirnames if d not in SKIP]
                for fn in filenames:
                    full = Path(dirpath) / fn
                    rel = str(full.relative_to(repo)).replace("\\", "/")
                    types = classify_path(rel)
                    if not types:
                        continue
                    try:
                        text = full.read_text(encoding="utf-8", errors="replace")
                    except Exception:
                        n_err += 1
                        continue
                    records.append(
                        {
                            "cohort": "top" if cohort == "top_repos" else "bottom",
                            "repo": repo.name,
                            "path": rel,
                            "types": sorted(types),
                            "n_headings": len(extract_headings(text)),
                            "n_chars": len(text),
                            "categories": categorize_text(text),
                            "headings": extract_headings(text),
                        }
                    )

    rec_path = rq2_data / "rq2_file_records.jsonl"
    with open(rec_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    by_type = Counter()
    for r in records:
        for t in r["types"]:
            by_type[t] += 1
    (rq2_data / "rq2_file_records_meta.json").write_text(
        json.dumps(
            {
                "n_files": len(records),
                "n_errors": n_err,
                "files_per_type": dict(by_type),
                "paper_n_files": 3387,
                "paper_files_per_type": {
                    "AGENTS.md": 1677,
                    "CLAUDE.md": 1107,
                    "Copilot instructions": 538,
                    "Cursor rules": 65,
                },
                "note": (
                    "Re-extracted from packaged instruction_extracts using the same "
                    "path classifier + keyword category pilot as analyze_rq2_taxonomy.py."
                ),
                "coding": "Automated keyword pilot (same as analysis script).",
            },
            indent=2,
        )
    )
    print(f"  file records: {len(records)} (paper 3387); {dict(by_type)}")

    print("== labeled unified_files ==")
    uf_src = AGIT / "unified_files"
    uf_index = []
    uf_4fmt = []
    for p in sorted(uf_src.glob("*.json")):
        o = json.loads(p.read_text(encoding="utf-8"))
        files_4 = []
        for f in o.get("files", []):
            types = classify_path(f.get("source_path", ""))
            if types:
                files_4.append({**f, "types": sorted(types)})
        uf_index.append(
            {
                "folder_name": o.get("folder_name"),
                "repo_tier": o.get("repo_tier"),
                "language": o.get("language"),
                "stars": o.get("stars"),
                "forks": o.get("forks"),
                "license": o.get("license"),
                "n_files_all": len(o.get("files", [])),
                "n_files_4fmt": len(files_4),
                "formats": sorted({t for f in files_4 for t in f["types"]}),
            }
        )
        if files_4:
            uf_4fmt.append(
                {
                    "folder_name": o.get("folder_name"),
                    "repo_tier": o.get("repo_tier"),
                    "language": o.get("language"),
                    "stars": o.get("stars"),
                    "forks": o.get("forks"),
                    "license": o.get("license"),
                    "files": files_4,
                }
            )

    (rq2_data / "labeled_repo_index.json").write_text(json.dumps(uf_index, indent=2))
    with open(rq2_data / "labeled_files_4fmt.jsonl", "w", encoding="utf-8") as f:
        for o in uf_4fmt:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    n_lab_files = sum(len(o["files"]) for o in uf_4fmt)
    (rq2_data / "labeled_corpus_meta.json").write_text(
        json.dumps(
            {
                "source": "agit_model/unified_files (= study parsedAndProcessedDatasetForRQ3)",
                "n_repos": len(uf_index),
                "n_repos_with_4fmt": len(uf_4fmt),
                "n_files_all_formats": sum(x["n_files_all"] for x in uf_index),
                "n_files_4fmt_path_classified": n_lab_files,
                "note": (
                    "Full labeled corpus (incl. SKILL/GEMINI/README) is "
                    "labeled_unified_files.tar.gz; 4fmt subset is labeled_files_4fmt.jsonl."
                ),
            },
            indent=2,
        )
    )
    uf_tar = rq2_data / "labeled_unified_files.tar.gz"
    if uf_tar.exists():
        uf_tar.unlink()
    with tarfile.open(uf_tar, "w:gz") as tar:
        tar.add(uf_src, arcname="unified_files")
    hardlink_or_copy(uf_tar, corpus / "labeled_unified_files.tar.gz")
    print(
        f"  repos={len(uf_index)} 4fmt_files={n_lab_files} "
        f"tarball={uf_tar.stat().st_size/1e6:.1f}MB"
    )

    print("== RQ2 consistency ==")
    copy_file(INTER / "section_pairs_labeled.jsonl", rq2c_data / "section_pairs_population_3154.jsonl")
    copy_file(INTER / "summary.json", rq2c_data / "population_summary.json")
    copy_file(INTER / "command_conflicts.json", rq2c_data / "command_conflicts.json")
    for name in [
        "rq2_consistency_n150.csv",
        "rq2_consistency_n386.csv",
        "rq2_consistency_scope_audit_n386.csv",
    ]:
        src = PKG / "rq2_consistency" / name
        if src.exists():
            hardlink_or_copy(src, rq2c_data / name)

    n386 = INTER / "llm_judge_n386"
    if (n386 / "sample_definition.json").exists():
        copy_file(n386 / "sample_definition.json", rq2c_data / "rq2_consistency_sample_definition_n386.json")
        hardlink_or_copy(
            n386 / "sample_definition.json",
            PKG / "rq2_consistency" / "rq2_consistency_sample_definition_n386.json",
        )
    if (n386 / "llm_judge_metrics.json").exists():
        copy_file(n386 / "llm_judge_metrics.json", rq2c_data / "rq2_consistency_metrics_n386.json")
        hardlink_or_copy(
            n386 / "llm_judge_metrics.json",
            PKG / "rq2_consistency" / "rq2_consistency_metrics_n386.json",
        )
    if (INTER / "llm_judge_metrics.json").exists():
        copy_file(INTER / "llm_judge_metrics.json", rq2c_data / "rq2_consistency_metrics_n150.json")
        hardlink_or_copy(
            INTER / "llm_judge_metrics.json",
            PKG / "rq2_consistency" / "rq2_consistency_metrics_n150.json",
        )

    analysis_dst = ensure(PKG / "rq2_consistency" / "analysis")
    for src_name, dst_name in [
        ("llm_judge_n386/run_batch_judge_n386.py", "run_batch_judge_n386.py"),
        ("llm_judge_n386/summary.md", "llm_judge_n386_summary.md"),
        ("llm_judge_n386/scope_report_n386.md", "scope_report_n386.md"),
        ("rq2_divergent_scope_report.md", "rq2_divergent_scope_report.md"),
    ]:
        src = INTER / src_name
        if src.exists():
            copy_file(src, analysis_dst / dst_name)
    hardlink_or_copy(rq2c_data / "population_summary.json", analysis_dst / "population_summary.json")

    print("== RQ3 ==")
    for name in [
        "rq3_instruction_events.csv",
        "rq3_file_lifecycle.csv",
        "rq3_category_durability_all16.csv",
        "rq3_category_durability.csv",
        "rq3_cliffs_delta.csv",
        "rq3_kruskal_wallis.csv",
        "rq3_durable_headings.csv",
        "rq3_ephemeral_headings.csv",
        "rq3_results.json",
    ]:
        src = PKG / "rq3_maintenance" / name
        if src.exists():
            hardlink_or_copy(src, rq3_data / name)

    cache_dst = ensure(rq3_data / "aidev_cache")
    cache_src = STUDY / "aidev_cache"
    for name in [
        "repository.parquet",
        "pull_request.parquet",
        "pr_task_type.parquet",
        "pr_reviews.parquet",
        "pr_commits.parquet",
    ]:
        src = cache_src / name
        if src.exists():
            copy_file(src, cache_dst / name)
            print(f"  {name}: {src.stat().st_size/1e6:.1f}MB")

    print("  extracting instruction rows from pr_commit_details...")
    import pandas as pd

    details = pd.read_parquet(cache_src / "pr_commit_details.parquet")
    mask = details["filename"].fillna("").map(lambda p: bool(classify_path(str(p))))
    inst_details = details.loc[mask].copy()
    inst_path = cache_dst / "pr_commit_details_instruction_rows.parquet"
    inst_details.to_parquet(inst_path, index=False)
    print(f"  instruction rows: {len(inst_details)} -> {inst_path.stat().st_size/1e6:.1f}MB")

    (rq3_data / "aidev_cache_meta.json").write_text(
        json.dumps(
            {
                "included": [
                    "repository.parquet",
                    "pull_request.parquet",
                    "pr_task_type.parquet",
                    "pr_reviews.parquet",
                    "pr_commits.parquet",
                    "pr_commit_details_instruction_rows.parquet",
                ],
                "omitted": {
                    "pr_commit_details.parquet": {
                        "bytes": (cache_src / "pr_commit_details.parquet").stat().st_size,
                        "reason": (
                            "Full AIDev-pop commit-file table (~463MB); needed for "
                            "co-change stats in analyze_rq3_maintenance.py. Use "
                            "scripts/fetch_aidev_cache.sh."
                        ),
                    }
                },
                "n_instruction_detail_rows": int(len(inst_details)),
                "shipped_events_csv": (
                    "rq3_instruction_events.csv (n=2146) is the primary derived input."
                ),
            },
            indent=2,
        )
    )

    print("== sizes ==")
    for p in [corpus, rq1_data, rq2_data, rq2c_data, rq3_data]:
        print(f"  {p.relative_to(PKG)}: {du(p)/1e6:.1f} MB")
    print("DONE")


if __name__ == "__main__":
    main()
