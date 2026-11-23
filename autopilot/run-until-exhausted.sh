#!/usr/bin/env bash
# Run the autopilot until the model quota is exhausted.
#
# Exit codes from the driver:
#   0 finished   3 quota exhausted   4 blocked   5 stalled
# Anything else is treated as transient and retried after a pause.
#
# Usage:
#   bash autopilot/run-until-exhausted.sh
#   bash autopilot/run-until-exhausted.sh --max-hours 8 --print-timeout 45m
set -uo pipefail

REPO="${IDP_REPO:-/home/harish/IDP-LOCAL}"
cd "$REPO" || { echo "repo not found: $REPO" >&2; exit 1; }

PAUSE="${IDP_RETRY_PAUSE:-120}"
ATTEMPT=0

while :; do
  ATTEMPT=$((ATTEMPT + 1))
  echo
  echo "=== autopilot run $ATTEMPT · $(date -Is) ==="
  python3 autopilot/autopilot.py --until-exhausted "$@"
  rc=$?

  case $rc in
    0) echo "=== finished cleanly ==="; break ;;
    3) echo "=== quota exhausted — stopping. Re-run after your limits reset. ==="; break ;;
    4) echo "=== blocked — a human is needed. See autopilot/state.json ==="; break ;;
    5) echo "=== state machine stalled — inspect state.json ==="; break ;;
    *) echo "=== exit $rc — transient? retrying in ${PAUSE}s ==="; sleep "$PAUSE" ;;
  esac

  [ "$ATTEMPT" -ge "${IDP_MAX_RESTARTS:-50}" ] && { echo "=== restart cap reached ==="; break; }
done
