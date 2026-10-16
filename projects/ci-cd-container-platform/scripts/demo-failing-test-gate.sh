#!/usr/bin/env bash
# Shows how a failing test blocks the pipeline (temporary intentional failure).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

FAIL_FILE="tests/test_intentional_fail.py"
cleanup() { rm -f "$FAIL_FILE"; }
trap cleanup EXIT

cat > "$FAIL_FILE" <<'PY'
def test_intentional_pipeline_blocker():
    assert False, "intentional failure to demonstrate CI test gate"
PY

echo "==> Running pytest; expect non-zero exit"
if pytest -q; then
  echo "ERROR: expected pytest failure" >&2
  exit 1
fi
echo "OK: failing tests would block deployment promotion"
