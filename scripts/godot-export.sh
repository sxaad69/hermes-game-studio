#!/bin/bash
# Headless Godot web export for a project on the VPS.
# Usage: godot-export.sh <project_dir> <export_preset_name> [output_dir]
# Requires godot binary + web export templates installed.
set -euo pipefail
PROJECT="${1:?project_dir required}"
PRESET="${2:-Web}"
OUT="${3:-$PROJECT/build/web}"
echo "Exporting $PROJECT (preset $PRESET) -> $OUT"
godot --headless --path "$PROJECT" --export-release "$PRESET" "$OUT/index.html"
echo "Export complete: $OUT"
du -sh "$OUT" 2>/dev/null || true
