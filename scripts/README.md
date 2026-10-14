# Package helper scripts

| Script | Purpose |
|---|---|
| `fetch_instruction_extracts.sh` | Optional GitHub sparse-clone rebuild of instruction extracts (prefer shipped `corpus/instruction_extracts.tar.gz`) |
| `fetch_aidev_cache.sh` | Copy/download full `pr_commit_details.parquet` (~463 MB) for RQ3 re-derivation |
| `pack_data.py` | Regenerates `corpus/` + `*/data/` from the study root (maintainer use) |

```bash
chmod +x fetch_*.sh
./fetch_aidev_cache.sh
./fetch_instruction_extracts.sh   # slow; usually unnecessary
```
