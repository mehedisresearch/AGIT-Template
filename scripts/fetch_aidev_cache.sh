#!/usr/bin/env bash
# Fetch the full AIDev-pop parquet cache needed to re-run analyze_rq3_maintenance.py.
# The package already ships derived tables (rq3_instruction_events.csv, etc.) and a
# slim aidev_cache/ under rq3_maintenance/data/ (all tables except full pr_commit_details).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-${ROOT}/rq3_maintenance/data/aidev_cache}"
mkdir -p "${DEST}"

STUDY_DEFAULT="/gpuhome/shanto1/Agents Instruction/ai_agent_instruction_files/aidev_cache"
HF_DATASET="${HF_DATASET:-hao-li/AIDev}"

if [[ -f "${STUDY_DEFAULT}/pr_commit_details.parquet" ]]; then
  echo "Copying full pr_commit_details.parquet from study cache..."
  cp -f "${STUDY_DEFAULT}/pr_commit_details.parquet" "${DEST}/"
  # Refresh smaller tables if missing
  for f in repository.parquet pull_request.parquet pr_task_type.parquet pr_reviews.parquet pr_commits.parquet; do
    if [[ ! -f "${DEST}/${f}" && -f "${STUDY_DEFAULT}/${f}" ]]; then
      cp -f "${STUDY_DEFAULT}/${f}" "${DEST}/"
    fi
  done
  echo "OK -> ${DEST}/pr_commit_details.parquet ($(du -h "${DEST}/pr_commit_details.parquet" | cut -f1))"
  exit 0
fi

echo "Study cache not found at: ${STUDY_DEFAULT}"
echo "Falling back to Hugging Face dataset: ${HF_DATASET}"
echo "Requires: pip install datasets huggingface_hub pyarrow"
python3 - "$DEST" "$HF_DATASET" <<'PY'
import sys
from pathlib import Path
dest = Path(sys.argv[1])
ds_name = sys.argv[2]
try:
    from datasets import load_dataset
except ImportError as e:
    raise SystemExit("Install datasets: pip install datasets pyarrow") from e

# AIDev-pop tables used by RQ3 (names may vary by dataset revision)
wanted = {
    "pr_commit_details": "pr_commit_details.parquet",
    "pull_request": "pull_request.parquet",
    "repository": "repository.parquet",
    "pr_task_type": "pr_task_type.parquet",
    "pr_reviews": "pr_reviews.parquet",
    "pr_commits": "pr_commits.parquet",
}
print(f"Loading {ds_name} (this can take a while / several GB)...")
# Try loading each config/split if present; otherwise dump known local cache paths.
from huggingface_hub import snapshot_download
path = snapshot_download(repo_id=ds_name, repo_type="dataset")
print("Downloaded snapshot to", path)
# Copy any matching parquet filenames into DEST
import shutil
for p in Path(path).rglob("*.parquet"):
    if p.name in wanted.values() or p.stem in wanted:
        shutil.copy2(p, dest / p.name)
        print("copied", p.name)
print("Done. Point AGIT_STUDY_ROOT so that aidev_cache/ resolves to", dest.parent if dest.name == "aidev_cache" else dest)
PY
