# Archived branches (DVC-tracked git bundles)

Heavy or stale branches we don't want cluttering git refs are preserved here as **git
bundles**, tracked by **DVC** — the bytes live on the Hetzner remote, git keeps only a tiny
`*.dvc` pointer. Keeps the repo lean without losing history.

## Contents
| Bundle | What | Size |
|---|---|---|
| `paper-submission-20251114.bundle` | The Nov-2025 FAIRmat `backup/paper-submission-20251114` branch — an earlier paper submission (tex, SVG/PNG figures, InkScape edits). **Incremental** (unique commits on top of `main`); the 14 MB demo video is *not* included, it already lives in `main`. | ~2 MB |

## Restore a bundle
```bash
uv run dvc pull archive/<name>.bundle.dvc                 # fetch from Hetzner
git bundle verify archive/<name>.bundle                    # sanity + shows base commits
git fetch archive/<name>.bundle 'refs/*:refs/restored/*'   # refs appear under refs/restored/
```
Incremental bundles require `main` (their base) to be present.
