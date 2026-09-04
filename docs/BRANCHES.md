# Branch & tag map

Quick map of what's what after the 2026-09-04 branch cleanup. Local is intentionally kept
to just the two active branches; everything else is either a tag or lives on origin.

## Active branches (local + origin)
| Branch | Purpose |
|---|---|
| `main` | Trunk / tool release line (the parse-patrol MCP harness). |
| `paper/full-version` | Active research follow-up. Holds the submitted ML4Molecules 2026 workshop paper, the `agent_study/` harness-effectiveness experiment, and the DVC-tracked data. Developing toward a fuller paper. |

## Preservation tags
| Tag | What |
|---|---|
| `ml4molecules-2026-submission` | Clean, DVC-tracked snapshot of the submitted paper (PDF, `main_v2.tex`, figure, data pointers). |
| `as-submitted-raw` | Exact commit at the 13:59 AOE submission deadline (`952dac5`). |
| `v0.0.1-beta`, `v0.0.2-beta` | Earlier tool releases. |

## Archived branches
Stale local-only work, commits preserved as **tags** (also pushed to origin) — recover
with `git checkout -b <name> <tag>`: `archive/cclib`, `archive/claude-desktop`,
`archive/post-merge-hotfixes`.

The heavier **Nov-2025 paper-submission** backup is instead a **DVC-tracked git bundle**
(`archive/paper-submission-20251114.bundle`, ~2 MB on the Hetzner remote) — kept out of
git refs because of its binary assets. See `archive/README.md` to restore.

## On origin only (not checked out locally)
Kept because they hold unique unmerged work or belong to collaborators. Fetch with
`git fetch origin <name> && git checkout <name>`.
- **Feature / WIP:** `ase-parser`, `ase-parser-copy`, `paper-submission`,
  `32-provide-installation-instructions`, `add-iodata-parser`, `fix-cclib`, `pipelines`,
  `polish-docs`, `remote_mcp_setup`, `14-async-research-and-testing`,
  `2-deploy-resource-code-documentation`.
- **Collaborators:** `chrisdev`, `chrisdev_`, `chrisdev_bak`, `paper-notes-sascha`.

## What the 2026-09-04 cleanup did
- **Deleted (work already contained elsewhere):** `agent-scaffold-study` (identical to
  `paper/full-version`), `parser-reliability-benchmark` + `claude-instructions` (absorbed
  into `paper/full-version`), `add-typechecking` (in `main`). The first three were also
  removed from origin.
- **Pruned locally, kept on origin:** `ase-parser`, `ase-parser-copy`, `paper-submission`,
  `32-provide-installation-instructions` (unique work, still recoverable from origin).
- **Untouched:** `main`, all collaborator branches, old feature branches on origin, release
  tags, and the DVC data.
