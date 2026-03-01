# Repo Hygiene Note

This repository is intentionally preserved as a hackathon snapshot, but it contains large data and generated artifacts that make long-term GitHub maintenance harder.

## Lightweight Hygiene Baseline
1. Keep source code and docs in Git.
2. Keep only small sample datasets in Git where possible.
3. Move large datasets and model artifacts to Git LFS or release assets.
4. Do not commit local virtual environments, caches, or build output.
5. Document how generated artifacts are reproduced (script + input source).
6. Keep pull requests focused and avoid unrelated file churn.

## Immediate Practical Effect
- The root `.gitignore` now blocks common local artifacts from being newly added.
- Existing tracked files remain tracked until explicitly untracked in a future cleanup pass.

## Recommended Follow-Up Cleanup
1. Audit large tracked files and classify into:
   - keep in Git
   - move to LFS
   - publish in release storage
2. Remove tracked local environment/build artifacts from version control history policy going forward.
3. Add a small reproducible sample dataset for local development and CI.
