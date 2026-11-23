#!/usr/bin/env bash
# Create the IoT-23 repository tree, place the archives, and verify every path.
#
#   bash setup-tree.sh                # create + extract + verify
#   bash setup-tree.sh --verify-only  # verify only
set -uo pipefail

REPO="${IDP_REPO:-/home/harish/IDP-LOCAL}"
VAULT="${IDP_VAULT:-/home/harish/obsidian/IoT23 Dataset}"
DL="${IDP_DOWNLOADS:-$HOME/Downloads}"
VERIFY_ONLY=0
[ "${1:-}" = "--verify-only" ] && VERIFY_ONLY=1

fail=0
ok()   { printf '  \033[32mOK\033[0m       %s\n' "$1"; }
miss() { printf '  \033[31mMISSING\033[0m  %s\n' "$1"; fail=$((fail+1)); }

if [ "$VERIFY_ONLY" -eq 0 ]; then
  echo "==> repository: $REPO"
  mkdir -p "$REPO" || { echo "cannot create $REPO" >&2; exit 1; }
  # first run: put this script where it belongs so later runs are one command
  if [ ! -f "$REPO/setup-tree.sh" ] && [ -f "$0" ] && [ "$(readlink -f "$0")" != "$(readlink -f "$REPO/setup-tree.sh")" ]; then
    cp "$0" "$REPO/setup-tree.sh" && echo "    copied setup-tree.sh into the repo"
  fi
  cd "$REPO" || exit 1

  echo "==> directory skeleton"
  mkdir -p docs/00-project docs/01-decisions docs/02-stages docs/03-reviews docs/04-reports docs/05-log
  mkdir -p notebooks src/iot23 tests/unit tests/gates tests/fixtures out data/raw data/prepared
  mkdir -p .agents/agents .agents/rules .agents/skills .github autopilot/logs

  echo "==> extracting archives (order matters: 1, 2, 3)"
  for z in IDP-LOCAL-agents.zip IDP-LOCAL-autopilot.zip IDP-LOCAL-autopilot-v2.zip; do
    if [ -f "$DL/$z" ]; then
      unzip -oq "$DL/$z" -d "$REPO" && echo "    $z"
    else
      echo "    $z not found in $DL — skipped"
    fi
  done

  echo "==> branch"
  if git rev-parse --git-dir >/dev/null 2>&1; then
    if git show-ref --verify --quiet refs/heads/EDL-Pipeline; then
      echo "    EDL-Pipeline exists"
    else
      git switch -c EDL-Pipeline 2>/dev/null && echo "    created EDL-Pipeline" || echo "    could not create branch (commit something first)"
    fi
  else
    echo "    not a git repository — run: git init && git remote add origin https://github.com/Harish020904/IDP-LOCAL.git"
  fi
fi

cd "$REPO" 2>/dev/null || { echo "repo not found: $REPO" >&2; exit 1; }

echo
echo "==> verifying"
for f in \
  AGENTS.md AUTOPILOT.md KAGGLE-COMPUTE.md PLACEMENT.md \
  .agents/hooks.json \
  .agents/agents/manager.md .agents/agents/data-engineer.md .agents/agents/tester.md .agents/agents/autopilot.md \
  .agents/rules/data-safety.md .agents/rules/kaggle-compute.md .agents/rules/stage-gate.md \
  .agents/rules/python-conventions.md .agents/rules/model-routing.md .agents/rules/autopilot-guardrails.md \
  .agents/skills/kaggle-run/SKILL.md .agents/skills/kaggle-run/scripts/kaggle_run.sh \
  .agents/skills/stage-gate/SKILL.md \
  .agents/skills/obsidian-sync/SKILL.md .agents/skills/obsidian-sync/scripts/sync_brain.sh \
  autopilot/autopilot.py autopilot/model_router.py autopilot/policy.yaml \
  autopilot/run-until-exhausted.sh autopilot/hooks/hooks.py \
  autopilot/prompts/build.md autopilot/prompts/review.md autopilot/prompts/verify.md \
  .github/CODEOWNERS .github/pull_request_template.md \
  notebooks/kernel-metadata.template.json ; do
  [ -e "$f" ] && ok "$f" || miss "$f"
done

echo
echo "==> directories"
for d in docs/00-project docs/01-decisions docs/02-stages docs/03-reviews docs/04-reports docs/05-log \
         notebooks src/iot23 tests/unit tests/gates out data/raw data/prepared ; do
  [ -d "$d" ] && ok "$d/" || miss "$d/"
done

echo
echo "==> process documents in docs/ (from round 1)"
for f in docs/build-guide.md docs/manager.md docs/data-engineer.md docs/tester.md ; do
  [ -e "$f" ] && ok "$f" || miss "$f (mv it in: mv build-guide.md docs/)"
done

echo
echo "==> vault"
if [ -d "$VAULT" ]; then
  for d in "01 Stages" "02 Decisions" "03 Reports" "04 Reviews" "05 Log"; do
    [ -e "$VAULT/$d" ] && ok "$VAULT/$d" || miss "$VAULT/$d (run sync_brain.sh)"
  done
else
  miss "vault directory $VAULT"
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "all checks passed. next: agy agents  →  agy"
  exit 0
else
  echo "$fail check(s) failed — see MISSING above"
  exit 1
fi
