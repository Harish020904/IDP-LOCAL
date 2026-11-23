---
name: obsidian-sync
description: Writes and updates project notes in the Obsidian second-brain vault at /home/harish/obsidian/IoT23 Dataset, keeping it in sync with the git repository. Use when a stage note, decision, review or weekly log needs to be readable in Obsidian.
---

# obsidian-sync

The Obsidian vault is the **human-readable** brain. Git is the **machine-readable** record. Neither is allowed to be the only copy of anything.

- Vault: `/home/harish/obsidian/IoT23 Dataset` (override with `$IDP_VAULT`)
- Repo: `/home/harish/IDP-LOCAL` (override with `$IDP_REPO`)

## The layout decision

Do not copy notes into the vault by hand. Symlink the repo's docs into the vault, so Obsidian shows the real files and git sees the same bytes:

```
/home/harish/obsidian/IoT23 Dataset/
├── 00 Home.md                  # hand-written index, links to everything
├── 01 Stages/                  -> symlink to $IDP_REPO/docs/02-stages
├── 02 Decisions/               -> symlink to $IDP_REPO/docs/01-decisions
├── 03 Reports/                 -> symlink to $IDP_REPO/docs/04-reports
├── 04 Reviews/                 -> symlink to $IDP_REPO/docs/03-reviews
├── 05 Log/                     -> symlink to $IDP_REPO/docs/05-log
└── 06 Learning/                # genuinely vault-only: your own notes
```

Run `sync_brain.sh` to create or repair the links:

```bash
bash .agents/skills/obsidian-sync/scripts/sync_brain.sh
```

Obsidian follows symlinks on Linux. If your setup does not, fall back to `rsync --delete` on the five folders — but then remember that the vault is a copy and git is the truth.

## Frontmatter for every note

```yaml
---
stage: 06
status: done          # todo | active | review | done
milestone: M3
pr: 7
tags: [iot23, stage, cleaning]
date: 2026-12-04
---
```

Obsidian's graph and dataview queries depend on this. A note without frontmatter is a note nobody finds again.

## Linking conventions

- Link stages to the stage before and after: `[[Stage 05 — Data quality]]` / `[[Stage 07 — Feature governance]]`.
- Link a decision from the stage that made it: `[[ADR-0002 Scenario-based split]]`.
- Link a review from the PR it reviewed: `[[PR-006 review]]`.
- One concept per note. A stage note is not the place for a library tutorial; that belongs in `06 Learning/`.

## What goes in the vault only

Notes about your own understanding: how Polars expressions differ from Pandas, why Little's Law matters, what a Zeek header is. These are the actual "second brain" — they are not project artifacts and they do not belong in the repo.

## What must never live in the vault only

Stage notes, decisions, reports, review records. Those are project artifacts and they must be in git, reviewed by the manager, before they exist anywhere else.

Rule of thumb: if the manager would review it, it goes in the repo first and the vault second.
