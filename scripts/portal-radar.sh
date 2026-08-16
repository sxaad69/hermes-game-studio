#!/bin/bash
# Portal radar sweep — JINA FALLBACK PATH (plan Task 8 Step 2).
# Primary is charts-sweep.sh (CDP-driven, real plays). This script exists for
# when the chromium-cdp daemon (127.0.0.1:9222) is unavailable: it fetches
# new/hot pages from CrazyGames + Poki via jina.ai and dumps normalized .txt
# per page. jina misses JS-rendered play counts (plays=null) — that's why the
# CDP tool replaced it.
# Usage: portal-radar.sh [output_dir]
set -u
OUT="${1:-/tmp/radar}"
mkdir -p "$OUT"
URLS=(
  "https://www.crazygames.com/new"
  "https://www.crazygames.com/hot"
  "https://www.crazygames.com/c/puzzle"
  "https://www.crazygames.com/c/arcade"
  "https://poki.com/en"
)
for u in "${URLS[@]}"; do
  slug=$(echo "$u" | sed 's|https://||; s|/|_|g')
  curl -s -m 60 "https://r.jina.ai/$u" -o "$OUT/$slug.txt" 2>/dev/null
  echo "fetched $u -> $OUT/$slug.txt ($(wc -c < "$OUT/$slug.txt" 2>/dev/null || echo 0) bytes)"
done
