#!/usr/bin/env bash
# Push a stage notebook to Kaggle, poll to completion, pull the outputs.
# Usage: kaggle_run.sh <stage-number> [--timeout <seconds>] [--interval <seconds>]
set -euo pipefail

STAGE="${1:?usage: kaggle_run.sh <stage-number> [--timeout N] [--interval N]}"
TIMEOUT=3600
INTERVAL=30
shift || true

while [ $# -gt 0 ]; do
  case "$1" in
    --timeout)  TIMEOUT="$2"; shift 2 ;;
    --interval) INTERVAL="$2"; shift 2 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

REPO="${IDP_REPO:-/home/harish/IDP-LOCAL}"
cd "$REPO"

STAGE_DIR=$(ls -d notebooks/stage-"$STAGE"-*/ 2>/dev/null | head -1)
[ -n "$STAGE_DIR" ] || { echo "no notebook directory for stage $STAGE" >&2; exit 1; }
META="$STAGE_DIR/kernel-metadata.json"
[ -f "$META" ] || { echo "missing $META" >&2; exit 1; }

KERNEL_ID=$(python -c "import json,sys;print(json.load(open('$META'))['id'])")
OUT="out/stage-$STAGE"
mkdir -p "$OUT"

echo "==> preflight"
[ -f "$HOME/.kaggle/kaggle.json" ] || { echo "missing ~/.kaggle/kaggle.json" >&2; exit 1; }
kaggle datasets list -m >/dev/null 2>&1 || { echo "kaggle auth check failed" >&2; exit 1; }

echo "==> push $KERNEL_ID"
kaggle kernels push -p "$STAGE_DIR"

echo "==> poll (timeout ${TIMEOUT}s, interval ${INTERVAL}s)"
ELAPSED=0
while :; do
  STATUS=$(kaggle kernels status "$KERNEL_ID" 2>/dev/null | tr -d '\r' | awk '{print $NF}' | tr -d '"')
  echo "    ${ELAPSED}s  $STATUS"
  case "$STATUS" in
    *Complete*) break ;;
    *Error*|*Cancel*) echo "kernel ended: $STATUS" >&2; break ;;
  esac
  [ "$ELAPSED" -ge "$TIMEOUT" ] && { echo "timed out after ${TIMEOUT}s" >&2; break; }
  sleep "$INTERVAL"
  ELAPSED=$((ELAPSED + INTERVAL))
done

echo "==> pull outputs to $OUT"
kaggle kernels output "$KERNEL_ID" -p "$OUT" || true

if [ -f "$OUT/checksums.txt" ]; then
  echo "==> verify checksums"
  ( cd "$OUT" && sha256sum -c checksums.txt ) || echo "CHECKSUM MISMATCH - do not trust this run" >&2
fi

echo "==> log tail"
tail -40 "$OUT/run.log" 2>/dev/null || echo "(no run.log pulled)"

case "$STATUS" in
  *Complete*) echo "OK: $KERNEL_ID complete" ;;
  *)          echo "FAILED: $KERNEL_ID -> $STATUS" >&2; exit 1 ;;
esac
