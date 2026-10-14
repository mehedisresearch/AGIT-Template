#!/usr/bin/env bash
# Optional: rebuild instruction_extracts/ from GitHub using corpus inventories.
# Prefer the shipped tarball (corpus/instruction_extracts.tar.gz) for replication.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CORPUS="${ROOT}/corpus"
OUT="${CORPUS}/instruction_extracts_fetched"
DEPTH="${CLONE_DEPTH:-1}"

mkdir -p "${OUT}/top_repos" "${OUT}/bottom_repos"

fetch_cohort() {
  local cohort="$1"
  local csv="${CORPUS}/${cohort}_500_projects_instruction_files.csv"
  python3 - "$csv" "$OUT" "$cohort" "$DEPTH" <<'PY'
import csv, json, os, subprocess, sys
from pathlib import Path

csv_path, out_root, cohort, depth = sys.argv[1:5]
out = Path(out_root) / f"{cohort}_repos"
out.mkdir(parents=True, exist_ok=True)

with open(csv_path, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Only adopters with instruction paths need clones for RQ2-style extracts.
rows = [r for r in rows if int(r.get("has_any") or 0) == 1]
print(f"{cohort}: cloning {len(rows)} adopter repos (depth={depth})")

for i, row in enumerate(rows, 1):
    full = row["full_name"]
    folder = full.replace("/", "_")
    dest = out / folder
    files = json.loads(row["files"]) if row.get("files") else []
    if dest.exists():
        print(f"[{i}/{len(rows)}] skip existing {folder}")
        continue
    url = f"https://github.com/{full}.git"
    tmp = dest.with_name(folder + ".__tmp")
    if tmp.exists():
        subprocess.run(["rm", "-rf", str(tmp)], check=False)
    print(f"[{i}/{len(rows)}] {full}")
    r = subprocess.run(
        ["git", "clone", "--depth", str(depth), "--filter=blob:none", "--sparse", url, str(tmp)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"  WARN clone failed: {r.stderr.strip()[:200]}")
        continue
    # sparse-checkout requested paths (+ common instruction globs)
    patterns = sorted(set(files) | {
        "AGENTS.md", "CLAUDE.md", ".cursorrules",
        ".cursor/rules", ".github/instructions",
        ".github/copilot-instructions.md",
    })
    subprocess.run(["git", "-C", str(tmp), "sparse-checkout", "set", "--cone", *patterns], check=False)
    # Keep only instruction-like files
    keep = []
    for p in tmp.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        rel = str(p.relative_to(tmp)).replace("\\", "/")
        pl = rel.lower()
        name = Path(pl).name
        if (
            name in ("agents.md", "claude.md", ".cursorrules")
            or "/.cursor/rules/" in ("/" + pl + "/")
            or name == "copilot-instructions.md"
            or name.endswith(".instructions.md")
            or "/.github/instructions/" in ("/" + pl + "/")
            or name.endswith(".mdc")
        ):
            keep.append(rel)
    dest.mkdir(parents=True, exist_ok=True)
    for rel in keep:
        src = tmp / rel
        dst = dest / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
    subprocess.run(["rm", "-rf", str(tmp)], check=False)
    print(f"  kept {len(keep)} files")
PY
}

fetch_cohort top
fetch_cohort bottom
echo "Done. Extracts under ${OUT}"
echo "To use: export AGIT_STUDY_ROOT=${OUT}  (or replace corpus/instruction_extracts)"
