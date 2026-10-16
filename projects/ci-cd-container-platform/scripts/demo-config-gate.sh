#!/usr/bin/env bash
# Demonstrates a failing quality gate (bad prod config) and a passing gate.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT"

echo "==> Expect FAIL for bad-prod-sqlite.json"
if python3 scripts/validate_config.py configs/bad-prod-sqlite.json; then
  echo "ERROR: bad config unexpectedly passed" >&2
  exit 1
fi
echo "OK: bad config blocked"

echo "==> Expect PASS for prod.json"
python3 scripts/validate_config.py configs/prod.json
echo "OK: good config allowed"

echo "==> Config gate demo succeeded"
