#!/usr/bin/env bash
# Link the repo's docs into the Obsidian vault so both see the same files.
set -euo pipefail

REPO="${IDP_REPO:-/home/harish/IDP-LOCAL}"
VAULT="${IDP_VAULT:-/home/harish/obsidian/IoT23 Dataset}"

[ -d "$REPO" ]  || { echo "repo not found: $REPO" >&2; exit 1; }
mkdir -p "$VAULT"

link() {  # link <vault-name> <repo-subdir>
  local name="$1" target="$REPO/$2"
  mkdir -p "$target"
  local dest="$VAULT/$name"
  if [ -L "$dest" ]; then
    rm "$dest"
  elif [ -e "$dest" ]; then
    echo "skip: $dest exists and is not a symlink (move it first)" >&2
    return
  fi
  ln -s "$target" "$dest"
  echo "linked $name -> $target"
}

link "01 Stages"    docs/02-stages
link "02 Decisions" docs/01-decisions
link "03 Reports"   docs/04-reports
link "04 Reviews"   docs/03-reviews
link "05 Log"       docs/05-log

mkdir -p "$VAULT/06 Learning"

if [ ! -f "$VAULT/00 Home.md" ]; then
  cat > "$VAULT/00 Home.md" <<'HOME'
---
tags: [iot23, home]
---
# IoT-23 Dataset Engineering

Thirteen stages, four milestones, one notebook and one PR each.

## Stages
0 Definition · 1 Acquisition · 2 Inventory · 3 Schema · 4 Profiling · 5 Quality
6 Cleaning · 7 Features · 8 Split · 9 Preprocess · 10 Storage · 11 Integrity · 12 Imbalance

## Milestones
- M1 Foundation — stages 0-3 — `v1-inspected`
- M2 Understanding — stages 4-5 — `v2-audited`
- M3 Transformation — stages 6-9 — `v3-transformed`
- M4 Product — stages 10-12 — `v5-validated`

## Invariants
Raw immutable · labels preserved · no balancing · no scenario crossing · fit on train only
HOME
  echo "created $VAULT/00 Home.md"
fi

echo "done. vault: $VAULT"
