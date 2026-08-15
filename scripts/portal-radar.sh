#!/bin/bash
# Portal radar sweep — fetch new/hot pages from CrazyGames + Poki via jina.ai.
# Usage: portal-radar.sh [output_dir]
# Output: normalized .txt dump per page (post-processing is the worker's job).
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
