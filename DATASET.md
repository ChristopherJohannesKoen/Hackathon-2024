# Dataset And Artifact Policy

## Current State
This repository currently includes:
- Raw and transformed cloud billing CSV datasets
- Preprocessed ML outputs
- Runtime CSV slices per cloud service
- Some generated frontend/static artifacts

Based on a local scan, tracked content is large (about 0.92 GB total), with several very large CSV files.

## What Is Currently Tracked
Representative tracked data categories:

1. Source or base billing data
- `SRC/server/bigData.csv`
- `SRC/Data/gcp_billing_data_20240816 - gcp_billing_data_20240816.csv`
- Related copies under `visualization`, `SRC/Data/Prophet`, and `SRC/christiaan_data`

2. Derived ML and preprocessing outputs
- `SRC/Data/LSTM/preprocessed_data.csv`
- `SRC/Data/LSTM/original_and_combined_scores*.csv`
- `SRC/Data/LSTM/predictions*.csv`

3. Runtime service data
- `SRC/server/runTimeData/<service>/data.csv`
- `SRC/server/runTimeData/<service>/pateStandard...ProcessedData.csv`

4. Local environment and generated bundles (currently tracked in parts)
- `.venv/*`
- `localhost_3000/*`

## What Is Generated (And Should Usually Not Be Versioned)
- Python virtual environments (`.venv/`)
- Build output and static app snapshots (`localhost_3000/`, `.next/`, `dist/`, `build/`)
- Cache/scraper folders (`hts-cache/`)
- Runtime or local-only logs and temp files
- Recreated runtime artifacts where deterministic regeneration is possible

## Recommendation: Move Large Data To LFS Or Releases
For long-term GitHub maintainability:

1. Use Git LFS for large, versioned datasets
- Large CSV files that must stay in-repo history should move to LFS.

2. Use GitHub Releases (or external object storage) for non-versioned data drops
- Keep only small samples in Git for development.

3. Keep reproducible generation scripts in Git
- Retain scripts and metadata needed to recreate generated outputs.

## Suggested Classification
- Keep in Git:
  - Source code
  - Docs
  - Small sample datasets
  - Configs and schema files
- Move to LFS/Releases:
  - Large raw datasets
  - Preprocessed full-size outputs
  - Model binaries and heavy experiment artifacts
- Ignore:
  - Local envs
  - Caches
  - Build output
  - Local runtime-only files

## Next Cleanup Milestone
See [REPO_HYGIENE.md](./REPO_HYGIENE.md) for a lightweight cleanup baseline to prepare a public-quality repository snapshot.
