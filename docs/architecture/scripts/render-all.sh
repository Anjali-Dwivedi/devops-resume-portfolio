#!/usr/bin/env bash
# Render Mermaid sources → SVG + PNG for GitHub Markdown embedding.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/sources"
OUT="$ROOT/rendered"
THEME="$SRC/theme.json"
PUPPETEER="$ROOT/puppeteer.json"
mkdir -p "$OUT"

export PUPPETEER_EXECUTABLE_PATH="/usr/bin/google-chrome-stable"

render_one() {
  local in="$1"
  local base
  base="$(basename "$in" .mmd)"
  echo "==> Rendering $base"
  npx --yes @mermaid-js/mermaid-cli@11.4.0 \
    -i "$in" \
    -o "$OUT/${base}.svg" \
    -c "$THEME" \
    -p "$PUPPETEER" \
    -b transparent \
    -w 1600 \
    -H 1000
  npx --yes @mermaid-js/mermaid-cli@11.4.0 \
    -i "$in" \
    -o "$OUT/${base}.png" \
    -c "$THEME" \
    -p "$PUPPETEER" \
    -b "#F4F7FA" \
    -w 1600 \
    -H 1000 \
    -s 2
}

shopt -s nullglob
for f in "$SRC"/*.mmd; do
  render_one "$f"
done

echo "Rendered files:"
ls -la "$OUT"
