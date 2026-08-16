#!/bin/bash
# charts-sweep.sh — run the CDP-driven charts sweep (primary radar fetch).
# Replaces jina as the portal-radar fetch (plan Task 8 Step 2); jina stays as
# a fallback in portal-radar.sh when the CDP daemon is down.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${PYTHON:-python3}"

# CDP daemon check (QA's harness)
if ! curl -s -m 5 http://127.0.0.1:9222/json/version >/dev/null 2>&1; then
  echo "charts-sweep: CDP daemon not reachable on 127.0.0.1:9222 — use portal-radar.sh (jina fallback)" >&2
  exit 2
fi

"$PY" "$HERE/tools/charts/fetch_charts.py" "$@"
